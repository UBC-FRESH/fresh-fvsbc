"""Tests for the ingrowth model and its FVS ESTAB rendering."""

from __future__ import annotations

import pandas as pd
import pytest

from fresh_fvsbc.bundle import load_bundle
from fresh_fvsbc.ingrowth import IngrowthError, IngrowthModel


def _model() -> IngrowthModel:
    return IngrowthModel.from_record(
        {
            "model_id": "test",
            "version": "0.1.0",
            "method": "test",
            "rates": [
                {"bec": "IDFdk3", "species": "FD", "rate": 56.6},
                {
                    "bec": "IDFdk3",
                    "species": "FD",
                    "rate": 10.0,
                    "ba_min": 30.0,
                    "ba_max": 999.0,
                    "qmd_min": 0.0,
                    "qmd_max": 999.0,
                },
            ],
        }
    )


def test_model_selects_the_density_row() -> None:
    """The matching BA range adds its rate to the full-range row."""
    model = _model()
    assert model.selected("IDFdk3", 20.0, 10.0) == {"FD": 56.6}
    assert model.selected("idfdk3", 40.0, 10.0) == {"FD": 66.6}
    assert model.selected("IDFdk1", 20.0, 10.0) == {}


def test_estab_keyword_renders_one_cycle() -> None:
    """The block carries the rate as trees per hectare for the selected interval."""
    keyword = _model().estab_keyword(bec="IDFdk3", years=10.0, ba=20.0, qmd=10.0)
    assert keyword is not None
    assert keyword.name == "ESTAB"
    assert keyword.nested[0].parameters == ("1", "FD", "566.0", "100.0")


def test_estab_keyword_uses_trees_per_hectare() -> None:
    """The BC metric reader expects TPH, not TPA."""
    keyword = _model().estab_keyword(bec="IDFdk3", years=10.0, ba=20.0, qmd=10.0)
    assert keyword is not None
    assert keyword.nested[0].parameters[2] == "566.0"


def test_estab_keyword_renders_periodic_cycles() -> None:
    """A two-cycle projection gets one NATURAL line per cycle."""
    keyword = _model().estab_keyword(bec="IDFdk3", years=20.0, ba=20.0, qmd=10.0, cycles=2)
    assert keyword is not None
    assert len(keyword.nested) == 2
    assert [line.parameters[0] for line in keyword.nested] == ["1", "2"]


def test_model_refuses_an_empty_range() -> None:
    """A range with min >= max is not a usable model."""
    with pytest.raises(IngrowthError, match="BA range"):
        IngrowthModel.from_record(
            {
                "model_id": "bad",
                "version": "0.1.0",
                "rates": [{"bec": "x", "species": "FD", "rate": 1.0, "ba_min": 10, "ba_max": 10}],
            }
        )


def test_the_idfdk_pilot_bundle_carries_ingrowth() -> None:
    """The shipped pilot loads and renders its ESTAB block."""
    bundle = load_bundle("notes/reference/calibration/d7-idfdk-bundle.json")
    assert bundle.ingrowth is not None
    assert bundle.ingrowth.model_id == "idfdk-ingrowth-2026-11-03"
    keyword = bundle.ingrowth_keyword(bec="IDFdk3", years=10.0, ba=24.7, qmd=9.0)
    assert keyword is not None
    assert keyword.name == "ESTAB"
    assert any("not signed off" in warning for warning in bundle.warnings)


def _recruitment_frames() -> tuple[pd.DataFrame, pd.DataFrame]:

    intervals = pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "visit0": 1,
                "visit1": 2,
                "PLOT": 1,
                "BEC": "IDFdk3",
                "TSA_DESC": "100 Mile House TSA",
                "years": 10.0,
                "interval_id": "1|1|2000|2010",
                "ba0": 20.0,
                "qmd": 10.0,
                "tph0": 500.0,
            }
        ]
    )
    trees = pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "VISIT_NUMBER": 1,
                "PLOT": 1,
                "TREE_NO": 1,
                "SPECIES": "FD",
                "LV_D": "L",
                "PHF_TREE": 100.0,
            },
            {
                "SITE_IDENTIFIER": 1,
                "VISIT_NUMBER": 2,
                "PLOT": 1,
                "TREE_NO": 1,
                "SPECIES": "FD",
                "LV_D": "L",
                "PHF_TREE": 100.0,
            },
            {
                "SITE_IDENTIFIER": 1,
                "VISIT_NUMBER": 2,
                "PLOT": 1,
                "TREE_NO": 2,
                "SPECIES": "FD",
                "LV_D": "L",
                "PHF_TREE": 50.0,
            },
        ]
    )
    return intervals, trees


