"""Optional local LLM assistant for the fresh-fvsbc web cockpit.

The service shells out to the installed ``opencode`` CLI. It never reads provider keys; the CLI
owns authentication. The assistant is disabled unless the service starts with ``--allow-agent``.

The model runs in the *plan* agent, not the build agent. This cockpit is a reader over run
artefacts, and the assistant must not edit a run, a calibration bundle, or the repository merely
because a browser prompt asked it to.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

__all__ = [
    "AGENT_GUIDE",
    "DEFAULT_AGENT_MODEL",
    "DEFAULT_AGENT_TIMEOUT",
    "FRESH_PANELS",
    "FRESH_WORKSPACES",
    "AgentError",
    "agent_info",
    "parse_agent_events",
    "run_agent",
    "split_actions",
]

#: The same model the other FRESH public demos use by default.
DEFAULT_AGENT_MODEL = "opencode-go/deepseek-v4.1-flash"

#: One turn may take five minutes; the CLI's first cold start is slow.
DEFAULT_AGENT_TIMEOUT = 300.0

#: Workspaces the browser can open through a validated chip.
FRESH_WORKSPACES = frozenset({"runs", "stand", "results", "evidence", "calibration"})

#: Panels the browser can open through a validated chip.
FRESH_PANELS = frozenset(
    {"summary", "tables", "trees", "compare", "visuals", "provenance", "keywords"}
)

AGENT_GUIDE = """\
You are the fresh-fvsbc assistant. You help a reader understand an FVS-BC run and the web cockpit.

This surface is a read-only reader. It shows files an FVS-BC run already wrote: the summary, the
SQLite tables, the keyword set, the provenance record, and the schematic stand view. The browser
context is supplied as JSON and is the source of truth for what the user is looking at. The server
may also include a compact run record: state, latest summary rows, provenance pins, and calibration
review state.

Rules:
- Use only values in the context or values you obtain by reading files. Never invent a number, run
  id, table name, calibration id, model pin, or path.
- The summary is a trajectory, not a causal model. Say what changed; do not claim why unless the
  evidence in the context or a file establishes it.
- A calibration bundle is data, not a certificate. Say `unsigned` or `signed` from its review
  record, never infer a sign-off, and never claim calibration, yield, AAC, legal, or whole-block
  validity that the context does not support.
- The oracle flag means a table was checked against a reference build, not that every number is
  certified. Keep that distinction.
- Treat the stand 2D/3D layout as schematic: FVS writes no x/y coordinates and the ground is flat.
- You may read the repository and docs, but do not edit files, run a projection, start a run, change
  a calibration bundle, or write outside a temporary note. The user is asking for an explanation,
  not an implementation.
- Keep the reply compact and concrete; use short bullets and small code blocks. The panel is narrow.
- Never print credentials, tokens, environment secrets, or private data.

If a safe UI follow-up helps, end the reply with exactly one line:

FRESH_ACTIONS: [{"label": "Open summary", "action": "open_panel", "target": "summary"}]

Allowed actions:
- `open_workspace` with target: runs, stand, results, evidence, calibration
- `open_panel` with target: summary, tables, trees, compare, visuals, provenance, keywords
- `open_run` with target: an existing run id
- `select_year` with target: an integer year shown by the stand view
- `ask` with target: a short follow-up prompt to put in the input

