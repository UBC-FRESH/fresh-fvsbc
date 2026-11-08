"""Tests for the optional OpenCode assistant bridge."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from fresh_fvsbc.web import agent


def _events(*, text: str = "OK", tool: str = "read", session: str = "ses_test") -> str:
    """Build a minimal OpenCode JSON-lines stream."""
    return "\n".join(
        [
            json.dumps({"type": "step_start", "sessionID": session, "part": {}}),
            json.dumps(
                {
                    "type": "tool_use",
                    "sessionID": session,
                    "part": {
                        "tool": tool,
                        "state": {"title": "Read the summary", "input": {"path": "summary.csv"}},
                    },
                }
            ),
            json.dumps(
                {
                    "type": "text",
                    "sessionID": session,
                    "part": {"text": text},
                }
            ),
        ]
    )


def test_agent_info_reports_availability(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The info payload distinguishes enabled from executable availability."""
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/opencode")
    info = agent.agent_info(enabled=True, model="p/m", workspace=tmp_path, timeout=12.0)
    assert info == {
        "enabled": True,
        "available": True,
        "model": "p/m",
        "workspace": str(tmp_path),
        "timeout": 12.0,
    }
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert (
        agent.agent_info(enabled=True, model="p/m", workspace=tmp_path, timeout=12.0)["available"]
        is False
    )


@pytest.mark.parametrize(
    ("reply", "visible", "expected_actions"),
    [
        (
            "Here is the result.\nFRESH_ACTIONS: "
            + json.dumps([{"label": "Summary", "action": "open_panel", "target": "summary"}]),
            "Here is the result.",
            [{"label": "Summary", "action": "open_panel", "target": "summary"}],
        ),
        (
            "No actions here.",
            "No actions here.",
            [],
        ),
        (
            'One.\nFRESH_ACTIONS: [{"label":"Bad","action":"open_panel","target":"nope"}]',
            "One.",
            [],
        ),
        (
            'Year.\nFRESH_ACTIONS: [{"label":"Year 10","action":"select_year","target":10}]',
            "Year.",
            [{"label": "Year 10", "action": "select_year", "target": 10}],
        ),
    ],
)
def test_split_actions_returns_only_safe_chips(
    reply: str, visible: str, expected_actions: list[dict[str, Any]]
) -> None:
    """Unknown actions and panels are dropped rather than sent to the browser."""
    text, chips = agent.split_actions(reply)
    assert text == visible
    assert chips == expected_actions


def test_split_actions_caps_the_chip_count() -> None:
    """A runaway list cannot produce an unbounded chip row."""
    items = [
        {"label": f"Panel {index}", "action": "open_panel", "target": "summary"}
        for index in range(8)
    ]
    text, chips = agent.split_actions("Here.\nFRESH_ACTIONS: " + json.dumps(items))
    assert text == "Here."
    assert len(chips) == 4


def test_parse_agent_events_reads_text_tools_and_errors() -> None:
    """The parser uses text parts, ignores step metadata, and preserves a session id."""
    stdout = "\n".join(
        [
            json.dumps({"type": "step_start", "sessionID": "ses_a", "part": {}}),
            json.dumps(
                {
                    "type": "tool_use",
                    "sessionID": "ses_a",
                    "part": {
                        "tool": "bash",
                        "state": {"input": {"command": "python -m pytest"}},
                    },
                }
            ),
            json.dumps({"type": "text", "sessionID": "ses_a", "part": {"text": "Answer"}}),
            json.dumps({"type": "error", "sessionID": "ses_a", "error": {"message": "nope"}}),
        ]
    )
    text, session, tools, errors = agent.parse_agent_events(stdout)
    assert text == "Answer"
    assert session == "ses_a"
    assert tools == [{"tool": "bash", "summary": "python -m pytest"}]
    assert errors == ["nope"]


