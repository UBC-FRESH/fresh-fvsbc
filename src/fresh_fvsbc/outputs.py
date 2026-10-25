"""The FVS-BC output reader.

``docs/reference/outputs.rst`` is the contract. This module reads the run's SQLite database back,
exposes the tables it has tested, and separates the two kinds of row that ``FVS_Error`` holds.

What the run actually gives, and why this reader is shaped this way
-------------------------------------------------------------------

The contract says the database is the primary output and names 44 ``FVS_`` tables. **Which of
them a run writes is the keyword set's business**: a ``DATABASE`` block names the tables, and a
table it does not name is absent. An earlier revision of this docstring said a run produced
``FVS_Cases`` and ``FVS_Error`` and no more, because PyFVS occupied the block; both claims were
wrong, and the run that reads thirteen tables disproved them.

Some tables need more than a ``DATABASE`` option. ``FMIN`` is a block of options — ``FUELOUT``,
``POTFIRE``, ``CARBREPT`` and ``SIMFIRE`` live inside it, not in the keyword table — and it is how
a caller reaches the fuels, potfire, carbon and consumption tables. ``SIMFIRE`` schedules a fire
event, which is what makes a consumption row exist at all. ``notes/reference/table-reachability.md``
records which of the rest can be written at all, and why the others cannot.

The summary is also returned in memory by ``FVS.summary``, and the run writes a fixed-width ``.sum``
report beside the database.

``FVS_Error`` is not an error channel only
------------------------------------------

It holds FVS warnings as well as errors. A run whose site data is outside the model's range writes
``FVS03 WARNING: FOREST CODE INDICATES THE GEOGRAPHIC LOCATION IS OUTSIDE THE RANGE OF THE MODEL``,
which is not a failure. So the contract's rule that a non-empty ``FVS_Error`` means a failed run is
not the rule a reader can apply; the rule is that the rows *of severity* ``ERROR`` make a run
failed, and this module separates the two by reading the severity FVS writes into each message.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Literal, TypeAlias

import pandas as pd

__all__ = [
    "CASES_COLUMNS",
    "DATABASE_TABLES",
    "EXPOSED_TABLES",
    "IDENTITY_COLUMN",
    "MissingOutputError",
    "OutputError",
    "RunFailedError",
    "Severity",
    "UnknownTableError",
    "check_run",
    "errors_in",
    "read_cases",
    "read_errors",
    "read_table",
    "severity_of",
    "warnings_in",
]

#: The severity FVS writes into a message, or ``UNKNOWN`` for a message that names none.
Severity: TypeAlias = Literal["ERROR", "WARNING", "UNKNOWN"]

#: Every ``FVS_``-prefixed table the database component can create, per the contract.
DATABASE_TABLES: tuple[str, ...] = (
    "FVS_ATRTList_Metric",
    "FVS_BurnReport_Metric",
    "FVS_CalibStats",
    "FVS_CanProfile",
    "FVS_Carbon_Metric",
    "FVS_Cases",
    "FVS_Climate_Metric",
    "FVS_Compute",
    "FVS_Consumption_Metric",
    "FVS_CutList_Metric",
    "FVS_DM_Spp_Sum_Metric",
    "FVS_DM_Stnd_Sum_Metric",
    "FVS_DM_Sz_Sum_Metric",
    "FVS_DM_TreeList_Metric",
    "FVS_Down_Wood_Cov_Metric",
    "FVS_Down_Wood_Vol_Metric",
    "FVS_EconHarvestValue_Metric",
    "FVS_EconSummary_Metric",
    "FVS_Error",
    "FVS_FIAVBC_ATRTList",
    "FVS_FIAVBC_CutList",
    "FVS_FIAVBC_Summary",
    "FVS_FIAVBC_TreeList",
    "FVS_Fuels_Metric",
    "FVS_Hrv_Carbon",
    "FVS_InvReference",
    "FVS_Mortality_Metric",
    "FVS_PotFire_Cond_Metric",
    "FVS_PotFire_Metric",
    "FVS_RD_Beetle_Metric",
    "FVS_RD_Det_Metric",
    "FVS_RD_Sum_Metric",
    "FVS_Regen_HabType",
    "FVS_Regen_Ingrow_Metric",
    "FVS_Regen_SitePrep",
    "FVS_Regen_Sprouts_Metric",
    "FVS_Regen_Tally_Metric",
    "FVS_SnagDet_Metric",
    "FVS_SnagSum_Metric",
    "FVS_Stats_Species_Metric",
    "FVS_Stats_Stand",
    "FVS_StrClass_Metric",
    "FVS_Summary_Metric",
    "FVS_TreeList_Metric",
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
EXPOSED_TABLES: tuple[str, ...] = (
    "FVS_ATRTList_Metric",
    "FVS_CanProfile",
    "FVS_Carbon_Metric",
    "FVS_Cases",
    "FVS_Compute",
    "FVS_Consumption_Metric",
    "FVS_CutList_Metric",
    "FVS_Down_Wood_Cov_Metric",
    "FVS_Down_Wood_Vol_Metric",
    "FVS_Error",
    "FVS_Fuels_Metric",
    "FVS_Hrv_Carbon",
    "FVS_InvReference",
    "FVS_PotFire_Cond_Metric",
    "FVS_PotFire_Metric",
    "FVS_SnagDet_Metric",
    "FVS_SnagSum_Metric",
    "FVS_Stats_Species_Metric",
    "FVS_StrClass_Metric",
    "FVS_Summary_Metric",
    "FVS_TreeList_Metric",
)

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


def read_table(db_path: str | Path, table: str) -> pd.DataFrame:
    """Read one table from a run's output database.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.
    table : str
        The table to read. It must be one this reader exposes.

    Returns
    -------
    pandas.DataFrame
        One row per record, with the database's own column names.

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
        frame = pd.DataFrame.from_records([dict(row) for row in cursor])
        if frame.empty:
            # A table with no rows still has a schema, and a frame without columns loses it.
            frame = pd.DataFrame(columns=[column[0] for column in cursor.description])
        return frame
    finally:
        connection.close()