Never use a chip to start a run, edit data, run a command, or change calibration. If no chip is
needed, omit the marker.
"""


class AgentError(RuntimeError):
    """An assistant failure with an HTTP-like status code."""

    def __init__(self, message: str, *, status_code: int = 503) -> None:
        self.status_code = status_code
        super().__init__(message)


def agent_info(
    *,
    enabled: bool,
    model: str,
    workspace: Path,
    timeout: float,
) -> dict[str, Any]:
    """Return assistant availability and configuration.

    Parameters
    ----------
    enabled : bool
        Whether the service was started with ``--allow-agent``.
    model : str
        The provider/model string passed to OpenCode.
    workspace : Path
        The directory OpenCode runs in.
    timeout : float
        Seconds one turn may run.

    Returns
    -------
    dict
        ``enabled``, ``available``, ``model``, ``workspace``, and ``timeout``.
    """
    return {
        "enabled": enabled,
        "available": shutil.which("opencode") is not None,
        "model": model,
        "workspace": str(workspace),
        "timeout": timeout,
    }


def _chip(item: object) -> dict[str, Any] | None:
    """Validate one action chip; return ``None`` when it cannot be applied safely."""
    if not isinstance(item, Mapping):
        return None
    label = item.get("label")
    action = item.get("action")
    target = item.get("target")
    if not isinstance(label, str) or not label.strip() or not isinstance(action, str):
        return None
    label = label.strip()[:80]
    action = action.strip()
    if not isinstance(target, (str, int)):
        return None
    if action in {"open_workspace", "open_panel", "open_run", "ask"}:
        if not isinstance(target, str) or not target.strip():
            return None
        target = target.strip()
        if action == "open_workspace" and target not in FRESH_WORKSPACES:
            return None
        if action == "open_panel" and target not in FRESH_PANELS:
            return None
        if action == "open_run" and len(target) > 200:
            return None
        if action == "ask" and len(target) > 500:
            return None
        return {"label": label, "action": action, "target": target[:500]}
    if action == "select_year":
        if isinstance(target, bool):
            return None
        try:
            year = int(target)
        except (TypeError, ValueError):
            return None
        if year < 0 or year > 1000:
            return None
        return {"label": label, "action": action, "target": year}
    return None


def split_actions(reply: str) -> tuple[str, list[dict[str, Any]]]:
    """Remove a ``FRESH_ACTIONS`` marker and return validated UI chips.

    Parameters
    ----------
    reply : str
        The agent's text, possibly ending with a marker and JSON array.

    Returns
    -------
    tuple
        The visible reply and at most four validated action chips.
    """
    marker = re.search(r"FRESH_ACTIONS\s*:", reply, re.IGNORECASE)
    if marker is None:
        return reply, []
    visible = re.sub(r"\n?\s*```\s*$", "", reply[: marker.start()]).strip()
    suffix = reply[marker.end() :]
    decoder = json.JSONDecoder()
    chips: list[dict[str, Any]] = []
    position = 0
    while position < len(suffix):
        start = suffix.find("[", position)
        if start < 0:
            break
        try:
            parsed, consumed = decoder.raw_decode(suffix[start:])
        except json.JSONDecodeError:
            position = start + 1
            continue
        position = start + consumed
        if not isinstance(parsed, list):
            continue
        for item in parsed:
            chip = _chip(item)
            if chip is not None:
                chips.append(chip)
            if len(chips) == 4:
                return visible, chips
    return visible, chips


def run_agent(
    message: str,
    *,
    session: str | None,
    context: Mapping[str, Any] | None,
    workspace: Path,
    model: str = DEFAULT_AGENT_MODEL,
    timeout: float = DEFAULT_AGENT_TIMEOUT,
) -> dict[str, Any]:
    """Run one assistant turn through the installed OpenCode CLI.

    Parameters
    ----------
    message : str
        The user's prompt, already bounded by the endpoint.
    session : str or None
        An OpenCode session id to continue, or ``None`` for a new session.
    context : mapping or None
        The browser's compact UI context plus server-enriched run facts.
    workspace : Path
        The directory the agent may read.
    model : str, optional
        The provider/model string.
    timeout : float, optional
        Seconds before the turn is abandoned.

    Returns
    -------
    dict
        ``reply``, ``session``, ``actions``, and ``chips``.

    Raises
    ------
    AgentError
        When the CLI is missing, times out, or returns no text.
    """
    executable = shutil.which("opencode")
    if executable is None:
        raise AgentError("opencode is not on the service PATH", status_code=503)
    prompt = (
        f"{AGENT_GUIDE}\n\nCurrent UI context (JSON): "
        f"{json.dumps(dict(context or {}), ensure_ascii=False)[:6000]}\n\nUser: {message}"
    )
    command = [
        executable,
        "run",
        "--agent",
        "plan",
        "--model",
        model,
        "--format",
        "json",
        "--auto",
    ]
    if session and session.startswith("ses"):
        command.extend(["--session", session])
    command.append(prompt)
    try:
        completed = subprocess.run(
            command,
            cwd=str(workspace),
            env=_agent_environment(workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise AgentError(
            f"the assistant did not answer within {timeout:g} seconds", status_code=504
        ) from error
    except OSError as error:
        raise AgentError(f"could not start opencode: {error}", status_code=503) from error
    reply, session_id, actions, errors = parse_agent_events(completed.stdout)
    if not reply:
        detail = (
            errors[-1] if errors else (completed.stderr.strip() or "the assistant returned no text")
        )
        raise AgentError(detail[:500], status_code=502)
    visible, chips = split_actions(reply)
    return {
        "reply": visible,
        "session": session_id or session,
        "actions": actions,
        "chips": chips,
    }


def parse_agent_events(stdout: str) -> tuple[str, str | None, list[dict[str, str]], list[str]]:
    """Parse the JSON-lines output of ``opencode run --format json``.

    Parameters
    ----------
    stdout : str
        The command's standard output.

    Returns
    -------
    tuple
        Joined text, session id, tool-use summaries, and error messages.
    """
    texts: list[str] = []
    actions: list[dict[str, str]] = []
    errors: list[str] = []
    session_id: str | None = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, Mapping):
            continue
        candidate = event.get("sessionID")
        if isinstance(candidate, str) and candidate.startswith("ses"):
            session_id = candidate
        event_type = event.get("type")
        if event_type == "error":
            failure = event.get("error")
            if isinstance(failure, Mapping) and isinstance(failure.get("message"), str):
                errors.append(str(failure["message"]))
            continue
        part = event.get("part")
        if not isinstance(part, Mapping):
            continue
        if event_type == "text":
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
        elif event_type == "tool_use":
            tool = part.get("tool")
            state = part.get("state")
            summary = ""
            if isinstance(state, Mapping):
                title = state.get("title")
                if isinstance(title, str):
                    summary = title
                inputs = state.get("input")
                if isinstance(inputs, Mapping):
                    for key in ("command", "filePath", "path", "pattern", "url", "description"):
                        value = inputs.get(key)
                        if isinstance(value, str) and value.strip():
                            summary = value.strip()
                            break
            if isinstance(tool, str):
                action = {"tool": tool, "summary": summary[:160]}
                if action not in actions:
                    actions.append(action)
    return "\n\n".join(texts).strip(), session_id, actions[-12:], errors


def _agent_environment(workspace: Path) -> dict[str, str]:
    """Build a sanitized environment for the assistant subprocess."""
    environment = dict(os.environ)
    paths = [str(workspace / "src")]
    if environment.get("PYTHONPATH"):
        paths.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(paths)
    environment["FRESH_FVSBC_WORKSPACE"] = str(workspace)
    for name in (
        "OPENCODE_SESSION_ID",
        "OPENCODE_TERMINAL",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "AWS_DEFAULT_REGION",
        "S3_ENDPOINT_URL",
        "GLOBUS_ACCESS_TOKEN",
        "GLOBUS_REFRESH_TOKEN",
        "CF_ACCESS_CLIENT_ID",
        "CF_ACCESS_CLIENT_SECRET",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "OPENROUTER_API_KEY",
    ):
        environment.pop(name, None)
    return environment
