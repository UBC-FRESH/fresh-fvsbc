"""The recruitment v1 bundle: rates, scale, and the multi-cycle block."""

from __future__ import annotations

from pathlib import Path

import pytest

from fresh_fvsbc.bundle import load_bundle

_BUNDLE = (
    Path(__file__).resolve().parents[1]
    / "notes/reference/calibration/recruitment-bc-v1-bundle.json"
)


@pytest.fixture(scope="module")
def bundle() -> object:
    """Load the shipped bundle once."""
    return load_bundle(_BUNDLE)


def test_bundle_carries_rates_and_the_calibration_scale(bundle: object) -> None:
    """The bundle is a recruitment model, not an empty provenance record."""
    from fresh_fvsbc.bundle import CalibrationBundle

    assert isinstance(bundle, CalibrationBundle)
    assert bundle.ingrowth is not None
    assert bundle.ingrowth.scale == pytest.approx(0.4)
    assert len(bundle.ingrowth.rates) > 2000
    assert "BWBS" in bundle.domain.becs
    assert "CMA" not in bundle.domain.becs


def test_bwbs_rates_are_species_resolved(bundle: object) -> None:
    """A BWBS cell returns more than the four calibration groups."""
    from fresh_fvsbc.bundle import CalibrationBundle

    assert isinstance(bundle, CalibrationBundle)
    assert bundle.ingrowth is not None
    selected = bundle.ingrowth.selected("BWBSmw", 30.0, 10.0)
    assert {"AT", "PL", "SE"} <= set(selected)
    assert all(rate >= 0 for rate in selected.values())


def test_multi_cycle_block_skips_the_inventory_year(bundle: object) -> None:
    """No NATURAL line lands on cycle 1, and the total TPH is preserved."""
    from fresh_fvsbc.bundle import CalibrationBundle

    assert isinstance(bundle, CalibrationBundle)
    model = bundle.ingrowth
    assert model is not None
    keyword = model.estab_keyword(bec="BWBSmw", years=9.0, ba=30.0, qmd=10.0, cycles=3)
    assert keyword is not None
    dates = {line.parameters[0] for line in keyword.nested}
    assert dates == {"2", "3"}
    total = sum(float(line.parameters[2]) for line in keyword.nested)
    expected = sum(model.selected("BWBSmw", 30.0, 10.0).values()) * model.scale * 9.0
    assert total == pytest.approx(expected, rel=0.01)


def test_single_cycle_still_establishes_at_cycle_one(bundle: object) -> None:
    """The single-cycle path keeps its old behaviour, which is documented as not recommended."""
    from fresh_fvsbc.bundle import CalibrationBundle

    assert isinstance(bundle, CalibrationBundle)
    assert bundle.ingrowth is not None
    keyword = bundle.ingrowth.estab_keyword(bec="BWBSmw", years=9.0, ba=30.0, qmd=10.0)
    assert keyword is not None
    assert {line.parameters[0] for line in keyword.nested} == {"1"}
