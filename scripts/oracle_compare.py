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


@dataclass(frozen=True)
class Comparison:
    """What happened to one table.

    Attributes
    ----------
    table : str
        The table's name.
    status : str
        ``match``, ``differ``, ``missing`` (absent from the standalone's database) or ``extra``
        (present
        there and not in ours).
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
    text = frame.astype(str)
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
        One record per table either database holds, ordered by table name.
    """
    mine = {name for name in EXPOSED_TABLES if _has_table(ours, name)}
    other = {name for name in EXPOSED_TABLES if _has_table(theirs, name)}
    results: list[Comparison] = []
    for name in sorted(mine | other):
        if name not in other:
            results.append(Comparison(name, "missing", "the standalone wrote no such table"))
            continue
        if name not in mine:
            results.append(Comparison(name, "extra", "only the standalone wrote it"))
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
        if left.equals(right):
            results.append(Comparison(name, "match", ""))
            continue
        differing = int((left != right).any(axis=1).sum())
        results.append(Comparison(name, "differ", f"{differing} row(s) differ"))
    return tuple(results)


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
        The keyword file, with the ``DSNin`` block first.
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
    return input_block(database_name, stand_id) + "\n".join(kept) + "\n"


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
        carry is left out, and the database writes NULL for it.
    """
    stand: dict[str, object] = {"Stand_ID": stand_id, "Variant": "BC"}
    inventory = _keyword_fields(key_text, "INVYEAR")
    if inventory and inventory[0]:
        stand["Inv_Year"] = int(float(inventory[0]))
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
    run = args.run
    key_path = run / KEYWORD_FILE_NAME
    tree_path = tree_file_name(key_path)
    database = run / DATABASE_NAME
    for required in (key_path, tree_path, database):
        if not required.is_file():
            print(f"oracle_compare: {required} is missing", file=sys.stderr)
            return 2

    workdir = Path(tempfile.mkdtemp(prefix="oracle-compare-"))
    try:
        key_text = key_path.read_text(encoding="utf-8")
        trees = parse_trees(tree_path.read_text(encoding="utf-8"))
        if not trees:
            print(f"oracle_compare: {tree_path} holds no tree records", file=sys.stderr)
            return 2
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
            print(
                f"oracle_compare: the standalone wrote no database (exit {completed.returncode})\n"
                f"{completed.stdout[-2000:]}\n{completed.stderr[-2000:]}",
                file=sys.stderr,
            )
            return 2
        if completed.returncode != 0:
            print(
                f"  note: the standalone exited {completed.returncode} and wrote a database "
                "anyway; FVS logs an error and carries on",
                file=sys.stderr,
            )
        results = compare(database, theirs)
        width = max((len(result.table) for result in results), default=10)
        for result in results:
            line = f"  {result.table:<{width}}  {result.status}"
            print(line + (f"  ({result.detail})" if result.detail else ""))
        differing = [result for result in results if result.status != "match"]
        agreed = len(results) - len(differing)
        print(f"\n  {agreed} of {len(results)} tables agree; {len(differing)} do not.")
        return 0 if not differing else 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


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
                    # ``tree_num`` shares its columns with ``plot_id``, so the field carries
                    # both, and FVS reads the embedded blanks as zeros: "   1  1" is tree 1001.
                    # The parse has to agree with the reader, or the two databases' ids differ.
                    record[field] = int(raw.replace(" ", "0") if field == "tree_num" else raw)
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
