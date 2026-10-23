"""The `nemora` adapter.

``docs/reference/nemora-ingest.rst`` is the contract. It takes a synthetic stem population shaped
like `nemora`'s output and returns the tree-list fields that :mod:`fresh_fvsbc.treelist` writes.

Three things the adapter cannot take from the population
--------------------------------------------------------

`nemora` emits no species and no tree age, and FVS-BC needs both, so the caller supplies them. The
adapter fails when either is missing rather than choosing one, which is what the contract requires;
a defaulted species would quietly model the wrong tree.

The plot-level fields — slope, aspect, habitat, topographic position, and site preparation — are
properties of a run rather than of a stem population, so the contract takes them from the keyword
set. This adapter writes the values it is given for them, and zero when it is given none, because a
tree record has to carry something in those columns and the keyword set supplies the run's own.

The crown ratio is a conversion, not a copy
-------------------------------------------

The two sides are not the same shape. `nemora` emits a **fraction**, and the tree-list field is a
**crown class, 1 to 9**, which FVS expands to a percent crown ratio by ``n*10-5`` — see
:mod:`fresh_fvsbc.treelist` and the contract for the source. So class 7 means 65 percent.

The adapter takes the class whose expanded percentage is nearest the fraction's, and **refuses a
fraction it cannot represent**. FVS's own arithmetic sets the reachable band: class 9 reaches 85
percent and class 10 would be needed above it, which the field's single digit cannot hold. So a
fraction at or above 0.9 is refused rather than rounded down, because rounding it down would
silently understate a crown by up to five percent.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TypedDict

from fresh_fvsbc.treelist import TreeListFields, resolve_species

__all__ = [
    "CROWN_CLASS_MAX",
    "CROWN_CLASS_MIN",
    "CrownRatioError",
    "MissingAssignmentError",
    "PlotFields",
    "PopulationError",
    "crown_class",
    "crown_percent",
    "to_tree_list",
]

#: The reachable crown classes. FVS treats a value below 10 as a class and expands it by ``n*10-5``.
CROWN_CLASS_MIN: int = 1
CROWN_CLASS_MAX: int = 9


#: The tree-list fields a run's keyword set supplies, which the adapter passes through.
class PlotFields(TypedDict, total=False):
    """The plot-level fields, which belong to a run rather than to a stem population."""

    plot_slope: int
    plot_aspect: int
    plot_habitat: int
    plot_topo_pos: int
    plot_site_prep: int


#: The plot-level fields, with the value used when the caller supplies none.
_PLOT_FIELDS: tuple[str, ...] = (
    "plot_slope",
    "plot_aspect",
    "plot_habitat",
    "plot_topo_pos",
    "plot_site_prep",
)


class PopulationError(ValueError):
    """A population the adapter cannot turn into a tree list."""


class MissingAssignmentError(PopulationError):
    """An input the caller must supply, which `nemora` does not emit."""


class CrownRatioError(PopulationError):
    """A crown ratio that the one-digit tree-list field cannot carry."""


def crown_percent(crown_class_value: int) -> int:
    """Return the percent crown ratio FVS expands a class to.

    Parameters
    ----------
    crown_class_value : int
        A crown class, 1 to 9.

    Returns
    -------
    int
        ``n*10-5``, which is what ``base/intree.f`` computes for a value below 10.

    Raises
    ------
    CrownRatioError
        If the class is outside 1 to 9.
    """
    if not CROWN_CLASS_MIN <= crown_class_value <= CROWN_CLASS_MAX:
        raise CrownRatioError(
            f"{crown_class_value} is not a crown class; the field holds "
            f"{CROWN_CLASS_MIN} to {CROWN_CLASS_MAX}"
        )
    return crown_class_value * 10 - 5


def crown_class(crown_ratio: float) -> int:
    """Return the crown class nearest a fraction.

    Parameters
    ----------
    crown_ratio : float
        A crown ratio as a fraction, which is the shape `nemora` emits.

    Returns
    -------
    int
        The crown class whose expanded percentage is nearest, by
        :func:`crown_percent`.

    Raises
    ------
    CrownRatioError
        If the fraction is outside 0 to 1, or if the nearest class falls outside 1 to 9. The second
        is the case the contract calls a value the one-digit field cannot represent: a fraction at
        or above 0.9 would need class 10, and rounding it down would understate a crown by up to
        five percent, so it is refused rather than approximated.
    """
    if not 0.0 <= crown_ratio <= 1.0:
        raise CrownRatioError(f"{crown_ratio!r} is not a crown ratio; it is a fraction, 0 to 1")
    percent = crown_ratio * 100.0
    nearest = math.floor((percent + 5.0) / 10.0 + 0.5)
    if not CROWN_CLASS_MIN <= nearest <= CROWN_CLASS_MAX:
        raise CrownRatioError(
            f"a crown ratio of {crown_ratio!r} needs crown class {nearest}, and the field holds "
            f"{CROWN_CLASS_MIN} to {CROWN_CLASS_MAX}"
        )
    return nearest


def _text(record: Mapping[str, object], field: str) -> str:
    """Return a population field as text, refusing a record that does not carry it."""
    if field not in record:
        raise PopulationError(f"the population record has no {field!r}")
    return str(record[field])


def _number(record: Mapping[str, object], field: str) -> float:
    """Return a population field as a number, refusing a record that does not carry it."""
    if field not in record:
        raise PopulationError(f"the population record has no {field!r}")
    value = record[field]
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise PopulationError(f"the population field {field!r} is not a number: {value!r}")
    return float(value)


def to_tree_list(
    population: Sequence[Mapping[str, object]],
    *,
    species: str | None = None,
    tree_age: float | None = None,
    plot_fields: PlotFields | None = None,
) -> list[TreeListFields]:
    """Turn a synthetic stem population into tree-list fields.

    Parameters
    ----------
    population : Sequence of Mapping
        The stems, shaped like `nemora`'s output. Only `stand_id`, `dbh_cm`, `height_m`, and
        `crown_ratio` are read; the spatial fields have no home in an FVS tree list, and the
        attribute fields are not columns FVS-BC reads.
    species : str, optional
        The species code, from any of BC's three lists. Required: `nemora` emits none, and the
        adapter fails rather than defaulting.
    tree_age : float, optional
        The age at breast height, in years. Required, for the same reason.
    plot_fields : PlotFields, optional
        The plot-level fields, which belong to a run. Each defaults to zero.

    Returns
    -------
    list of TreeListFields
        One record per stem, ready for :func:`fresh_fvsbc.treelist.write_tree_record`.

    Raises
    ------
    MissingAssignmentError
        If ``species`` or ``tree_age`` is not supplied.
    PopulationError
        If a record is missing a field the adapter reads, or carries a non-numeric one.
    CrownRatioError
        If a crown ratio cannot be represented by the tree-list field.
    SpeciesError
        If the species code resolves to no BC species, or to more than one.
    """
    if species is None:
        raise MissingAssignmentError(
            "the adapter needs a species, because nemora emits none; pass one from BC's three lists"
        )
    if tree_age is None:
        raise MissingAssignmentError(
            "the adapter needs a tree age, because nemora emits none; pass one in years"
        )
    resolved = resolve_species(species)
    supplied = plot_fields or {}
    records: list[TreeListFields] = []
    plots: dict[str, int] = {}
    tree_numbers: dict[str, int] = {}
    for stem in population:
        stand = _text(stem, "stand_id")
        plot_id = plots.setdefault(stand, len(plots) + 1)
        tree_number = tree_numbers.get(stand, 0) + 1
        tree_numbers[stand] = tree_number
        record: TreeListFields = {
            "plot_id": plot_id,
            "tree_num": tree_number,
            "tree_count": 1.0,
            "tree_history": 0,
            "species": resolved,
            "diam": _number(stem, "dbh_cm"),
            "dg_incr": 0.0,
            "live_ht": _number(stem, "height_m"),
            "trunc_ht": 0.0,
            "htg_incr": 0.0,
            "crown_ratio": crown_class(_number(stem, "crown_ratio")),
            "damage1": 0,
            "severity1": 0,
            "damage2": 0,
            "severity2": 0,
            "damage3": 0,
            "severity3": 0,
            "tree_val": 0,
            "tree_rx": 0,
            "plot_slope": int(supplied.get("plot_slope", 0)),
            "plot_aspect": int(supplied.get("plot_aspect", 0)),
            "plot_habitat": int(supplied.get("plot_habitat", 0)),
            "plot_topo_pos": int(supplied.get("plot_topo_pos", 0)),
            "plot_site_prep": int(supplied.get("plot_site_prep", 0)),
            "tree_age": float(tree_age),
        }
        records.append(record)
    return records
