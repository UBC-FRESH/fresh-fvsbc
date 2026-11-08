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
from fresh_fvsbc.web.agent import AgentError


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
    # The standalone comparison is the broader source and the one the page leads with. Reporting
    # only the dump's four would understate the surface by a factor of seven.
    assert payload["standalone"] == 28
    assert "FVS_InvReference" in payload["standalone_tables"]
    assert "FVS_Regen_SitePrep" not in payload["standalone_tables"]


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


def test_starting_a_run_passes_cycle_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The browser's cycle fields reach the CLI as the flags that rewrite TIMEINT and NUMCYCLE."""
    recorded: list[list[str]] = []

    class _Stub:
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
            "id": "cycled",
            "cycles": 2,
            "cycle_years": 5,
        },
    )
    assert response.status_code == 202
    command = recorded[0]
    assert command[command.index("--cycles") + 1] == "2"
    assert command[command.index("--cycle-years") + 1] == "5"
    for bad in ({"cycles": 0}, {"cycles": "2"}, {"cycle_years": 0}, {"cycle_years": "five"}):
        refused = client.post(
            "/api/runs",
            json={"population": "p.json", "species": "FD", "tree_age": 60, **bad},
        )
        assert refused.status_code == 400


def test_starting_a_run_can_apply_a_calibration_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A selected bundle is passed as a server-side path, never as an arbitrary client path."""
    recorded: list[list[str]] = []

    class _Stub:
        def __init__(self, command: list[str], **_: object) -> None:
            recorded.append(command)

    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    source = (
        Path(__file__).resolve().parents[1] / "notes/reference/calibration/d7-cwh-4cm-bundle.json"
    )
    (bundle_dir / "cwh.json").write_bytes(source.read_bytes())
    monkeypatch.setattr(subprocess, "Popen", _Stub)
    client = TestClient(webapp.create_app([tmp_path / "runs"], bundles=[bundle_dir]))
    response = client.post(
        "/api/runs",
        json={
            "population": "p.json",
            "species": "FD",
            "tree_age": 60,
            "id": "with-bundle",
            "bundle": "cwh-growth-4cm-pilot-2026-11-04",
            "min_dbh": 4,
        },
    )
    assert response.status_code == 202
    assert "--calibration" in recorded[0]
    assert "--min-dbh" in recorded[0]
    assert recorded[0][recorded[0].index("--calibration") + 1].endswith("cwh.json")
    assert (
        client.post(
            "/api/runs",
            json={"population": "p.json", "species": "FD", "tree_age": 60, "bundle": "missing"},
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Is the calibration bundle signed?", "no calibration"),
        ("Show provenance.", "fresh_fvsbc_version"),
        ("Why did TPH change?", "tph"),
        ("What is the basal area?", "ba"),
        ("Summarize this run.", "run-a"),
    ],
)
def test_the_assistant_answers_from_the_open_run(
    client: TestClient, message: str, expected: str
) -> None:
    """The assistant reads summary, provenance, and calibration without inventing facts."""
    response = client.post("/api/assistant", json={"run": "run-a", "message": message})
    assert response.status_code == 200
    payload = response.json()
    assert expected in payload["reply"].lower()
    assert payload["citations"]


def test_the_assistant_refuses_bad_input_and_has_a_no_run_answer(client: TestClient) -> None:
    """Empty, overlong, and unknown-run requests are refused; no-run gets a safe prompt."""
    no_run = client.post("/api/assistant", json={"message": "Summarize this run."})
    assert no_run.status_code == 200
    assert "open a run" in no_run.json()["reply"].lower()
    assert client.post("/api/assistant", json={"message": "  "}).status_code == 422
    assert client.post("/api/assistant", json={"message": "x" * 4001}).status_code == 422
    assert (
        client.post("/api/assistant", json={"run": "nope", "message": "summary"}).status_code == 404
    )


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
    assert "workspace-nav" in response.text
    assert "new-run-dialog" in response.text
    assert 'class="skip-link"' in response.text
    assert 'role="tabpanel"' in response.text
    assert "app.js?v=" in response.text
    assert response.headers["cache-control"].startswith("no-store")
    script = client.get("/app.js")
    assert script.status_code == 200
    assert script.headers["cache-control"].startswith("no-store")


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


def test_calibration_bundles_are_listed_without_exposing_invalid_json(tmp_path: Path) -> None:
    """The service lists valid bundles and ignores unrelated JSON in the directory."""
    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    source = (
        Path(__file__).resolve().parents[1] / "notes/reference/calibration/d7-cwh-4cm-bundle.json"
    )
    (bundle_dir / "cwh.json").write_bytes(source.read_bytes())
    (bundle_dir / "not-a-bundle.json").write_text('{"not": "a bundle"}')
    client = TestClient(webapp.create_app([tmp_path / "runs"], bundles=[bundle_dir]))
    response = client.get("/api/calibrations")
    assert response.status_code == 200
    records = response.json()
    assert [record["bundle_id"] for record in records] == ["cwh-growth-4cm-pilot-2026-11-04"]
    assert records[0]["warnings"]
    assert client.get("/api/calibrations/cwh-growth-4cm-pilot-2026-11-04").status_code == 200
    assert client.get("/api/calibrations/missing").status_code == 404


def test_the_shell_carries_the_visuals_import_map_and_the_vendored_runtime() -> None:
    """The 3D view is local, so the import map and the vendored three.js must ship together."""
    index = (webapp.STATIC_DIRECTORY / "index.html").read_text(encoding="utf-8")
    assert '"three": "./vendor/three/three.module.js"' in index
    assert (webapp.STATIC_DIRECTORY / "visuals.js").is_file()
    vendor = webapp.STATIC_DIRECTORY / "vendor" / "three"
    assert (vendor / "three.module.js").is_file()
    assert (vendor / "OrbitControls.js").is_file()
    assert (vendor / "LICENSE").is_file()


def test_the_agent_endpoint_reports_disabled_by_default(client: TestClient) -> None:
    """The LLM bridge is opt-in even when the browser surface is otherwise available."""
    payload = client.get("/api/agent").json()
    assert payload["enabled"] is False
    assert payload["model"]
    assert "workspace" in payload
    assert "timeout" in payload


def test_the_agent_guide_is_served_as_markdown(client: TestClient) -> None:
    """The browser can show the same instruction sheet the agent receives."""
    response = client.get("/api/agent/guide.md")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "FRESH_ACTIONS" in response.text
    assert "read-only" in response.text


def test_agent_chat_is_refused_when_disabled(client: TestClient) -> None:
    """A page cannot start the local agent without the explicit service flag."""
    response = client.post("/api/agent/chat", json={"message": "hello"})
    assert response.status_code == 403


def test_agent_chat_enriches_context_and_validates_chips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The server injects run facts and drops a chip that names a missing run."""
    _make_run(tmp_path / "run-a")
    captured: dict[str, object] = {}

    def fake_run(
        message: str,
        *,
        session: str | None,
        context: dict[str, object] | None,
        workspace: Path,
        model: str,
        timeout: float,
    ) -> dict[str, object]:
        captured.update(
            {
                "message": message,
                "session": session,
                "context": context,
                "workspace": workspace,
                "model": model,
                "timeout": timeout,
            }
        )
        return {
            "reply": "The summary is here.",
            "session": "ses_new",
            "actions": [{"tool": "read", "summary": "summary.csv"}],
            "chips": [
                {"label": "Summary", "action": "open_panel", "target": "summary"},
                {"label": "Missing", "action": "open_run", "target": "nope"},
            ],
        }

    monkeypatch.setattr(webapp, "run_agent", fake_run)
    client = TestClient(
        webapp.create_app(
            [tmp_path],
            allow_agent=True,
            agent_model="provider/model",
            agent_workspace=tmp_path,
            agent_timeout=12.0,
        )
    )
    response = client.post(
        "/api/agent/chat",
        json={
            "message": "What is the latest TPH?",
            "session": "ses_old",
            "run": "run-a",
            "year": 10,
            "context": {"workspace": "stand", "panel": "visuals"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] == "The summary is here."
    assert payload["session"] == "ses_new"
    assert [chip["target"] for chip in payload["chips"]] == ["summary"]
    context = captured["context"]
    assert isinstance(context, dict)
    assert context["workspace"] == "stand"
    assert context["year"] == 10
    assert context["run"]["id"] == "run-a"
    assert context["run"]["state"] == "complete"
    assert context["run"]["summary"][-1]["year"] == 10
    assert captured["workspace"] == tmp_path
    assert captured["model"] == "provider/model"
    assert captured["timeout"] == 12.0


def test_agent_chat_refuses_a_bad_session_and_missing_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bad sessions and stale run ids are refused before a subprocess starts."""
    _make_run(tmp_path / "run-a")
    client = TestClient(webapp.create_app([tmp_path], allow_agent=True, agent_workspace=tmp_path))
    assert (
        client.post("/api/agent/chat", json={"message": "x", "session": "bad"}).status_code == 422
    )
    assert client.post("/api/agent/chat", json={"message": "x", "run": "nope"}).status_code == 404


def test_agent_chat_translates_agent_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A timeout or unavailable CLI has a useful HTTP status, not a generic 500."""

    def fail(*args: object, **kwargs: object) -> dict[str, object]:
        raise AgentError("the agent did not answer", status_code=504)

    monkeypatch.setattr(webapp, "run_agent", fail)
    client = TestClient(webapp.create_app([tmp_path], allow_agent=True, agent_workspace=tmp_path))
    response = client.post("/api/agent/chat", json={"message": "hello"})
    assert response.status_code == 504
    assert "did not answer" in response.json()["detail"]


def test_agent_chat_can_context_a_running_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A running run has no summary yet; the assistant still gets its state."""
    _make_run(tmp_path / "run-b", summary=False)
    captured: dict[str, object] = {}

    def fake_run(
        message: str,
        *,
        session: str | None,
        context: dict[str, object] | None,
        workspace: Path,
        model: str,
        timeout: float,
    ) -> dict[str, object]:
        captured["context"] = context
        return {"reply": "Still running.", "session": "ses_new", "actions": [], "chips": []}

    monkeypatch.setattr(webapp, "run_agent", fake_run)
    client = TestClient(webapp.create_app([tmp_path], allow_agent=True, agent_workspace=tmp_path))
    response = client.post("/api/agent/chat", json={"message": "status?", "run": "run-b"})
    assert response.status_code == 200
    context = captured["context"]
    assert isinstance(context, dict)
    assert context["run"]["state"] == "running"
    assert context["run"]["summary"] == []


def _add_metric_summary(directory: Path) -> None:
    """Add the metric summary table the run list and overview read."""
    connection = sqlite3.connect(directory / "FVSOut.db")
    try:
        connection.execute(
            "create table FVS_Summary_Metric ("
            "Year integer, Age integer, Tph real, BA real, QMD real, TopHt real, "
            "CCF real, TCuM real, MCuM real)"
        )
        connection.executemany(
            "insert into FVS_Summary_Metric values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (0, 0, 551.0, 30.0, 26.5, 31.0, 130.0, 306.0, 293.0),
                (10, 10, 210.0, 18.0, 33.7, 33.0, 72.0, 207.0, 200.0),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def test_the_run_list_carries_the_latest_metric_summary(tmp_path: Path) -> None:
    """The overview cards get metric values, not the native summary columns."""
    _make_run(tmp_path / "run-c")
    _add_metric_summary(tmp_path / "run-c")
    client = TestClient(webapp.create_app([tmp_path]))
    listed = client.get("/api/runs").json()
    assert listed[0]["latest"]["year"] == 10
    assert listed[0]["latest"]["ba"] == 18.0
    assert listed[0]["latest"]["tph"] == 210.0
    assert listed[0]["latest"]["top_height"] == 33.0


def test_the_metric_summary_endpoint_returns_the_metric_rows(tmp_path: Path) -> None:
    """The summary panel reads FVS_Summary_Metric when it exists."""
    _make_run(tmp_path / "run-c")
    _add_metric_summary(tmp_path / "run-c")
    client = TestClient(webapp.create_app([tmp_path]))
    rows = client.get("/api/runs/run-c/metric-summary").json()
    assert [row["Year"] for row in rows] == [0, 10]
    assert rows[-1]["Tph"] == 210.0
    assert client.get("/api/runs/run-a/metric-summary").status_code == 404
