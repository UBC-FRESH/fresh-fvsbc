"""The oracle harness: the standalone keyword rendering, the comparison, and the exit paths."""

from __future__ import annotations

import sqlite3
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

import oracle_compare as oc

RUN_KEY = """STDIDENT
fixture
NUMCYCLE  2
TREEFMT
(I4,T1,I7)
TREEDATA
PROCESS
STOP
"""

TREE_TEXT = "   1  1     1FD  10.0\n-999\n"


def _database(path: Path, tables: Mapping[str, Sequence[Sequence[object]]]) -> Path:
    """Write a small database with the given tables and rows.

    Parameters
    ----------
    path : Path
        Where to write it.
    tables : dict
        One entry per table; the columns are ``c0``, ``c1`` and so on, derived from the rows' width.

    Returns
    -------
    Path
        The database.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        for name, rows in tables.items():
            columns = " ,".join(f"c{index}" for index in range(len(rows[0])))
            connection.execute(f'create table "{name}" ({columns})')
            placeholders = ",".join("?" for _ in rows[0])
            connection.executemany(f'insert into "{name}" values ({placeholders})', rows)
        connection.commit()
    finally:
        connection.close()
    return path


def _make_run(directory: Path, tables: Mapping[str, Sequence[Sequence[object]]]) -> Path:
    """Build a run directory holding a keyword file, a tree list and a database.

    Parameters
    ----------
    directory : Path
        Where to build it.
    tables : dict
        The database's tables.

    Returns
    -------
    Path
        The run directory.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.key").write_text(RUN_KEY, encoding="utf-8")
    (directory / "run.tre").write_text(TREE_TEXT, encoding="utf-8")
    _database(directory / "FVSOut.db", tables)
    return directory


def test_the_standalone_key_inlines_the_trees_after_treedata() -> None:
    """The standalone reads the tree records inline, so they go directly after ``TREEDATA``."""
    rendered = oc.standalone_key(RUN_KEY, TREE_TEXT)
    assert "TREEDATA\n   1  1     1FD  10.0\n-999\nPROCESS" in rendered


def test_a_keyword_file_without_treedata_is_refused() -> None:
    """There is nowhere to put the trees, so the harness says so rather than writing garbage."""
    with pytest.raises(ValueError, match="TREEDATA"):
        oc.standalone_key("STDIDENT\nx\n", TREE_TEXT)


def test_identical_databases_agree(tmp_path: Path) -> None:
    """Every exposed table present in both, with the same values, matches."""
    tables: dict[str, list[tuple[object, ...]]] = {
        "FVS_Cases": [("c1", "S1")],
        "FVS_Summary_Metric": [("c1", 2020), ("c1", 2024)],
    }
    ours = _database(tmp_path / "ours.db", tables)
    theirs = _database(tmp_path / "theirs.db", tables)
    results = oc.compare(ours, theirs)
    assert {result.status for result in results} == {"match"}
    assert {result.table for result in results} == set(tables)


def test_a_different_value_is_a_difference(tmp_path: Path) -> None:
    """A single changed cell is reported as a difference with a count of the rows."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("c1", "S1")]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("c1", "S2")]})
    results = oc.compare(ours, theirs)
    assert results[0].status == "differ"
    assert "1 row" in results[0].detail


def test_a_row_count_difference_is_reported(tmp_path: Path) -> None:
    """A missing row is a difference, and the detail says how many rows each side wrote."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("c1", "S1"), ("c2", "S1")]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("c1", "S1")]})
    detail = oc.compare(ours, theirs)[0].detail
    assert "2 rows here" in detail
    assert "1 there" in detail


def test_a_table_only_one_side_wrote_is_reported(tmp_path: Path) -> None:
    """The comparison covers the union, so a table one side omitted cannot pass unnoticed."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("c1",)], "FVS_Compute": [("c1",)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("c1",)]})
    results = {result.table: result for result in oc.compare(ours, theirs)}
    assert results["FVS_Compute"].status == "differ"
    assert "only this package wrote it" in results["FVS_Compute"].detail


def test_an_unexposed_table_is_ignored(tmp_path: Path) -> None:
    """The comparison is over the reader's surface, not everything the database holds."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("c1",)], "Not_Exposed": [("c1",)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("c1",)]})
    assert {result.table for result in oc.compare(ours, theirs)} == {"FVS_Cases"}


def test_missing_binary_is_a_reported_input_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without the binary the harness says which variable to set, and exits 2."""
    monkeypatch.delenv(oc.ENV_BINARY, raising=False)
    assert oc.main(["--run", str(tmp_path)]) == 2
    assert oc.ENV_BINARY in capsys.readouterr().err


def test_missing_inputs_are_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A run directory without its artefacts is refused before anything is spawned."""
    binary = tmp_path / "FVSbc"
    binary.write_text("", encoding="utf-8")
    assert oc.main(["--run", str(tmp_path), "--binary", str(binary)]) == 2
    assert "missing" in capsys.readouterr().err


