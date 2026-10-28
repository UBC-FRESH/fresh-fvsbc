"""Compare a run's database against the standalone ``FVSbc``'s own output.

The package's own runs come from the **pinned** source; the standalone binary is built from
**upstream
``main``** (ADR 0008), because the pin's tree-regeneration routines depend on PyFVS's API. So a
difference
between the two is not automatically a defect — it can be source drift. What the comparison proves
is the
other direction: **where the two agree, this project's keyword rendering, tree list and build
reproduce
FVS's own writer**, table by table, for the tables that have no other oracle.

Four of the 31 exposed tables are checked against FVS's own database dump. This is how the rest get
a check.

The binary is not in the repository. Point at it with ``--binary`` or ``FVSBC_STANDALONE``; without
it the
command reports that and exits 2, and the test suite skips.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from fresh_fvsbc.outputs import EXPOSED_TABLES, read_table
from fresh_fvsbc.run import DATABASE_NAME, KEYWORD_FILE_NAME, tree_file_name
from fresh_fvsbc.treelist import FIELD_DESCRIPTORS, READ_COLUMNS

__all__ = [
    "ENV_BINARY",
    "EXPLAINED_COLUMNS",
    "NOT_COMPARABLE",
    "RUN_COLUMNS",
    "Comparison",
    "compare",
    "database_key",
    "input_block",
    "input_database",
    "main",
    "parse_trees",
    "stand_record",
    "standalone_key",
]

#: The environment variable naming the standalone binary.
ENV_BINARY: str = "FVSBC_STANDALONE"

#: The line that ends a tree-data block, as ``intree.f`` reads it.
TREE_END: str = "-999"

#: The keyword that begins the inline tree records in a standalone keyword file.
TREE_DATA_KEYWORD: str = "TREEDATA"

#: The input database's file name, which the ``DSNin`` block names.
INPUT_DATABASE: str = "input.db"

#: The keyword file name the standalone is given.
STANDALONE_KEY: str = "case.key"

#: The columns that name the **run** rather than the stand: FVS mints a fresh case identifier and a
#: timestamp every time it runs, records the keyword file's own name, and stamps the build's version
#: and revision. Two builds cannot agree on any of them, and none of them is a model result.
RUN_COLUMNS: tuple[str, ...] = ("CaseID", "RunDateTime", "KeywordFile", "Version", "RV")

#: Tables one side writes and the other does not, with the reason. A table here is **not compared**,
#: which is different from agreeing; the summary counts them apart for that reason.
NOT_COMPARABLE: dict[str, str] = {
    "FVS_Error": (
        "FVS writes it only when it logs something. The input-database path calls FORKOD with no "
        "location code and logs FVS03, which the keyword path never does, so the standalone writes "
        "the table and this package's run does not"
    ),
    "FVS_Regen_SitePrep": (
        "its PcntNone, PcntMech and PcntBurn come from an UNINITIALISED local: estab.f reads LOAD "
        "at 'IF(LOAD.NE.1) GO TO 249' and only assigns it when the stand is more than 20 years "
        "past inventory or a site-prep activity exists, and esetpr.f assigns it only inside an "
        "activity loop. Measured: LOAD=0 in this build and LOAD=1 in the standalone, so one "
        "samples the stub's 0.75/0.20/0.05 and the other reuses IPPREP and writes 100/0/0. The "
        "two builds disagree by luck of the stack, so the table cannot be compared"
    ),
}

#: Columns whose disagreement is explained, with the reason. Anything not named here is a
#: difference the comparison fails on.
EXPLAINED_COLUMNS: dict[str, dict[str, str]] = {
    "FVS_Cases": {
        "SamplingWt": (
            "FVS copies the sampling weight into the case row from DBSCASE(2), which only "
            "updates a row that already exists; the two drivers create that row at different "
            "points"
        ),
    },
}


@dataclass(frozen=True)
class Comparison:
    """What happened to one table.

    Attributes
    ----------
    table : str
        The table's name.
    status : str
        ``match`` when every comparable value agrees, ``explained`` when the only disagreements are
        named in :data:`EXPLAINED_COLUMNS`, ``not comparable`` when only one side wrote the table
        and :data:`NOT_COMPARABLE` says why, ``differ`` when something is unexplained, and
        ``stale`` when an explanation no longer applies.
    detail : str
        A short explanation, empty for a match.
    """

    table: str
    status: str
    detail: str


def standalone_key(run_key: str, tree_text: str) -> str:
    """Build a keyword file the standalone binary can read from a run's keyword file and tree list.

    The standalone reads the tree records **inline**, between ``TREEDATA`` and the next keyword. A
    run directory keeps them in a separate file, because the package drives FVS through PyFVS's
    step API.

    .. warning::

       **This route is known not to work yet.** ``P45`` found that ``TREEDATA``'s field 1 is a file
       reference number — ``15`` for inline records, ``2`` by default for an external file — and
       that the standalone reads these records as keywords whichever side of the stand setup they
       sit. The route that is known to work is the official case's ``DATABASE ... DSNin ...
       TreeSQL`` block, which needs an input database this module does not write.
       ``notes/triage.md`` carries the detail. Until it is finished the comparison reports
       differences that are this handoff, not the tables.

    Parameters
    ----------
    run_key : str
        The contents of ``run.key``.
    tree_text : str
        The contents of ``run.tre``, which ends with the ``-999`` terminator.

    Returns
    -------
    str
        A keyword file with the tree records inlined.

    Raises
    ------
    ValueError
        If the keyword file carries no ``TREEDATA`` line, because then there is nowhere to put them.
    """
    lines = run_key.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == TREE_DATA_KEYWORD:
            body = tree_text if tree_text.endswith("\n") else tree_text + "\n"
            return (
                "\n".join(lines[: index + 1]) + "\n" + body + "\n".join(lines[index + 1 :]) + "\n"
            )
    raise ValueError(
        f"the keyword file has no {TREE_DATA_KEYWORD} line to put the tree records after"
    )


def _canonical(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a frame whose row order cannot affect equality.

    Parameters
    ----------
    frame : pandas.DataFrame
        The table.

    Returns
    -------
    pandas.DataFrame
        The same values as strings, sorted by every column, with a fresh index.
    """
    text = frame.drop(columns=[name for name in RUN_COLUMNS if name in frame.columns]).astype(str)
    return text.sort_values(by=list(text.columns)).reset_index(drop=True)