def test_recruitment_table_counts_only_new_live_trees() -> None:
    """The old tree is not recruitment; the new tree is."""
    from fresh_fvsbc.ingrowth import recruitment_table

    intervals, trees = _recruitment_frames()
    table = recruitment_table(intervals, trees)
    assert len(table) == 1
    assert table.loc[0, "new_FD"] == 50.0
    assert table.loc[0, "new_total"] == 50.0


def test_fit_rates_and_bins_preserve_the_rate() -> None:
    """A 50 TPH new cohort over ten years is 5 TPH/year."""
    from fresh_fvsbc.ingrowth import fit_rates, recruitment_table

    intervals, trees = _recruitment_frames()
    table = recruitment_table(intervals, trees)
    constant = fit_rates(table)
    assert constant.selected("IDFdk3", 20.0, 10.0) == {"FD": 5.0}
    binned = fit_rates(table, ba_bins=(15.0, 25.0), qmd_bins=(6.0, 12.0))
    assert binned.selected("IDFdk3", 20.0, 10.0) == {"FD": 5.0}


def test_applies_handles_missing_stand_values() -> None:
    """A binned row does not apply when the caller cannot supply its range."""
    from fresh_fvsbc.ingrowth import IngrowthRate

    rate = IngrowthRate("IDFdk3", "FD", 2.0, ba_min=15.0, qmd_min=6.0)
    assert not rate.applies("IDFdk1", 20.0, 10.0)
    assert not rate.applies("IDFdk3", None, 10.0)
    assert not rate.applies("IDFdk3", 20.0, None)
    assert rate.applies("idfdk3", 20.0, 10.0)


def test_model_refuses_bad_records() -> None:
    """Malformed model records fail with a named error."""
    from fresh_fvsbc.ingrowth import IngrowthError, IngrowthModel

    for record in (
        {"version": "x", "rates": [{"bec": "x", "species": "FD", "rate": 1}]},
        {"model_id": "x", "rates": [{"bec": "x", "species": "FD", "rate": 1}]},
        {"model_id": "x", "version": "1", "rates": []},
        {"model_id": "x", "version": "1", "rates": [{"bec": "x", "species": "FD", "rate": -1}]},
        {
            "model_id": "x",
            "version": "1",
            "rates": [{"bec": "x", "species": "FD", "rate": 1, "qmd_min": 10, "qmd_max": 5}],
        },
        {
            "model_id": "x",
            "version": "1",
            "rates": [{"bec": "x", "species": "FD", "rate": 1}],
            "scale": -1,
        },
    ):
        with pytest.raises(IngrowthError):
            IngrowthModel.from_record(record)


def test_estab_skips_a_rate_that_rounds_to_zero() -> None:
    """A tiny rate cannot produce a zero-stems NATURAL line."""
    from fresh_fvsbc.ingrowth import IngrowthError, IngrowthModel

    model = IngrowthModel.from_record(
        {
            "model_id": "x",
            "version": "1",
            "rates": [{"bec": "IDFdk3", "species": "FD", "rate": 0.001}],
        }
    )
    assert model.estab_keyword(bec="IDFdk3", years=1.0) is None
    with pytest.raises(IngrowthError, match="cycles"):
        model.estab_keyword(bec="IDFdk3", years=1.0, cycles=0)


def test_fit_rates_can_use_a_median_and_cap_an_outlier() -> None:
    """A disturbance interval does not dominate a robust fit."""
    from fresh_fvsbc.ingrowth import fit_rates

    table = pd.DataFrame(
        {
            "BEC": ["IDFdk3", "IDFdk3"],
            "years": [10.0, 10.0],
            "ba0": [20.0, 20.0],
            "qmd": [10.0, 10.0],
            "new_FD": [100.0, 10.0],
            "new_PL": [0.0, 0.0],
            "new_SE": [0.0, 0.0],
            "new_HW": [0.0, 0.0],
        }
    )
    median = fit_rates(table, statistic="median")
    capped = fit_rates(table, statistic="median", max_rate=5.0)
    assert median.selected("IDFdk3", 20.0, 10.0) == {"FD": 5.5}
    assert capped.selected("IDFdk3", 20.0, 10.0) == {"FD": 3.0}