def test_a_successful_comparison_exits_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A matching standalone run reports the agreement and exits 0."""
    tables: dict[str, list[tuple[object, ...]]] = {"FVS_Cases": [("c1", "S1")]}
    run = _make_run(tmp_path / "run", tables)
    binary = tmp_path / "FVSbc"
    binary.write_text("", encoding="utf-8")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        cwd = Path(str(kwargs["cwd"]))
        _database(cwd / "FVSOut.db", tables)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert oc.main(["--run", str(run), "--binary", str(binary)]) == 0
    assert "1 of 1 comparable tables agree" in capsys.readouterr().out


def test_a_failing_standalone_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A non-zero standalone exit is an input error, not a comparison result."""
    run = _make_run(tmp_path / "run", {"FVS_Cases": [("c1",)]})
    binary = tmp_path / "FVSbc"
    binary.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        subprocess, "run", lambda command, **kw: subprocess.CompletedProcess(command, 20, "", "")
    )
    assert oc.main(["--run", str(run), "--binary", str(binary)]) == 2
    assert "wrote no database (exit 20)" in capsys.readouterr().err


def test_a_written_tree_list_round_trips_through_the_reader() -> None:
    """The parser uses the writer's own spans, so a tree's values survive the round trip."""
    from fresh_fvsbc.nemora import crown_class
    from fresh_fvsbc.treelist import TreeListFields, resolve_species, write_tree_file

    fields = TreeListFields(
        plot_id=1,
        tree_num=1,
        tree_count=1.0,
        tree_history=0,
        species=resolve_species("FD"),
        diam=10.0,
        dg_incr=0.0,
        live_ht=8.0,
        trunc_ht=0.0,
        htg_incr=0.0,
        crown_ratio=crown_class(0.45),
        damage1=0,
        severity1=0,
        damage2=0,
        severity2=0,
        damage3=0,
        severity3=0,
        tree_val=0,
        tree_rx=0,
        plot_slope=0,
        plot_aspect=0,
        plot_habitat=0,
        plot_topo_pos=0,
        plot_site_prep=0,
        tree_age=60.0,
    )
    trees = oc.parse_trees(write_tree_file([fields]))
    assert len(trees) == 1
    assert trees[0]["species"] == "FD"
    assert trees[0]["diam"] == 10.0
    assert trees[0]["plot_id"] == 1


def test_the_tree_id_is_read_the_way_fvs_reads_it() -> None:
    """``tree_num`` shares its columns with the plot, and Fortran ignores the embedded blanks.

    ``BC_TREFMT`` reads ``I4`` for the plot, tabs back to column 1, then reads ``I7`` for the
    tree, so a record for plot 1 tree 1 is the integer 11 — which is what FVS puts in its own
    table. An earlier revision zero-filled the blanks and wrote 1001, a tree that does not exist.
    """
    trees = oc.parse_trees("   1  1     1FD  10.0\n-999\n")
    assert trees[0]["tree_num"] == 11


def test_the_terminator_is_not_a_tree() -> None:
    """``-999`` ends the records and must not become one."""
    assert oc.parse_trees("-999\n") == []


def test_the_input_database_holds_the_stand_and_its_trees(tmp_path: Path) -> None:
    """The ``DSNin`` database is what the standalone reads trees from, so both tables exist."""
    database = oc.input_database(
        tmp_path / "input.db",
        stand_id="S1",
        trees=[{"plot_id": 1, "tree_num": 1001, "species": "FD", "diam": 10.0}],
        stand={"Stand_ID": "S1", "Variant": "BC", "Inv_Year": 2020},
    )
    connection = sqlite3.connect(database)
    try:
        assert connection.execute("select count(*) from FVS_TreeInit").fetchone()[0] == 1
        assert connection.execute("select Stand_ID from FVS_StandInit").fetchone()[0] == "S1"
        assert connection.execute("select Species from FVS_TreeInit").fetchone()[0] == "FD"
    finally:
        connection.close()


def test_the_input_block_names_the_stand_twice() -> None:
    """Both statements are filtered by the stand, and a mismatch would load nothing."""
    block = oc.input_block("input.db", "S1")
    assert block.count("WHERE Stand_ID = 'S1'") == 2
    assert "DSNin" in block


def test_the_database_key_drops_the_inline_tree_block() -> None:
    """The trees come from the database, so the format and data records must not be sent as well."""
    rendered = oc.database_key(RUN_KEY, "input.db", "S1")
    assert "TREEFMT" not in rendered
    assert "TREEDATA" not in rendered
    assert "DSNin" in rendered


def test_the_stand_record_is_read_from_the_runs_own_keywords() -> None:
    """The stand row comes from ``INVYEAR``, ``SITECODE`` and ``DESIGN``, not a second source."""
    key = (
        "STDIDENT\nS1\n"
        "SITECODE  FD        15\n"
        "INVYEAR   2020\n"
        "DESIGN    0         1         999       5         0         5         1\n"
    )
    stand = oc.stand_record(key, "S1", [{"plot_id": 1}])
    assert stand["Stand_ID"] == "S1"
    assert stand["Site_Species"] == "FD"
    assert stand["Site_Index"] == 15.0
    assert stand["Num_Plots"] == 5


