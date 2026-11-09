"""Discovery and reading of the artefacts a run leaves behind.

This module is the service's whole contract with a result. It reads files; it computes no value the
CLI
cannot reproduce, and it never writes into a run directory. The one thing it adds is the **oracle
flag**
per table: four exposed tables are checked against FVS's own database dump and the rest are not, and
a
surface that shows a number has to be able to say which kind it is showing.

Nothing here imports FastAPI, so the readers are testable without the web extra installed.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import pandas as pd

from fresh_fvsbc.outputs import EXPOSED_TABLES, REFERENCE_VERIFIED, read_table
from fresh_fvsbc.run import (
    DATABASE_NAME,
    KEYWORD_FILE_NAME,
    PROVENANCE_FILE_NAME,
    SUMMARY_FILE_NAME,
    VARIANTS_FILE_NAME,
)

__all__ = [
    "Run",
    "RunError",
    "discover",
    "keywords",
    "provenance",
    "summary",
    "table",
    "table_csv",
    "tables",
]

# #: A run is ``complete`` once the child has written its summary, and ``running`` until then. There
# is no
#: third state: a failed run still writes its summary, and its ``FVS_Error`` rows carry the failure.
RunState = Literal["complete", "running"]

# #: How many rows one table request returns unless the caller asks for another number. A table can
# hold
#: thousands of rows, and the browser renders a page of them rather than all of them.
DEFAULT_LIMIT: int = 200

#: The largest page a caller may ask for.
MAX_LIMIT: int = 5000


#: The log the service writes when it starts a run. A directory holding one is a run the service
#: made, even when the child died before it wrote its keyword file — which is exactly the case that
#: has to be visible, because it is the one that failed.
SERVICE_LOG_FILE_NAME: str = "service.log"


class RunError(Exception):
    """A run directory, or an artefact inside it, could not be read."""


@dataclass(frozen=True)
class Run:
    """One run directory under a configured root.

    Attributes
    ----------
    id : str
        The directory's name, which is how the API addresses the run.
    path : Path
        The absolute path of the run directory.
    state : {"complete", "running"}
        ``complete`` once ``summary.csv`` exists, ``running`` until then.
    """

    id: str
    path: Path
    state: RunState

    @property
    def database(self) -> Path:
        """The output database this run wrote.

        Returns
        -------
        Path
            The path of ``FVSOut.db``, whether or not it exists yet.
        """
        return self.path / DATABASE_NAME

    @property
    def keyword_file(self) -> Path:
        """The keyword set this run was given.

        Returns
        -------
        Path
            The path of ``run.key``, whether or not it exists.
        """
        return self.path / KEYWORD_FILE_NAME


def _looks_like_a_run(path: Path) -> bool:
    """Say whether a directory holds a run.

    Parameters
    ----------
    path : Path
        The directory to test.

    Returns
    -------
    bool
        ``True`` when the directory carries a keyword file or an output database. A directory with
        neither is not a run, and a root may hold others.
    """
    return path.is_dir() and any(
        (path / name).is_file()
        for name in (KEYWORD_FILE_NAME, DATABASE_NAME, SERVICE_LOG_FILE_NAME)
    )


def discover(roots: Sequence[Path]) -> tuple[Run, ...]:
    """List the run directories under a set of roots.

    A root may itself be a run directory, in which case it is the only result for that root.

    Parameters
    ----------
    roots : sequence of Path
        The directories to search, one level deep.

    Returns
    -------
    tuple of Run
        The runs found, ordered by identifier, which sorts a timestamped directory name oldest
        first.
    """
    found: dict[Path, Run] = {}
    for root in roots:
        if _looks_like_a_run(root):
            found[root.resolve()] = Run(root.name, root.resolve(), _state(root))
            continue
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if _looks_like_a_run(child):
                found[child.resolve()] = Run(child.name, child.resolve(), _state(child))
    return tuple(found[key] for key in sorted(found, key=lambda p: p.name))


def _state(path: Path) -> RunState:
    """Return a run directory's state from the artefacts it holds.

    Parameters
    ----------
    path : Path
        The run directory.

    Returns
    -------
    {"complete", "running"}
        ``complete`` when the child has written ``summary.csv``.
    """
    return "complete" if (path / SUMMARY_FILE_NAME).is_file() else "running"


def _require_run(run: Run) -> None:
    """Raise when a run directory has gone away between discovery and a request.

    Parameters
    ----------
    run : Run
        The run to check.

    Raises
    ------
    RunError
        If the directory is no longer there.
    """
    if not run.path.is_dir():
        raise RunError(f"the run directory {run.path} is no longer there")


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Turn a dataframe into JSON-ready records.

    ``to_json`` is the conversion rather than ``to_dict`` because a numpy scalar is not JSON, and a
    ``NaN`` has to become ``null`` rather than the string ``"NaN"``.

    Parameters
    ----------
    frame : pandas.DataFrame
        The frame to convert.

    Returns
    -------
    list of dict
        One dictionary per row.
    """
    if frame.empty:
        return []
    payload: list[dict[str, Any]] = json.loads(frame.to_json(orient="records"))
    return payload