def compare(ours: Path, theirs: Path) -> tuple[Comparison, ...]:
    """Compare every exposed table in two run databases.

    Parameters
    ----------
    ours : Path
        This package's database.
    theirs : Path
        The standalone binary's database.

    Returns
    -------
    tuple of Comparison
        One record per table either database holds, ordered by table name, followed by a ``stale``
        record for every explanation that no longer applies.
    """
    mine = {name for name in EXPOSED_TABLES if _has_table(ours, name)}
    other = {name for name in EXPOSED_TABLES if _has_table(theirs, name)}
    results: list[Comparison] = []
    applicable: set[str] = set()
    for name in sorted(mine | other):
        # A table in NOT_COMPARABLE is not compared whatever its presence: the reason may be that
        # only one side writes it, or that both do and the difference is FVS's own rather than this
        # package's. Reporting either as a pass would be a claim the module cannot make.
        if name in NOT_COMPARABLE:
            results.append(Comparison(name, "not comparable", NOT_COMPARABLE[name]))
            continue
        if name not in other or name not in mine:
            side = "the standalone" if name in other else "this package"
            results.append(Comparison(name, "differ", f"only {side} wrote it"))
            continue
        left = _canonical(read_table(ours, name))
        right = _canonical(read_table(theirs, name))
        if list(left.columns) != list(right.columns):
            results.append(Comparison(name, "differ", "the column lists differ"))
            continue
        if left.shape != right.shape:
            results.append(
                Comparison(name, "differ", f"{left.shape[0]} rows here, {right.shape[0]} there")
            )
            continue
        explained = EXPLAINED_COLUMNS.get(name, {})
        if explained and all(column in left.columns for column in explained):
            applicable.add(name)
        if left.equals(right):
            results.append(Comparison(name, "match", ""))
            continue
        results.append(_difference(name, left, right))
    return tuple(results + _stale(results, applicable))


