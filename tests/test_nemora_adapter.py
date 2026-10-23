"""Tests for the `nemora` adapter.

The population comes from the fixture, which is shaped like `nemora`'s own output. The adapter must
never import `nemora`, and one test here holds it to that.
"""

from __future__ import annotations

import sys

import pytest

from fresh_fvsbc.nemora import (
    CROWN_CLASS_MAX,
    CROWN_CLASS_MIN,
    CrownRatioError,
    MissingAssignmentError,
    PopulationError,
    crown_class,
    crown_percent,
    to_tree_list,
)
from fresh_fvsbc.treelist import (
    RECORD_WIDTH,
    TreeListFields,
    UnknownSpeciesError,
    write_tree_list,
)
from nemora_fixtures import synthetic_population


def adapted(**overrides: object) -> list[TreeListFields]:
    """Return the fixture's population, adapted, with ``overrides`` applied to the call."""
    arguments: dict[str, object] = {"species": "PIMO3", "tree_age": 60.0}
    arguments.update(overrides)
    # The keyword arguments are checked by the tests that pass them.
    return list(to_tree_list(synthetic_population(), **arguments))  # type: ignore[arg-type]


def test_the_population_becomes_one_record_per_stem() -> None:
    """A population of eight stems is eight records, and no coalescing happens."""
    assert len(adapted()) == 8


def test_plots_are_assigned_in_order_of_first_appearance() -> None:
    """The contract assigns one plot per stand, in the order the stands appear."""
    records = list(
        to_tree_list(
            synthetic_population(stands=("B", "A"), trees_per_stand=2), species="FD", tree_age=60.0
        )
    )
    assert [(record["plot_id"], record["tree_num"]) for record in records] == [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
    ]


def test_tree_numbers_are_sequential_within_a_plot() -> None:
    """The contract numbers trees from one, within each plot."""
    records = adapted()
    seen: dict[int, list[int]] = {}
    for record in records:
        seen.setdefault(int(record["plot_id"]), []).append(int(record["tree_num"]))
    assert list(seen.values()) == [[1, 2, 3, 4], [1, 2, 3, 4]]


def test_the_diameter_and_the_height_are_copied_unchanged() -> None:
    """Both are centimetres or metres on both sides, so neither is converted."""
    records = adapted()
    stems = synthetic_population()
    assert [record["diam"] for record in records] == [stem["dbh_cm"] for stem in stems]
    assert [record["live_ht"] for record in records] == [stem["height_m"] for stem in stems]


def test_the_derived_columns_are_the_ones_the_contract_names() -> None:
    """Everything FVS computes, or that `nemora` does not carry, is written as a fixed value."""
    for record in adapted():
        assert record["tree_count"] == 1.0
        assert record["tree_history"] == 0
        assert record["dg_incr"] == 0.0
        assert record["htg_incr"] == 0.0
        assert record["trunc_ht"] == 0.0
        assert record["tree_val"] == 0
        assert record["tree_rx"] == 0
        assert (record["damage1"], record["damage2"], record["damage3"]) == (0, 0, 0)
        assert (record["severity1"], record["severity2"], record["severity3"]) == (0, 0, 0)


def test_the_crown_ratio_becomes_a_class_the_field_can_hold() -> None:
    """`nemora` emits a fraction and the field is a class, so this is a conversion."""
    for record in adapted():
        assert CROWN_CLASS_MIN <= int(record["crown_ratio"]) <= CROWN_CLASS_MAX


def test_the_crown_class_round_trips_through_fvs_arithmetic() -> None:
    """A class expands by ``n*10-5``, and the class chosen is the nearest to the fraction."""
    assert crown_percent(crown_class(0.45)) == 45
    assert crown_percent(crown_class(0.44)) == 45
    assert crown_percent(crown_class(0.85)) == 85
    assert crown_percent(crown_class(0.0)) == 5


def test_every_representable_fraction_lands_within_five_percent() -> None:
    """Nearest-class means nearest: no representable crown may be understated by more than five."""
    for step in range(0, 86):
        fraction = step / 100.0
        assert abs(crown_percent(crown_class(fraction)) - fraction * 100.0) <= 5.0


def test_a_crown_ratio_the_field_cannot_hold_is_refused() -> None:
    """Class 10 would be needed above 85 percent, and the field's single digit cannot hold it."""
    for fraction in (0.9, 0.95, 1.0):
        with pytest.raises(CrownRatioError, match="needs crown class"):
            crown_class(fraction)


def test_a_fraction_outside_zero_and_one_is_refused() -> None:
    """A percentage is not a fraction, and the adapter says so rather than dividing it."""
    for fraction in (1.5, -0.1, 45.0):
        with pytest.raises(CrownRatioError, match="it is a fraction, 0 to 1"):
            crown_class(fraction)


def test_expanding_a_class_outside_the_field_is_refused() -> None:
    """The inverse refuses what the field cannot carry, at both ends."""
    for value in (0, CROWN_CLASS_MAX + 1):
        with pytest.raises(CrownRatioError, match="is not a crown class"):
            crown_percent(value)


def test_the_species_is_required_and_is_not_defaulted() -> None:
    """`nemora` emits no species, so the adapter fails rather than choosing one."""
    with pytest.raises(MissingAssignmentError, match="needs a species"):
        to_tree_list(synthetic_population(), tree_age=60.0)


def test_the_tree_age_is_required_and_is_not_defaulted() -> None:
    """`nemora` emits no age either."""
    with pytest.raises(MissingAssignmentError, match="needs a tree age"):
        to_tree_list(synthetic_population(), species="FD")


def test_the_supplied_species_is_resolved_before_it_is_written() -> None:
    """A PLANTS symbol reaches the record as the BC code."""
    assert {record["species"] for record in adapted(species="PIMO3")} == {"PW"}
    assert {record["species"] for record in adapted(species="119")} == {"PW"}


def test_an_unknown_species_is_refused() -> None:
    """A code in none of BC's lists cannot be adapted into a run."""
    with pytest.raises(UnknownSpeciesError):
        adapted(species="ZZ")


def test_the_plot_fields_default_to_zero_and_can_be_supplied() -> None:
    """They belong to a run rather than to a population, so they are passed through, not derived."""
    defaulted = adapted()[0]
    assert [defaulted[field] for field in ("plot_slope", "plot_aspect", "plot_habitat")] == [
        0,
        0,
        0,
    ]
    supplied = adapted(plot_fields={"plot_slope": 3, "plot_aspect": 180})[0]
    assert supplied["plot_slope"] == 3
    assert supplied["plot_aspect"] == 180
    assert supplied["plot_habitat"] == 0


def test_a_record_missing_a_field_the_adapter_reads_is_refused() -> None:
    """A population that is not shaped like `nemora`'s output is refused by name."""
    stems = [dict(stem) for stem in synthetic_population()]
    del stems[0]["dbh_cm"]
    with pytest.raises(PopulationError, match="has no 'dbh_cm'"):
        to_tree_list(stems, species="FD", tree_age=60.0)


def test_the_adapter_never_imports_nemora() -> None:
    """The contract keeps the dependency out of the suite, and this is what holds it out."""
    adapted()
    assert "nemora" not in sys.modules


def test_the_adapted_records_are_what_the_writer_writes() -> None:
    """The two modules compose: every record writes to a full-width line."""
    text = write_tree_list(adapted())
    lines = text.splitlines()
    assert len(lines) == 8
    assert all(len(line) == RECORD_WIDTH for line in lines)


def test_the_same_population_adapts_the_same_way_twice() -> None:
    """The adapter adds no nondeterminism of its own."""
    assert adapted() == adapted()
