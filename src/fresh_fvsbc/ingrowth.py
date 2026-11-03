"""Public-data recruitment rendered as FVS natural regeneration.

The model is a list of annual recruitment rates, in trees per hectare per year,
for a BEC and species group. A row may also carry an initial-BA and initial-QMD
range; that is how the density/age refinement is expressed without a new model
class. The rows are data, not code, and the bundle can carry them.

FVS reads natural regeneration through an ``ESTAB`` block and a ``NATURAL``
line. The line's stems field is trees per acre, so the rate is multiplied by the
interval length and by 0.404686. ``NATURAL`` also implies ``NOINGROW`` and
``NOAUTALY``; it replaces the automatic establishment for that stand, which is
the intended behaviour here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

import pandas as pd

from fresh_fvsbc.keywords import Keyword

__all__ = ["IngrowthModel", "IngrowthRate"]

#: 1 tree per hectare is this many trees per acre.
TPH_TO_TPA: float = 0.404686


class IngrowthError(ValueError):
    """An ingrowth model that cannot be loaded or applied."""


@dataclass(frozen=True, slots=True)
class IngrowthRate:
    """One annual recruitment rate and its applicable stand range.

    Parameters
    ----------
    bec : str
        The BEC label the rate applies to, such as ``IDFdk3``.
    species : str
        The FVS species code, such as ``FD``.
    rate : float
        New trees per hectare per year.
    ba_min : float, optional
        Minimum initial basal area, in m2/ha.
    ba_max : float, optional
        Maximum initial basal area, in m2/ha.
    qmd_min : float, optional
        Minimum initial QMD, in cm.
    qmd_max : float, optional
        Maximum initial QMD, in cm.
    """

    bec: str
    species: str
    rate: float
    ba_min: float = 0.0
    ba_max: float = 999.0
    qmd_min: float = 0.0
    qmd_max: float = 999.0

    def __post_init__(self) -> None:
        """Normalize the text fields so direct construction matches the loader."""
        object.__setattr__(self, "bec", self.bec.strip().upper())
        object.__setattr__(self, "species", self.species.strip().upper())

    def applies(self, bec: str, ba: float | None, qmd: float | None) -> bool:
        """Return whether this rate applies to a stand.

        Parameters
        ----------
        bec : str
            The stand's BEC label.
        ba : float or None
            The stand's initial BA, in m2/ha.
        qmd : float or None
            The stand's initial QMD, in cm.

        Returns
        -------
        bool
            True when the BEC and both ranges match.
        """
        if bec.strip().upper() != self.bec:
            return False
        if ba is not None and not (self.ba_min <= ba <= self.ba_max):
            return False
        if qmd is not None and not (self.qmd_min <= qmd <= self.qmd_max):
            return False
        if ba is None and (self.ba_min > 0 or self.ba_max < 999):
            return False
        return not (qmd is None and (self.qmd_min > 0 or self.qmd_max < 999))


@dataclass(frozen=True, slots=True)
class IngrowthModel:
    """A validated set of recruitment rates.

    Parameters
    ----------
    model_id : str
        The stable identifier.
    version : str
        The semantic version.
    method : str
        The method note, such as ``bec-species mean annual TPH``.
    rates : tuple of IngrowthRate
        The rows.
    scale : float, optional
        A multiplier on every rate, for sensitivity. Defaults to 1.
    """

    model_id: str
    version: str
    method: str
    rates: tuple[IngrowthRate, ...]
    scale: float = 1.0

    @classmethod
    def from_record(cls, record: Mapping[str, object]) -> IngrowthModel:
        """Validate one decoded ingrowth record.

        Parameters
        ----------
        record : Mapping
            The decoded model.

        Returns
        -------
        IngrowthModel
            The validated model.

        Raises
        ------
        IngrowthError
            If a required field is missing or a range is invalid.
        """
        model_id = record.get("model_id")
        version = record.get("version")
        method = record.get("method", "")
        if not isinstance(model_id, str) or not model_id.strip():
            raise IngrowthError("ingrowth.model_id must be a non-empty string")
        if not isinstance(version, str) or not version.strip():
            raise IngrowthError("ingrowth.version must be a non-empty string")
        if not isinstance(method, str):
            raise IngrowthError("ingrowth.method must be a string")
        rates_raw = record.get("rates")
        if not isinstance(rates_raw, list) or not rates_raw:
            raise IngrowthError("ingrowth.rates must be a non-empty list")
        rates: list[IngrowthRate] = []
        for raw in rates_raw:
            if not isinstance(raw, Mapping):
                raise IngrowthError("every ingrowth rate must be an object")
            bec = raw.get("bec")
            species = raw.get("species")
            rate = raw.get("rate")
            if not isinstance(bec, str) or not bec.strip():
                raise IngrowthError("ingrowth rate bec must be a non-empty string")
            if not isinstance(species, str) or not species.strip():
                raise IngrowthError("ingrowth rate species must be a non-empty string")
            if not isinstance(rate, (int, float)) or float(rate) < 0:
                raise IngrowthError(
                    f"ingrowth rate for {bec}/{species} must be a non-negative number"
                )
            values = {
                key: float(cast(float, raw.get(key, default)))
                for key, default in (
                    ("ba_min", 0.0),
                    ("ba_max", 999.0),
                    ("qmd_min", 0.0),
                    ("qmd_max", 999.0),
                )
            }
            if values["ba_min"] >= values["ba_max"]:
                raise IngrowthError(f"ingrowth BA range for {bec}/{species} is empty")
            if values["qmd_min"] >= values["qmd_max"]:
                raise IngrowthError(f"ingrowth QMD range for {bec}/{species} is empty")
            rates.append(
                IngrowthRate(
                    bec=bec.strip().upper(),
                    species=species.strip().upper(),
                    rate=float(rate),
                    **values,
                )
            )
        scale_value = record.get("scale", 1.0)
        if not isinstance(scale_value, (int, float)) or float(scale_value) < 0:
            raise IngrowthError("ingrowth.scale must be a non-negative number")
        return cls(
            model_id=model_id.strip(),
            version=version.strip(),
            method=method,
            rates=tuple(rates),
            scale=float(scale_value),
        )

    def selected(self, bec: str, ba: float | None, qmd: float | None) -> dict[str, float]:
        """Return the summed rate by species for a stand.

        Parameters
        ----------
        bec : str
            The stand's BEC label.
        ba : float or None
            The stand's initial BA, in m2/ha.
        qmd : float or None
            The stand's initial QMD, in cm.

        Returns
        -------
        dict
            Species code to annual trees per hectare per year.
        """
        selected: dict[str, float] = {}
        for row in self.rates:
            if row.applies(bec, ba, qmd):
                selected[row.species] = selected.get(row.species, 0.0) + row.rate
        return {species: rate for species, rate in selected.items() if rate > 0}

    def estab_keyword(
        self,
        *,
        bec: str,
        years: float,
        ba: float | None = None,
        qmd: float | None = None,
        cycles: int = 1,
        cycle_years: float | None = None,
        cycle: int = 1,
    ) -> Keyword | None:
        """Build the ``ESTAB`` block for a stand.

        Parameters
        ----------
        bec : str
            The stand's BEC label.
        years : float
            The total interval length, in years.
        ba : float or None, optional
            The stand's initial BA, in m2/ha.
        qmd : float or None, optional
            The stand's initial QMD, in cm.
        cycles : int, optional
            The number of establishment cycles. Defaults to one.
        cycle_years : float or None, optional
            The length of each cycle. Defaults to ``years / cycles``.
        cycle : int, optional
            The first cycle number. Defaults to one.

        Returns
        -------
        Keyword or None
            An ``ESTAB`` block, or ``None`` when nothing applies.

        Raises
        ------
        IngrowthError
            If the cycle settings are invalid.
        """
        if years < 0:
            raise IngrowthError("years must not be negative")
        if cycles < 1:
            raise IngrowthError("cycles must be at least one")
        length = years / cycles if cycle_years is None else cycle_years
        if length < 0:
            raise IngrowthError("cycle_years must not be negative")
        selected = self.selected(bec, ba, qmd)
        if not selected:
            return None
        lines: list[Keyword] = []
        for offset in range(cycles):
            cycle_number = cycle + offset
            for species, rate in selected.items():
                tph = rate * length * self.scale
                tpa = tph * TPH_TO_TPA
                if tpa < 0.05:
                    continue
                lines.append(
                    Keyword("NATURAL", (str(cycle_number), species, f"{tpa:.1f}", "100.0"))
                )
        if not lines:
            return None
        return Keyword("ESTAB", nested=tuple(lines))


def rates_from_mean(
    rows: Sequence[Mapping[str, object]],
    *,
    scale: float = 1.0,
) -> IngrowthModel:
    """Build a constant-rate model from already aggregated rows.

    Parameters
    ----------
    rows : sequence of Mapping
        Rows with ``bec``, ``species``, and ``rate``.
    scale : float, optional
        A multiplier on every rate.

    Returns
    -------
    IngrowthModel
        A model with a full BA/QMD range for every row.
    """
    return IngrowthModel.from_record(
        {
            "model_id": "derived",
            "version": "0.0.0",
            "method": "aggregated mean annual TPH",
            "scale": scale,
            "rates": [
                {
                    "bec": str(row["bec"]),
                    "species": str(row["species"]),
                    "rate": float(cast(float, row["rate"])),
                }
                for row in rows
            ],
        }
    )


def recruitment_table(
    intervals: pd.DataFrame,
    trees: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per interval with new-tree TPH by calibration group.

    Parameters
    ----------
    intervals : pandas.DataFrame
        The interval table with ``SITE_IDENTIFIER``, ``visit0``, ``visit1``,
        ``PLOT``, ``BEC``, ``TSA_DESC``, ``years``, and ``interval_id``.
    trees : pandas.DataFrame
        The raw tree rows with ``SITE_IDENTIFIER``, ``VISIT_NUMBER``, ``PLOT``,
        ``TREE_NO``, ``SPECIES``, ``LV_D``, and ``PHF_TREE``.

    Returns
    -------
    pandas.DataFrame
        ``new_total`` and ``new_FD``/``new_PL``/``new_SE``/``new_HW``/``new_other``
        in trees per hectare, plus the interval's stand variables.

    Raises
    ------
    ValueError
        If a required column is missing.
    """
    from fresh_fvsbc.calibration import SPECIES_GROUPS
    from fresh_fvsbc.treelist import DONOR_SPECIES

    tree_columns = {
        "SITE_IDENTIFIER",
        "VISIT_NUMBER",
        "PLOT",
        "TREE_NO",
        "SPECIES",
        "LV_D",
        "PHF_TREE",
    }
    interval_columns = {
        "SITE_IDENTIFIER",
        "visit0",
        "visit1",
        "PLOT",
        "BEC",
        "TSA_DESC",
        "years",
        "interval_id",
    }
    missing_trees = tree_columns - set(trees.columns)
    missing_intervals = interval_columns - set(intervals.columns)
    if missing_trees:
        raise ValueError(f"the tree table lacks {', '.join(sorted(missing_trees))}")
    if missing_intervals:
        raise ValueError(f"the interval table lacks {', '.join(sorted(missing_intervals))}")
    live = trees[(trees["LV_D"] == "L") & (trees["PHF_TREE"] > 0)]
    groups: dict[tuple[object, object, object], pd.DataFrame] = {}
    for key, frame in live.groupby(["SITE_IDENTIFIER", "VISIT_NUMBER", "PLOT"], sort=False):
        groups[cast(tuple[object, object, object], tuple(key))] = frame
    rows: list[dict[str, object]] = []
    for interval in intervals.itertuples(index=False):
        start = groups.get((interval.SITE_IDENTIFIER, interval.visit0, interval.PLOT))
        end = groups.get((interval.SITE_IDENTIFIER, interval.visit1, interval.PLOT))
        if start is None or end is None:
            continue
        old = set(start["TREE_NO"])
        new = end[~end["TREE_NO"].isin(old)]
        by_group: dict[str, float] = {}
        for species, value in new.groupby("SPECIES")["PHF_TREE"].sum().items():
            code = DONOR_SPECIES.get(str(species).upper(), str(species).upper())
            species_group = SPECIES_GROUPS.get(code, "UNKNOWN")
            by_group[species_group] = by_group.get(species_group, 0.0) + float(value)
        rows.append(
            {
                "BEC": interval.BEC,
                "TSA_DESC": interval.TSA_DESC,
                "interval_id": interval.interval_id,
                "year0": int(getattr(interval, "year0", 0)),
                "year1": int(getattr(interval, "year1", 0)),
                "years": float(cast(float, interval.years)),
                "ba0": float(cast(float, getattr(interval, "ba0", 0.0))),
                "qmd": float(cast(float, getattr(interval, "qmd", 0.0))),
                "tph0": float(cast(float, getattr(interval, "tph0", 0.0))),
                "new_total": sum(by_group.values()),
                "new_FD": by_group.get("FD", 0.0),
                "new_PL": by_group.get("PL", 0.0),
                "new_SE": by_group.get("SE", 0.0),
                "new_HW": by_group.get("HW", 0.0),
                "new_other": sum(
                    v for k, v in by_group.items() if k not in {"FD", "PL", "SE", "HW"}
                ),
            }
        )
    return pd.DataFrame(rows)


