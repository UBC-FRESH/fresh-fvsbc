"""The HTTP surface: a reader over a run's artefacts.

Every response is something the CLI already wrote — a run's summary, a table from its database, its
keyword set, its provenance — or the skin manifests the front end renders. The service holds no
model
state and computes no value the CLI cannot reproduce.

A run is started by invoking the CLI in a subprocess, never by importing the Fortran extension into
the
request process, so a projection that crashes cannot take the surface down with it.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from collections.abc import Awaitable, Callable, Iterator, Sequence
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from fresh_fvsbc.bundle import BundleError, CalibrationBundle, load_bundle
from fresh_fvsbc.outputs import EXPOSED_TABLES, ORACLE_TABLES, STANDALONE_VERIFIED
from fresh_fvsbc.web import runs as runstore
from fresh_fvsbc.web import visuals as visualstore
from fresh_fvsbc.web.agent import (
    AGENT_GUIDE,
    DEFAULT_AGENT_MODEL,
    DEFAULT_AGENT_TIMEOUT,
    AgentError,
    agent_info,
    run_agent,
)
from fresh_fvsbc.web.skins import load_skins

__all__ = ["create_app", "main"]

#: The directory the front end is served from.
STATIC_DIRECTORY: Path = Path(__file__).resolve().parent / "static"

#: How often the event stream re-reads a run's directory while it is running, in seconds.
POLL_SECONDS: float = 1.0

#: How long a live event stream stays open before it closes and the browser reconnects, in seconds.
STREAM_SECONDS: float = 600.0


class AgentChatRequest(BaseModel):
    """One assistant turn from the browser."""

    message: str = Field(min_length=1, max_length=8000)
    session: str | None = Field(default=None, max_length=200)
    context: dict[str, Any] | None = None
    run: str | None = Field(default=None, max_length=200)
    year: int | None = Field(default=None, ge=0, le=1000)


def fmt_like(value: object) -> str:
    """Format a summary value without assuming whether it is a float or an integer."""
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return f"{value:,}" if isinstance(value, int) else str(value)


def create_app(
    roots: Sequence[Path],
    *,
    allow_remote: bool = False,
    root_path: str = "",
    bundles: Sequence[Path] = (),
    allow_agent: bool = False,
    agent_model: str = DEFAULT_AGENT_MODEL,
    agent_workspace: Path | None = None,
    agent_timeout: float = DEFAULT_AGENT_TIMEOUT,
) -> FastAPI:
    """Build the application over a set of run roots.

    Parameters
    ----------
    roots : sequence of Path
        The directories searched for run directories, one level deep.
    root_path : str, optional
        The prefix the app is served under. The service strips it from the request path when the
        proxy leaves it on, and answers without it when the proxy removes it, so one build serves
        either way. A proxy that forwards the prefix is the normal case: JupyterHub does not strip
        it.
    allow_remote : bool, optional
        Whether the caller has accepted a non-loopback bind. The flag is carried into the app so
        the decision is recorded where it is used. Behind the JupyterHub port proxy this is the
        normal case: the proxy authenticates the request, and the service has to listen off
        loopback for it.
    allow_agent : bool, optional
        Whether the assistant may run an OpenCode turn. It remains disabled by default because
        the process can read the workspace and execute commands as the service user.
    agent_model : str, optional
        The provider/model handed to ``opencode run``.
    agent_workspace : Path or None, optional
        The directory the assistant may read. ``None`` uses the service's working directory.
    agent_timeout : float, optional
        Seconds one assistant turn may run.

    Returns
    -------
    fastapi.FastAPI
        The application.
    """
    app = FastAPI(
        title="fresh-fvsbc",
        description="A reader over the artefacts an FVS-BC run leaves behind.",
    )

    @app.middleware("http")
    async def _no_store_shell(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Keep the shell and its assets out of browser and edge caches.

        The demo is updated in place, and a stale ``app.js`` is indistinguishable from a broken
        assistant. The shell is tiny, so revalidation costs less than a cache surprise.
        """
        response = await call_next(request)
        path = request.scope.get("path", "")
        if path in {"/", "/index.html"} or path.endswith((".html", ".js", ".css")):
            response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    if root_path:
        prefix = "/" + root_path.strip("/")

        @app.middleware("http")
        async def _strip_prefix(
            request: Request, call_next: Callable[[Request], Awaitable[Response]]
        ) -> Response:
            """Strip the proxy's prefix when the request still carries it.

            JupyterHub forwards ``/user/<name>/proxy/<port>/...`` without removing it, and a
            proxy that does remove it is equally valid. Both land on the same routes.

            Parameters
            ----------
            request : fastapi.Request
                The incoming request.
            call_next : callable
                The rest of the stack.

            Returns
            -------
            fastapi.responses.Response
                The response.
            """
            path = request.scope.get("path", "")
            if path == prefix or path.startswith(prefix + "/"):
                request.scope["path"] = path[len(prefix) :] or "/"
                request.scope["root_path"] = prefix
            return await call_next(request)

    resolved = tuple(Path(root).resolve() for root in roots)
    bundle_roots = tuple(Path(root).resolve() for root in bundles)
    skins = load_skins()
    app.state.roots = resolved
    app.state.bundle_roots = bundle_roots
    app.state.allow_remote = allow_remote
    app.state.allow_agent = allow_agent
    app.state.agent_model = agent_model
    app.state.agent_workspace = (
        Path(agent_workspace).expanduser().resolve()
        if agent_workspace is not None
        else Path.cwd().resolve()
    )
    app.state.agent_timeout = agent_timeout
    app.state.skins = {skin.id: skin for skin in skins}
    #: The child processes this service started, so a run that died is reported as failed rather
    #: than running forever. A restarted service loses this, and a dead run stays ``running``.
    app.state.processes = {}

    def _find(run_id: str) -> runstore.Run:
        """Resolve a run identifier to a run, or raise the HTTP error for it.

        Parameters
        ----------
        run_id : str
            The directory name of the run.

        Returns
        -------
        fresh_fvsbc.web.runs.Run
            The run.

        Raises
        ------
        fastapi.HTTPException
            404 when no run under the configured roots has that identifier.
        """
        for run in runstore.discover(app.state.roots):
            if run.id == run_id:
                return run
        raise HTTPException(status_code=404, detail=f"no run {run_id!r} under the configured roots")

    def _metric_rows(run: runstore.Run) -> list[dict[str, Any]]:
        """Return the metric summary rows, or an empty list when the table is absent.

        ``summary.csv`` is FVS's native summary and uses the variant's internal units. The web
        cockpit is metric, so its overview reads ``FVS_Summary_Metric`` instead and falls back to
        the native file only with an explicit unit warning.
        """
        try:
            return list(runstore.table(run, "FVS_Summary_Metric", limit=runstore.MAX_LIMIT)["rows"])
        except runstore.RunError:
            return []

    def _latest_metric(run: runstore.Run) -> dict[str, Any] | None:
        """Return the last metric-summary row for a complete run, when available."""
        rows = _metric_rows(run)
        if not rows:
            return None
        latest = max(rows, key=lambda row: float(row.get("Year") or 0))
        return {
            "year": latest.get("Year"),
            "age": latest.get("Age"),
            "tph": latest.get("Tph"),
            "ba": latest.get("BA"),
            "qmd": latest.get("QMD"),
            "top_height": latest.get("TopHt"),
            "merchantable_m3_ha": latest.get("MCuM"),
            "total_m3_ha": latest.get("TCuM"),
            "ccf": latest.get("CCF"),
        }

    def _bundle_files() -> list[Path]:
        """Return candidate bundle files under the configured roots, sorted."""
        files: set[Path] = set()
        for root in app.state.bundle_roots:
            if root.is_file() and root.suffix == ".json":
                files.add(root)
            elif root.is_dir():
                files.update(root.glob("*.json"))
        return sorted(files)

    def _bundle_record(bundle: CalibrationBundle, path: Path) -> dict[str, Any]:
        """Serialize the parts of a bundle a reviewer needs to see."""
        domain = bundle.domain
        return {
            "bundle_id": bundle.bundle_id,
            "version": bundle.version,
            "path": str(path),
            "claim": bundle.claim,
            "pins": dict(bundle.pins),
            "domain": {
                "regions": list(domain.regions),
                "tsas": list(domain.tsas),
                "becs": list(domain.becs),
                "species_groups": list(domain.species_groups),
                "management": list(domain.management),
                "qmd_min": domain.qmd_min,
                "ba_min": domain.ba_min,
                "dbh_classes": [list(item) for item in domain.dbh_classes],
            },
            "parameters": [
                {
                    "keyword": parameter.keyword,
                    "fields": list(parameter.fields),
                    "units": parameter.units,
                    "bounds": list(parameter.bounds) if parameter.bounds is not None else None,
                }
                for parameter in bundle.parameters
            ],
            "training": dict(bundle.training),
            "review": dict(bundle.review),
            "warnings": list(bundle.warnings),
            "ingrowth": None
            if bundle.ingrowth is None
            else {
                "model_id": bundle.ingrowth.model_id,
                "version": bundle.ingrowth.version,
                "method": bundle.ingrowth.method,
                "rates": len(bundle.ingrowth.rates),
                "scale": bundle.ingrowth.scale,
            },
        }

    def _bundles() -> list[dict[str, Any]]:
        """Load every valid bundle under the configured roots."""
        records: list[dict[str, Any]] = []
        for path in _bundle_files():
            try:
                bundle = load_bundle(path)
            except (BundleError, OSError, ValueError):
                continue
            records.append(_bundle_record(bundle, path))
        return records

    def _assistant_answer(message: str, run_id: str | None) -> dict[str, Any]:
        """Answer from the open run's own summary and provenance, without inventing causes."""
        text = message.lower()
        citations: list[dict[str, str]] = []
        suggestions = [
            "Summarize this run.",
            "Why did TPH change?",
            "Is the calibration bundle signed?",
            "Show provenance.",
        ]
        if not run_id:
            return {
                "reply": "Open a run first; I can read its summary, calibration, and provenance.",
                "citations": [],
                "suggestions": suggestions,
            }
        run = _find(run_id)
        try:
            rows = runstore.summary(run)
            provenance = runstore.provenance(run)
        except runstore.RunError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        latest = rows[-1] if rows else {}
        first = rows[0] if rows else {}
        recorded = provenance.get("provenance", {})
        calibration_id = recorded.get("calibration_id", "")
        bundle = next((item for item in _bundles() if item["bundle_id"] == calibration_id), None)
        if "signed" in text or "calibration" in text or "bundle" in text:
            if not calibration_id:
                reply = f"Run {run.id} records no calibration bundle."
            else:
                state_text = (
                    "signed"
                    if bundle and bundle.get("review", {}).get("signed_off")
                    else "unsigned"
                )
                reply = (
                    f"The run records calibration {calibration_id} "
                    f"({recorded.get('calibration_version', 'unknown version')}); "
                    f"the bundle is {state_text}."
                )
                if bundle and bundle.get("warnings"):
                    reply += " Warnings: " + "; ".join(bundle["warnings"][:2])
            citations.extend(
                [
                    {"label": "Calibration", "kind": "workspace", "target": "calibration"},
                    {"label": "Provenance", "kind": "panel", "target": "provenance"},
                ]
            )
        elif "provenance" in text or "version" in text or "pin" in text:
            keys = ("fresh_fvsbc_version", "pyfvs_commit", "fvs_source_commit", "variant")
            reply = (
                "Provenance: " + ", ".join(f"{key}={recorded.get(key, '—')}" for key in keys) + "."
            )
            citations.append({"label": "Provenance", "kind": "panel", "target": "provenance"})
        elif "tph" in text or "tree" in text or "density" in text:
            reply = (
                f"TPH in the summary goes from {fmt_like(first.get('tpa'))} at year "
                f"{first.get('year', '?')} to {fmt_like(latest.get('tpa'))} at year "
                f"{latest.get('year', '?')}. This view reads the summary; it cannot prove a cause. "
                "The Details drawer shows the calibration and provenance."
            )
            citations.append({"label": "Summary", "kind": "panel", "target": "summary"})
        elif "ba" in text or "basal" in text:
            reply = (
                f"BA in the summary goes from {fmt_like(first.get('baa'))} to "
                f"{fmt_like(latest.get('baa'))} between years {first.get('year', '?')} and "
                f"{latest.get('year', '?')}."
            )
            citations.append({"label": "Summary", "kind": "panel", "target": "summary"})
        else:
            reply = (
                f"Run {run.id} is {run.state}; the summary has {len(rows)} rows, from "
                f"year {first.get('year', '?')} to {latest.get('year', '?')}. "
                f"Latest TPH (summary) is {fmt_like(latest.get('tpa'))} and latest BA is "
                f"{fmt_like(latest.get('baa'))}."
            )
            citations.append({"label": "Summary", "kind": "panel", "target": "summary"})
        return {"reply": reply, "citations": citations, "suggestions": suggestions}

    @app.post("/api/assistant")
    def assistant(body: dict[str, Any] | None = None) -> dict[str, Any]:
        """Answer a context-aware question from the open run's own artefacts."""
        payload = body or {}
        message = str(payload.get("message", "") or "").strip()
        if not message:
            raise HTTPException(status_code=422, detail="the message is empty")
        if len(message) > 4000:
            raise HTTPException(status_code=422, detail="the message is too long")
        return _assistant_answer(message, str(payload.get("run", "") or "").strip() or None)

    def _agent_context(
        payload: dict[str, Any] | None,
        run_id: str | None,
        year: int | None,
    ) -> dict[str, Any]:
        """Merge browser context with server-read run facts.

        The browser supplies what it is showing; the server supplies the run's own summary and
        provenance so the assistant cannot be tricked into inventing a run's numbers by a page
        that has gone stale.
        """
        context: dict[str, Any] = dict(payload or {})
        if year is not None:
            context["year"] = year
        if not run_id:
            return context
        run = _find(run_id)
        rows: list[dict[str, Any]] = []
        summary_source = "none"
        if run.state == "complete":
            metric_rows = _metric_rows(run)
            if metric_rows:
                rows = metric_rows
                summary_source = "FVS_Summary_Metric (metric units)"
            else:
                try:
                    rows = runstore.summary(run)
                    summary_source = "summary.csv (FVS native units, not metric)"
                except runstore.RunError as error:
                    context["run"] = {"id": run.id, "state": run.state, "error": str(error)}
                    return context
        try:
            provenance = runstore.provenance(run)
        except runstore.RunError:
            provenance = {}
        recorded = provenance.get("provenance", {})
        compact_rows = rows if len(rows) <= 24 else [*rows[:2], *rows[-16:]]
        calibration_id = recorded.get("calibration_id", "")
        bundle = next((item for item in _bundles() if item["bundle_id"] == calibration_id), None)
        context["run"] = {
            "id": run.id,
            "state": run.state,
            "summary_source": summary_source,
            "summary": compact_rows,
            "provenance": {
                key: recorded.get(key)
                for key in (
                    "fresh_fvsbc_version",
                    "pyfvs_commit",
                    "fvs_source_commit",
                    "variant",
                    "calibration_id",
                    "calibration_version",
                    "bec",
                    "qmd",
                    "ba",
                    "tsa",
                )
            },
            "calibration": None
            if bundle is None
            else {
                "bundle_id": bundle["bundle_id"],
                "version": bundle["version"],
                "claim": bundle["claim"],
                "review": bundle["review"],
                "warnings": bundle["warnings"],
            },
        }
        return context

    @app.get("/api/agent")
    def agent_status() -> dict[str, Any]:
        """Report whether the optional local agent is enabled and available."""
        return agent_info(
            enabled=bool(app.state.allow_agent),
            model=str(app.state.agent_model),
            workspace=Path(app.state.agent_workspace),
            timeout=float(app.state.agent_timeout),
        )

    @app.get("/api/agent/guide.md")
    def agent_guide() -> Response:
        """Return the assistant instruction sheet as Markdown."""
        return Response(content=AGENT_GUIDE, media_type="text/markdown; charset=utf-8")

    @app.post("/api/agent/chat")
    def agent_chat(body: AgentChatRequest) -> dict[str, Any]:
        """Run one assistant turn through the local OpenCode CLI."""
        if not app.state.allow_agent:
            raise HTTPException(
                status_code=403,
                detail="the assistant is disabled; restart the service with --allow-agent",
            )
        session = (body.session or "").strip()
        if session and not session.startswith("ses"):
            raise HTTPException(
                status_code=422,
                detail="an assistant session must be an OpenCode session id starting with 'ses'",
            )
        context = _agent_context(body.context, body.run, body.year)
        if len(json.dumps(context, ensure_ascii=False)) > 20_000:
            raise HTTPException(status_code=413, detail="the assistant context is too large")
        try:
            result = run_agent(
                body.message,
                session=session or None,
                context=context,
                workspace=Path(app.state.agent_workspace),
                model=str(app.state.agent_model),
                timeout=float(app.state.agent_timeout),
            )
        except AgentError as error:
            raise HTTPException(status_code=error.status_code, detail=str(error)) from error
        chips: list[dict[str, Any]] = []
        for chip in result.get("chips", []):
            if chip.get("action") == "open_run":
                try:
                    _find(str(chip["target"]))
                except HTTPException:
                    continue
            chips.append(chip)
        return {**result, "chips": chips}

    @app.get("/api/calibrations")
    def calibrations() -> list[dict[str, Any]]:
        """List the valid calibration bundles visible to this service.

        Returns
        -------
        list of dict
            Bundle metadata, claim, domain, parameters, review state, and warnings.
        """
        return _bundles()

    @app.get("/api/calibrations/{bundle_id}")
    def calibration(bundle_id: str) -> dict[str, Any]:
        """Return one calibration bundle by its stable identifier."""
        for record in _bundles():
            if record["bundle_id"] == bundle_id:
                return record
        raise HTTPException(status_code=404, detail=f"no calibration bundle {bundle_id!r}")

    @app.get("/api/skins")
    def list_skins() -> list[dict[str, Any]]:
        """Return the shipped skin manifests.

        Returns
        -------
        list of dict
            One record per skin, with its panels and actions already filtered by ``read_only``.
        """
        return [
            {
                "id": skin.id,
                "title": skin.title,
                "panels": list(skin.panels),
                "actions": list(skin.actions),
                "read_only": skin.read_only,
            }
            for skin in app.state.skins.values()
        ]

    @app.get("/api/oracle")
    def oracle() -> dict[str, Any]:
        """Return which exposed tables are checked against an independent source.

        Returns
        -------
        dict
            ``exposed``, ``oracle`` (the official dump), ``standalone`` (a standalone ``FVSbc``) and
            the table lists, so a client can say how much of the surface is verified without having
            to know the numbers.

        Notes
        -----
        The standalone comparison is the broader of the two: it covers every table either build
        writes, not only the four the official dump carries.
        """
        return {
            "exposed": len(EXPOSED_TABLES),
            "oracle": len(ORACLE_TABLES),
            "tables": list(ORACLE_TABLES),
            "standalone": len(STANDALONE_VERIFIED),
            "standalone_tables": list(STANDALONE_VERIFIED),
        }

    @app.get("/api/runs")
    def list_runs() -> list[dict[str, Any]]:
        """List the runs under the configured roots.

        Returns
        -------
        list of dict
            One record per run, with its identifier, state and the tables it wrote.
        """
        records: list[dict[str, Any]] = []
        for run in runstore.discover(app.state.roots):
            state: str = run.state
            process = app.state.processes.get(run.id)
            if state == "running" and process is not None and process.poll() is not None:
                state = "complete" if process.returncode == 0 else "failed"
            records.append(
                {
                    "id": run.id,
                    "state": state,
                    "path": str(run.path),
                    "tables": len(runstore.tables(run)) if run.state == "complete" else 0,
                    "latest": _latest_metric(run) if state == "complete" else None,
                }
            )
        return records

    @app.get("/api/runs/{run_id}/metric-summary")
    def run_metric_summary(run_id: str) -> list[dict[str, Any]]:
        """Return the metric summary table, which is what the overview renders."""
        run = _find(run_id)
        rows = _metric_rows(run)
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"the run {run.id} wrote no FVS_Summary_Metric table",
            )
        return rows

    @app.get("/api/runs/{run_id}/summary")
    def run_summary(run_id: str) -> list[dict[str, Any]]:
        """Return a run's parsed summary.

        Parameters
        ----------
        run_id : str
            The run's identifier.

        Returns
        -------
        list of dict
            One record per stand-period.
        """
        run = _find(run_id)
        try:
            return runstore.summary(run)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/api/runs/{run_id}/tables")
    def run_tables(run_id: str) -> list[dict[str, Any]]:
        """Return the exposed tables a run wrote, with row counts and the oracle flag.

        Parameters
        ----------
        run_id : str
            The run's identifier.

        Returns
        -------
        list of dict
            One record per table.
        """
        run = _find(run_id)
        try:
            return runstore.tables(run)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/api/runs/{run_id}/tables/{name}")
    def run_table(
        run_id: str,
        name: str,
        limit: int = Query(runstore.DEFAULT_LIMIT, ge=1, le=runstore.MAX_LIMIT),
        offset: int = Query(0, ge=0),
        q: str | None = Query(None, max_length=200),
    ) -> dict[str, Any]:
        """Return one table, as a page.

        Parameters
        ----------
        run_id : str
            The run's identifier.
        name : str
            The table, which must be one this package exposes.
        limit : int, optional
            The page size.
        offset : int, optional
            The first row of the page.
        q : str, optional
            A literal, case-insensitive filter applied across every column before paging.

        Returns
        -------
        dict
            The columns, the page of rows, the filtered total, the query, and the oracle flag.
        """
        run = _find(run_id)
        try:
            return runstore.table(run, name, limit=limit, offset=offset, query=q)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/api/runs/{run_id}/tables/{name}/csv")
    def run_table_csv(
        run_id: str,
        name: str,
        q: str | None = Query(None, max_length=200),
    ) -> Response:
        """Return one exposed table as a CSV attachment, with the same literal filter."""
        run = _find(run_id)
        try:
            text = runstore.table_csv(run, name, query=q)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        filename = f"{run.id}-{name}.csv"
        return Response(
            content=text,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.get("/api/runs/{run_id}/visuals")
    def run_visuals(run_id: str, year: int | None = Query(None)) -> dict[str, Any]:
        """Return the schematic 2D and 3D stand payload for one year.

        Parameters
        ----------
        run_id : str
            The run's identifier.
        year : int, optional
            The year to draw. The first year in the tree list is used when this is omitted.

        Returns
        -------
        dict
            The layout, the trees, the cut trees, the species counts, and the summary row for the
            year. A run with no per-tree table answers with ``available`` false and a reason.
        """
        run = _find(run_id)
        try:
            return visualstore.visuals(run, year)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/api/runs/{run_id}/keywords")
    def run_keywords(run_id: str) -> Response:
        """Return a run's keyword file as plain text.

        Parameters
        ----------
        run_id : str
            The run's identifier.

        Returns
        -------
        fastapi.responses.Response
            The keyword set, as ``text/plain``.
        """
        run = _find(run_id)
        try:
            text = runstore.keywords(run)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return Response(content=text, media_type="text/plain; charset=utf-8")

    @app.get("/api/runs/{run_id}/provenance")
    def run_provenance(run_id: str) -> dict[str, Any]:
        """Return a run's provenance and the build's variant list.

        Parameters
        ----------
        run_id : str
            The run's identifier.

        Returns
        -------
        dict
            ``provenance`` and ``variants``, each ``None`` when the run did not write it.
        """
        run = _find(run_id)
        try:
            return runstore.provenance(run)
        except runstore.RunError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.post("/api/runs")
    def start_run(payload: dict[str, Any]) -> JSONResponse:
        """Start a run by invoking the CLI in a subprocess.

        The service never imports the extension: it writes nothing itself and returns as soon as the
        child is launched.

        Parameters
        ----------
        payload : dict
            ``population`` (a path), ``species``, ``tree_age``, optional ``keywords`` (an
            **ordered** list: an entry carrying ``|`` is a block ``NAME|LINE|LINE``, anything else a
            keyword ``NAME=FIELD,...``), and optional ``id``.

        Returns
        -------
        fastapi.responses.JSONResponse
            202 with the new run's identifier.

        Raises
        ------
        fastapi.HTTPException
            400 when a required field is missing or the identifier is already taken.
        """
        population = payload.get("population")
        species = payload.get("species")
        tree_age = payload.get("tree_age")
        if not isinstance(population, str) or not isinstance(species, str) or tree_age is None:
            raise HTTPException(
                status_code=400,
                detail="a run needs 'population' (a path), 'species' and 'tree_age'",
            )
        identifier = str(payload.get("id") or time.strftime("%Y-%m-%dT%H-%M-%S"))
        if not app.state.roots:
            raise HTTPException(
                status_code=400, detail="the service was started with no --runs root"
            )
        directory = app.state.roots[0] / identifier
        if directory.exists():
            raise HTTPException(status_code=400, detail=f"the run {identifier!r} already exists")

        command = [
            sys.executable,
            "-m",
            "fresh_fvsbc",
            population,
            "--directory",
            str(directory),
            "--species",
            species,
            "--tree-age",
            str(tree_age),
        ]
        # One ordered list, because order is part of the contract: a DATABASE block must precede
        # the stand setup, while FMIN, MISTOE, RDIN and ESTAB follow it. An entry carrying "|" is a
        # block (``NAME|LINE|LINE``); anything else is a keyword (``NAME=FIELD,...``). A block is
        # also how a caller asks for output tables: without a DATABASE block a run writes
        # FVS_Cases and FVS_Error and nothing else.
        for entry in payload.get("keywords", []):
            text = str(entry)
            command.extend(["--block" if "|" in text else "--keyword", text])
        bundle_id = payload.get("bundle")
        if bundle_id:
            bundle_records = [record for record in _bundles() if record["bundle_id"] == bundle_id]
            if not bundle_records:
                raise HTTPException(status_code=400, detail=f"no calibration bundle {bundle_id!r}")
            command.extend(["--calibration", bundle_records[0]["path"]])
        if payload.get("tsa"):
            command.extend(["--tsa", str(payload["tsa"])])
        if payload.get("min_dbh") is not None:
            command.extend(["--min-dbh", str(payload["min_dbh"])])
        cycles = payload.get("cycles", 1)
        if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles < 1:
            raise HTTPException(status_code=400, detail="cycles must be a positive integer")
        cycle_years = payload.get("cycle_years")
        if cycle_years is not None and (
            isinstance(cycle_years, bool)
            or not isinstance(cycle_years, (int, float))
            or not math.isfinite(float(cycle_years))
            or float(cycle_years) <= 0
        ):
            raise HTTPException(status_code=400, detail="cycle_years must be a positive number")
        if cycles != 1:
            command.extend(["--cycles", str(cycles)])
        if cycle_years is not None:
            command.extend(["--cycle-years", str(cycle_years)])
        directory.mkdir(parents=True)
        log = (directory / "service.log").open("w", encoding="utf-8")
        app.state.processes[identifier] = subprocess.Popen(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=str(directory),
        )
        return JSONResponse(status_code=202, content={"id": identifier, "state": "running"})

    @app.get("/api/runs/{run_id}/log")
    def run_log(run_id: str) -> Response:
        """Return the log the service captured for a run it started.

        A run that failed wrote its traceback here and nowhere else, so this is how a caller
        sees why.

        Parameters
        ----------
        run_id : str
            The run's identifier.

        Returns
        -------
        fastapi.responses.Response
            The log as ``text/plain``, empty when the run was not started by this service.
        """
        run = _find(run_id)
        path = run.path / "service.log"
        text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        return Response(content=text, media_type="text/plain; charset=utf-8")

    @app.get("/api/runs/{run_id}/events")
    def run_events(run_id: str, request: Request) -> Response:
        """Stream a run's state until it finishes.

        A finished run answers **204**, not a short stream the browser reconnects to. The stream
        reports
        what the run's directory holds — it never invents progress the child did not write.

        Parameters
        ----------
        run_id : str
            The run's identifier.
        request : fastapi.Request
            The request, used to notice a client that has gone away.

        Returns
        -------
        fastapi.responses.Response
            204 when the run is already complete, otherwise an SSE stream.
        """
        run = _find(run_id)
        if run.state == "complete":
            return Response(status_code=204)

        def stream() -> Iterator[bytes]:
            """Yield state events until the run completes or the stream times out.

            Yields
            ------
            bytes
                One SSE frame per poll.
            """
            deadline = time.monotonic() + STREAM_SECONDS
            while time.monotonic() < deadline:
                if runstore.discover(app.state.roots) and run.path.is_dir():
                    state = "complete" if (run.path / "summary.csv").is_file() else "running"
                else:
                    state = "gone"
                frame = {"run": run.id, "state": state}
                yield f"event: status\ndata: {json.dumps(frame)}\n\n".encode()
                if state in {"complete", "gone"}:
                    return
                time.sleep(POLL_SECONDS)

        return StreamingResponse(stream(), media_type="text/event-stream")

    app.mount("/", StaticFiles(directory=str(STATIC_DIRECTORY), html=True), name="static")
    return app


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser for the service command.

    Returns
    -------
    argparse.ArgumentParser
        The parser for ``fresh-fvsbc web``.
    """
    parser = argparse.ArgumentParser(
        prog="fresh-fvsbc web",
        description="Serve a browser surface over the runs under one or more roots.",
    )
    parser.add_argument(
        "--runs",
        type=Path,
        action="append",
        required=True,
        metavar="DIR",
        help="a directory holding run directories; repeatable",
    )
    parser.add_argument(
        "--bundles",
        type=Path,
        action="append",
        default=[],
        metavar="DIR",
        help="a directory holding calibration bundle JSON files; repeatable",
    )
    parser.add_argument("--host", default="127.0.0.1", metavar="ADDR", help="the bind address")
    parser.add_argument("--port", type=int, default=8765, metavar="PORT", help="the bind port")
    parser.add_argument(
        "--root-path",
        default="",
        dest="root_path",
        metavar="PREFIX",
        help="the prefix the app is served under, for a notebook proxy",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        dest="allow_remote",
        help="permit a non-loopback bind; there is no authentication",
    )
    parser.add_argument(
        "--allow-agent",
        action="store_true",
        dest="allow_agent",
        help="permit the optional OpenCode assistant; it can read the workspace and run commands",
    )
    parser.add_argument(
        "--agent-model",
        default=DEFAULT_AGENT_MODEL,
        metavar="PROVIDER/MODEL",
        help=f"the assistant model (default: {DEFAULT_AGENT_MODEL})",
    )
    parser.add_argument(
        "--agent-workspace",
        type=Path,
        default=None,
        metavar="DIR",
        help="the directory the assistant may read (default: the service working directory)",
    )
    parser.add_argument(
        "--agent-timeout",
        type=float,
        default=DEFAULT_AGENT_TIMEOUT,
        metavar="SECONDS",
        help=f"assistant turn timeout (default: {DEFAULT_AGENT_TIMEOUT:g})",
    )
    return parser


def _is_loopback(host: str) -> bool:
    """Say whether a bind address is loopback.

    Parameters
    ----------
    host : str
        The address the service would bind.

    Returns
    -------
    bool
        ``True`` for the loopback names and addresses.
    """
    return host in {"127.0.0.1", "::1", "localhost"}


def main(argv: Sequence[str] | None = None) -> int:
    """Run the service.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments to parse. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when the server stops normally, ``2`` for a bind the service refuses.

    Raises
    ------
    SystemExit
        When the web extra is not installed, because uvicorn cannot be imported.
    """
    args = _parser().parse_args(argv)
    if not _is_loopback(args.host) and not args.allow_remote:
        print(
            "fresh-fvsbc web: refusing to bind a non-loopback address; "
            "there is no authentication. Pass --allow-remote to accept that.",
            file=sys.stderr,
        )
        return 2
    try:
        import uvicorn
    except ImportError:  # pragma: no cover - depends on the extra being installed
        print(
            "fresh-fvsbc web: the web extra is not installed; run `pip install 'fresh-fvsbc[web]'`",
            file=sys.stderr,
        )
        return 2
    application = create_app(
        args.runs,
        allow_remote=args.allow_remote,
        root_path=args.root_path,
        bundles=args.bundles,
        allow_agent=args.allow_agent,
        agent_model=args.agent_model,
        agent_workspace=args.agent_workspace,
        agent_timeout=args.agent_timeout,
    )
    uvicorn.run(application, host=args.host, port=args.port, log_level="info")
    return 0
