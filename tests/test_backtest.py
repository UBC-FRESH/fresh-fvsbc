"""Tests for the baseline backtest and the envelope flag.

The fixture is one IDFdk3 interval with three live trees, one of them a species
that does not resolve. The FVS run itself is faked at the seam; the real run is
a command a maintainer runs against the built extension.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import run_baseline_backtest as cli
from fresh_fvsbc import backtest
from fresh_fvsbc.backtest import (
    compare_rows,
    keywords_for,
    psp_tree_records,
    select_intervals,
    summarise,
)
from fresh_fvsbc.envelope import envelope_flags, load_envelope


def _intervals() -> pd.DataFrame:
    """Return two BECs with two intervals each."""
    return pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": "S1",
                "CLSTR_ID": "S1-PSP1",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "year0": 2000,
                "year1": 2010,
                "years": 10.0,
                "ba0": 30.0,
                "tph0": 900.0,
                "BEC": "IDFdk3",
                "TSA_DESC": "Williams Lake TSA",
                "interval_id": "S1|1|2000|2010",
            },
            {
                "SITE_IDENTIFIER": "S2",
                "CLSTR_ID": "S2-PSP1",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "year0": 2000,
                "year1": 2010,
                "years": 10.0,
                "ba0": 35.0,
                "tph0": 800.0,
                "BEC": "IDFdk3",
                "TSA_DESC": "Kamloops TSA",
                "interval_id": "S2|1|2000|2010",
            },
            {
                "SITE_IDENTIFIER": "S3",
                "CLSTR_ID": "S3-PSP1",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "year0": 2000,
                "year1": 2010,
                "years": 10.0,
                "ba0": 40.0,
                "tph0": 700.0,
                "BEC": "SBSmc2",
                "TSA_DESC": "Prince George TSA",
                "interval_id": "S3|1|2000|2010",
            },
        ]
    )


def _row(frame: pd.DataFrame, index: int = 0) -> dict[str, object]:
    """Return one frame row as a string-keyed mapping."""
    return {str(key): value for key, value in frame.iloc[index].items()}


def _trees() -> pd.DataFrame:
    """Return the start trees for the first interval."""
    return pd.DataFrame(
        [
            _tree("S1", "S1-PSP1", 1, 1, "FD", 20.0, 18.0, "C"),
            _tree("S1", "S1-PSP1", 1, 2, "PL", 15.0, 14.0, "I"),
            _tree("S1", "S1-PSP1", 1, 3, "ZZ", 10.0, 9.0, "S"),
        ]
    )


def _tree(
    site: str,
    cluster: str,
    visit: int,
    tree: int,
    species: str,
    dbh: float,
    height: float,
    crown: str,
) -> dict[str, object]:
    """Build one raw FAIB tree row."""
    return {
        "SITE_IDENTIFIER": site,
        "CLSTR_ID": cluster,
        "VISIT_NUMBER": visit,
        "PLOT": 1,
        "TREE_NO": tree,
        "SPECIES": species,
        "DBH": dbh,
        "HEIGHT": height,
        "LV_D": "L",
        "PHF_TREE": 10.0,
        "CR_CL": crown,
    }


def _visits() -> pd.DataFrame:
    """Return the second-measurement visit for the first interval."""
    return pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": "S1",
                "CLSTR_ID": "S1-PSP1",
                "VISIT_NUMBER": 2,
                "PLOT": 1,
                "ba": 32.0,
                "tph": 880.0,
                "qmd": 21.0,
                "top_height": 19.0,
                "volume": 210.0,
            }
        ]
    )


def _envelope() -> dict[str, dict[str, float]]:
    """Return a minimal envelope."""
    return {"IDFdk3": {"ba_p99": 54.1, "ba_max": 63.7}}


def test_select_intervals_is_stratified_and_deterministic() -> None:
    """One interval per BEC, and the same one on a second call."""
    first = select_intervals(_intervals(), per_bec=1)
    second = select_intervals(_intervals(), per_bec=1)
    assert first["BEC"].tolist() == ["IDFdk3", "SBSmc2"]
    assert first["interval_id"].tolist() == second["interval_id"].tolist()


def test_tree_records_use_the_expansion_factor_and_skip_unknown_species() -> None:
    """The tree count is PHF_TREE, and the unknown code is counted, not mapped."""
    records, skipped = psp_tree_records(_trees(), _row(_intervals()))
    assert len(records) == 2
    assert skipped == 1
    assert records[0]["tree_count"] == 10.0
    assert records[0]["species"] == "FD"
    assert records[0]["crown_ratio"] == 6


def test_keywords_use_the_interval_length_and_the_bec() -> None:
    """The run is one cycle of the interval's length, in the interval's BEC."""
    keywords = keywords_for(_row(_intervals()))
    fields = {keyword.name: keyword.parameters for keyword in keywords}
    assert fields["STDINFO"][:2] == ("CAR", "IDFdk3/01")
    assert fields["TIMEINT"] == ("", "10")
    assert fields["INVYEAR"] == ("2000",)
    assert fields["NUMCYCLE"] == ("1",)


def test_a_prediction_above_the_envelope_is_flagged() -> None:
    """77 m2/ha is above the IDFdk3 maximum; 50 is inside it."""
    assert envelope_flags(77.0, "IDFdk3", _envelope()) == "above_max"
    assert envelope_flags(50.0, "IDFdk3", _envelope()) == "ok"
    assert envelope_flags(60.0, "IDFdk3", _envelope()) == "above_p99"
    assert envelope_flags(10.0, "CWHvm1", _envelope()) == "unknown"


def test_compare_rows_carries_the_bias_and_the_flag() -> None:
    """The row compares the second measurement with the end of the run."""
    interval = _row(_intervals())
    observed = {"ba": 32.0, "tph": 880.0, "qmd": 21.0, "top_height": 19.0, "volume": 210.0}
    start = {"ba": 30.0, "tph": 900.0, "qmd": 20.0, "top_height": 18.0, "volume": 200.0}
    end = {"ba": 77.0, "tph": 900.0, "qmd": 22.0, "top_height": 20.0, "volume": 250.0}
    row = compare_rows(interval, observed, start, end, _envelope())
    assert row["bias_ba"] == 45.0
    assert row["flag_predicted"] == "above_max"


def test_summarise_groups_by_bec() -> None:
    """Two rows in one BEC become one summary row."""
    interval = _row(_intervals())
    observed = {"ba": 32.0, "tph": 880.0, "qmd": 21.0, "top_height": 19.0, "volume": 210.0}
    start = {"ba": 30.0, "tph": 900.0, "qmd": 20.0, "top_height": 18.0, "volume": 200.0}
    end = {"ba": 50.0, "tph": 900.0, "qmd": 22.0, "top_height": 20.0, "volume": 250.0}
    frame = pd.DataFrame(
        [
            compare_rows(interval, observed, start, end, _envelope()),
            compare_rows(interval, observed, start, end, _envelope()),
        ]
    )
    summary = summarise(frame)
    assert summary.loc[0, "intervals"] == 2


def test_load_envelope_refuses_a_missing_column(tmp_path: Path) -> None:
    """The envelope table has to carry the two columns the flag reads."""
    path = tmp_path / "envelope.csv"
    path.write_text("BEC,ba_p99\nIDFdk3,54.1\n")
    with pytest.raises(ValueError, match="ba_max"):
        load_envelope(path)


def test_run_backtest_uses_the_seam(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The loop builds a row when the drive and the summary are stubbed."""

    def fake_run(records: object, keywords: object, *, directory: Path) -> SimpleNamespace:
        return SimpleNamespace(database=directory / "fake.db")

    def fake_summary(database: object, year: int) -> dict[str, float]:
        return {
            "ba": 30.0 if year == 2000 else 40.0,
            "tph": 900.0 if year == 2000 else 880.0,
            "qmd": 20.0 if year == 2000 else 21.0,
            "top_height": 18.0 if year == 2000 else 19.0,
            "volume": 200.0 if year == 2000 else 210.0,
        }

    monkeypatch.setattr(backtest, "run_case", fake_run)
    monkeypatch.setattr(backtest, "summary_for_year", fake_summary)
    rows, summary, skips = backtest.run_backtest(
        _intervals(),
        _trees(),
        _visits(),
        _envelope(),
        tmp_path / "runs",
        per_bec=2,
    )
    assert len(rows) == 1
    assert summary.loc[0, "BEC"] == "IDFdk3"
    assert int(skips["skipped"].sum()) == 1