def _difference(name: str, left: pd.DataFrame, right: pd.DataFrame) -> Comparison:
    """Classify a table whose values disagree.

    Parameters
    ----------
    name : str
        The table's name.
    left : pandas.DataFrame
        This package's table, canonicalised.
    right : pandas.DataFrame
        The standalone's table, canonicalised.

    Returns
    -------
    Comparison
        ``explained`` when every differing column is named in :data:`EXPLAINED_COLUMNS`, and
        ``differ`` naming the columns otherwise, because a row count tells a reader nothing about
        which number moved.
    """
    differing = [column for column in left.columns if bool((left[column] != right[column]).any())]
    explained = EXPLAINED_COLUMNS.get(name, {})
    if differing and all(column in explained for column in differing):
        reasons = "; ".join(f"{column}: {explained[column]}" for column in differing)
        return Comparison(name, "explained", reasons)
    rows = int((left != right).any(axis=1).sum())
    return Comparison(name, "differ", f"{rows} row(s) differ in {', '.join(differing)}")


def _stale(results: list[Comparison], applicable: set[str]) -> list[Comparison]:
    """Return a record for every explanation that no longer applies.

    An explanation that has stopped being needed is a claim about the code that is no longer true,
    and leaving it in place would hide the next difference of the same kind. It is reported as an
    error rather than dropped, the rule the mutation harness follows for its anchors.

    Parameters
    ----------
    results : list of Comparison
        The comparisons made so far.
    applicable : set of str
        The tables whose explained columns both databases carry, so an explanation was in scope.

    Returns
    -------
    list of Comparison
        One ``stale`` record per explanation that was not needed.
    """
    stale: list[Comparison] = []
    seen = {result.table: result.status for result in results}
    for table in applicable:
        if seen[table] != "explained":
            stale.append(
                Comparison(table, "stale", "the explained columns now agree; drop the explanation")
            )
    for table in NOT_COMPARABLE:
        if table not in EXPOSED_TABLES:
            stale.append(
                Comparison(
                    table, "stale", "it is not an exposed table; drop the not-comparable entry"
                )
            )
    return stale


def _has_table(database: Path, name: str) -> bool:
    """Say whether a database holds a table.

    Parameters
    ----------
    database : Path
        The database to look in.
    name : str
        The table.

    Returns
    -------
    bool
        ``True`` when the table is there and the database exists.
    """
    if not database.is_file():
        return False
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        row = connection.execute(
            "select count(*) from sqlite_master where type='table' and name = ?", (name,)
        ).fetchone()
        return bool(row and row[0])
    finally:
        connection.close()


def _keyword_fields(key_text: str, name: str) -> list[str]:
    """Return one keyword's parameter fields from a written keyword file.

    Parameters
    ----------
    key_text : str
        The contents of ``run.key``.
    name : str
        The keyword to read.

    Returns
    -------
    list of str
        Its fields, stripped, in order. Empty when the keyword is absent.
    """
    for line in key_text.splitlines():
        if line[:8].strip() != name:
            continue
        return [line[index : index + 10].strip() for index in range(10, len(line), 10)]
    return []


def database_key(run_key: str, database_name: str, stand_id: str) -> str:
    """Build a standalone keyword file that reads its trees from a ``DSNin`` database.

    The tree records and their format are removed: the standalone reads the same trees from the
    database, which is how the official case does it.

    Parameters
    ----------
    run_key : str
        The contents of ``run.key``.
    database_name : str
        The input database's file name, relative to the working directory.
    stand_id : str
        The stand to read.

    Returns
    -------
    str
        The keyword file, with the ``DSNin`` block placed after the run's own ``DATABASE`` block.

    Notes
    -----
    The order is not cosmetic. A ``DATABASE`` block naming ``DSNOut`` is rejected once a case has
    begun, and reading a stand from an input database calls ``FORKOD`` with no location code, which
    logs a warning — and logging a warning writes to the output database, which starts the case. Put
    the output block first and it is opened while the case is still empty; put it second and FVS
    answers ``FVS16``, ignores it, and writes the default tables instead.
    """
    kept: list[str] = []
    in_format = False
    for line in run_key.splitlines():
        stripped = line.strip()
        if stripped == "TREEFMT":
            in_format = True
            continue
        if stripped == "TREEDATA":
            in_format = False
            continue
        if in_format:
            continue
        kept.append(line)
    start = next(
        (index for index, line in enumerate(kept) if line.strip().upper() == "DATABASE"), None
    )
    if start is None:
        return input_block(database_name, stand_id) + "\n".join(kept) + "\n"
    end = _database_block_end(kept, start)
    return (
        "\n".join(kept[: end + 1])
        + "\n"
        + input_block(database_name, stand_id)
        + "\n".join(kept[end + 1 :])
        + "\n"
    )


