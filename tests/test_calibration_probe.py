"""Tests for the calibration probe's pure selection and keyword helpers."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import run_calibration_probe as probe
from fresh_fvsbc.calibration_probe import (
    eligible_intervals,
    ingrowth_keyword,
    insert_parameters,
    interval_checksum,
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
    assert records[0].parameters == ("45",)
    assert records[1].parameters == ("1", "PL", "0.5000")
    assert records[2].parameters == ("1", "SE", "2.0000", "0", "999")
    assert records[3].parameters == ("1", "PL", "0.7500")


def test_interval_checksum_is_order_independent() -> None:
    """The checksum identifies the sample, not the pandas row order."""
    frame = pd.DataFrame(
        {
            "interval_id": ["b", "a"],
            "BEC": ["SBPSmk", "SBPSmk"],
            "TSA_DESC": ["Quesnel TSA", "Quesnel TSA"],
            "ba0": [20.0, 25.0],
            "qmd": [18.0, 19.0],
            "tph0": [800.0, 900.0],
            "years": [10.0, 10.0],
            "dead_ba": [1.0, 2.0],
        }
    )
    assert interval_checksum(frame) == interval_checksum(frame.iloc[::-1])
    assert interval_checksum(frame).startswith("sha256:")


def test_parameter_keywords_render_small_tree_growth_multipliers() -> None:
    """Small-tree growth is a separate calibration lever, not another BAIMULT."""
    records = parameter_keywords(regdmul={"CW": 2.0}, reghmul={"CW": 1.5})
    assert [record.name for record in records] == ["REGDMULT", "REGHMULT"]
    assert records[0].parameters == ("1", "CW", "2.0000")
    assert records[1].parameters == ("1", "CW", "1.5000")


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


def test_probe_parser_carries_the_common_minimum_dbh() -> None:
    """A 4+ cm cross-program run is explicit on the command line."""
    args = probe._parser().parse_args(
        [
            "--data-dir",
            "data",
            "--psp-dir",
            "psp",
            "--out-dir",
            "out",
            "--domain",
            "CWH",
            "--candidates",
            "candidates.json",
            "--min-dbh",
            "4",
        ]
    )
    assert args.min_dbh == 4.0


def test_probe_main_writes_a_summary_with_a_mocked_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI wiring is covered without a Fortran run."""
    data = tmp_path / "data"
    data.mkdir()
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "CLSTR_ID": "1-PSP",
                "visit0": 1,
                "visit1": 2,
                "PLOT": 1,
                "ba0": 30.0,
                "dead_ba": 2.0,
                "qmd": 12.0,
                "BEC": "SBPSmk",
                "TSA_DESC": "Quesnel TSA",
                "year0": 2000,
                "year1": 2010,
                "years": 10,
                "interval_id": "1|1|2000|2010",
            }
        ]
    ).to_csv(data / "intervals.csv", index=False)
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "VISIT_NUMBER": 2,
                "PLOT": 1,
                "ba": 32.0,
                "tph": 900.0,
            }
        ]
    ).to_csv(data / "visits.csv", index=False)
    candidates = tmp_path / "candidates.json"
    candidates.write_text(json.dumps([{"label": "base", "bamax": 50.0}]), encoding="utf-8")
    monkeypatch.setattr(probe, "_read_trees", lambda *_args, **_kwargs: pd.DataFrame({"x": [1]}))
    monkeypatch.setattr(
        probe, "psp_tree_records", lambda *_args, **_kwargs: ([{"species": "PL"}], 0)
    )
    monkeypatch.setattr(
        probe,
        "run_case",
        lambda *_args, **_kwargs: SimpleNamespace(database=tmp_path / "FVSOut.db"),
    )
    monkeypatch.setattr(
        probe, "summary_for_year", lambda *_args, **_kwargs: {"ba": 31.0, "tph": 950.0}
    )
    status = probe.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(tmp_path / "psp"),
            "--out-dir",
            str(tmp_path / "out"),
            "--domain",
            "SBPS",
            "--candidates",
            str(candidates),
            "--test-year-from",
            "1995",
        ]
    )
    assert status == 0
    summary = pd.read_csv(tmp_path / "out" / "probe_summary.csv")
    assert summary.loc[0, "candidate"] == "base"
    assert summary.loc[0, "bias_ba"] == -1.0
    probe_rows = pd.read_csv(tmp_path / "out" / "probe.csv")
    assert probe_rows["fold"].tolist() == ["test"]
    metadata = json.loads((tmp_path / "out" / "probe.json").read_text())
    assert metadata["test_year_from"] == 1995
    assert metadata["data_checksum"].startswith("sha256:")


def test_candidates_refuses_empty_and_unlabelled_lists(tmp_path: Path) -> None:
    """A candidate file that cannot name a row is refused."""
    path = tmp_path / "candidates.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty"):
        probe._candidates(path)
    path.write_text('[{"bamax": 50.0}]', encoding="utf-8")
    with pytest.raises(ValueError, match="label"):
        probe._candidates(path)


def test_probe_main_refuses_missing_data_and_empty_tree_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI reports a bad input without trying to run FVS."""
    candidates = tmp_path / "candidates.json"
    candidates.write_text('[{"label": "base", "bamax": 50.0}]', encoding="utf-8")
    base = [
        "--psp-dir",
        str(tmp_path / "psp"),
        "--out-dir",
        str(tmp_path / "out"),
        "--domain",
        "SBPS",
        "--candidates",
        str(candidates),
    ]
    assert probe.main(["--data-dir", str(tmp_path / "missing"), *base]) == 2

    data = tmp_path / "data"
    data.mkdir()
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "CLSTR_ID": "1-PSP",
                "visit0": 1,
                "visit1": 2,
                "PLOT": 1,
                "ba0": 30.0,
                "dead_ba": 2.0,
                "qmd": 12.0,
                "BEC": "SBPSmk",
                "TSA_DESC": "Quesnel TSA",
                "year0": 2000,
                "year1": 2010,
                "years": 10,
                "interval_id": "1|1|2000|2010",
            }
        ]
    ).to_csv(data / "intervals.csv", index=False)
    pd.DataFrame(
        [{"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 32.0, "tph": 900.0}]
    ).to_csv(data / "visits.csv", index=False)
    monkeypatch.setattr(probe, "_read_trees", lambda *_args, **_kwargs: pd.DataFrame())
    assert probe.main(["--data-dir", str(data), *base]) == 2

    monkeypatch.setattr(probe, "_read_trees", lambda *_args, **_kwargs: pd.DataFrame({"x": [1]}))
    monkeypatch.setattr(probe, "psp_tree_records", lambda *_args, **_kwargs: ([], 0))
    assert probe.main(["--data-dir", str(data), *base]) == 2


def test_ingrowth_keyword_builds_natural_regeneration() -> None:
    """A BEC rate becomes one NATURAL line per species, in TPA."""
    keyword = ingrowth_keyword(
        bec="IDFdk3", years=10.0, rates={"IDFdk3": {"FD": 56.6, "PL": 5.1}}, scale=1.0
    )
    assert keyword is not None
    assert keyword.name == "ESTAB"
    assert [line.name for line in keyword.nested] == ["NATURAL", "NATURAL"]
    assert keyword.nested[0].parameters == ("1", "FD", "229.1", "100.0")
    assert keyword.nested[1].parameters == ("1", "PL", "20.6", "100.0")


def test_ingrowth_keyword_returns_none_without_a_rate() -> None:
    """A BEC with no recruitment does not add an empty ESTAB block."""
    assert ingrowth_keyword(bec="IDFdk3", years=10.0, rates={}) is None
