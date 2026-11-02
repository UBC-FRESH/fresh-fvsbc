"""The schematic stand payload and its endpoint.

The layout is a presentation choice, so these tests pin the two things that make it honest:
the same rows always produce the same positions, and every displayed value comes from the run.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from pathlib import Path

import pandas as pd
import pytest

from fresh_fvsbc.web import runs
from fresh_fvsbc.web import visuals as visualstore

_COLUMNS = (
    "CaseID, StandID, Year, TreeId, TreeIndex, PtIndex, SpeciesFVS, SpeciesPLANTS, "
    "DBH, Ht, TPH, PctCr, CrWidth, TreeAge"
)


def _make_run(
    directory: Path,
    *,
    tree_rows: Sequence[tuple[object, ...]] | None = None,
    cut_rows: Sequence[tuple[object, ...]] | None = None,
    summary: bool = True,
    database: bool = True,
    tree_table: bool = True,
) -> Path:
    """Build a run holding the tables the visual reader uses.

    Parameters
    ----------
    directory : Path
        Where to build it.
    tree_rows : list of tuple, optional
        Rows for ``FVS_TreeList_Metric``.
    cut_rows : list of tuple, optional
        Rows for ``FVS_CutList_Metric``.
    summary : bool, optional
        Whether to write ``summary.csv``.
    database : bool, optional
        Whether to write ``FVSOut.db``.
    tree_table : bool, optional
        Whether to create ``FVS_TreeList_Metric``.

    Returns
    -------
    Path
        The run directory.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.key").write_text("STDIDENT\nvisual fixture\n", encoding="utf-8")
    if summary:
        (directory / "summary.csv").write_text(
            "year,age,tpa,baa\n0,60,3,30.0\n10,70,2,25.0\n", encoding="utf-8"
        )
    if database:
        connection = sqlite3.connect(directory / "FVSOut.db")
        try:
            connection.execute("create table FVS_Cases (CaseID text, StandID text)")
            connection.execute("insert into FVS_Cases values ('c1', 'S1')")
            if tree_table:
                connection.execute(f"create table FVS_TreeList_Metric ({_COLUMNS})")
                if tree_rows:
                    placeholders = ", ".join("?" for _ in range(14))
                    connection.executemany(
                        f"insert into FVS_TreeList_Metric values ({placeholders})", tree_rows
                    )
            if cut_rows is not None:
                connection.execute(f"create table FVS_CutList_Metric ({_COLUMNS})")
                placeholders = ", ".join("?" for _ in range(14))
                connection.executemany(
                    f"insert into FVS_CutList_Metric values ({placeholders})", cut_rows
                )
            connection.commit()
        finally:
            connection.close()
    (directory / "provenance.json").write_text(
        json.dumps({"pyfvs_commit": "e95172b"}), encoding="utf-8"
    )
    (directory / "variants.json").write_text(json.dumps({"BC": "OK"}), encoding="utf-8")
    return directory


def _run(
    directory: Path,
    *,
    tree_rows: Sequence[tuple[object, ...]] | None = None,
    cut_rows: Sequence[tuple[object, ...]] | None = None,
    summary: bool = True,
    database: bool = True,
    tree_table: bool = True,
) -> runs.Run:
    """Build a run and return it as the reader sees it.

    Parameters
    ----------
    directory : Path
        Where to build it.
    tree_rows : list of tuple, optional
        Rows for ``FVS_TreeList_Metric``.
    cut_rows : list of tuple, optional
        Rows for ``FVS_CutList_Metric``.
    summary : bool, optional
        Whether to write ``summary.csv``.
    database : bool, optional
        Whether to write ``FVSOut.db``.
    tree_table : bool, optional
        Whether to create ``FVS_TreeList_Metric``.

    Returns
    -------
    fresh_fvsbc.web.runs.Run
        The discovered run.
    """
    _make_run(
        directory,
        tree_rows=tree_rows,
        cut_rows=cut_rows,
        summary=summary,
        database=database,
        tree_table=tree_table,
    )
    found = runs.discover([directory.parent])
    assert found
    return found[0]


def _three_trees() -> list[tuple[object, ...]]:
    """Return two plots with three trees.

    Returns
    -------
    list of tuple
        Rows in the fixture's column order.
    """
    return [
        ("c1", "S1", 0, "11", 1, 1, "FD", "PSME", 10.0, 8.0, 100.0, 40.0, 2.0, 60.0),
        ("c1", "S1", 0, "12", 2, 1, "FD", "PSME", 20.0, 15.0, 50.0, 30.0, 3.0, 60.0),
        ("c1", "S1", 0, "21", 1, 2, "CW", "TSHE", 15.0, 12.0, 75.0, 35.0, 2.5, 60.0),
        ("c1", "S1", 10, "12", 2, 1, "FD", "PSME", 22.0, 17.0, 45.0, 30.0, 3.0, 70.0),
    ]