def _database_block_end(lines: list[str], start: int) -> int:
    """Return the index of the line that ends the ``DATABASE`` block beginning at ``start``.

    Parameters
    ----------
    lines : list of str
        The keyword file's lines.
    start : int
        The index of the line holding ``DATABASE``.

    Returns
    -------
    int
        The index of the block's terminator, or ``start`` when the file has none, which leaves the
        input block where it was rather than dropping the run's own block.
    """
    for index in range(start + 1, len(lines)):
        if lines[index].strip().upper() == "END":
            return index
    return start


def stand_record(key_text: str, stand_id: str, trees: list[dict[str, object]]) -> dict[str, object]:
    """Build the stand row the input database needs from a run's own keywords.

    Parameters
    ----------
    key_text : str
        The contents of ``run.key``.
    stand_id : str
        The stand identifier.
    trees : list of dict
        The parsed trees, used only to count plots when ``DESIGN`` says nothing.

    Returns
    -------
    dict
        Values keyed by the official schema's column names. Everything the keyword set does not
        carry is left out, and the database writes NULL for it. The inventory year is left out even
        when the set carries it, so the standalone reads it from the run's own ``INVYEAR`` in the
        order the run uses; see the comment in the body for the tables that depend on it.
    """
    stand: dict[str, object] = {"Stand_ID": stand_id, "Variant": "BC"}
    # ``Inv_Year`` is deliberately **not** copied from ``INVYEAR``. ``FUELOUT`` and ``POTFIRE``
    # capture the inventory year when they are read, and ``fmdout.f`` and ``fmpofl.f`` treat any
    # positive value as "suppress this report". A stand read from the database sets the year before
    # the fire-model block, and the fuels and potfire tables then never appear; the run's own
    # ``INVYEAR`` keyword sets it in the order the run uses, so the database leaves it NULL.
    site = _keyword_fields(key_text, "SITECODE")
    if len(site) >= 2:
        stand["Site_Species"] = site[0]
        stand["Site_Index"] = float(site[1])
    design = _keyword_fields(key_text, "DESIGN")
    if len(design) >= 7:
        stand["Basal_Area_Factor"] = float(design[0]) if design[0] else None
        stand["Brk_DBH"] = float(design[2]) if design[2] else None
        stand["Num_Plots"] = int(float(design[3])) if design[3] else 1
        stand["Sam_Wt"] = float(design[5]) if design[5] else None
    plots = {tree.get("plot_id") for tree in trees}
    stand.setdefault("Num_Plots", len(plots) or 1)
    return stand


