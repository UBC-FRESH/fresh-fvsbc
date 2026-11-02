"""Group the supported BEC variants into calibration domains and score their sample size.

This module is the reproducible core of the W1.6 design. It does **not** fit a parameter. It
applies a pre-registered sample-size rule to the aggregate coverage table, so the domains and
their readiness are the same every time the table is rebuilt:

- a supported variant is ``calibration`` when it has at least 15 repeat sites and 50 intervals;
- it is ``validation-only`` when it has at least 5 repeat sites or 10 intervals;
- it is ``insufficient`` otherwise;
- a variant in one of the five zones the BC variant does not resolve is ``upstream``.

The power columns are approximate and deliberately labelled as such. The mortality figure is the
minimum detectable relative change in a binomial rate at 80 percent power and a two-sided 5 percent
test, ``2.8 / sqrt(dead trees)``. The basal-area figure assumes a between-interval standard
deviation of 10 m2/ha and uses ``2.8 * 10 / sqrt(intervals)``. Both are sample-size sufficiency
checks, not a substitute for the fitted standard errors.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

__all__ = [
    "ASSUMED_BA_SD_M2HA",
    "CALIBRATION_MIN_INTERVALS",
    "CALIBRATION_MIN_REPEAT_SITES",
    "GROWTH_MIN_INTERVALS",
    "MORTALITY_MIN_DEAD_TREES",
    "POWER_MULTIPLIER",
    "UPSTREAM_ZONES",
    "VALIDATION_MIN_INTERVALS",
    "VALIDATION_MIN_REPEAT_SITES",
    "ZONES",
    "DomainError",
    "DomainTables",
    "classify_variant",
    "prepare_coverage",
    "summarise_domains",
    "write_domain_tables",
]

#: The seven BEC zones the BC variant resolves.
ZONES: tuple[str, ...] = ("ESSF", "ICH", "IDF", "MS", "PP", "SBS", "SBPS")

#: The five BEC zones the BC variant does not resolve; W2 is their upstream gate.
UPSTREAM_ZONES: tuple[str, ...] = ("CWH", "CDF", "BWBS", "CMA", "MH")

#: A variant needs this many repeat sites and intervals before it is a calibration variant.
CALIBRATION_MIN_REPEAT_SITES: int = 15
CALIBRATION_MIN_INTERVALS: int = 50

#: A variant needs this many dead trees before the mortality multiplier is identifiable.
MORTALITY_MIN_DEAD_TREES: int = 1000

#: A variant needs this many intervals before growth is identifiable rather than validation-only.
GROWTH_MIN_INTERVALS: int = 100

#: A variant with at least one of these stays in the table as a validation-only variant.
VALIDATION_MIN_REPEAT_SITES: int = 5
VALIDATION_MIN_INTERVALS: int = 10

#: The two-sided 5 percent, 80 percent power multiplier used by the approximate MDE columns.
POWER_MULTIPLIER: float = 2.8

#: The assumed between-interval standard deviation for the basal-area MDE, in m2/ha.
ASSUMED_BA_SD_M2HA: float = 10.0

_ZONE_PATTERN: str = r"^(ESSF|ICH|IDF|MS|PP|SBS|SBPS|CWH|CDF|BWBS|CMA|MH)"
_REQUIRED_COVERAGE: tuple[str, ...] = (
    "BEC",
    "supported",
    "sites",
    "visits",
    "repeat_sites",
    "intervals",
    "live_trees",
    "dead_trees",
    "missing_trees",
    "damaged_trees",
)
_REQUIRED_BASELINE: tuple[str, ...] = ("BEC", "above_p99", "above_max")


class DomainError(Exception):
    """The coverage or baseline table cannot be used to build the domains."""


@dataclass(frozen=True)
class DomainTables:
    """Where the two domain tables were written and what they contain.

    Attributes
    ----------
    power_path : Path
        The per-variant coverage and power table.
    summary_path : Path
        The per-zone domain summary.
    variants : int
        The number of BEC variants in the coverage table.
    calibration : int
        The number of calibration variants.
    validation_only : int
        The number of validation-only variants.
    insufficient : int
        The number of supported but too-thin variants.
    upstream : int
        The number of variants in the five upstream zones.
    """

    power_path: Path
    summary_path: Path
    variants: int
    calibration: int
    validation_only: int
    insufficient: int
    upstream: int


def _integer(value: object) -> int:
    """Convert a table value to an integer, or zero when it is not numeric.

    Parameters
    ----------
    value : object
        The value to convert.

    Returns
    -------
    int
        The integer, or ``0``.
    """
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return 0


def _require_columns(frame: pd.DataFrame, required: tuple[str, ...], name: str) -> None:
    """Raise when a table is missing a column the design needs.

    Parameters
    ----------
    frame : pandas.DataFrame
        The table to check.
    required : tuple of str
        The column names that must be present.
    name : str
        What the table is, for the message.

    Raises
    ------
    DomainError
        If any required column is absent.
    """
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise DomainError(f"the {name} table is missing {', '.join(missing)}")


def classify_variant(*, supported: bool, repeat_sites: int, intervals: int) -> str:
    """Classify one BEC variant by its sample size.

    Parameters
    ----------
    supported : bool
        Whether the BC variant resolves the zone.
    repeat_sites : int
        Sites with at least two visits.
    intervals : int
        Measurement intervals available for the variant.

    Returns
    -------
    str
        ``"upstream"``, ``"calibration"``, ``"validation-only"`` or ``"insufficient"``.
    """
    if not supported:
        return "upstream"
    if repeat_sites >= CALIBRATION_MIN_REPEAT_SITES and intervals >= CALIBRATION_MIN_INTERVALS:
        return "calibration"
    if repeat_sites >= VALIDATION_MIN_REPEAT_SITES or intervals >= VALIDATION_MIN_INTERVALS:
        return "validation-only"
    return "insufficient"


def _supported_column(frame: pd.DataFrame) -> pd.Series:
    """Return the ``supported`` column as booleans.

    Parameters
    ----------
    frame : pandas.DataFrame
        The coverage table.

    Returns
    -------
    pandas.Series
        One boolean per row.
    """
    if frame["supported"].dtype == bool:
        return frame["supported"]
    return frame["supported"].astype(str).str.lower().isin({"true", "1", "yes"})


def prepare_coverage(frame: pd.DataFrame) -> pd.DataFrame:
    """Add the domain, status, readiness and sample-size columns to a coverage table.

    Parameters
    ----------
    frame : pandas.DataFrame
        The aggregate ``bec_coverage.csv`` table.

    Returns
    -------
    pandas.DataFrame
        A copy with ``zone``, ``status``, ``capacity_ready``, ``mortality_ready``,
        ``growth_ready``, ``mortality_mde_pct`` and ``ba_mde_m2ha``.

    Raises
    ------
    DomainError
        If a required column is absent, or a BEC does not start with a known zone.
    """
    _require_columns(frame, _REQUIRED_COVERAGE, "coverage")
    prepared = frame.copy()
    prepared["supported"] = _supported_column(prepared)
    prepared["zone"] = prepared["BEC"].astype(str).str.extract(_ZONE_PATTERN, expand=False)
    unknown = prepared.loc[prepared["zone"].isna(), "BEC"].astype(str).tolist()
    if unknown:
        raise DomainError(f"BEC code(s) do not name a known zone: {', '.join(unknown)}")
    prepared["status"] = [
        classify_variant(
            supported=bool(row.supported),
            repeat_sites=_integer(row.repeat_sites),
            intervals=_integer(row.intervals),
        )
        for row in prepared.itertuples(index=False)
    ]
    calibration = prepared["status"].eq("calibration")
    prepared["capacity_ready"] = calibration
    prepared["mortality_ready"] = calibration & (prepared["dead_trees"] >= MORTALITY_MIN_DEAD_TREES)
    prepared["growth_ready"] = calibration & (prepared["intervals"] >= GROWTH_MIN_INTERVALS)
    prepared["mortality_mde_pct"] = [
        round(100.0 * POWER_MULTIPLIER / math.sqrt(dead), 2) if dead > 0 else None
        for dead in (_integer(value) for value in prepared["dead_trees"])
    ]
    prepared["ba_mde_m2ha"] = [
        round(POWER_MULTIPLIER * ASSUMED_BA_SD_M2HA / math.sqrt(intervals), 2)
        if intervals > 0
        else None
        for intervals in (_integer(value) for value in prepared["intervals"])
    ]
    columns = [
        "BEC",
        "zone",
        "supported",
        "sites",
        "visits",
        "repeat_sites",
        "intervals",
        "live_trees",
        "dead_trees",
        "missing_trees",
        "damaged_trees",
        "status",
        "capacity_ready",
        "mortality_ready",
        "growth_ready",
        "mortality_mde_pct",
        "ba_mde_m2ha",
    ]
    return prepared[columns]


def _verdict(
    *,
    variants: int,
    upstream: int,
    calibration: int,
    validation_only: int,
    capacity_ready: int,
    mortality_ready: int,
    growth_ready: int,
) -> str:
    """Return the domain verdict from its counts.

    Parameters
    ----------
    variants : int
        Variants in the zone.
    upstream : int
        Variants the BC variant does not resolve.
    calibration : int
        Calibration variants.
    validation_only : int
        Validation-only variants.
    capacity_ready : int
        Calibration variants with enough intervals for capacity.
    mortality_ready : int
        Calibration variants with enough dead trees for mortality.
    growth_ready : int
        Calibration variants with enough intervals for growth.

    Returns
    -------
    str
        ``"upstream"``, ``"calibration"``, ``"partial"``, ``"validation-only"`` or
        ``"insufficient"``.
    """
    if upstream == variants:
        return "upstream"
    if calibration == 0:
        return "validation-only" if validation_only else "insufficient"
    if capacity_ready and mortality_ready and growth_ready:
        return "calibration"
    return "partial"


def _claim(verdict: str, calibration: int) -> str:
    """Return the claim the verdict supports.

    Parameters
    ----------
    verdict : str
        The domain verdict.
    calibration : int
        The number of calibration variants in the domain.

    Returns
    -------
    str
        A short claim boundary.
    """
    if verdict == "upstream":
        return "W2 extension required before any calibration."
    if verdict == "validation-only":
        return "No calibration; use for validation and the empirical envelope only."
    if verdict == "insufficient":
        return "Not enough repeat measurement; do not use for a claim."
    if verdict == "partial":
        return "Calibrate the ready parameters; hold the rest as validation-only."
    if calibration < 3:
        return (
            "Narrow claim: fewer than three calibration variants; validate leave-one-variant-out."
        )
    return "Calibrate capacity, mortality and growth; validate on held-out sites and variants."


def summarise_domains(frame: pd.DataFrame, baseline: pd.DataFrame | None = None) -> pd.DataFrame:
    """Summarise the prepared coverage by BEC zone.

    Parameters
    ----------
    frame : pandas.DataFrame
        A table returned by :func:`prepare_coverage`.
    baseline : pandas.DataFrame, optional
        The baseline summary, used to count the intervals above the p99 or the observed maximum.

    Returns
    -------
    pandas.DataFrame
        One row per zone with counts, readiness totals, a verdict, a claim and the baseline flags.

    Raises
    ------
    DomainError
        If a required column is absent, or the baseline has no zone code.
    """
    _require_columns(
        frame, ("BEC", "zone", "status", "sites", "repeat_sites", "intervals"), "coverage"
    )
    flags: dict[str, int] = {}
    if baseline is not None and not baseline.empty:
        _require_columns(baseline, _REQUIRED_BASELINE, "baseline")
        zones = baseline["BEC"].astype(str).str.extract(_ZONE_PATTERN, expand=False)
        unknown = baseline.loc[zones.isna(), "BEC"].astype(str).tolist()
        if unknown:
            raise DomainError(f"BEC code(s) do not name a known zone: {', '.join(unknown)}")
        counted = baseline.assign(zone=zones)
        flags = {
            str(zone): int(value)
            for zone, value in counted.groupby("zone")[["above_p99", "above_max"]]
            .sum()
            .sum(axis=1)
            .astype(int)
            .to_dict()
            .items()
        }
    records: list[dict[str, Any]] = []
    for zone, group in frame.groupby("zone", sort=True):
        calibration = int(group["status"].eq("calibration").sum())
        validation_only = int(group["status"].eq("validation-only").sum())
        insufficient = int(group["status"].eq("insufficient").sum())
        upstream = int(group["status"].eq("upstream").sum())
        capacity_ready = int(group["capacity_ready"].sum())
        mortality_ready = int(group["mortality_ready"].sum())
        growth_ready = int(group["growth_ready"].sum())
        verdict = _verdict(
            variants=len(group),
            upstream=upstream,
            calibration=calibration,
            validation_only=validation_only,
            capacity_ready=capacity_ready,
            mortality_ready=mortality_ready,
            growth_ready=growth_ready,
        )
        intervals = int(group["intervals"].sum())
        dead = int(group["dead_trees"].sum())
        records.append(
            {
                "zone": zone,
                "variants": len(group),
                "supported": int(group["supported"].sum()),
                "calibration": calibration,
                "validation_only": validation_only,
                "insufficient": insufficient,
                "upstream": upstream,
                "sites": int(group["sites"].sum()),
                "repeat_sites": int(group["repeat_sites"].sum()),
                "intervals": intervals,
                "dead_trees": dead,
                "capacity_ready": capacity_ready,
                "mortality_ready": mortality_ready,
                "growth_ready": growth_ready,
                "mortality_mde_pct": round(100.0 * POWER_MULTIPLIER / math.sqrt(dead), 2)
                if dead > 0
                else None,
                "ba_mde_m2ha": round(
                    POWER_MULTIPLIER * ASSUMED_BA_SD_M2HA / math.sqrt(intervals), 2
                )
                if intervals > 0
                else None,
                "baseline_flags": int(flags.get(str(zone), 0)),
                "verdict": verdict,
                "claim": _claim(verdict, calibration),
            }
        )
    return pd.DataFrame.from_records(records)


def write_domain_tables(
    coverage_path: Path, baseline_path: Path | None, out_dir: Path
) -> DomainTables:
    """Read the aggregate tables, classify the variants, and write both domain tables.

    Parameters
    ----------
    coverage_path : Path
        The aggregate ``bec_coverage.csv``.
    baseline_path : Path or None
        The baseline summary, when the baseline flags are wanted.
    out_dir : Path
        Where ``domain_power.csv`` and ``domain_summary.csv`` are written.

    Returns
    -------
    DomainTables
        The paths and the counts the command reports.

    Raises
    ------
    DomainError
        If a table is missing a required column or names an unknown zone.
    OSError
        If an input cannot be read or the output cannot be written.
    """
    coverage = pd.read_csv(coverage_path)
    prepared = prepare_coverage(coverage)
    baseline = pd.read_csv(baseline_path) if baseline_path is not None else None
    summary = summarise_domains(prepared, baseline)
    out_dir.mkdir(parents=True, exist_ok=True)
    power_path = out_dir / "domain_power.csv"
    summary_path = out_dir / "domain_summary.csv"
    prepared.to_csv(power_path, index=False)
    summary.to_csv(summary_path, index=False)
    counts = prepared["status"].value_counts()
    return DomainTables(
        power_path=power_path,
        summary_path=summary_path,
        variants=len(prepared),
        calibration=int(counts.get("calibration", 0)),
        validation_only=int(counts.get("validation-only", 0)),
        insufficient=int(counts.get("insufficient", 0)),
        upstream=int(counts.get("upstream", 0)),
    )
