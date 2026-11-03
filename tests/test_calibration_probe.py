"""Tests for the calibration probe's pure selection and keyword helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from fresh_fvsbc.calibration_probe import (
    eligible_intervals,
    insert_parameters,
    parameter_keywords,
    summarise_probe,
)
from fresh_fvsbc.keywords import Keyword


def _intervals() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "interval_id": ["young", "mortality", "eligible", "small"],
            "ba0": [10.0, 20.0, 30.0, 30.0],
            "dead_ba": [2.0, 15.0, 2.0, 2.0],
            "qmd": [15.0, 12.0, 8.0, 4.0],
        }
    )


def test_eligible_intervals_removes_young_mortality_and_small_qmd() -> None:
    """Only the established, low-mortality interval survives."""
    frame = eligible_intervals(_intervals(), min_ba0=15.0, max_mortality_fraction=0.4, min_qmd=6.0)
    assert frame["interval_id"].tolist() == ["eligible"]
    assert frame["mortality_fraction"].tolist() == [2.0 / 30.0]


def test_eligible_intervals_refuses_a_missing_column() -> None:
    """A caller that forgets qmd gets a named error."""
    with pytest.raises(ValueError, match="qmd"):
        eligible_intervals(_intervals().drop(columns="qmd"))


def test_parameter_keywords_render_bounds_and_species() -> None:
    """A candidate becomes the FVS records in a stable order."""
    records = parameter_keywords(
        bamax=45.0,
        baimult={"PL": 0.5},
        mortmult={"SE": 2.0},
        htgmul={"PL": 0.75},
    )
    assert [record.name for record in records] == ["BAMAX", "BAIMULT", "MORTMULT", "HTGMULT"]
    assert records[0].parameters == ("45.0",)
    assert records[1].parameters == ("1", "PL", "0.5000")
    assert records[2].parameters == ("1", "SE", "2.0000", "0", "999")
    assert records[3].parameters == ("1", "PL", "0.7500")


def test_insert_parameters_places_records_before_process() -> None:
    """The calibration records are read before the projection starts."""
    base = (Keyword("STDINFO", ("CAR", "SBPSmc/01")), Keyword("PROCESS"), Keyword("STOP"))
    combined = insert_parameters(base, parameter_keywords(bamax=45.0))
    assert [keyword.name for keyword in combined] == ["STDINFO", "BAMAX", "PROCESS", "STOP"]


def test_insert_parameters_needs_a_projection() -> None:
    """A set that cannot accept parameters is refused."""
    with pytest.raises(ValueError, match="PROCESS"):
        insert_parameters((Keyword("STDINFO", ("CAR", "SBPSmc/01")),), ())


def test_summarise_probe_reports_bias_and_mae() -> None:
    """The probe summary is the arithmetic the report quotes."""
    rows = pd.DataFrame(
        {
            "candidate": ["a", "a", "b"],
            "fold": ["train", "test", "train"],
            "ba_error": [2.0, -2.0, 10.0],
            "tph_error": [100.0, -100.0, 500.0],
        }
    )
    summary = summarise_probe(rows)
    first = summary[(summary["candidate"] == "a") & (summary["fold"] == "train")].iloc[0]
    assert first["intervals"] == 1
    assert first["bias_ba"] == 2.0
    assert first["mae_ba"] == 2.0
    assert first["bias_tph"] == 100.0