def test_the_payload_names_the_first_year_and_counts_the_stand(tmp_path: Path) -> None:
    """A complete run answers with the first year, its trees, plots and species."""
    run = _run(tmp_path / "run", tree_rows=_three_trees())
    payload = visualstore.visuals(run)
    assert payload["available"] is True
    assert payload["reason"] is None
    assert payload["year"] == 0
    assert payload["years"] == [0, 10]
    assert payload["layout"]["kind"] == "schematic"
    assert "no x/y" in payload["layout"]["basis"]
    assert payload["counts"] == {"trees": 3, "cut": 0, "plots": 2, "shown": 3, "total": 3}
    assert len(payload["trees"]) == 3
    assert payload["cut_trees"] == []
    assert payload["species"] == [
        {"code": "FD", "count": 2},
        {"code": "CW", "count": 1},
    ]
    assert payload["summary"]["baa"] == 30.0


def test_the_layout_is_deterministic_and_keeps_plots_apart(tmp_path: Path) -> None:
    """The same rows always produce the same picture, and a plot has one cell."""
    run = _run(tmp_path / "run", tree_rows=_three_trees())
    first = visualstore.visuals(run)
    second = visualstore.visuals(run)
    assert [(tree["x"], tree["y"]) for tree in first["trees"]] == [
        (tree["x"], tree["y"]) for tree in second["trees"]
    ]
    centers = {(plot["x"], plot["y"]) for plot in first["plots"]}
    assert len(centers) == 2
    left, bottom, right, top = first["bounds"]
    for tree in first["trees"]:
        assert left <= tree["x"] <= right
        assert bottom <= tree["y"] <= top
    assert first["layout"]["cell_m"] >= visualstore._MIN_CELL_METERS


def test_a_year_selects_its_rows_and_marks_cut_trees(tmp_path: Path) -> None:
    """A later year is filtered, and a cut tree is shown as cut."""
    rows = _three_trees()
    cut = [
        ("c1", "S1", 10, "12", 2, 1, "FD", "PSME", 22.0, 17.0, 45.0, 30.0, 3.0, 70.0),
        ("c1", "S1", 10, "31", 3, 2, "CW", "TSHE", 18.0, 14.0, 40.0, 25.0, 2.0, 70.0),
    ]
    run = _run(tmp_path / "run", tree_rows=rows, cut_rows=cut)
    payload = visualstore.visuals(run, 10)
    assert payload["year"] == 10
    assert payload["counts"] == {"trees": 0, "cut": 2, "plots": 2, "shown": 2, "total": 2}
    assert {tree["tree_id"] for tree in payload["cut_trees"]} == {"12", "31"}
    assert payload["trees"] == []


def test_a_tree_in_both_tables_is_one_cut_tree(tmp_path: Path) -> None:
    """The cut list marks a tree; it does not duplicate it."""
    rows = _three_trees()
    cut = [("c1", "S1", 0, "11", 1, 1, "FD", "PSME", 10.0, 8.0, 100.0, 40.0, 2.0, 60.0)]
    run = _run(tmp_path / "run", tree_rows=rows, cut_rows=cut)
    payload = visualstore.visuals(run)
    assert payload["counts"] == {"trees": 2, "cut": 1, "plots": 2, "shown": 3, "total": 3}
    assert [tree["tree_id"] for tree in payload["trees"]] == ["12", "21"]
    assert [tree["tree_id"] for tree in payload["cut_trees"]] == ["11"]


def test_an_unknown_year_falls_back_to_the_first(tmp_path: Path) -> None:
    """A year the run did not write is answered with the first year, not an empty picture."""
    run = _run(tmp_path / "run", tree_rows=_three_trees())
    payload = visualstore.visuals(run, 999)
    assert payload["year"] == 0
    assert payload["available"] is True


def test_a_run_without_a_tree_table_is_explained(tmp_path: Path) -> None:
    """A run that wrote no per-tree table gets a reason, not a 404 and not an empty picture."""
    run = _run(tmp_path / "run", tree_table=False)
    payload = visualstore.visuals(run)
    assert payload["available"] is False
    assert visualstore.TREE_TABLE in payload["reason"]
    assert payload["trees"] == []


def test_a_run_without_a_database_is_explained(tmp_path: Path) -> None:
    """A missing database is a reason, not a traceback."""
    run = _run(tmp_path / "run", database=False)
    payload = visualstore.visuals(run)
    assert payload["available"] is False
    assert "FVSOut.db" in payload["reason"]


def test_an_empty_tree_table_is_explained(tmp_path: Path) -> None:
    """A table with no rows is not a picture."""
    run = _run(tmp_path / "run", tree_rows=[])
    payload = visualstore.visuals(run)
    assert payload["available"] is False
    assert "no rows" in payload["reason"]


