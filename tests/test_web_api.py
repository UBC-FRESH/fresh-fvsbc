"""The HTTP surface, exercised with ``fastapi.testclient`` over a fixture run directory."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="the web extra is not installed")

from fastapi.testclient import TestClient

from fresh_fvsbc.web import app as webapp


def _make_run(directory: Path, *, summary: bool = True) -> Path:
    """Build a run directory for the API tests.

    Parameters
    ----------
    directory : Path
        Where to build it.
    summary : bool, optional
        Whether to write ``summary.csv``, which is what makes a run complete.

    Returns
    -------
    Path
        The run directory.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "run.key").write_text("STDIDENT\nweb api fixture\n", encoding="utf-8")
    if summary:
        (directory / "summary.csv").write_text(
            "year,age,tpa,baa\n0,60,3,3.0\n10,70,2,2.4\n", encoding="utf-8"
        )
    connection = sqlite3.connect(directory / "FVSOut.db")
    try:
        connection.execute("create table FVS_Cases (CaseID text, StandID text, Variant text)")
        connection.execute("insert into FVS_Cases values ('c1', 'S1', 'BC')")
        connection.commit()
    finally:
        connection.close()
    (directory / "provenance.json").write_text(
        json.dumps({"pyfvs_commit": "e95172b"}), encoding="utf-8"
    )
    (directory / "variants.json").write_text(json.dumps({"BC": "OK"}), encoding="utf-8")
    return directory


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    """A client over one complete run under a temporary root.

    Parameters
    ----------
    tmp_path : Path
        The root pytest provides.

    Returns
    -------
    fastapi.testclient.TestClient
        The client.
    """
    _make_run(tmp_path / "run-a")
    return TestClient(webapp.create_app([tmp_path]))


def test_the_shipped_skins_are_served(client: TestClient) -> None:
    """The front end reads its roles from the service, not from a hard-coded list."""
    skins = client.get("/api/skins").json()
    assert {skin["id"] for skin in skins} == {"analyst", "carbon", "reviewer", "tables"}
    reviewer = next(skin for skin in skins if skin["id"] == "reviewer")
    assert reviewer["read_only"] is True
    assert reviewer["actions"] == []


def test_the_oracle_endpoint_reports_how_much_is_verified(client: TestClient) -> None:
    """The surface can say how many exposed tables have an independent check."""
    payload = client.get("/api/oracle").json()
    assert payload["exposed"] == 31
    assert payload["oracle"] == 4
    assert "FVS_SnagDet_Metric" in payload["tables"]


def test_runs_lists_the_discovered_run(client: TestClient) -> None:
    """A run is listed with its state and how many tables it wrote."""
    listed = client.get("/api/runs").json()
    assert [run["id"] for run in listed] == ["run-a"]
    assert listed[0]["state"] == "complete"
    assert listed[0]["tables"] == 1


def test_the_summary_is_served(client: TestClient) -> None:
    """The summary is the parsed ``summary.csv``, one record per stand-period."""
    rows = client.get("/api/runs/run-a/summary").json()
    assert [row["year"] for row in rows] == [0, 10]


def test_an_unknown_run_is_a_404_naming_it(client: TestClient) -> None:
    """A missing run is refused with its name, not an empty result."""
    response = client.get("/api/runs/nope/summary")
    assert response.status_code == 404
    assert "nope" in response.json()["detail"]


def test_tables_lists_the_exposed_tables(client: TestClient) -> None:
    """The table list carries the oracle flag per table."""
    tables = client.get("/api/runs/run-a/tables").json()
    assert [table["name"] for table in tables] == ["FVS_Cases"]
    assert tables[0]["oracle"] is False


def test_a_table_page_is_served(client: TestClient) -> None:
    """The table endpoint returns columns, rows, the total and the oracle flag."""
    page = client.get("/api/runs/run-a/tables/FVS_Cases").json()
    assert page["total"] == 1
    assert page["rows"][0]["StandID"] == "S1"
    assert page["columns"] == ["CaseID", "StandID", "Variant"]
    assert page["oracle"] is False


