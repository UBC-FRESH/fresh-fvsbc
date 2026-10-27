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
    ours = _database(tmp_path / "ours.db", {"FVS_Cases": [("c1",)], "FVS_Error": [("c1",)]})
    theirs = _database(tmp_path / "theirs.db", {"FVS_Cases": [("c1",)]})
    statuses = {result.table: result.status for result in oc.compare(ours, theirs)}
    assert statuses["FVS_Error"] == "missing"


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
    assert "1 of 1 tables agree" in capsys.readouterr().out


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
    assert "exited 20" in capsys.readouterr().err