def test_a_tree_table_with_no_dated_rows_is_explained(tmp_path: Path) -> None:
    """A year that cannot be read leaves nothing to draw."""
    rows = [("c1", "S1", None, "11", 1, 1, "FD", "PSME", 10.0, 8.0, 100.0, 40.0, 2.0, 60.0)]
    run = _run(tmp_path / "run", tree_rows=rows)
    payload = visualstore.visuals(run)
    assert payload["available"] is False
    assert "dated rows" in payload["reason"]


def test_missing_values_are_reported_as_nulls(tmp_path: Path) -> None:
    """A blank species, DBH and tree id are shown as absent, not as zero or a guess."""
    rows = [
        ("c1", "S1", 0, None, None, 1, None, None, "not a number", None, None, None, None, None),
    ]
    run = _run(tmp_path / "run", tree_rows=rows)
    payload = visualstore.visuals(run)
    tree = payload["trees"][0]
    assert tree["tree_id"] == "1:0"
    assert tree["species"] == "??"
    assert tree["dbh_cm"] is None
    assert tree["height_m"] is None


def test_a_run_without_a_summary_has_no_summary(tmp_path: Path) -> None:
    """The payload still draws when the summary is absent."""
    run = _run(tmp_path / "run", tree_rows=_three_trees(), summary=False)
    payload = visualstore.visuals(run)
    assert payload["available"] is True
    assert payload["summary"] is None


def test_a_summary_without_the_year_is_not_invented(tmp_path: Path) -> None:
    """A missing summary row is ``None``, not the nearest year."""
    run = _run(tmp_path / "run", tree_rows=_three_trees())
    (tmp_path / "run" / "summary.csv").write_text(
        "year,age,tpa,baa\n0,60,3,30.0\n", encoding="utf-8"
    )
    payload = visualstore.visuals(run, 10)
    assert payload["year"] == 10
    assert payload["summary"] is None


def test_a_large_stand_says_it_was_truncated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The cap is reported instead of pretending the picture is the whole stand."""
    monkeypatch.setattr(visualstore, "MAX_TREES", 2)
    run = _run(tmp_path / "run", tree_rows=_three_trees())
    payload = visualstore.visuals(run)
    assert payload["truncated"] is True
    assert payload["counts"]["shown"] == 2
    assert len(payload["trees"]) + len(payload["cut_trees"]) == 2


def test_a_missing_run_directory_is_refused(tmp_path: Path) -> None:
    """A run that went away between discovery and the request is a reader error."""
    run = _run(tmp_path / "run", tree_rows=_three_trees())
    run.path.rename(tmp_path / "gone")
    with pytest.raises(runs.RunError, match="no longer there"):
        visualstore.visuals(run)


def test_missing_markers_are_recognised() -> None:
    """NaN, pandas' null markers and containers are handled without guessing."""
    assert visualstore._is_missing(float("nan")) is True
    assert visualstore._is_missing(pd.NA) is True
    assert visualstore._is_missing(pd.NaT) is True
    assert visualstore._is_missing(pd.Series([1, 2])) is False
    assert visualstore._is_missing([1, 2]) is False
    assert visualstore._is_missing("FD") is False


def test_an_empty_layout_has_a_default_bounds() -> None:
    """The layout function answers an empty stand with a unit box."""
    plots, bounds, cell = visualstore.plot_layout([])
    assert plots == []
    assert bounds == [0.0, 0.0, 1.0, 1.0]
    assert cell == visualstore._MIN_CELL_METERS


def test_a_repeated_tree_id_is_one_record(tmp_path: Path) -> None:
    """The merge keeps one record per tree id, even if a table repeats a row."""
    rows = [
        ("c1", "S1", 0, "11", 1, 1, "FD", "PSME", 10.0, 8.0, 100.0, 40.0, 2.0, 60.0),
        ("c1", "S1", 0, "11", 1, 1, "FD", "PSME", 11.0, 8.0, 100.0, 40.0, 2.0, 60.0),
    ]
    run = _run(tmp_path / "run", tree_rows=rows)
    payload = visualstore.visuals(run)
    assert payload["counts"]["trees"] == 1
    assert payload["trees"][0]["dbh_cm"] == 11.0


def test_the_endpoint_serves_the_payload(tmp_path: Path) -> None:
    """The API exposes the same reader, with the year as a query parameter."""
    pytest.importorskip("fastapi", reason="the web extra is not installed")
    from fastapi.testclient import TestClient

    from fresh_fvsbc.web import app as webapp

    _make_run(tmp_path / "run", tree_rows=_three_trees())
    client = TestClient(webapp.create_app([tmp_path]))
    first = client.get("/api/runs/run/visuals")
    assert first.status_code == 200
    assert first.json()["year"] == 0
    later = client.get("/api/runs/run/visuals", params={"year": 10})
    assert later.status_code == 200
    assert later.json()["year"] == 10
    missing = client.get("/api/runs/nope/visuals")
    assert missing.status_code == 404
