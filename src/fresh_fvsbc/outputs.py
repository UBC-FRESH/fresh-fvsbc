"""The FVS-BC output reader.

``docs/reference/outputs.rst`` is the contract. This module reads the run's SQLite database back,
exposes the tables it has tested, and separates the two kinds of row that ``FVS_Error`` holds.

What the run actually gives, and why this reader is shaped this way
-------------------------------------------------------------------

The contract says the database is the primary output and names 32 ``FVS_`` tables. A run driven
through PyFVS's step API — the route this project uses — produces a database holding
**``FVS_Cases`` and ``FVS_Error``**, and no more. The rest need a ``DATABASE`` output block to ask
for them, and PyFVS already occupies that block: a keyword file carrying its own is refused with
``FVS16 ERROR: KEYWORD ENTERED IS USED IN WRONG CONTEXT AND WAS IGNORED``. PyFVS's own API exposes
no output-database configuration either, so there is no supported way to ask through it.

The summary is still available, in two other places: ``FVS.summary`` returns it in memory, and the
run writes a fixed-width ``.sum`` report beside the database. Reading those is not this work.

``FVS_Error`` is not an error channel only
-----------------------------------------

It holds FVS warnings as well as errors. A run whose site data is outside the model's range writes
``FVS03 WARNING: FOREST CODE INDICATES THE GEOGRAPHIC LOCATION IS OUTSIDE THE RANGE OF THE MODEL``,
which is not a failure. So the contract's rule that a non-empty ``FVS_Error`` means a failed run is
not the rule a reader can apply; the rule is that the rows *of severity* ``ERROR`` make a run
failed, and this module separates the two by reading the severity FVS writes into each message.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, TypeAlias

__all__ = [
    "CASES_COLUMNS",
    "DATABASE_TABLES",
    "EXPOSED_TABLES",
    "IDENTITY_COLUMN",
    "MissingOutputError",
    "OutputError",
    "RunFailedError",
    "Severity",
    "TableRow",
    "UnknownTableError",
    "check_run",
    "errors_in",
    "read_cases",
    "read_errors",
    "read_table",
    "severity_of",
    "warnings_in",
]

#: One row of a table, keyed by the database's own column names. The contract forbids renaming, so a
#: key is exactly what FVS called the column.
TableRow: TypeAlias = dict[str, object]

#: The severity FVS writes into a message, or ``UNKNOWN`` for a message that names none.
Severity: TypeAlias = Literal["ERROR", "WARNING", "UNKNOWN"]

#: Every ``FVS_``-prefixed table the database component can create, per the contract.
DATABASE_TABLES: tuple[str, ...] = (
    "FVS_BurnReport",
    "FVS_CalibStats",
    "FVS_CanProfile",
    "FVS_Carbon",
    "FVS_Cases",
    "FVS_Climate",
    "FVS_Compute",
    "FVS_Consumption",
    "FVS_DM_Spp_Sum",
    "FVS_DM_Stnd_Sum",
    "FVS_DM_Sz_Sum",
    "FVS_Down_Wood_Cov",
    "FVS_Down_Wood_Vol",
    "FVS_EconHarvestValue",
    "FVS_EconSummary",
    "FVS_Error",
    "FVS_Fuels",
    "FVS_Hrv_Carbon",
    "FVS_Mortality",
    "FVS_RD_Beetle",
    "FVS_RD_Det",
    "FVS_RD_Sum",
    "FVS_Regen_HabType",
    "FVS_Regen_Ingrow",
    "FVS_Regen_SitePrep",
    "FVS_Regen_Sprouts",
    "FVS_Regen_Tally",
    "FVS_SnagDet",
    "FVS_SnagSum",
    "FVS_Stats_Species",
    "FVS_Stats_Stand",
    "FVS_StrClass",
)

#: The columns of ``FVS_Cases``, from ``dbsqlite/dbscase.f``.
CASES_COLUMNS: tuple[str, ...] = (
    "CaseID",
    "Stand_CN",
    "StandID",
    "MgmtID",
    "RunTitle",
    "KeywordFile",
    "SamplingWt",
    "Variant",
    "Version",
    "RV",
    "Groups",
    "RunDateTime",
)

#: The column that joins a table back to ``FVS_Cases``.
IDENTITY_COLUMN: str = "CaseID"

#: The tables this reader exposes. Contract rule 3: a table it has not tested is not in the API, and
#: these two are the ones a run through the FFI is known to write.
EXPOSED_TABLES: tuple[str, ...] = ("FVS_Cases", "FVS_Error")

#: The severities FVS spells into a message, usually in the second token.
_SEVERITIES: dict[str, Severity] = {"ERROR:": "ERROR", "WARNING:": "WARNING"}


class OutputError(Exception):
    """A problem with a run's output database."""