def test_the_command_dry_run_writes_the_sample(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The dry run selects the sample before any FVS run."""
    data = tmp_path / "data"
    data.mkdir()
    _intervals().to_csv(data / "intervals.csv", index=False)
    _visits().to_csv(data / "visits.csv", index=False)
    pd.DataFrame([{"BEC": "IDFdk3", "ba_p99": 54.1, "ba_max": 63.7}]).to_csv(
        data / "bec_envelope.csv", index=False
    )
    code = cli.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(tmp_path / "psp"),
            "--out-dir",
            str(tmp_path / "out"),
            "--dry-run",
        ]
    )
    assert code == cli.EXIT_OK
    assert (tmp_path / "out" / "baseline_sample.csv").is_file()
    assert "2 intervals" in capsys.readouterr().out


def test_the_command_refuses_a_missing_dataset(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing dataset is bad input, not a traceback."""
    code = cli.main(
        [
            "--data-dir",
            str(tmp_path / "absent"),
            "--psp-dir",
            str(tmp_path / "psp"),
            "--out-dir",
            str(tmp_path / "out"),
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "intervals.csv" in capsys.readouterr().err


def test_classes_for_names_the_dominant_group_and_the_classes() -> None:
    """The class fields used by the grouped summaries are derived from the trees."""
    records, _ = psp_tree_records(_trees(), _row(_intervals()))
    classes = backtest.classes_for(records, 35.0)
    assert classes["species_group"] == "FD"
    assert classes["dbh_class"] == "10-25"
    assert classes["ba_class"] == "30-40"


def test_tree_records_fill_a_missing_height_and_map_an_alias() -> None:
    """A low height is estimated from DBH, and SX is the SE alias."""
    trees = _trees()
    trees.loc[0, "HEIGHT"] = 0.0
    trees.loc[1, "SPECIES"] = "SX"
    records, skipped = psp_tree_records(trees, _row(_intervals()))
    assert skipped == 1
    assert records[0]["live_ht"] == 11.3
    assert records[1]["species"] == "SE"


def test_keywords_use_the_region_from_the_tsa() -> None:
    """Kamloops and Nelson get their region tokens; the rest default to CAR."""
    kamloops = dict(_row(_intervals()))
    kamloops["TSA_DESC"] = "Kamloops TSA"
    nelson = dict(_row(_intervals()))
    nelson["TSA_DESC"] = "Nelson TSA"
    assert keywords_for(kamloops)[2].parameters[0] == "KAM"
    assert keywords_for(nelson)[2].parameters[0] == "NEL"


def test_compare_rows_returns_unknown_for_a_bec_outside_the_envelope() -> None:
    """The flag is not a pass when the BEC is outside the table."""
    interval = dict(_row(_intervals()))
    interval["BEC"] = "CWHvm1"
    observed = {"ba": 32.0, "tph": 880.0, "qmd": 21.0, "top_height": 19.0, "volume": 210.0}
    start = {"ba": 30.0, "tph": 900.0, "qmd": 20.0, "top_height": 18.0, "volume": 200.0}
    end = {"ba": 50.0, "tph": 900.0, "qmd": 22.0, "top_height": 20.0, "volume": 250.0}
    row = compare_rows(interval, observed, start, end, _envelope())
    assert row["flag_predicted"] == "unknown"


def test_summarise_an_empty_frame_returns_an_empty_frame() -> None:
    """No rows is not an error."""
    assert summarise(pd.DataFrame()).empty


def test_run_backtest_records_an_interval_with_no_resolved_trees(
    tmp_path: Path,
) -> None:
    """An interval whose trees all fail the species crosswalk is reported, not run."""
    rows, summary, skips = backtest.run_backtest(
        _intervals(),
        pd.DataFrame(
            columns=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "PLOT", "LV_D", "PHF_TREE"]
        ),
        _visits(),
        _envelope(),
        tmp_path / "runs",
        per_bec=1,
    )
    assert rows.empty
    assert summary.empty
    assert set(skips["reason"].dropna()) == {"no tree resolved to one of BC's 15 species"}


def test_the_markdown_helper_handles_an_empty_frame() -> None:
    """An empty frame is a sentence, not a crash."""
    assert cli._markdown(pd.DataFrame()) == "No rows."


def test_the_tree_reader_filters_the_sample(tmp_path: Path) -> None:
    """The raw tree reader keeps only the sampled interval's rows."""
    psp = tmp_path / "psp"
    psp.mkdir()
    _trees().to_csv(psp / "faib_tree_detail.csv", index=False)
    sample = _intervals().iloc[[0]]
    rows = cli._read_trees(psp, sample)
    assert len(rows) == 3
    assert set(rows["SITE_IDENTIFIER"]) == {"S1"}


def test_the_command_runs_with_the_seams_stubbed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The real path writes every grouped table when the run seam is stubbed."""
    data = tmp_path / "data"
    data.mkdir()
    _intervals().to_csv(data / "intervals.csv", index=False)
    _visits().to_csv(data / "visits.csv", index=False)
    pd.DataFrame([{"BEC": "IDFdk3", "ba_p99": 54.1, "ba_max": 63.7}]).to_csv(
        data / "bec_envelope.csv", index=False
    )
    rows = pd.DataFrame(
        [
            {
                "interval_id": "S1|1|2000|2010",
                "BEC": "IDFdk3",
                "TSA": "Williams Lake TSA",
                "species_group": "FD",
                "dbh_class": "10-25",
                "ba_class": "30-40",
                "observed_ba0": 30.0,
                "predicted_ba0": 30.0,
                "observed_ba1": 32.0,
                "predicted_ba1": 33.0,
                "bias_ba": 1.0,
                "bias_tph": -10.0,
                "bias_net_ba_rate": 0.1,
                "bias_net_tph_rate": -1.0,
                "bias_qmd": 0.1,
                "bias_top_height": 0.2,
                "bias_volume": 1.0,
                "flag_predicted": "ok",
            }
        ]
    )
    skips = pd.DataFrame(
        [{"interval_id": "S1|1|2000|2010", "BEC": "IDFdk3", "trees": 1, "skipped": 0, "reason": ""}]
    )
    monkeypatch.setattr(cli, "_read_trees", lambda psp, sample: _trees())
    monkeypatch.setattr(
        cli,
        "run_backtest",
        lambda *args, **kwargs: (rows, summarise(rows), skips),
    )
    code = cli.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(tmp_path / "psp"),
            "--out-dir",
            str(tmp_path / "out"),
        ]
    )
    assert code == cli.EXIT_OK
    for name in (
        "baseline_backtest.csv",
        "baseline_summary.csv",
        "baseline_by_species.csv",
        "baseline_report.md",
        "baseline_skip_reasons.csv",
    ):
        assert (tmp_path / "out" / name).is_file()