def test_run_agent_builds_the_command_and_sanitizes_the_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The bridge runs the plan agent with a bounded prompt and no provider secrets."""
    captured: dict[str, Any] = {}

    def fake_run(
        command: list[str],
        **kwargs: Any,  # noqa: ANN401 - subprocess.run keyword surface
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, _events(), "")

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/opencode")
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    result = agent.run_agent(
        "What changed?",
        session="ses_old",
        context={"view": "summary"},
        workspace=tmp_path,
        model="p/m",
        timeout=9.0,
    )
    command = captured["command"]
    assert command[:8] == [
        "/usr/bin/opencode",
        "run",
        "--agent",
        "plan",
        "--model",
        "p/m",
        "--format",
        "json",
    ]
    assert command[8:10] == ["--auto", "--session"]
    assert command[10] == "ses_old"
    assert "What changed?" in command[-1]
    assert result["reply"] == "OK"
    assert result["session"] == "ses_test"
    environment = captured["kwargs"]["env"]
    assert "OPENAI_API_KEY" not in environment
    assert "GITHUB_TOKEN" not in environment
    assert environment["FRESH_FVSBC_WORKSPACE"] == str(tmp_path)


def test_run_agent_failures_are_named(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A missing CLI, a timeout, and empty output each get their own status."""
    monkeypatch.setattr(shutil, "which", lambda name: None)
    with pytest.raises(agent.AgentError) as missing:
        agent.run_agent("x", session=None, context={}, workspace=tmp_path)
    assert missing.value.status_code == 503

    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/opencode")

    def timeout(
        command: list[str],
        **kwargs: Any,  # noqa: ANN401 - subprocess.run keyword surface
    ) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(command, 1)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(agent.AgentError) as timed:
        agent.run_agent("x", session=None, context={}, workspace=tmp_path)
    assert timed.value.status_code == 504

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "", ""),
    )
    with pytest.raises(agent.AgentError) as empty:
        agent.run_agent("x", session=None, context={}, workspace=tmp_path)
    assert empty.value.status_code == 502


def test_chip_validation_rejects_unsafe_or_malformed_actions() -> None:
    """The browser only receives chips whose action and target are known."""
    assert agent._chip(None) is None
    assert agent._chip({}) is None
    assert agent._chip({"label": "", "action": "ask", "target": "x"}) is None
    assert agent._chip({"label": "x", "action": "delete", "target": "x"}) is None
    assert agent._chip({"label": "x", "action": "ask", "target": []}) is None
    assert agent._chip({"label": "x", "action": "open_workspace", "target": "nope"}) is None
    assert agent._chip({"label": "x", "action": "open_panel", "target": "nope"}) is None
    assert agent._chip({"label": "x", "action": "open_run", "target": "r" * 201}) is None
    assert agent._chip({"label": "x", "action": "ask", "target": "q" * 501}) is None
    assert agent._chip({"label": "x", "action": "select_year", "target": True}) is None
    assert agent._chip({"label": "x", "action": "select_year", "target": "not-a-year"}) is None
    assert agent._chip({"label": "x", "action": "select_year", "target": 1001}) is None


def test_split_actions_tolerates_malformed_json_before_a_valid_array() -> None:
    """A broken marker does not hide a later valid chip."""
    text, chips = agent.split_actions(
        "Answer\nFRESH_ACTIONS: [broken, {still broken}] "
        + json.dumps([{"label": "Ask", "action": "ask", "target": "Follow up"}]),
    )
    assert text == "Answer"
    assert chips == [{"label": "Ask", "action": "ask", "target": "Follow up"}]


def test_split_actions_without_an_array_returns_no_chips() -> None:
    """A marker with no JSON is removed from the visible text."""
    text, chips = agent.split_actions("Answer\nFRESH_ACTIONS: not-json")
    assert text == "Answer"
    assert chips == []


def test_parse_agent_events_ignores_non_events_and_empty_text() -> None:
    """Malformed lines, scalar JSON, missing parts, and blank text are inert."""
    stdout = "\n".join(
        [
            "not-json",
            json.dumps(1),
            json.dumps({"type": "step_start"}),
            json.dumps({"type": "text", "part": {"text": "  "}}),
            json.dumps({"type": "error", "error": "not-a-mapping"}),
            json.dumps(
                {
                    "type": "tool_use",
                    "part": {
                        "tool": "read",
                        "state": {"title": "Read it", "input": {"filePath": "run.key"}},
                    },
                }
            ),
            json.dumps(
                {
                    "type": "tool_use",
                    "part": {
                        "tool": "read",
                        "state": {"title": "Read it", "input": {"filePath": "run.key"}},
                    },
                }
            ),
        ]
    )
    text, session, tools, errors = agent.parse_agent_events(stdout)
    assert text == ""
    assert session is None
    assert tools == [{"tool": "read", "summary": "run.key"}]
    assert errors == []


def test_run_agent_reports_a_process_start_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An OS-level launch failure is a 503, not an unhandled traceback."""
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/opencode")

    def broken(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("no exec")

    monkeypatch.setattr(subprocess, "run", broken)
    with pytest.raises(agent.AgentError) as error:
        agent.run_agent("x", session=None, context={}, workspace=tmp_path)
    assert error.value.status_code == 503
    assert "no exec" in str(error.value)


def test_agent_environment_keeps_an_existing_pythonpath(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The workspace src path is prepended without discarding the service path."""
    monkeypatch.setenv("PYTHONPATH", "/service/path")
    environment = agent._agent_environment(tmp_path)
    assert environment["PYTHONPATH"] == f"{tmp_path / 'src'}:/service/path"
    assert environment["FRESH_FVSBC_WORKSPACE"] == str(tmp_path)