def test_the_input_block_follows_the_runs_own_output_block() -> None:
    """The output block must open before a case begins, or FVS refuses it as a redefinition.

    A stand read from an input database calls ``FORKOD`` with no location code and logs a
    warning; logging it writes to the output database and starts the case. So an output block
    placed after the input block is answered with ``FVS16``, ignored, and the default tables are
    written instead.
    """
    key = "DATABASE\nDSNOut\nFVSOut.db\nSummary\nEND\nSTDIDENT\nS1\nPROCESS\n"
    rendered = oc.database_key(key, "input.db", "S1")
    assert rendered.index("DSNOut") < rendered.index("DSNin")
    assert rendered.index("DSNin") < rendered.index("STDIDENT")


def test_a_run_identity_column_is_not_a_difference(tmp_path: Path) -> None:
    """``CaseID`` is minted per run, so two builds can never agree on it and it is not a result."""
    ours = _database(tmp_path / "ours.db", {"FVS_Summary_Metric": [("case-a", 2020)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Summary_Metric": [("case-b", 2020)]})
    columns = ("CaseID", "Year")
    for path in (tmp_path / "ours.db", tmp_path / "theirs.db"):
        connection = sqlite3.connect(path)
        try:
            connection.execute("alter table FVS_Summary_Metric rename to old")
            connection.execute(f'create table FVS_Summary_Metric ("{columns[0]}", "{columns[1]}")')
            connection.execute("insert into FVS_Summary_Metric select * from old")
            connection.commit()
        finally:
            connection.close()
    results = oc.compare(ours, theirs)
    assert [result.status for result in results] == ["match"]


def test_an_explained_column_is_reported_as_explained(tmp_path: Path) -> None:
    """A difference the module already accounts for is counted apart from an unexplained one."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("S1", 1.0)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("S1", -9.9)]})
    for path in (tmp_path / "ours.db", tmp_path / "theirs.db"):
        connection = sqlite3.connect(path)
        try:
            connection.execute("alter table FVS_Cases rename to old")
            connection.execute("create table FVS_Cases (StandID, SamplingWt)")
            connection.execute("insert into FVS_Cases select * from old")
            connection.commit()
        finally:
            connection.close()
    results = oc.compare(ours, theirs)
    assert [result.status for result in results] == ["explained"]
    assert "SamplingWt" in results[0].detail


def test_an_explanation_that_is_no_longer_needed_is_stale(tmp_path: Path) -> None:
    """An explanation that has stopped applying is an error, never a silent pass."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("S1", 1.0)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("S1", 1.0)]})
    for path in (tmp_path / "ours.db", tmp_path / "theirs.db"):
        connection = sqlite3.connect(path)
        try:
            connection.execute("alter table FVS_Cases rename to old")
            connection.execute("create table FVS_Cases (StandID, SamplingWt)")
            connection.execute("insert into FVS_Cases select * from old")
            connection.commit()
        finally:
            connection.close()
    results = oc.compare(ours, theirs)
    assert [result.status for result in results] == ["match", "stale"]


def test_a_table_that_is_not_comparable_says_why(tmp_path: Path) -> None:
    """A table only one side writes is not a pass, and the reason is on the record."""
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("c1",)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("c1",)], "FVS_Error": [("c1",)]})
    statuses = {result.table: result.status for result in oc.compare(ours, theirs)}
    assert statuses["FVS_Error"] == "not comparable"


def test_the_stand_row_leaves_the_inventory_year_to_the_runs_own_keyword() -> None:
    """``FUELOUT`` and ``POTFIRE`` capture the inventory year, and FVS reads a positive value as
    'suppress'. A database that sets the year before the fire-model block silently costs three
    tables, so the harness lets the run's own ``INVYEAR`` set it in the order the run uses."""
    key = "STDIDENT\nS1\nINVYEAR   2020\nSITECODE  FD        15\n"
    stand = oc.stand_record(key, "S1", [{"plot_id": 1}])
    assert "Inv_Year" not in stand
    assert stand["Site_Index"] == 15.0


def test_a_not_comparable_table_is_skipped_whatever_its_presence(tmp_path: Path) -> None:
    """A table can be not comparable because *both* sides write it and FVS makes them disagree.

    ``FVS_Regen_SitePrep`` is that case: the two builds read an uninitialised local and disagree by
    luck of the stack. Reporting it as a difference would send the next person chasing this package
    for FVS's bug, so the entry short-circuits before any comparison.
    """
    ours = _database(tmp_path / "ours.db", {"FVS_Regen_SitePrep": [("c1", 74)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Regen_SitePrep": [("c1", 100)]})
    results = oc.compare(ours, theirs)
    assert [result.status for result in results] == ["not comparable"]
    assert "UNINITIALISED" in results[0].detail