def _stand_id(key_text: str, run: Path) -> str:
    """Return the stand identifier a run was given.

    ``STDIDENT`` carries it on the record after the keyword; when the set has none, the run
    directory's name stands in, which keeps the database and the block naming the same value.

    Parameters
    ----------
    key_text : str
        The contents of ``run.key``.
    run : Path
        The run directory, used for the fallback.

    Returns
    -------
    str
        The stand identifier.
    """
    lines = key_text.splitlines()
    for index, line in enumerate(lines):
        if line[:8].strip() == "STDIDENT" and index + 1 < len(lines):
            return lines[index + 1].strip() or run.name
    return run.name


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns
    -------
    argparse.ArgumentParser
        The parser for ``oracle_compare.py``.
    """
    parser = argparse.ArgumentParser(
        prog="oracle_compare.py",
        description=(
            "Compare a run's database against the standalone FVSbc's output for the same case."
        ),
    )
    parser.add_argument(
        "--run",
        type=Path,
        required=True,
        metavar="DIR",
        help="a run directory holding run.key, run.tre and the output database",
    )
    parser.add_argument(
        "--binary",
        type=Path,
        default=None,
        metavar="PATH",
        help=f"the standalone FVSbc, default from ${ENV_BINARY}",
    )
    return parser


class OracleInputError(RuntimeError):
    """An input the comparison needs is missing or unusable.

    Attributes
    ----------
    detail : str
        What is wrong, in the words the command prints.
    """

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def compare_run(run: Path, binary: Path) -> tuple[Comparison, ...]:
    """Compare a run's database against a standalone binary's output for the same case.

    Parameters
    ----------
    run : Path
        The run directory, holding the keyword file, the tree list and the database.
    binary : Path
        The standalone ``FVSbc``.

    Returns
    -------
    tuple of Comparison
        One record per table, as :func:`compare` returns them.

    Raises
    ------
    OracleInputError
        If the run is missing an artefact, holds no trees, or the standalone wrote no database.
    """
    key_path = run / KEYWORD_FILE_NAME
    tree_path = tree_file_name(key_path)
    database = run / DATABASE_NAME
    for required in (key_path, tree_path, database):
        if not required.is_file():
            raise OracleInputError(f"{required} is missing")
    workdir = Path(tempfile.mkdtemp(prefix="oracle-compare-"))
    try:
        key_text = key_path.read_text(encoding="utf-8")
        trees = parse_trees(tree_path.read_text(encoding="utf-8"))
        if not trees:
            raise OracleInputError(f"{tree_path} holds no tree records")
        stand_id = _stand_id(key_text, run)
        input_database(
            workdir / INPUT_DATABASE,
            stand_id=stand_id,
            trees=trees,
            stand=stand_record(key_text, stand_id, trees),
        )
        (workdir / STANDALONE_KEY).write_text(
            database_key(key_text, INPUT_DATABASE, stand_id), encoding="utf-8"
        )
        completed = subprocess.run(
            [str(binary), f"--keywordfile={STANDALONE_KEY}"],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            check=False,
        )
        # FVS exits non-zero when it *logs* an error, and it can log one and still write a
        # complete database — a `DATABASE` block it refuses, for instance. So the exit code is
        # reported and the database is what decides whether the comparison can run.
        theirs = workdir / DATABASE_NAME
        if not theirs.is_file():
            raise OracleInputError(
                f"the standalone wrote no database (exit {completed.returncode})\n"
                f"{completed.stdout[-2000:]}\n{completed.stderr[-2000:]}"
            )
        return compare(database, theirs)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments to parse. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when every table present in both agrees, ``1`` when any differs, ``2`` when the binary
        or an
        input is missing.
    """
    args = _parser().parse_args(argv)
    binary = args.binary or (Path(os.environ[ENV_BINARY]) if ENV_BINARY in os.environ else None)
    if binary is None or not Path(binary).is_file():
        print(
            f"oracle_compare: no standalone binary; pass --binary or set ${ENV_BINARY}",
            file=sys.stderr,
        )
        return 2
    try:
        results = compare_run(args.run, Path(binary))
    except OracleInputError as error:
        print(f"oracle_compare: {error.detail}", file=sys.stderr)
        return 2
    width = max((len(result.table) for result in results), default=10)
    for result in results:
        line = f"  {result.table:<{width}}  {result.status}"
        print(line + (f"  ({result.detail})" if result.detail else ""))
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    comparable = counts.get("match", 0) + counts.get("explained", 0) + counts.get("differ", 0)
    parts = [f"{counts.get('match', 0)} of {comparable} comparable tables agree"]
    if counts.get("explained"):
        parts.append(f"{counts['explained']} explained")
    if counts.get("not comparable"):
        parts.append(f"{counts['not comparable']} not comparable")
    print("\n  " + "; ".join(parts) + ".")
    failed = counts.get("differ", 0) + counts.get("stale", 0)
    return 0 if not failed else 1