def summary(run: Run) -> list[dict[str, Any]]:
    """Read a run's parsed summary.

    Parameters
    ----------
    run : Run
        The run to read.

    Returns
    -------
    list of dict
        One record per stand-period, as the child wrote ``summary.csv``.

    Raises
    ------
    RunError
        If the summary has not been written yet.
    """
    _require_run(run)
    path = run.path / SUMMARY_FILE_NAME
    if not path.is_file():
        raise RunError(f"the run {run.id} has no {SUMMARY_FILE_NAME} yet")
    return _records(pd.read_csv(path))


def _table_names(database: Path) -> set[str]:
    """List the tables a database holds.

    Parameters
    ----------
    database : Path
        The output database.

    Returns
    -------
    set of str
        The table names, or an empty set when the database is absent.
    """
    if not database.is_file():
        return set()
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return {
            str(row[0])
            for row in connection.execute("select name from sqlite_master where type='table'")
        }
    finally:
        connection.close()


def tables(run: Run) -> list[dict[str, Any]]:
    """List the exposed tables this run wrote, with their row counts and oracle flag.

    Parameters
    ----------
    run : Run
        The run to inspect.

    Returns
    -------
    list of dict
        One record per table, with ``name``, ``rows``, ``columns``, ``oracle`` and ``exposed``. The
        ``exposed`` key is always true here — the reader refuses an unexposed table — and it is
        present so
        a client can render the contract without special-casing.
    """
    _require_run(run)
    present = _table_names(run.database)
    records: list[dict[str, Any]] = []
    for name in EXPOSED_TABLES:
        if name not in present:
            continue
        frame = read_table(run.database, name)
        records.append(
            {
                "name": name,
                "rows": len(frame),
                "columns": [str(column) for column in frame.columns],
                "oracle": name in REFERENCE_VERIFIED,
                "exposed": True,
            }
        )
    return records


def _table_frame(run: Run, name: str) -> pd.DataFrame:
    """Read one exposed table and enforce the reader's table contract."""
    _require_run(run)
    if name not in EXPOSED_TABLES:
        raise RunError(
            f"{name!r} is not an exposed table; this reader exposes {len(EXPOSED_TABLES)}"
        )
    if not run.database.is_file():
        raise RunError(f"the run {run.id} has no {DATABASE_NAME}")
    if name not in _table_names(run.database):
        raise RunError(f"the run {run.id} wrote no table {name!r}")
    return read_table(run.database, name)


def _filter_frame(
    frame: pd.DataFrame, query: str | None, column: str | None = None
) -> pd.DataFrame:
    """Return rows containing a literal, case-insensitive query.

    When ``column`` is given the match is restricted to that column; otherwise every column is
    searched. The caller has already checked that the column exists.
    """
    if query is None or not query.strip():
        return frame
    needle = query.strip()
    if column:
        mask = (
            frame[column].astype("string").str.contains(needle, case=False, regex=False, na=False)
        )
        return frame[mask]
    mask = frame.apply(
        lambda item: item.astype("string").str.contains(needle, case=False, regex=False, na=False)
    ).any(axis=1)
    return cast(pd.DataFrame, frame[mask])