def fit_rates(
    table: pd.DataFrame,
    *,
    model_id: str = "derived",
    version: str = "0.0.0",
    ba_bins: Sequence[float] = (),
    qmd_bins: Sequence[float] = (),
) -> IngrowthModel:
    """Fit mean annual recruitment by BEC, species group, and optional bins.

    Parameters
    ----------
    table : pandas.DataFrame
        A recruitment table from :func:`recruitment_table`.
    model_id : str, optional
        The model identifier.
    version : str, optional
        The model version.
    ba_bins : sequence of float, optional
        Initial-BA boundaries in m2/ha, low to high. A single group is used when
        absent.
    qmd_bins : sequence of float, optional
        Initial-QMD boundaries in cm, low to high.

    Returns
    -------
    IngrowthModel
        The fitted rows.

    Raises
    ------
    ValueError
        If a rate column is missing or a bin list is not increasing.
    """
    required = {"BEC", "years", "new_FD", "new_PL", "new_SE", "new_HW", "ba0", "qmd"}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"the recruitment table lacks {', '.join(sorted(missing))}")
    if len(set(ba_bins)) != len(ba_bins) or list(ba_bins) != sorted(ba_bins):
        raise ValueError("ba_bins must be strictly increasing")
    if len(set(qmd_bins)) != len(qmd_bins) or list(qmd_bins) != sorted(qmd_bins):
        raise ValueError("qmd_bins must be strictly increasing")
    frame: pd.DataFrame = table.copy()
    groups = ("FD", "PL", "SE", "HW")
    for group in groups:
        frame[f"rate_{group}"] = frame[f"new_{group}"] / frame["years"].where(frame["years"] > 0)
    if ba_bins:
        frame["ba_bin"] = pd.cut(frame["ba0"], bins=[*ba_bins, 999.0], right=False, labels=False)
    else:
        frame["ba_bin"] = 0
    if qmd_bins:
        frame["qmd_bin"] = pd.cut(frame["qmd"], bins=[*qmd_bins, 999.0], right=False, labels=False)
    else:
        frame["qmd_bin"] = 0
    grouped = frame.groupby(["BEC", "ba_bin", "qmd_bin"], sort=True)[
        [f"rate_{group}" for group in groups]
    ].mean()
    rows: list[dict[str, object]] = []
    for index, values in grouped.iterrows():
        bec, ba_bin, qmd_bin = cast(tuple[str, int, int], index)
        ba_index = int(ba_bin)
        qmd_index = int(qmd_bin)
        ba_min = float(ba_bins[ba_index]) if ba_bins else 0.0
        ba_max = float(ba_bins[ba_index + 1]) if ba_bins and ba_index + 1 < len(ba_bins) else 999.0
        qmd_min = float(qmd_bins[qmd_index]) if qmd_bins else 0.0
        qmd_max = (
            float(qmd_bins[qmd_index + 1]) if qmd_bins and qmd_index + 1 < len(qmd_bins) else 999.0
        )
        for group in groups:
            rate = float(values[f"rate_{group}"])
            if rate > 0:
                rows.append(
                    {
                        "bec": str(bec),
                        "species": group,
                        "rate": rate,
                        "ba_min": ba_min,
                        "ba_max": ba_max,
                        "qmd_min": qmd_min,
                        "qmd_max": qmd_max,
                    }
                )
    if not rows:
        raise ValueError("no positive recruitment rate was found")
    method = "mean annual new-tree TPH by BEC/species"
    if ba_bins or qmd_bins:
        method += " and initial BA/QMD bin"
    return IngrowthModel.from_record(
        {
            "model_id": model_id,
            "version": version,
            "method": method,
            "rates": rows,
        }
    )