#: The columns of the official input schema's tree table, in the order the FVS source declares
#: them. Taken from ``tests/FVSbc/FVS-BC.Stand.Structure.Data.db``, which the official case reads.
TREE_INIT_COLUMNS: tuple[str, ...] = (
    "Stand_CN",
    "Stand_ID",
    "StandPlot_CN",
    "StandPlot_ID",
    "Plot_ID",
    "Tree_ID",
    "Tree_Count",
    "History",
    "Species",
    "DBH",
    "DG",
    "Ht",
    "HTG",
    "HtTopK",
    "CrRatio",
    "Damage1",
    "Severity1",
    "Damage2",
    "Severity2",
    "Damage3",
    "Severity3",
    "TreeValue",
    "Prescription",
    "Age",
    "Slope",
    "Aspect",
    "PV_Code",
    "TopoCode",
    "SitePrep",
)

#: The columns of the official input schema's stand table. Only the ones this harness can fill are
#: used; the rest are left NULL, which is what the official case does for most of them.
STAND_INIT_COLUMNS: tuple[str, ...] = (
    "Stand_CN",
    "Stand_ID",
    "Variant",
    "Inv_Year",
    "Groups",
    "AddFiles",
    "FVSKeywords",
    "Latitude",
    "Longitude",
    "Region",
    "Forest",
    "District",
    "Compartment",
    "Location",
    "Ecoregion",
    "BEC",
    "PV_Code",
    "PV_Ref_Code",
    "Age",
    "Aspect",
    "Slope",
    "Elevation",
    "ElevFt",
    "Basal_Area_Factor",
    "Inv_Plot_Size",
    "Brk_DBH",
    "Num_Plots",
    "NonStk_Plots",
    "Sam_Wt",
    "Stk_Pcnt",
    "DG_Trans",
    "DG_Measure",
    "HTG_Trans",
    "HTG_Measure",
    "Mort_Measure",
    "Max_BA",
    "Max_SDI",
    "Site_Species",
    "Site_Index",
    "Model_Type",
    "Physio_Region",
    "Forest_Type",
    "State",
    "County",
    "Fuel_Model",
    "Fuel_0_25_H",
    "Fuel_25_1_H",
    "Fuel_1_3_H",
    "Fuel_3_6_H",
    "Fuel_6_12_H",
    "Fuel_12_20_H",
    "Fuel_20_35_H",
    "Fuel_35_50_H",
    "Fuel_gt_50_H",
    "Fuel_0_25_S",
    "Fuel_25_1_S",
    "Fuel_1_3_S",
    "Fuel_3_6_S",
    "Fuel_6_12_S",
    "Fuel_12_20_S",
    "Fuel_20_35_S",
    "Fuel_35_50_S",
    "Fuel_gt_50_S",
    "Fuel_Litter",
    "Fuel_Duff",
    "Fuel_0_06_H",
    "Fuel_06_25_H",
    "Fuel_25_76_H",
    "Fuel_76_152_H",
    "Fuel_152_305_H",
    "Fuel_305_508_H",
    "Fuel_508_889_H",
    "Fuel_889_1270_H",
    "Fuel_gt_1270_H",
    "Fuel_0_06_S",
    "Fuel_06_25_S",
    "Fuel_25_76_S",
    "Fuel_76_152_S",
    "Fuel_152_305_S",
    "Fuel_305_508_S",
    "Fuel_508_889_S",
    "Fuel_889_1270_S",
    "Fuel_gt_1270_S",
    "Photo_Ref",
    "Photo_code",
    "Moisture",
)


def parse_trees(tree_text: str) -> list[dict[str, object]]:
    """Read a written tree list back into one dictionary per tree.

    The reader uses the same column spans and edits the writer does, so a round trip cannot drift.

    Parameters
    ----------
    tree_text : str
        The contents of a run's ``.tre`` file, including its ``-999`` terminator.

    Returns
    -------
    list of dict
        One record per tree, keyed by the writer's field names. Blank fields are omitted.
    """
    records: list[dict[str, object]] = []
    for line in tree_text.splitlines():
        if not line.strip() or line.strip().startswith("-999"):
            continue
        record: dict[str, object] = {}
        for field, edit in FIELD_DESCRIPTORS:
            if field is None:
                continue
            first, last = READ_COLUMNS[field]
            raw = line[first - 1 : last].strip()
            if not raw:
                continue
            kind = edit[0]
            try:
                if kind == "I":
                    # ``tree_num`` shares its columns with ``plot_id``: the format reads ``I4``
                    # for the plot, tabs back to column 1, and reads ``I7`` for the tree. Fortran
                    # ignores embedded blanks in a numeric field, so "   1  1" is tree **11**, not
                    # 1001. An earlier revision zero-filled them, which put a different tree id in
                    # the database than FVS put in its own table.
                    record[field] = int(raw.replace(" ", "") if field == "tree_num" else raw)
                elif kind == "F":
                    record[field] = float(raw)
                else:
                    record[field] = raw
            except ValueError:
                continue
        records.append(record)
    return records