def test_fit_rates_refuses_an_unknown_statistic_or_bad_cap() -> None:
    """The robust-fit controls are validated before the groupby."""
    from fresh_fvsbc.ingrowth import fit_rates, recruitment_table

    intervals, trees = _recruitment_frames()
    table = recruitment_table(intervals, trees)
    with pytest.raises(ValueError, match="statistic"):
        fit_rates(table, statistic="mode")
    with pytest.raises(ValueError, match="max_rate"):
        fit_rates(table, max_rate=0.0)


def test_recruitment_and_fit_refuse_bad_inputs() -> None:
    """The builders name a missing column or an invalid bin order."""
    from fresh_fvsbc.ingrowth import fit_rates, recruitment_table

    intervals, trees = _recruitment_frames()
    with pytest.raises(ValueError, match="lacks"):
        recruitment_table(intervals.drop(columns="years"), trees)
    table = recruitment_table(intervals, trees)
    with pytest.raises(ValueError, match="lacks"):
        fit_rates(table.drop(columns="new_FD"))
    with pytest.raises(ValueError, match="increasing"):
        fit_rates(table, ba_bins=(25.0, 15.0))
    with pytest.raises(ValueError, match="increasing"):
        fit_rates(table, qmd_bins=(12.0, 6.0))


def test_rates_from_mean_round_trips() -> None:
    """The convenience constructor produces the same rates."""
    from fresh_fvsbc.ingrowth import rates_from_mean

    model = rates_from_mean(
        [{"bec": "IDFdk3", "species": "FD", "rate": 5.0}],
        scale=2.0,
    )
    assert model.selected("IDFdk3", 20.0, 10.0) == {"FD": 5.0}


def test_model_refuses_bad_text_and_shape_fields() -> None:
    """Text and container fields are checked before any rate is used."""
    from fresh_fvsbc.ingrowth import IngrowthError, IngrowthModel

    base = {"model_id": "x", "version": "1", "rates": [{"bec": "x", "species": "FD", "rate": 1}]}
    mutations: tuple[dict[str, object], ...] = (
        {"model_id": 1},
        {"version": ""},
        {"method": 1},
        {"rates": {}},
        {"rates": [1]},
        {"rates": [{"species": "FD", "rate": 1}]},
        {"rates": [{"bec": "x", "rate": 1}]},
        {"scale": "x"},
    )
    for mutation in mutations:
        record = {**base, **mutation}
        with pytest.raises(IngrowthError):
            IngrowthModel.from_record(record)


def test_a_full_range_rate_accepts_a_missing_stand_value() -> None:
    """The constant model does not require BA/QMD inputs."""
    from fresh_fvsbc.ingrowth import IngrowthRate

    assert IngrowthRate("IDFdk3", "FD", 1.0).applies("IDFdk3", None, None)


def test_recruitment_table_refuses_a_bad_interval_table() -> None:
    """The interval side gets the same named-column check as the tree side."""
    from fresh_fvsbc.ingrowth import recruitment_table

    intervals, trees = _recruitment_frames()
    with pytest.raises(ValueError, match="interval table lacks"):
        recruitment_table(intervals.drop(columns="BEC"), trees)


def test_fit_rates_refuses_an_all_zero_table() -> None:
    """A table with no positive recruitment has no model."""
    from fresh_fvsbc.ingrowth import fit_rates, recruitment_table

    intervals, trees = _recruitment_frames()
    table = recruitment_table(intervals, trees)
    for group in ("FD", "PL", "SE", "HW"):
        table[f"new_{group}"] = 0.0
    with pytest.raises(ValueError, match="no positive"):
        fit_rates(table)


def test_the_binned_bundle_selects_by_ba_and_qmd() -> None:
    """The binned pilot uses the BA/QMD class, not the constant row."""
    bundle = load_bundle("notes/reference/calibration/d7-idfdk-binned-bundle.json")
    assert bundle.ingrowth is not None
    low = bundle.ingrowth.selected("IDFdk3", 20.0, 10.0)
    high = bundle.ingrowth.selected("IDFdk3", 30.0, 15.0)
    assert low["FD"] > high["FD"]
