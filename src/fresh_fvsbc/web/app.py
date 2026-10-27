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
import subprocess
import sys
import time
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from fresh_fvsbc.outputs import EXPOSED_TABLES, ORACLE_TABLES
from fresh_fvsbc.web import runs as runstore
from fresh_fvsbc.web.skins import load_skins

__all__ = ["create_app", "main"]

#: The directory the front end is served from.
STATIC_DIRECTORY: Path = Path(__file__).resolve().parent / "static"

#: How often the event stream re-reads a run's directory while it is running, in seconds.
POLL_SECONDS: float = 1.0

#: How long a live event stream stays open before it closes and the browser reconnects, in seconds.
STREAM_SECONDS: float = 600.0


def create_app(
    roots: Sequence[Path],
    *,
    allow_remote: bool = False,
    root_path: str = "",
) -> FastAPI:
    """Build the application over a set of run roots.

    Parameters
    ----------
    roots : sequence of Path
        The directories searched for run directories, one level deep.
    allow_remote : bool, optional
        Whether the caller has accepted a non-loopback bind. The flag is carried into the app so the
        decision is recorded where it is used.
    root_path : str, optional
        The prefix the app is served under, for a notebook proxy.

    Returns
    -------
    fastapi.FastAPI
        The application.
    """
    app = FastAPI(
        title="fresh-fvsbc",
        description="A reader over the artefacts an FVS-BC run leaves behind.",
        root_path=root_path,
    )
    resolved = tuple(Path(root).resolve() for root in roots)
    skins = load_skins()
    app.state.roots = resolved
    app.state.allow_remote = allow_remote
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
            ``exposed`` and ``oracle``, so a client can say how much of the surface is verified
            without
            having to know the number.
        """
        return {
            "exposed": len(EXPOSED_TABLES),
            "oracle": len(ORACLE_TABLES),
            "tables": list(ORACLE_TABLES),
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
                }
            )
        return records

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

        Returns
        -------
        dict
            The columns, the page of rows, the total, and whether the table has an oracle.
        """
        run = _find(run_id)
        try:
            return runstore.table(run, name, limit=limit, offset=offset)
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
    application = create_app(args.runs, allow_remote=args.allow_remote, root_path=args.root_path)
    uvicorn.run(application, host=args.host, port=args.port, log_level="info")
    return 0
