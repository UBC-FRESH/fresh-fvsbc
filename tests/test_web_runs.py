"""The artefact readers: discovery, the oracle flag, and the refusals.

These tests run without FastAPI, which is the point of keeping the readers in their own module.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from fresh_fvsbc.outputs import EXPOSED_TABLES, ORACLE_TABLES
from fresh_fvsbc.web import runs


def _make_run(directory: Path, *, summary: bool = True, database: bool = True) -> Path:
    """Build a run directory holding the artefacts a completed run leaves.

    Parameters
    ----------
    directory : Path
        Where to build it.
    summary : bool, optional
        Whether to write ``summary.csv``, which is what makes a run complete.
    database : bool, optional
        Whether to write an output database with one exposed table.

    Returns
    -------
    Path
        The run directory.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.key").write_text("STDIDENT\nweb fixture\n", encoding="utf-8")
    if summary:
        (directory / "summary.csv").write_text(
            "year,age,tpa,baa\n0,60,3,3.0\n10,70,2,2.4\n", encoding="utf-8"
        )
    if database:
        connection = sqlite3.connect(directory / "FVSOut.db")
        try:
            connection.execute("create table FVS_Cases (CaseID text, StandID text, Variant text)")
            connection.execute("insert into FVS_Cases values ('c1', 'S1', 'BC')")
            connection.execute("create table FVS_Summary_Metric (CaseID text, Year integer)")
            connection.execute("insert into FVS_Summary_Metric values ('c1', 0)")
            connection.execute("create table Not_Exposed (CaseID text)")
            connection.commit()
        finally:
            connection.close()
    (directory / "provenance.json").write_text(
        json.dumps({"pyfvs_commit": "e95172b"}), encoding="utf-8"
    )
    (directory / "variants.json").write_text(json.dumps({"BC": "OK"}), encoding="utf-8")
    return directory


def test_discovery_finds_a_run_directory_one_level_down(tmp_path: Path) -> None:
    """A root holds run directories, and the identifier is the directory's name."""
    _make_run(tmp_path / "run-a")
    _make_run(tmp_path / "run-b")
    (tmp_path / "not-a-run").mkdir()
    found = runs.discover([tmp_path])
    assert [run.id for run in found] == ["run-a", "run-b"]
    assert all(run.state == "complete" for run in found)


def test_a_root_that_is_itself_a_run_is_found(tmp_path: Path) -> None:
    """Pointing the service straight at a run directory is allowed."""
    _make_run(tmp_path)
    found = runs.discover([tmp_path])
    assert len(found) == 1
    assert found[0].id == tmp_path.name


def test_a_run_without_a_summary_is_running(tmp_path: Path) -> None:
    """``summary.csv`` is what marks a run complete."""
    _make_run(tmp_path / "run", summary=False)
    found = runs.discover([tmp_path])
    assert found[0].state == "running"


def test_a_missing_root_is_skipped_rather_than_fatal(tmp_path: Path) -> None:
    """A configured root that has gone away yields nothing, not an exception."""
    assert runs.discover([tmp_path / "absent"]) == ()


def test_tables_lists_only_exposed_tables_with_counts(tmp_path: Path) -> None:
    """The reader's surface is the reader's: ``Not_Exposed`` is in the database and is not
    listed."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    listed = {record["name"]: record for record in runs.tables(run)}
    assert set(listed) == {"FVS_Cases", "FVS_Summary_Metric"}
    assert listed["FVS_Cases"]["rows"] == 1
    assert listed["FVS_Cases"]["exposed"] is True


def test_the_oracle_flag_matches_the_checked_set(tmp_path: Path) -> None:
    """The flag is the difference between a verified number and one that is only read back."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    listed = {record["name"]: record for record in runs.tables(run)}
    assert listed["FVS_Summary_Metric"]["oracle"] is True
    assert listed["FVS_Cases"]["oracle"] is False
    assert set(ORACLE_TABLES) <= set(EXPOSED_TABLES)


def test_a_table_page_reports_the_total_and_the_slice(tmp_path: Path) -> None:
    """A page carries the whole table's count, so a client can say "showing 1 of N"."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    page = runs.table(run, "FVS_Cases", limit=1, offset=0)
    assert page["total"] == 1
    assert page["limit"] == 1
    assert page["rows"][0]["StandID"] == "S1"
    assert page["columns"] == ["CaseID", "StandID", "Variant"]


def test_the_page_size_is_clamped(tmp_path: Path) -> None:
    """A caller asking for a million rows gets the documented maximum."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    page = runs.table(run, "FVS_Cases", limit=10**6)
    assert page["limit"] == runs.MAX_LIMIT


def test_an_unexposed_table_is_refused(tmp_path: Path) -> None:
    """The database holds it and the reader does not expose it, so the service refuses it."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    with pytest.raises(runs.RunError, match="'Not_Exposed' is not an exposed table"):
        runs.table(run, "Not_Exposed")


def test_a_run_without_a_database_is_refused(tmp_path: Path) -> None:
    """A run that wrote no database is a reported failure, not an empty page."""
    run = runs.discover([_make_run(tmp_path / "run", database=False)])[0]
    with pytest.raises(runs.RunError, match=r"no FVSOut\.db"):
        runs.table(run, "FVS_Cases")


def test_summary_rows_are_records(tmp_path: Path) -> None:
    """The summary is returned as one record per stand-period."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    rows = runs.summary(run)
    assert [row["year"] for row in rows] == [0, 10]
    assert rows[0]["baa"] == 3.0


def test_a_running_run_has_no_summary_yet(tmp_path: Path) -> None:
    """Asking for the summary of a running run is a refusal naming the file."""
    run = runs.discover([_make_run(tmp_path / "run", summary=False)])[0]
    with pytest.raises(runs.RunError, match=r"no summary\.csv yet"):
        runs.summary(run)


def test_keywords_and_provenance_are_read_as_written(tmp_path: Path) -> None:
    """Both are returned verbatim: the reader does not interpret them."""
    run = runs.discover([_make_run(tmp_path / "run")])[0]
    assert "STDIDENT" in runs.keywords(run)
    payload = runs.provenance(run)
    assert payload["provenance"] == {"pyfvs_commit": "e95172b"}
    assert payload["variants"] == {"BC": "OK"}


def test_absent_provenance_is_none_rather_than_invented(tmp_path: Path) -> None:
    """A run that wrote no provenance reports ``None``; provenance that is assumed is not
    provenance."""
    directory = _make_run(tmp_path / "run")
    (directory / "provenance.json").unlink()
    run = runs.discover([tmp_path])[0]
    assert runs.provenance(run)["provenance"] is None


def test_a_vanished_directory_is_reported(tmp_path: Path) -> None:
    """A run discovered and then deleted is a refusal naming the path."""
    directory = _make_run(tmp_path / "run")
    run = runs.discover([tmp_path])[0]
    for child in directory.iterdir():
        child.unlink()
    directory.rmdir()
    with pytest.raises(runs.RunError, match="no longer there"):
        runs.keywords(run)
