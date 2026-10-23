"""Synthetic stem populations shaped like ``nemora`` output.

``docs/reference/nemora-ingest.rst`` is the contract these records satisfy, and it is why the field
set below is asserted rather than assumed. The adapter is contracted against the fields that
``nemora`` emits, so the fixture has to carry exactly those and nothing invented.

The shape is read from ``nemora``'s own source rather than guessed. A stem record leaves
``place_trees_with_dbh`` carrying ``stand_id``, ``bootstrap_id``, ``sampler_type``, ``x``, ``y``,
and ``dbh``; ``attach_tree_attributes`` adds an ``attributes`` object and an
``attributes_provenance`` mapping; and ``tree_records_to_dataframe`` flattens the attributes into
the row. What this module builds is that flattened row, minus pandas, which is not a dependency of
this project.

Two fields in the contract's table are **absent on purpose**. ``species`` and ``tree_age`` are not
emitted by ``nemora`` and the adapter requires them from the caller, so a fixture that carried them
would let that requirement go untested.

The population is built at runtime and seeded, so a test can pin exact values and still be
reproducible. The derived attributes follow ``nemora``'s own placeholder configuration, read from
``nemora/synthesis/stems.py``, because a tree list is more plausible when height and biomass follow
from the diameter rather than being drawn independently of it.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Literal, TypedDict

__all__ = ["NEMORA_FIELDS", "StemRecord", "synthetic_population"]

#: The fields a flattened ``nemora`` stem record carries, transcribed from
#: ``docs/reference/nemora-ingest.rst``. A test compares the built records against this, so a field
#: added to one side and not the other fails rather than passing quietly.
NEMORA_FIELDS: tuple[str, ...] = (
    "stand_id",
    "bootstrap_id",
    "sampler_type",
    "x",
    "y",
    "dbh",
    "dbh_cm",
    "height_m",
    "crown_ratio",
    "basal_area_m2",
    "biomass_tonnes",
    "bark_thickness_cm",
    "attributes_provenance",
)


class StemRecord(TypedDict):
    """One flattened ``nemora`` stem record, as the adapter receives it."""

    stand_id: str
    bootstrap_id: int
    sampler_type: Literal["bootstrap", "analytic"]
    x: float
    y: float
    dbh: float
    dbh_cm: float
    height_m: float
    crown_ratio: float
    basal_area_m2: float
    biomass_tonnes: float
    bark_thickness_cm: float
    attributes_provenance: dict[str, object]


# nemora's TreeAttributeConfig defaults, from nemora/synthesis/stems.py.
_HEIGHT_A: float = 1.3
_HEIGHT_B: float = 0.45
_BIOMASS_A: float = 0.05
_BIOMASS_B: float = 2.35
_BARK_A: float = 0.03
_BARK_B: float = 1.05
_CROWN_RATIO: float = 0.45
_PROVENANCE: str = "placeholder-v1"

#: The diameter range the draws are taken from, in centimetres. Wide enough that no two stems in a
#: small population share a diameter.
MIN_DBH_CM: float = 5.0
MAX_DBH_CM: float = 60.0

#: The side of the square the stems are placed in, in metres. FVS is distance-independent, so
#: placement only survives as an input to plot assignment.
PLOT_SIDE_M: float = 100.0


def _basal_area_m2(dbh_cm: float) -> float:
    """Return the basal area of one stem, in square metres, from its diameter in centimetres.

    Parameters
    ----------
    dbh_cm : float
        Diameter at breast height, in centimetres.

    Returns
    -------
    float
        The area of the stem's circle, in square metres.
    """
    radius_m = (dbh_cm / 100.0) / 2.0
    return math.pi * radius_m * radius_m


def synthetic_population(
    *,
    stands: Sequence[str] = ("S1", "S2"),
    trees_per_stand: int = 4,
    seed: int = 20261023,
) -> list[StemRecord]:
    """Build a synthetic stem population shaped like ``nemora`` output.

    Parameters
    ----------
    stands : Sequence[str], optional
        The stand identifiers, in the order they should first appear. The adapter assigns one plot
        per stand in that order, so the order is part of what the fixture fixes.
    trees_per_stand : int, optional
        The number of stems to place in each stand.
    seed : int, optional
        The seed for the diameter and placement draws. The same seed gives the same population.

    Returns
    -------
    list of StemRecord
        One record per stem, each carrying exactly the fields in ``NEMORA_FIELDS``.

    Raises
    ------
    ValueError
        If ``trees_per_stand`` is negative.
    """
    if trees_per_stand < 0:
        raise ValueError("trees_per_stand must not be negative")
    rng = random.Random(seed)
    records: list[StemRecord] = []
    for stand_id in stands:
        for tree_index in range(trees_per_stand):
            dbh_cm = rng.uniform(MIN_DBH_CM, MAX_DBH_CM)
            records.append(
                {
                    "stand_id": stand_id,
                    "bootstrap_id": tree_index,
                    "sampler_type": "bootstrap",
                    "x": rng.uniform(0.0, PLOT_SIDE_M),
                    "y": rng.uniform(0.0, PLOT_SIDE_M),
                    "dbh": dbh_cm,
                    "dbh_cm": dbh_cm,
                    "height_m": _HEIGHT_A * dbh_cm**_HEIGHT_B,
                    "crown_ratio": _CROWN_RATIO,
                    "basal_area_m2": _basal_area_m2(dbh_cm),
                    "biomass_tonnes": _BIOMASS_A * dbh_cm**_BIOMASS_B,
                    "bark_thickness_cm": _BARK_A * dbh_cm**_BARK_B,
                    "attributes_provenance": {
                        "height_a": _HEIGHT_A,
                        "height_b": _HEIGHT_B,
                        "biomass_a": _BIOMASS_A,
                        "biomass_b": _BIOMASS_B,
                        "bark_thickness_a": _BARK_A,
                        "bark_thickness_b": _BARK_B,
                        "crown_ratio": _CROWN_RATIO,
                        "provenance": _PROVENANCE,
                    },
                }
            )
    return records
