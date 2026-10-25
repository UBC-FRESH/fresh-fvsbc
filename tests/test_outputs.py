"""Tests for the FVS-BC output reader.

The databases are built at runtime, so the suite needs no run and no fixture file. What the tests
assert is the reader's contract: the columns are the database's own, the tables it refuses, and the
split between the two kinds of row that ``FVS_Error`` holds.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from fresh_fvsbc.outputs import (
    CASES_COLUMNS,
    DATABASE_TABLES,
    EXPOSED_TABLES,
    IDENTITY_COLUMN,
    MissingOutputError,
    RunFailedError,
    UnknownTableError,
    check_run,
    errors_in,
    read_cases,
    read_errors,
    read_table,
    severity_of,
    warnings_in,
)

WARNING = (
    "FVS03 WARNING:  FOREST CODE INDICATES THE GEOGRAPHIC LOCATION IS OUTSIDE THE RANGE OF THE "
    "MODEL.  DEFAULT CODE IS USED."
)
ERROR = "FVS16 ERROR:  KEYWORD ENTERED IS USED IN WRONG CONTEXT AND WAS IGNORED.  RECORDS READ= 19"


def a_database(path: Path, *, cases: int = 1, messages: tuple[str, ...] = ()) -> Path:
    """Build a database shaped like a run's output, and return its path."""
    connection = sqlite3.connect(path)
    try:
        connection.execute("create table FVS_Cases (CaseID text, StandID text, Variant text)")
        for index in range(cases):
            connection.execute(
                "insert into FVS_Cases values (?, ?, ?)", (f"case-{index}", "SYNTHETIC", "BC")
            )
        connection.execute("create table FVS_Error (CaseID text, StandID text, Message text)")
        for message in messages:
            connection.execute(
                "insert into FVS_Error values (?, ?, ?)", ("case-0", "SYNTHETIC", message)
            )
        connection.execute("create table FVS_Compute (CaseID text, Year integer, BigVol real)")
        connection.execute("create table FVS_Summary_Metric (CaseID text, Year integer, Tpa real)")
        connection.execute(
            "create table FVS_Down_Wood_Vol_Metric (CaseID text, Year integer, DWD_Volume real)"
        )
        connection.execute("create table FVS_InvReference (CaseID text, SpeciesFVS text)")
        connection.execute("create table FVS_Fuels_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_PotFire_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_PotFire_Cond_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_Carbon_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_Hrv_Carbon (CaseID text, Year integer)")
        connection.execute("create table FVS_Consumption_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_CutList_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_Down_Wood_Cov_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_Stats_Species_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_TreeList_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_SnagDet_Metric (CaseID text, Year integer)")
        connection.execute("create table FVS_SnagSum_Metric (CaseID text, Year integer)")
        connection.commit()
    finally:
        connection.close()
    return path


def test_the_table_list_is_the_metric_builds_forty_four() -> None:
    """The metric build creates the tables the contract names, and no others.

    **The list was the base schema's**, 33 names, most of which a run here never writes. It is
    derived from the schema's four layers now; ``notes/reference/table-names.md`` has the evidence.
    """
    assert len(DATABASE_TABLES) == 44
    assert len(set(DATABASE_TABLES)) == 44
    assert all(name.startswith("FVS_") for name in DATABASE_TABLES)
    assert "FVS_Cases" in DATABASE_TABLES
    assert "FVS_Error" in DATABASE_TABLES