def test_an_unexposed_table_is_a_404(client: TestClient) -> None:
    """The service refuses a table the reader does not expose, and says which."""
    response = client.get("/api/runs/run-a/tables/FVS_Carbon_Metric")
    assert response.status_code == 404
    assert "FVS_Carbon_Metric" in response.json()["detail"]


def test_the_keyword_file_is_plain_text(client: TestClient) -> None:
    """The keyword set is served verbatim, as text."""
    response = client.get("/api/runs/run-a/keywords")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "STDIDENT" in response.text


def test_provenance_is_served(client: TestClient) -> None:
    """Provenance and the variant list come back as written."""
    payload = client.get("/api/runs/run-a/provenance").json()
    assert payload["provenance"] == {"pyfvs_commit": "e95172b"}
    assert payload["variants"] == {"BC": "OK"}


def test_a_complete_run_answers_204_on_the_event_stream(client: TestClient) -> None:
    """204 is the protocol's "stop reconnecting"; a finished run must not hold a worker thread."""
    assert client.get("/api/runs/run-a/events").status_code == 204


def test_a_running_run_streams_its_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The stream reports what the directory holds, and closes when the run finishes."""
    _make_run(tmp_path / "run-b", summary=False)
    monkeypatch.setattr(webapp, "POLL_SECONDS", 0.0)
    application = webapp.create_app([tmp_path])

    with (
        TestClient(application) as streaming,
        streaming.stream("GET", "/api/runs/run-b/events") as response,
    ):
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        first = next(response.iter_lines())
        assert first.startswith("event: status")


def test_starting_a_run_needs_the_three_required_fields(client: TestClient) -> None:
    """A start request without a population, species or age is a 400 naming what is missing."""
    response = client.post("/api/runs", json={"species": "FD"})
    assert response.status_code == 400
    assert "population" in response.json()["detail"]


def test_starting_a_run_refuses_an_identifier_already_taken(tmp_path: Path) -> None:
    """A run identifier is a directory name, and a collision is refused rather than overwritten."""
    _make_run(tmp_path / "run-a")
    client = TestClient(webapp.create_app([tmp_path]))
    response = client.post(
        "/api/runs",
        json={"population": "p.json", "species": "FD", "tree_age": 60, "id": "run-a"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_starting_a_run_invokes_the_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A start spawns the CLI in a subprocess and returns immediately with the identifier."""
    recorded: list[list[str]] = []

    class _Stub:
        """Stand-in for ``subprocess.Popen``, which must not actually run FVS."""

        def __init__(self, command: list[str], **_: object) -> None:
            recorded.append(command)

    monkeypatch.setattr(subprocess, "Popen", _Stub)
    client = TestClient(webapp.create_app([tmp_path]))
    response = client.post(
        "/api/runs",
        json={
            "population": "p.json",
            "species": "FD",
            "tree_age": 60,
            "id": "new-run",
            "keywords": ["NUMCYCLE=2", "PROCESS"],
        },
    )
    assert response.status_code == 202
    assert response.json()["id"] == "new-run"
    assert recorded
    assert recorded[0][1:3] == ["-m", "fresh_fvsbc"]
    assert "--keyword" in recorded[0]
    assert (tmp_path / "new-run").is_dir()


