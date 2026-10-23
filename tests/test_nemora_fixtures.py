"""Tests for the synthetic `nemora`-shaped fixture.

They test the fixture rather than the package, which sounds circular and is not. The fixture is the
input every later adapter test trusts, so if it drifts from the contract's field set, or stops
drawing from its seed, the tests that consume it become quietly worthless.
"""

from __future__ import annotations

import math

import pytest

from nemora_fixtures import NEMORA_FIELDS, PLOT_SIDE_M, StemRecord, synthetic_population

# The two fields the contract marks as required from the caller, and that `nemora` does not emit.
REQUIRED_FROM_CALLER: tuple[str, ...] = ("species", "tree_age")


def test_records_carry_exactly_the_contract_fields() -> None:
    """Every record carries the fields ``nemora-ingest.rst`` lists, and no others."""
    records = synthetic_population()
    assert records
    for record in records:
        assert set(record) == set(NEMORA_FIELDS)


def test_the_field_list_matches_the_record_type() -> None:
    """The transcribed field list matches the record type, so neither drifts unnoticed."""
    assert tuple(StemRecord.__annotations__) == NEMORA_FIELDS


def test_the_field_list_has_no_duplicates() -> None:
    """A duplicated name would shrink the field check above without failing it."""
    assert len(set(NEMORA_FIELDS)) == len(NEMORA_FIELDS)


def test_species_and_tree_age_are_absent() -> None:
    """`nemora` emits neither, so the adapter's requirement for them stays testable."""
    for record in synthetic_population():
        for field in REQUIRED_FROM_CALLER:
            assert field not in record


def test_population_is_reproducible_for_a_seed() -> None:
    """The same seed gives the same population, so a test can pin exact values."""
    assert synthetic_population(seed=7) == synthetic_population(seed=7)


def test_the_seed_changes_the_draws() -> None:
    """A different seed gives a different population, so the seed is not decorative."""
    assert synthetic_population(seed=7) != synthetic_population(seed=8)


def test_every_stem_has_a_distinct_diameter() -> None:
    """No two stems share a diameter, so a test needing distinct trees can rely on the fixture."""
    dbhs = [record["dbh"] for record in synthetic_population()]
    assert len(set(dbhs)) == len(dbhs)


def test_stands_appear_in_first_appearance_order() -> None:
    """Plots are assigned in order of first appearance, so the fixture fixes that order."""
    records = synthetic_population(stands=("B", "A"), trees_per_stand=3)
    assert list(dict.fromkeys(record["stand_id"] for record in records)) == ["B", "A"]


def test_the_builder_honours_its_counts() -> None:
    """The stand list and the per-stand count both reach the population."""
    records = synthetic_population(stands=("X", "Y", "Z"), trees_per_stand=2)
    assert [record["stand_id"] for record in records] == ["X", "X", "Y", "Y", "Z", "Z"]


def test_values_are_physically_plausible() -> None:
    """Every derived attribute is positive, and the crown ratio is a fraction."""
    for record in synthetic_population():
        assert record["dbh_cm"] > 0
        assert record["height_m"] > 0
        assert record["basal_area_m2"] > 0
        assert record["biomass_tonnes"] > 0
        assert record["bark_thickness_cm"] > 0
        assert 0.0 <= record["crown_ratio"] <= 1.0


def test_height_follows_the_diameter() -> None:
    """A taller stem has the greater diameter, since height is derived rather than drawn."""
    records = synthetic_population(trees_per_stand=8)
    by_dbh = sorted(records, key=lambda record: record["dbh_cm"])
    heights = [record["height_m"] for record in by_dbh]
    assert heights == sorted(heights)


def test_basal_area_matches_its_diameter() -> None:
    """Basal area is the stem's circle, so a wrong conversion or unit is caught."""
    for record in synthetic_population():
        radius_m = record["dbh_cm"] / 200.0
        assert record["basal_area_m2"] == pytest.approx(math.pi * radius_m**2)


def test_placement_stays_inside_the_plot() -> None:
    """Every stem is placed inside the square, so plot assignment has something to work with."""
    for record in synthetic_population():
        assert 0.0 <= record["x"] <= PLOT_SIDE_M
        assert 0.0 <= record["y"] <= PLOT_SIDE_M


def test_a_negative_count_is_rejected() -> None:
    """A negative count is a caller error, not an empty stand."""
    with pytest.raises(ValueError, match="must not be negative"):
        synthetic_population(trees_per_stand=-1)


def test_an_empty_population_is_allowed() -> None:
    """Zero stems is a legitimate answer, so it returns an empty list rather than raising."""
    assert synthetic_population(trees_per_stand=0) == []