def test_the_cases_columns_are_the_contracts_twelve() -> None:
    """``FVS_Cases`` is read from ``dbscase.f``, and the contract lists its columns in order."""
    assert CASES_COLUMNS == (
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


def test_only_the_tested_tables_are_exposed() -> None:
    """Contract rule 3: a table the reader has not tested is not in the API."""
    assert EXPOSED_TABLES == (
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
        "FVS_Summary_Metric",
        "FVS_TreeList_Metric",
    )
    assert set(EXPOSED_TABLES) <= set(DATABASE_TABLES)


def test_the_columns_are_the_databases_own_names(tmp_path: Path) -> None:
    """Contract rule 2: a column is never renamed, because that breaks the trace to the schema."""
    path = a_database(tmp_path / "out.db")
    table = read_cases(path)
    assert isinstance(table, pd.DataFrame)
    assert len(table) == 1
    assert list(table.columns) == ["CaseID", "StandID", "Variant"]
    assert table["CaseID"].iloc[0] == "case-0"
    assert table["Variant"].iloc[0] == "BC"


def test_every_exposed_table_carries_the_identity_column(tmp_path: Path) -> None:
    """Contract rule 4: a parsed table can be joined back to ``FVS_Cases``."""
    path = a_database(tmp_path / "out.db", messages=(WARNING,))
    for name in EXPOSED_TABLES:
        assert IDENTITY_COLUMN in list(read_table(path, name).columns)


def test_an_unexposed_table_is_refused_even_though_the_database_holds_it(tmp_path: Path) -> None:
    """Rule 3 is about what the reader exposes, not about what is present."""
    path = a_database(tmp_path / "out.db")
    with pytest.raises(UnknownTableError, match="is not exposed"):
        read_table(path, "FVS_BurnReport_Metric")


def test_a_table_the_database_lacks_is_refused(tmp_path: Path) -> None:
    """A database from a run that never wrote the table is not the same as one that did."""
    connection = sqlite3.connect(tmp_path / "empty.db")
    connection.execute("create table Other (x integer)")
    connection.commit()
    connection.close()
    with pytest.raises(UnknownTableError, match="is not in the database"):
        read_table(tmp_path / "empty.db", "FVS_Cases")


def test_no_database_is_reported_rather_than_treated_as_empty(tmp_path: Path) -> None:
    """Contract rule 1: a run that cannot produce a database is a reported failure."""
    with pytest.raises(MissingOutputError, match="wrote no database"):
        read_cases(tmp_path / "absent.db")


def test_a_message_with_no_severity_is_unknown() -> None:
    """A message FVS wrote without a severity is neither an error nor a warning."""
    assert severity_of("something happened") == "UNKNOWN"
    assert severity_of("") == "UNKNOWN"


def test_the_severity_is_the_second_token() -> None:
    """FVS writes its code and then the severity."""
    assert severity_of(ERROR) == "ERROR"
    assert severity_of(WARNING) == "WARNING"


def test_the_first_severity_in_a_message_is_the_one_that_counts() -> None:
    """A severity word later in the text must not become the answer.

    This is the case that tells first-match from last-match, and it is why the check is written
    with a second severity word in it rather than with a plain message.
    """
    assert severity_of("FVS01 WARNING:  IGNORE THE ERROR: BELOW") == "WARNING"


def test_the_two_kinds_of_row_are_separated(tmp_path: Path) -> None:
    """``FVS_Error`` holds warnings as well as errors, so a reader has to separate them."""
    path = a_database(tmp_path / "out.db", messages=(WARNING, ERROR, WARNING))
    table = read_errors(path)
    assert len(table) == 3
    assert list(errors_in(table)["Message"].str[:6]) == ["FVS16 "]
    assert list(warnings_in(table)["Message"].str[:6]) == ["FVS03 ", "FVS03 "]


def test_an_empty_error_table_is_filtered_without_error(tmp_path: Path) -> None:
    """A run with no messages must not fail the filters."""
    path = a_database(tmp_path / "out.db")
    table = read_errors(path)
    assert table.empty
    assert errors_in(table).empty
    assert warnings_in(table).empty


def test_a_run_with_only_warnings_is_not_failed(tmp_path: Path) -> None:
    """A site outside the model's range is a warning, and the contract's rule must not fail it."""
    path = a_database(tmp_path / "out.db", messages=(WARNING,))
    warnings = check_run(path)
    assert isinstance(warnings, pd.DataFrame)
    assert warnings["Message"].tolist() == [WARNING]


def test_a_run_with_an_error_is_failed_and_says_what_failed(tmp_path: Path) -> None:
    """A failure that does not name what failed is not a report."""
    path = a_database(tmp_path / "out.db", messages=(WARNING, ERROR))
    with pytest.raises(RunFailedError, match="the run reported 1 error") as raised:
        check_run(path)
    assert "USED IN WRONG CONTEXT" in str(raised.value)
    assert "OUTSIDE THE RANGE" not in str(raised.value)


def test_a_run_with_no_messages_is_clean(tmp_path: Path) -> None:
    """An empty ``FVS_Error`` is the normal case, and it has no warnings either."""
    path = a_database(tmp_path / "out.db")
    assert check_run(path).empty


def test_a_run_with_no_database_cannot_be_checked(tmp_path: Path) -> None:
    """Checking a run that produced no database is the rule 1 failure, not a clean result."""
    with pytest.raises(MissingOutputError):
        check_run(tmp_path / "absent.db")