def test_a_non_loopback_bind_is_refused_without_the_flag(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """There is no authentication, so a remote bind needs an explicit decision."""
    code = webapp.main(["--runs", "/tmp", "--host", "0.0.0.0"])
    assert code == 2
    assert "allow-remote" in capsys.readouterr().err


def test_the_spa_is_served_at_the_root(client: TestClient) -> None:
    """The shell is a static file; there is no build step and no template rendering."""
    response = client.get("/")
    assert response.status_code == 200
    assert "fresh-fvsbc" in response.text
    assert "app.js" in response.text


def test_the_cli_dispatches_web_before_the_run_parser(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``fresh-fvsbc web`` never reaches the run parser, so a run's flags are untouched."""
    from fresh_fvsbc import cli

    assert cli.main(["web", "--runs", "/tmp", "--host", "0.0.0.0"]) == 2
    assert "allow-remote" in capsys.readouterr().err


class _DeadProcess:
    """A stand-in for a child that exited non-zero."""

    returncode = 1

    def poll(self) -> int:
        """Report the child as exited.

        Returns
        -------
        int
            The exit code.
        """
        return 1


def test_a_dead_child_is_reported_as_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run whose child died is ``failed``, not ``running`` forever — the bug a real case found."""
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: _DeadProcess())
    application = webapp.create_app([tmp_path])
    client = TestClient(application)
    started = client.post(
        "/api/runs", json={"population": "p.json", "species": "FD", "tree_age": 60, "id": "dead"}
    )
    assert started.status_code == 202
    # The CLI writes run.key before it does anything else, so a run that died still leaves one.
    (tmp_path / "dead" / "run.key").write_text("STDIDENT\ndead\n", encoding="utf-8")
    listed = client.get("/api/runs").json()
    assert listed[0]["state"] == "failed"


def test_the_run_log_is_served(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The child's traceback is reachable through the surface, where a failure is explained."""
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: _DeadProcess())
    client = TestClient(webapp.create_app([tmp_path]))
    client.post(
        "/api/runs", json={"population": "p.json", "species": "FD", "tree_age": 60, "id": "dead"}
    )
    (tmp_path / "dead" / "run.key").write_text("STDIDENT\ndead\n", encoding="utf-8")
    (tmp_path / "dead" / "service.log").write_text("boom\n", encoding="utf-8")
    response = client.get("/api/runs/dead/log")
    assert response.status_code == 200
    assert response.text == "boom\n"


def test_a_run_the_service_did_not_start_has_an_empty_log(client: TestClient) -> None:
    """A run directory found on disk has no service log, and an empty body says so."""
    response = client.get("/api/runs/run-a/log")
    assert response.status_code == 200
    assert response.text == ""


def test_a_block_entry_keeps_its_place_in_the_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An entry carrying ``|`` becomes ``--block`` in order: a DATABASE block must come first."""
    recorded: list[list[str]] = []

    class _Stub:
        """Stand-in for ``subprocess.Popen``."""

        def __init__(self, command: list[str], **_: object) -> None:
            recorded.append(command)

    monkeypatch.setattr(subprocess, "Popen", _Stub)
    client = TestClient(webapp.create_app([tmp_path]))
    client.post(
        "/api/runs",
        json={
            "population": "p.json",
            "species": "FD",
            "tree_age": 60,
            "id": "ordered",
            "keywords": ["DATABASE|DSNOut|FVSOut.db|ComputDB", "STDIDENT", "NUMCYCLE=2"],
        },
    )
    command = recorded[0]
    first = command.index("--block")
    second = command.index("--keyword")
    assert first < second, "the block must precede the keywords"
    assert command[first + 1] == "DATABASE|DSNOut|FVSOut.db|ComputDB"


def test_the_service_answers_with_and_without_its_root_path(tmp_path: Path) -> None:
    """A dev container publishes a port under a proxy prefix, and both forms must work.

    JupyterHub maps ``/user/<name>/proxy/<port>/`` onto the service. ``--root-path`` makes the app
    answer under that prefix as well as at the root, which is what the container needs.
    """
    _make_run(tmp_path / "run-a")
    prefix = "/jupyterhub32/user/me/codeserver/proxy/8765"
    client = TestClient(webapp.create_app([tmp_path], root_path=prefix))
    assert client.get("/api/runs").status_code == 200
    assert client.get(f"{prefix}/api/runs").status_code == 200
    assert client.get(f"{prefix}/").status_code == 200