class MissingOutputError(OutputError):
    """A run produced no database, which contract rule 1 reports as a failure."""


class UnknownTableError(OutputError):
    """A table this reader does not expose, or one this database does not hold."""


class RunFailedError(OutputError):
    """A run whose output holds one or more messages of severity ``ERROR``."""


def severity_of(message: str) -> Severity:
    """Return the severity FVS wrote into a message.

    FVS writes the message code and then the severity, as in ``FVS16 ERROR:  ...``. The first
    severity in the message is the one that counts, so a severity word appearing later, inside the
    text, does not change the answer.

    Parameters
    ----------
    message : str
        One message from ``FVS_Error``.

    Returns
    -------
    Severity
        ``"ERROR"``, ``"WARNING"``, or ``"UNKNOWN"`` when the message names neither.
    """
    for token in message.split():
        if token in _SEVERITIES:
            return _SEVERITIES[token]
    return "UNKNOWN"


def read_table(db_path: str | Path, table: str) -> list[TableRow]:
    """Read one table from a run's output database.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.
    table : str
        The table to read. It must be one this reader exposes.

    Returns
    -------
    list of TableRow
        One row per record, keyed by the database's own column names.

    Raises
    ------
    UnknownTableError
        If the table is not exposed, or the database does not hold it.
    MissingOutputError
        If the database is not there. Contract rule 1: a run that produced no database is a reported
        failure, not a silent fall back.
    """
    if table not in EXPOSED_TABLES:
        exposed = ", ".join(EXPOSED_TABLES)
        raise UnknownTableError(f"{table!r} is not exposed; this reader exposes {exposed}")
    path = Path(db_path)
    if not path.exists():
        raise MissingOutputError(f"the run wrote no database at {path}")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        try:
            cursor = connection.execute(f'SELECT * FROM "{table}"')
        except sqlite3.OperationalError as exc:
            raise UnknownTableError(f"{table!r} is not in the database at {path}") from exc
        return [dict(row) for row in cursor]
    finally:
        connection.close()


def read_cases(db_path: str | Path) -> list[TableRow]:
    """Read ``FVS_Cases``, the table that identifies the run.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.

    Returns
    -------
    list of TableRow
        One row per case.
    """
    return read_table(db_path, "FVS_Cases")


def read_errors(db_path: str | Path) -> list[TableRow]:
    """Read ``FVS_Error``, which holds messages of more than one severity.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.

    Returns
    -------
    list of TableRow
        Every row, errors and warnings together. Use :func:`errors_in` and :func:`warnings_in` to
        separate them.
    """
    return read_table(db_path, "FVS_Error")


def _rows_of_severity(rows: Sequence[TableRow], severity: Severity) -> list[TableRow]:
    """Return the rows whose message carries ``severity``."""
    return [row for row in rows if severity_of(str(row.get("Message", ""))) == severity]


def errors_in(rows: Sequence[TableRow]) -> list[TableRow]:
    """Return the rows of severity ``ERROR``.

    Parameters
    ----------
    rows : Sequence[TableRow]
        Rows from ``FVS_Error``.

    Returns
    -------
    list of TableRow
        The errors, in the order they were read.
    """
    return _rows_of_severity(rows, "ERROR")


def warnings_in(rows: Sequence[TableRow]) -> list[TableRow]:
    """Return the rows of severity ``WARNING``.

    Parameters
    ----------
    rows : Sequence[TableRow]
        Rows from ``FVS_Error``.

    Returns
    -------
    list of TableRow
        The warnings, in the order they were read.
    """
    return _rows_of_severity(rows, "WARNING")


def check_run(db_path: str | Path) -> list[TableRow]:
    """Report a run as failed when its output holds an error, and return its warnings.

    The contract says a run whose ``FVS_Error`` is non-empty is failed. In practice that table also
    holds warnings, so this function fails a run on the rows of severity ``ERROR`` and hands the
    warnings back rather than discarding them.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.

    Returns
    -------
    list of TableRow
        The warnings, which do not make a run failed.

    Raises
    ------
    RunFailedError
        If any message is of severity ``ERROR``. The message names each one, because a failure that
        does not say what failed is not a report.
    """
    rows = read_errors(db_path)
    errors = errors_in(rows)
    if errors:
        texts = "; ".join(str(row.get("Message", "")).strip() for row in errors)
        raise RunFailedError(f"the run reported {len(errors)} error(s): {texts}")
    return warnings_in(rows)