def read_cases(db_path: str | Path) -> pd.DataFrame:
    """Read ``FVS_Cases``, the table that identifies the run.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.

    Returns
    -------
    pandas.DataFrame
        One row per case.
    """
    return read_table(db_path, "FVS_Cases")


def read_errors(db_path: str | Path) -> pd.DataFrame:
    """Read ``FVS_Error``, which holds messages of more than one severity.

    Parameters
    ----------
    db_path : str or Path
        The database the run wrote.

    Returns
    -------
    pandas.DataFrame
        Every row, errors and warnings together. Use :func:`errors_in` and :func:`warnings_in` to
        separate them.
    """
    return read_table(db_path, "FVS_Error")


def _rows_of_severity(table: pd.DataFrame, severity: Severity) -> pd.DataFrame:
    """Return the rows of ``FVS_Error`` whose message carries ``severity``."""
    if table.empty:
        return table
    keep = table["Message"].map(lambda message: severity_of(str(message)) == severity)
    return table[keep]


def errors_in(table: pd.DataFrame) -> pd.DataFrame:
    """Return the rows of severity ``ERROR``.

    Parameters
    ----------
    table : pandas.DataFrame
        A table from ``FVS_Error``.

    Returns
    -------
    pandas.DataFrame
        The errors, in the order they were read.
    """
    return _rows_of_severity(table, "ERROR")


def warnings_in(table: pd.DataFrame) -> pd.DataFrame:
    """Return the rows of severity ``WARNING``.

    Parameters
    ----------
    table : pandas.DataFrame
        A table from ``FVS_Error``.

    Returns
    -------
    pandas.DataFrame
        The warnings, in the order they were read.
    """
    return _rows_of_severity(table, "WARNING")


def check_run(db_path: str | Path) -> pd.DataFrame:
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
    pandas.DataFrame
        The warnings, which do not make a run failed.

    Raises
    ------
    RunFailedError
        If any message is of severity ``ERROR``. The message names each one, because a failure that
        does not say what failed is not a report.
    """
    table = read_errors(db_path)
    errors = errors_in(table)
    if not errors.empty:
        texts = "; ".join(str(message).strip() for message in errors["Message"])
        raise RunFailedError(f"the run reported {len(errors)} error(s): {texts}")
    return warnings_in(table)
