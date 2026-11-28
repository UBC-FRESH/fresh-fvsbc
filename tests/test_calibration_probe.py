"""Tests for the calibration probe's pure selection and keyword helpers."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import run_calibration_probe as probe
from fresh_fvsbc.bundle import default_bundle_path
from fresh_fvsbc.calibration_probe import (
    eligible_intervals,
    ingrowth_keyword,
    insert_parameters,
    interval_checksum,
    parameter_keywords,
    split_cycles,
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


def test_drop_unaccounted_removals_keeps_recorded_mortality() -> None:
    """A harvest loses trees without a death record; natural mortality does not."""
    intervals = pd.DataFrame(
        [
            {
                "interval_id": "natural",
                "tph0": 1000.0,
                "next_tph": 900.0,
                "dead_tph": 100.0,
                "ba0": 40.0,
                "next_ba": 36.0,
                "dead_ba": 4.0,
            },
            {
                "interval_id": "harvest",
                "tph0": 1000.0,
                "next_tph": 500.0,
                "dead_tph": 100.0,
                "ba0": 40.0,
                "next_ba": 20.0,
                "dead_ba": 4.0,
            },
        ]
    )
    kept = probe._drop_unaccounted_removals(intervals, max_fraction=0.1)
    assert kept["interval_id"].tolist() == ["natural"]


def test_probe_parser_carries_the_removal_screen_option() -> None:
    """The unaccounted-removal screen is explicit on the command line."""
    args = probe._parser().parse_args(
        [
            "--data-dir",
            "data",
            "--psp-dir",
            "psp",
            "--out-dir",
            "out",
            "--domain",
            "CDF",
            "--candidates",
            "candidates.json",
            "--max-unaccounted-removal",
            "0.1",
        ]
    )
    assert args.max_unaccounted_removal == 0.1


def test_screen_tree_growth_flags_an_impossible_dbh_jump(tmp_path: Path) -> None:
    """A 98.3 -> 401.7 cm tree in sixteen years is a keying error, not growth."""
    psp = tmp_path / "psp"
    psp.mkdir()
    rows = []
    for site, cluster, tree, dbh in (
        (1, "1-PSP", 84, 98.3),
        (1, "1-PSP", 84, 401.7),
        (2, "2-PSP", 1, 20.0),
        (2, "2-PSP", 1, 22.0),
    ):
        visit = 1 if (site == 1 and dbh < 400) or (site == 2 and dbh == 20.0) else 2
        rows.append(
            {
                "SITE_IDENTIFIER": site,
                "CLSTR_ID": cluster,
                "VISIT_NUMBER": visit,
                "PLOT": 1,
                "TREE_NO": tree,
                "SPECIES": "FD",
                "DBH": dbh,
                "HEIGHT": 50.0,
                "LV_D": "L",
                "PHF_TREE": 2.47,
                "CR_CL": "C",
            }
        )
    pd.DataFrame(rows).to_csv(psp / "faib_tree_detail.csv", index=False)
    pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 1, "CLSTR_ID": "1-PSP"},
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "CLSTR_ID": "1-PSP"},
            {"SITE_IDENTIFIER": 2, "VISIT_NUMBER": 1, "CLSTR_ID": "2-PSP"},
            {"SITE_IDENTIFIER": 2, "VISIT_NUMBER": 2, "CLSTR_ID": "2-PSP"},
        ]
    ).to_csv(psp / "faib_sample_byvisit.csv", index=False)
    sample = pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "CLSTR_ID": "1-PSP",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "years": 16.0,
                "BEC": "CDFmm",
                "interval_id": "1|1|2008|2024",
            },
            {
                "SITE_IDENTIFIER": 2,
                "CLSTR_ID": "2-PSP",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "years": 10.0,
                "BEC": "CDFmm",
                "interval_id": "2|1|1990|2000",
            },
        ]
    )
    extra = pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 3,
                "CLSTR_ID": "3-PSP",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "years": 10.0,
                "BEC": "CDFmm",
                "interval_id": "3|1|1990|2000",
            },
            {
                "SITE_IDENTIFIER": 4,
                "CLSTR_ID": "4-PSP",
                "PLOT": 1,
                "visit0": 1,
                "visit1": 2,
                "years": 10.0,
                "BEC": "CDFmm",
                "interval_id": "4|1|1990|2000",
            },
        ]
    )
    screened = probe._screen_tree_growth(
        pd.concat([sample, extra], ignore_index=True), psp, max_rate=2.0
    )
    assert screened["interval_id"].tolist() == ["1|1|2008|2024"]
    assert screened.loc[0, "max_growth_cm_per_year"] == pytest.approx(18.96, abs=0.01)
    assert screened.loc[0, "max_end_dbh_cm"] == 401.7


def test_probe_parser_carries_the_growth_screen_option() -> None:
    """The tree-growth screen is explicit on the command line."""
    args = probe._parser().parse_args(
        [
            "--data-dir",
            "data",
            "--psp-dir",
            "psp",
            "--out-dir",
            "out",
            "--domain",
            "CDF",
            "--candidates",
            "candidates.json",
            "--max-dbh-growth-rate",
            "2.0",
        ]
    )
    assert args.max_dbh_growth_rate == 2.0


def test_probe_parser_carries_the_exact_bec_flag() -> None:
    """An exact subzone match is explicit, so SBSmc does not absorb SBSmc2."""
    args = probe._parser().parse_args(
        [
            "--data-dir",
            "data",
            "--psp-dir",
            "psp",
            "--out-dir",
            "out",
            "--domain",
            "SBSmc",
            "--candidates",
            "candidates.json",
            "--exact-bec",
        ]
    )
    assert args.exact_bec is True


def test_stable_dbh_limit_drops_changed_tally_limits(tmp_path: Path) -> None:
    """A visit that starts at 9.1 cm and ends at 2 cm is not a growth interval."""
    psp = tmp_path / "psp"
    psp.mkdir()
    pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 1, "DBH_LIMIT_TAG": "9.1"},
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "DBH_LIMIT_TAG": "2.0"},
            {"SITE_IDENTIFIER": 2, "VISIT_NUMBER": 1, "DBH_LIMIT_TAG": "2.0"},
            {"SITE_IDENTIFIER": 2, "VISIT_NUMBER": 2, "DBH_LIMIT_TAG": "2.0"},
        ]
    ).to_csv(psp / "faib_sample_byvisit.csv", index=False)
    intervals = pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "visit0": 1, "visit1": 2, "BEC": "SBSmk1"},
            {"SITE_IDENTIFIER": 2, "visit0": 1, "visit1": 2, "BEC": "SBSmk1"},
        ]
    )
    kept = probe._stable_dbh_limit(intervals, psp)
    assert kept["SITE_IDENTIFIER"].tolist() == [2]
    assert "limit0" not in kept.columns


def test_probe_main_exact_bec_excludes_the_sibling_subzones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A prefix match would mix SBSmc2 into the SBSmc fold; the flag prevents it."""
    data = tmp_path / "data"
    data.mkdir()
    row = {
        "SITE_IDENTIFIER": 1,
        "CLSTR_ID": "1-PSP",
        "visit0": 1,
        "visit1": 2,
        "PLOT": 1,
        "ba0": 30.0,
        "dead_ba": 2.0,
        "qmd": 12.0,
        "TSA_DESC": "Quesnel TSA",
        "year0": 2000,
        "year1": 2010,
        "years": 10,
        "interval_id": "1|1|2000|2010",
    }
    pd.DataFrame([{**row, "BEC": "SBSmc1"}, {**row, "BEC": "SBSmc2"}]).to_csv(
        data / "intervals.csv", index=False
    )
    pd.DataFrame(
        [{"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 32.0, "tph": 900.0}]
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
            "SBSmc1",
            "--exact-bec",
            "--candidates",
            str(candidates),
            "--test-year-from",
            "1995",
        ]
    )
    assert status == 0
    rows = pd.read_csv(tmp_path / "out" / "probe.csv")
    assert rows["BEC"].tolist() == ["SBSmc1"]


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


def test_probe_main_writes_screened_intervals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI drops a typo interval and records it for the calibration log."""
    data = tmp_path / "data"
    data.mkdir()
    common = {
        "CLSTR_ID": "1-PSP",
        "visit0": 1,
        "visit1": 2,
        "PLOT": 1,
        "ba0": 30.0,
        "next_ba": 32.0,
        "tph0": 900.0,
        "next_tph": 850.0,
        "dead_tph": 50.0,
        "dead_ba": 2.0,
        "qmd": 12.0,
        "BEC": "CDFmm",
        "TSA_DESC": "Quesnel TSA",
        "years": 16.0,
    }
    pd.DataFrame(
        [
            {
                **common,
                "SITE_IDENTIFIER": 1,
                "year0": 2008,
                "year1": 2024,
                "interval_id": "1|1|2008|2024",
            },
            {
                **common,
                "SITE_IDENTIFIER": 2,
                "CLSTR_ID": "2-PSP",
                "year0": 1990,
                "year1": 2000,
                "interval_id": "2|1|1990|2000",
            },
            {
                **common,
                "SITE_IDENTIFIER": 3,
                "CLSTR_ID": "3-PSP",
                "year0": 1990,
                "year1": 2000,
                "next_ba": 15.0,
                "next_tph": 400.0,
                "interval_id": "3|1|1990|2000",
            },
        ]
    ).to_csv(data / "intervals.csv", index=False)
    pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 32.0, "tph": 900.0},
            {"SITE_IDENTIFIER": 2, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 32.0, "tph": 900.0},
            {"SITE_IDENTIFIER": 3, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 15.0, "tph": 400.0},
        ]
    ).to_csv(data / "visits.csv", index=False)
    psp = tmp_path / "psp"
    psp.mkdir()
    rows = []
    for site, cluster, dbhs in (
        (1, "1-PSP", (98.3, 401.7)),
        (2, "2-PSP", (20.0, 22.0)),
        (3, "3-PSP", (20.0, 22.0)),
    ):
        for visit, dbh in zip((1, 2), dbhs, strict=True):
            rows.append(
                {
                    "SITE_IDENTIFIER": site,
                    "CLSTR_ID": cluster,
                    "VISIT_NUMBER": visit,
                    "PLOT": 1,
                    "TREE_NO": 1,
                    "SPECIES": "FD",
                    "DBH": dbh,
                    "HEIGHT": 40.0,
                    "LV_D": "L",
                    "PHF_TREE": 2.47,
                    "CR_CL": "C",
                }
            )
    pd.DataFrame(rows).to_csv(psp / "faib_tree_detail.csv", index=False)
    pd.DataFrame(
        [
            {"SITE_IDENTIFIER": site, "VISIT_NUMBER": visit, "CLSTR_ID": cluster}
            for site, cluster in ((1, "1-PSP"), (2, "2-PSP"), (3, "3-PSP"))
            for visit in (1, 2)
        ]
    ).to_csv(psp / "faib_sample_byvisit.csv", index=False)
    candidates = tmp_path / "candidates.json"
    candidates.write_text(json.dumps([{"label": "base", "bamax": 50.0}]), encoding="utf-8")
    monkeypatch.setattr(probe, "psp_tree_records", lambda *_a, **_k: ([{"species": "FD"}], 0))
    monkeypatch.setattr(
        probe,
        "run_case",
        lambda *_a, **_k: SimpleNamespace(database=tmp_path / "FVSOut.db"),
    )
    monkeypatch.setattr(probe, "summary_for_year", lambda *_a, **_k: {"ba": 31.0, "tph": 950.0})
    status = probe.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(psp),
            "--out-dir",
            str(tmp_path / "out"),
            "--domain",
            "CDF",
            "--candidates",
            str(candidates),
            "--max-dbh-growth-rate",
            "5",
            "--max-unaccounted-removal",
            "0.1",
        ]
    )
    assert status == 0
    screened = pd.read_csv(tmp_path / "out" / "screened_intervals.csv")
    assert screened["interval_id"].tolist() == ["1|1|2008|2024"]
    assert screened.loc[0, "max_end_dbh_cm"] == 401.7
    rows_out = pd.read_csv(tmp_path / "out" / "probe.csv")
    assert rows_out["interval_id"].tolist() == ["2|1|1990|2000"]


def _probe_data(tmp_path: Path) -> tuple[Path, Path]:
    """A one-interval dataset and candidate file for argument tests."""
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
                "next_ba": 32.0,
                "tph0": 900.0,
                "next_tph": 850.0,
                "dead_tph": 50.0,
                "dead_ba": 2.0,
                "qmd": 12.0,
                "BEC": "CDFmm",
                "TSA_DESC": "Quesnel TSA",
                "years": 16.0,
                "year0": 2008,
                "year1": 2024,
                "interval_id": "1|1|2008|2024",
            }
        ]
    ).to_csv(data / "intervals.csv", index=False)
    pd.DataFrame(
        [{"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 32.0, "tph": 850.0}]
    ).to_csv(data / "visits.csv", index=False)
    candidates = tmp_path / "candidates.json"
    candidates.write_text(json.dumps([{"label": "base", "bamax": 50.0}]), encoding="utf-8")
    return data, candidates


@pytest.mark.parametrize(
    "extra",
    [
        ("--cycles", "0"),
        ("--min-dbh", "-1"),
        ("--max-dbh-growth-rate", "-1"),
        ("--max-unaccounted-removal", "-1"),
        ("--max-cycle-years", "5"),
        ("--min-qmd", "-1"),
    ],
)
def test_probe_main_rejects_bad_arguments(tmp_path: Path, extra: tuple[str, ...]) -> None:
    """Invalid values exit with the bad-input code before any extension run."""
    data, candidates = _probe_data(tmp_path)
    args = [
        "--data-dir",
        str(data),
        "--psp-dir",
        str(tmp_path / "psp"),
        "--out-dir",
        str(tmp_path / "out"),
        "--domain",
        "CDF",
        "--candidates",
        str(candidates),
        *extra,
    ]
    if extra == ("--max-cycle-years", "5"):
        args += ["--cycles", "2"]
    assert probe.main(args) == 2


def test_probe_main_reports_an_empty_domain(tmp_path: Path) -> None:
    """A domain that matches no interval is a bad input, not an empty run."""
    data, candidates = _probe_data(tmp_path)
    status = probe.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(tmp_path / "psp"),
            "--out-dir",
            str(tmp_path / "out"),
            "--domain",
            "NOPE",
            "--exact-bec",
            "--candidates",
            str(candidates),
        ]
    )
    assert status == 2


def test_probe_main_renders_bundle_ingrowth_and_cycles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A bundle's ingrowth block and a multi-cycle interval are both rendered."""
    data, candidates = _probe_data(tmp_path)
    psp = tmp_path / "psp"
    psp.mkdir()
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "CLSTR_ID": "1-PSP",
                "VISIT_NUMBER": visit,
                "PLOT": 1,
                "TREE_NO": 1,
                "SPECIES": "FD",
                "DBH": dbh,
                "HEIGHT": 30.0,
                "LV_D": "L",
                "PHF_TREE": 2.47,
                "CR_CL": "C",
            }
            for visit, dbh in ((1, 20.0), (2, 22.0))
        ]
    ).to_csv(psp / "faib_tree_detail.csv", index=False)
    pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 1, "CLSTR_ID": "1-PSP"},
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "CLSTR_ID": "1-PSP"},
        ]
    ).to_csv(psp / "faib_sample_byvisit.csv", index=False)
    monkeypatch.setattr(probe, "psp_tree_records", lambda *_a, **_k: ([{"species": "FD"}], 0))
    monkeypatch.setattr(
        probe, "run_case", lambda *_a, **_k: SimpleNamespace(database=tmp_path / "FVSOut.db")
    )
    monkeypatch.setattr(probe, "summary_for_year", lambda *_a, **_k: {"ba": 31.0, "tph": 950.0})
    status = probe.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(psp),
            "--out-dir",
            str(tmp_path / "out"),
            "--domain",
            "CDF",
            "--candidates",
            str(candidates),
            "--bundle",
            str(default_bundle_path("recruitment-bc-v1")),
            "--max-cycle-years",
            "5",
            "--min-dbh",
            "1",
        ]
    )
    assert status == 0
    rows = pd.read_csv(tmp_path / "out" / "probe.csv")
    assert rows["cycles"].iloc[0] > 1


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
    """A BEC rate becomes one NATURAL line per species, in trees per hectare."""
    keyword = ingrowth_keyword(
        bec="IDFdk3", years=10.0, rates={"IDFdk3": {"FD": 56.6, "PL": 5.1}}, scale=1.0
    )
    assert keyword is not None
    assert keyword.name == "ESTAB"
    assert [line.name for line in keyword.nested] == ["NATURAL", "NATURAL"]
    assert keyword.nested[0].parameters == ("1", "FD", "566.0", "100.0")
    assert keyword.nested[1].parameters == ("1", "PL", "51.0", "100.0")


def test_ingrowth_keyword_returns_none_without_a_rate() -> None:
    """A BEC with no recruitment does not add an empty ESTAB block."""
    assert ingrowth_keyword(bec="IDFdk3", years=10.0, rates={}) is None


def test_split_cycles_keeps_each_cycle_within_the_ceiling() -> None:
    """A long interval becomes equal cycles no longer than the ceiling."""
    assert split_cycles(10.0, 20.0) == (1, 10.0)
    assert split_cycles(25.0, 20.0) == (2, 12.5)
    assert split_cycles(40.0, 20.0) == (2, 20.0)
    cycles, cycle_years = split_cycles(41.0, 20.0)
    assert cycles == 3
    assert cycle_years == pytest.approx(41.0 / 3)


@pytest.mark.parametrize(("years", "max_years"), [(0.0, 20.0), (-1.0, 20.0), (10.0, 0.0)])
def test_split_cycles_refuses_non_positive_input(years: float, max_years: float) -> None:
    """A zero or negative length is a caller error, not a one-cycle run."""
    with pytest.raises(ValueError, match="positive finite"):
        split_cycles(years, max_years)