def table(
    run: Run,
    name: str,
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    query: str | None = None,
    column: str | None = None,
) -> dict[str, Any]:
    """Read one exposed table from a run's database, as a filtered page.

    Parameters
    ----------
    run : Run
        The run to read.
    name : str
        The table, which must be one this package exposes.
    limit : int, optional
        The page size, clamped to ``MAX_LIMIT``.
    offset : int, optional
        The first row of the page, clamped at zero.
    query : str or None, optional
        A literal, case-insensitive filter applied before paging.
    column : str or None, optional
        Restrict the filter to this column; ``None`` searches every column.
    columns : sequence of str or None, optional
        The columns to write, in this order; ``None`` writes every column.

    Returns
    -------
    dict
        ``name``, ``columns``, ``rows``, ``total``, ``limit``, ``offset``, ``query``, ``column``
        and ``oracle``.

    Raises
    ------
    RunError
        If the run has no database, or the table is not in it.
    """
    raw = _table_frame(run, name)
    if column and column not in [str(item) for item in raw.columns]:
        raise RunError(f"the run {run.id} table {name!r} has no column {column!r}")
    frame = _filter_frame(raw, query, column)
    page_limit = max(1, min(int(limit), MAX_LIMIT))
    page_offset = max(0, int(offset))
    return {
        "name": name,
        "columns": [str(column) for column in frame.columns],
        "rows": _records(frame.iloc[page_offset : page_offset + page_limit]),
        "total": len(frame),
        "limit": page_limit,
        "offset": page_offset,
        "query": (query or "").strip(),
        "column": (column or "").strip(),
        "oracle": name in REFERENCE_VERIFIED,
    }


def table_csv(
    run: Run,
    name: str,
    *,
    query: str | None = None,
    column: str | None = None,
    columns: Sequence[str] | None = None,
) -> str:
    """Return one exposed table as CSV, with the same literal filter as :func:`table`.

    Parameters
    ----------
    run : Run
        The run to read.
    name : str
        The exposed table.
    query : str or None, optional
        A literal, case-insensitive filter applied before export.
    column : str or None, optional
        Restrict the filter to this column; ``None`` searches every column.

    Returns
    -------
    str
        The CSV text, including its header.

    Raises
    ------
    RunError
        If the run has no database, or the table is not in it.
    """
    raw = _table_frame(run, name)
    available = [str(item) for item in raw.columns]
    if column and column not in available:
        raise RunError(f"the run {run.id} table {name!r} has no column {column!r}")
    frame = _filter_frame(raw, query, column)
    if columns is not None:
        unknown = [item for item in columns if item not in available]
        if unknown:
            raise RunError(f"the run {run.id} table {name!r} has no column {unknown[0]!r}")
        frame = frame[list(columns)]
    return frame.to_csv(index=False)


def keywords(run: Run) -> str:
    """Read the keyword set a run was given, as text.

    Parameters
    ----------
    run : Run
        The run to read.

    Returns
    -------
    str
        The contents of ``run.key``.

    Raises
    ------
    RunError
        If the keyword file is missing.
    """
    _require_run(run)
    if not run.keyword_file.is_file():
        raise RunError(f"the run {run.id} has no {KEYWORD_FILE_NAME}")
    return run.keyword_file.read_text(encoding="utf-8", errors="replace")


def provenance(run: Run) -> dict[str, Any]:
    """Read a run's provenance and the build's variant list.

    Parameters
    ----------
    run : Run
        The run to read.

    Returns
    -------
    dict
        ``provenance`` and ``variants`` as the child wrote them, each ``None`` when the file is
        absent.
        A missing file is reported rather than invented, because provenance that is assumed is not
        provenance.
    """
    _require_run(run)
    payload: dict[str, Any] = {}
    for key, name in (("provenance", PROVENANCE_FILE_NAME), ("variants", VARIANTS_FILE_NAME)):
        path = run.path / name
        payload[key] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    return payload
