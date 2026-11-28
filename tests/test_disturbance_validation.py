"""Tests for the observed-disturbance contract and the validation harness."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from fresh_fvsbc import disturbance
from fresh_fvsbc.disturbance import DisturbanceError


def _observations(path: Path) -> Path:
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "DISTURBANCE_YEAR": 2003,
                "DISTURBANCE_TYPE": "Fire",
                "SEVERITY": 0.7,
                "EVENT_ID": "fire-1",
            },
            {
                "SITE_IDENTIFIER": 2,
                "DISTURBANCE_YEAR": 2010,
                "DISTURBANCE_TYPE": "harvest",
                "SEVERITY": 0.4,
                "EVENT_ID": "cut-1",
            },
            {
                "SITE_IDENTIFIER": 9,
                "DISTURBANCE_YEAR": 2015,
                "DISTURBANCE_TYPE": "mpb",
                "SEVERITY": 0.2,
                "EVENT_ID": "mpb-1",
            },
        ]
    ).to_csv(path, index=False)
    return path


def test_load_observations_normalises_type_and_year(tmp_path: Path) -> None:
    """Type is lower-cased, year an int, severity a float."""
    frame = disturbance.load_observations(_observations(tmp_path / "events.csv"))
    assert frame.loc[0, "DISTURBANCE_TYPE"] == "fire"
    assert frame.loc[0, "DISTURBANCE_YEAR"] == 2003
    assert frame.loc[0, "SEVERITY"] == pytest.approx(0.7)


def test_load_observations_rejects_a_missing_column(tmp_path: Path) -> None:
    """The contract names every required column."""
    path = tmp_path / "bad.csv"
    pd.DataFrame([{"SITE_IDENTIFIER": 1}]).to_csv(path, index=False)
    with pytest.raises(DisturbanceError, match="missing columns"):
        disturbance.load_observations(path)


def test_load_observations_rejects_bad_type_and_severity(tmp_path: Path) -> None:
    """Unknown types and out-of-range severity are refused."""
    path = tmp_path / "bad.csv"
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "DISTURBANCE_YEAR": 2000,
                "DISTURBANCE_TYPE": "flood",
                "SEVERITY": 0.5,
            }
        ]
    ).to_csv(path, index=False)
    with pytest.raises(DisturbanceError, match="unknown disturbance type"):
        disturbance.load_observations(path)
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "DISTURBANCE_YEAR": 2000,
                "DISTURBANCE_TYPE": "fire",
                "SEVERITY": 1.5,
            }
        ]
    ).to_csv(path, index=False)
    with pytest.raises(DisturbanceError, match="severity"):
        disturbance.load_observations(path)


def test_load_observations_rejects_non_numeric_values(tmp_path: Path) -> None:
    """A year that is not numeric is a bad input, not a silent NaN."""
    path = tmp_path / "bad.csv"
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "DISTURBANCE_YEAR": "year",
                "DISTURBANCE_TYPE": "fire",
                "SEVERITY": 0.5,
            }
        ]
    ).to_csv(path, index=False)
    with pytest.raises(DisturbanceError, match="non-numeric"):
        disturbance.load_observations(path)


def test_coverage_reports_matched_and_unmatched_sites() -> None:
    """Only sites in the interval table can be scored."""
    observations = pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "DISTURBANCE_TYPE": "fire", "SEVERITY": 0.7},
            {"SITE_IDENTIFIER": 2, "DISTURBANCE_TYPE": "harvest", "SEVERITY": 0.4},
            {"SITE_IDENTIFIER": 9, "DISTURBANCE_TYPE": "mpb", "SEVERITY": 0.2},
        ]
    )
    intervals = pd.DataFrame({"SITE_IDENTIFIER": [1, 2]})
    result = disturbance.coverage(observations, intervals)
    assert result["observations"] == 3
    assert result["sites"] == 3
    assert result["matched_sites"] == 2
    assert result["unmatched_sites"] == ["9"]
    assert result["by_type"] == {"fire": 1, "harvest": 1, "mpb": 1}
    assert result["severity_min"] == pytest.approx(0.2)
    assert result["severity_max"] == pytest.approx(0.7)


def test_coverage_accepts_an_empty_template() -> None:
    """The shipped template has no events and must still check cleanly."""
    empty = pd.DataFrame(columns=disturbance.REQUIRED_COLUMNS)
    result = disturbance.coverage(empty, pd.DataFrame({"SITE_IDENTIFIER": [1]}))
    assert result["observations"] == 0
    assert result["matched_sites"] == 0
    assert result["severity_min"] is None


def test_interval_coverage_counts_events_between_visits() -> None:
    """An event after the first visit and before the second is inside."""
    observations = pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "DISTURBANCE_YEAR": 2005, "DISTURBANCE_TYPE": "fire"},
            {"SITE_IDENTIFIER": 1, "DISTURBANCE_YEAR": 1995, "DISTURBANCE_TYPE": "harvest"},
        ]
    )
    intervals = pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "year0": 2000,
                "year1": 2010,
                "interval_id": "1|1|2000|2010",
            }
        ]
    )
    result = disturbance.interval_coverage(observations, intervals)
    assert result["events"] == 1
    assert result["intervals"] == 1
    assert result["sites"] == 1
    assert result["by_type"] == {"fire": 1}


def test_interval_coverage_handles_empty_and_missing_columns() -> None:
    """An empty table is zero; a bad interval table names the missing column."""
    empty = pd.DataFrame(columns=disturbance.REQUIRED_COLUMNS)
    assert disturbance.interval_coverage(empty, pd.DataFrame())["events"] == 0
    with pytest.raises(DisturbanceError, match="missing interval columns"):
        disturbance.interval_coverage(
            pd.DataFrame(
                [{"SITE_IDENTIFIER": 1, "DISTURBANCE_YEAR": 2000, "DISTURBANCE_TYPE": "fire"}]
            ),
            pd.DataFrame({"SITE_IDENTIFIER": [1]}),
        )


def test_summarise_scores_by_type_and_severity() -> None:
    """Bias and MAE are computed against the observed post-event stand."""
    predictions = pd.DataFrame(
        [
            {
                "DISTURBANCE_TYPE": "fire",
                "SEVERITY": 0.7,
                "observed_ba1": 10.0,
                "predicted_ba1": 12.0,
                "observed_tph1": 100.0,
                "predicted_tph1": 80.0,
            },
            {
                "DISTURBANCE_TYPE": "fire",
                "SEVERITY": 0.7,
                "observed_ba1": 10.0,
                "predicted_ba1": 8.0,
                "observed_tph1": 100.0,
                "predicted_tph1": 120.0,
            },
        ]
    )
    summary = disturbance.summarise(predictions)
    row = summary.iloc[0]
    assert row["intervals"] == 2
    assert row["bias_ba"] == pytest.approx(0.0)
    assert row["mae_ba"] == pytest.approx(2.0)
    assert row["bias_tph"] == pytest.approx(0.0)
    assert row["mae_tph"] == pytest.approx(20.0)


def test_summarise_rejects_missing_columns_and_handles_empty() -> None:
    """The prediction contract is checked; an empty table returns its columns."""
    with pytest.raises(DisturbanceError, match="missing prediction columns"):
        disturbance.summarise(pd.DataFrame([{"DISTURBANCE_TYPE": "fire"}]))
    empty = disturbance.summarise(pd.DataFrame(columns=disturbance.PREDICTION_COLUMNS))
    assert empty.empty
    assert "mae_tph" in empty.columns


def test_cli_reports_coverage_and_scores_predictions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The CLI reads the template, prints coverage, and scores a predictions file."""
    import validate_disturbance

    data = tmp_path / "calib"
    data.mkdir()
    pd.DataFrame(
        {
            "SITE_IDENTIFIER": [1, 2],
            "year0": [2000, 2000],
            "year1": [2010, 2010],
            "interval_id": ["1|1|2000|2010", "2|1|2000|2010"],
        }
    ).to_csv(data / "intervals.csv", index=False)
    events = _observations(tmp_path / "events.csv")
    status = validate_disturbance.main(["--observations", str(events), "--intervals", str(data)])
    assert status == 0
    printed = capsys.readouterr().out
    assert '"matched_sites": 2' in printed
    assert "coverage only" in printed

    predictions = tmp_path / "pred.csv"
    pd.DataFrame(
        [
            {
                "DISTURBANCE_TYPE": "fire",
                "SEVERITY": 0.7,
                "observed_ba1": 10.0,
                "predicted_ba1": 12.0,
                "observed_tph1": 100.0,
                "predicted_tph1": 80.0,
            }
        ]
    ).to_csv(predictions, index=False)
    status = validate_disturbance.main(
        [
            "--observations",
            str(events),
            "--intervals",
            str(data),
            "--predictions",
            str(predictions),
        ]
    )
    assert status == 0
    assert "bias_ba" in capsys.readouterr().out


def test_cli_refuses_missing_and_bad_inputs(tmp_path: Path) -> None:
    """Missing observations and bad predictions both return the bad-input code."""
    import validate_disturbance

    data = tmp_path / "calib"
    data.mkdir()
    pd.DataFrame({"SITE_IDENTIFIER": [1]}).to_csv(data / "intervals.csv", index=False)
    assert (
        validate_disturbance.main(
            [
                "--observations",
                str(tmp_path / "missing.csv"),
                "--intervals",
                str(data),
            ]
        )
        == 2
    )
    bad = tmp_path / "bad.csv"
    bad.write_text("x\n1\n", encoding="utf-8")
    assert validate_disturbance.main(["--observations", str(bad), "--intervals", str(data)]) == 2
    events = _observations(tmp_path / "events.csv")
    assert (
        validate_disturbance.main(
            [
                "--observations",
                str(events),
                "--intervals",
                str(data),
                "--predictions",
                str(bad),
            ]
        )
        == 2
    )