def input_database(
    path: Path,
    *,
    stand_id: str,
    trees: list[dict[str, object]],
    stand: dict[str, object],
) -> Path:
    """Write the ``DSNin`` input database the standalone reads trees from.

    The official case reads its trees this way, and it is the route that is known to work: the
    inline ``TREEDATA`` route needs an ``OPEN`` keyword whose layout is not established
    (``notes/triage.md``).

    Parameters
    ----------
    path : Path
        Where to write the database.
    stand_id : str
        The stand the trees belong to.
    trees : list of dict
        Records from :func:`parse_trees`.
    stand : dict
        Stand-level values keyed by the official schema's column names.

    Returns
    -------
    Path
        The database.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "create table FVS_TreeInit ("
            + ", ".join(f'"{name}"' for name in TREE_INIT_COLUMNS)
            + ")"
        )
        connection.execute(
            "create table FVS_StandInit ("
            + ", ".join(f'"{name}"' for name in STAND_INIT_COLUMNS)
            + ")"
        )
        tree_rows = []
        for tree in trees:
            row = {
                "Stand_ID": stand_id,
                "Plot_ID": tree.get("plot_id"),
                "Tree_ID": tree.get("tree_num"),
                "Tree_Count": tree.get("tree_count"),
                "History": tree.get("tree_history"),
                "Species": tree.get("species"),
                "DBH": tree.get("diam"),
                "Ht": tree.get("live_ht"),
                "CrRatio": tree.get("crown_ratio"),
                "Damage1": tree.get("damage1"),
                "Severity1": tree.get("severity1"),
                "Damage2": tree.get("damage2"),
                "Severity2": tree.get("severity2"),
                "Damage3": tree.get("damage3"),
                "Severity3": tree.get("severity3"),
                "TreeValue": tree.get("tree_val"),
                "Prescription": tree.get("tree_rx"),
                "Age": tree.get("tree_age"),
                "Slope": tree.get("plot_slope"),
                "Aspect": tree.get("plot_aspect"),
                "PV_Code": tree.get("plot_habitat"),
                "TopoCode": tree.get("plot_topo_pos"),
                "SitePrep": tree.get("plot_site_prep"),
            }
            tree_rows.append(tuple(row.get(name) for name in TREE_INIT_COLUMNS))
        placeholders = ", ".join("?" for _ in TREE_INIT_COLUMNS)
        connection.executemany(f"insert into FVS_TreeInit values ({placeholders})", tree_rows)
        stand_row = tuple(stand.get(name) for name in STAND_INIT_COLUMNS)
        connection.execute(
            "insert into FVS_StandInit values (" + ", ".join("?" for _ in STAND_INIT_COLUMNS) + ")",
            stand_row,
        )
        connection.commit()
    finally:
        connection.close()
    return path


def input_block(database_name: str, stand_id: str) -> str:
    """Render the ``DATABASE DSNin`` block that reads a stand's trees from an input database.

    Parameters
    ----------
    database_name : str
        The database file's name, relative to the working directory.
    stand_id : str
        The stand to read.

    Returns
    -------
    str
        The block, ready to prepend to a keyword file.
    """
    return (
        "DATABASE\n"
        "DSNin\n"
        f"{database_name}\n"
        "StandSQL\n"
        f"SELECT * FROM FVS_StandInit WHERE Stand_ID = '{stand_id}'\n"
        "EndSQL\n"
        "TreeSQL\n"
        f"SELECT * FROM FVS_TreeInit WHERE Stand_ID = '{stand_id}'\n"
        "EndSQL\n"
        "End\n"
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
