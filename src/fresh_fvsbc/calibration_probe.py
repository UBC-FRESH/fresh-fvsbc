"""Small, pure helpers for a calibration probe.

A probe is not a fit. It evaluates a fixed candidate set on an eligible sample,
with an explicit train/test split, so a domain can show whether a parameter
surface is identifiable before it gets a bundle. The FVS runs live in the CLI;
these functions only select intervals and build the keyword records.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

import pandas as pd

from fresh_fvsbc.keywords import Keyword

__all__ = [
    "eligible_intervals",
    "ingrowth_keyword",
    "insert_parameters",
    "interval_checksum",
    "parameter_keywords",
    "summarise_probe",
]


def eligible_intervals(
    intervals: pd.DataFrame,
    *,
    min_ba0: float = 15.0,
    max_mortality_fraction: float = 0.4,
    min_qmd: float = 6.0,
) -> pd.DataFrame:
    """Return intervals that are not dominated by ingrowth or a mortality event.

    Parameters
    ----------
    intervals : pandas.DataFrame
        The interval table. It must carry ``ba0``, ``dead_ba``, and ``qmd``.
    min_ba0 : float, optional
        The minimum initial basal area, in m2/ha. A lower initial BA is usually
        a young stand whose ingrowth the no-cut projection cannot represent.
    max_mortality_fraction : float, optional
        The largest ``dead_ba / ba0`` accepted. A larger value is a disturbance
        or a mortality event that a single multiplier should not absorb.
    min_qmd : float, optional
        The minimum initial quadratic mean diameter, in cm. A smaller QMD is a
        dense small-tree stand whose diameter growth is not an established-stand
        calibration target.

    Returns
    -------
    pandas.DataFrame
        A copy of the accepted rows, with a ``mortality_fraction`` column.

    Raises
    ------
    ValueError
        If the table lacks a required column or a bound is not positive.
    """
    missing = {"ba0", "dead_ba", "qmd"} - set(intervals.columns)
    if missing:
        raise ValueError(f"the interval table lacks {', '.join(sorted(missing))}")
    if min_ba0 <= 0:
        raise ValueError("min_ba0 must be positive")
    if not 0 < max_mortality_fraction <= 1:
        raise ValueError("max_mortality_fraction must be in (0, 1]")
    if min_qmd <= 0:
        raise ValueError("min_qmd must be positive")
    frame = intervals.copy()
    frame["mortality_fraction"] = frame["dead_ba"] / frame["ba0"].where(frame["ba0"] > 0)
    keep = (
        (frame["ba0"] >= min_ba0)
        & (frame["qmd"] >= min_qmd)
        & (frame["mortality_fraction"].fillna(0.0) <= max_mortality_fraction)
    )
    return frame[keep].reset_index(drop=True)


def interval_checksum(frame: pd.DataFrame) -> str:
    """Return a stable checksum of the interval sample.

    The checksum covers the identifiers and the initial/final stand values, not
    the pandas float formatting, so two environments hash the same sample the
    same way.

    Parameters
    ----------
    frame : pandas.DataFrame
        The interval sample. It must carry ``interval_id`` and the stand values
        used by the caller.

    Returns
    -------
    str
        ``sha256:`` followed by the digest.
    """
    columns = [
        column
        for column in ("interval_id", "BEC", "TSA_DESC", "ba0", "qmd", "tph0", "years", "dead_ba")
        if column in frame.columns
    ]
    records = []
    for row in frame.sort_values("interval_id")[columns].to_dict("records"):
        normalized = {
            key: round(float(value), 6) if isinstance(value, (int, float)) else str(value)
            for key, value in row.items()
        }
        records.append(normalized)
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parameter_keywords(
    *,
    bamax: float | None = None,
    baimult: Mapping[str, float] | None = None,
    mortmult: Mapping[str, float] | None = None,
    htgmul: Mapping[str, float] | None = None,
    regdmul: Mapping[str, float] | None = None,
    reghmul: Mapping[str, float] | None = None,
) -> tuple[Keyword, ...]:
    """Return the keyword records for one candidate.

    Parameters
    ----------
    bamax : float, optional
        The maximum basal area, in m2/ha.
    baimult : Mapping of str to float, optional
        Species code to BA increment multiplier.
    mortmult : Mapping of str to float, optional
        Species code to mortality multiplier.
    htgmul : Mapping of str to float, optional
        Species code to height growth multiplier.
    regdmul : Mapping of str to float, optional
        Species code to small-tree diameter growth multiplier.
    reghmul : Mapping of str to float, optional
        Species code to small-tree height growth multiplier.

    Returns
    -------
    tuple of Keyword
        The records, in a stable order.
    """
    keywords: list[Keyword] = []
    if bamax is not None:
        keywords.append(Keyword("BAMAX", (f"{bamax:g}",)))
    for name, values in (
        ("BAIMULT", baimult),
        ("MORTMULT", mortmult),
        ("HTGMULT", htgmul),
        ("REGDMULT", regdmul),
        ("REGHMULT", reghmul),
    ):
        for species, value in (values or {}).items():
            fields: tuple[str, ...]
            if name == "MORTMULT":
                fields = ("1", species, f"{value:.4f}", "0", "999")
            else:
                fields = ("1", species, f"{value:.4f}")
            keywords.append(Keyword(name, fields))
    return tuple(keywords)


def insert_parameters(
    keywords: Sequence[Keyword], parameters: Sequence[Keyword]
) -> tuple[Keyword, ...]:
    """Insert calibration records before the first projection keyword.

    Parameters
    ----------
    keywords : sequence of Keyword
        The stand's keyword set, which already has a ``PROCESS`` or ``STOP``.
    parameters : sequence of Keyword
        The calibration records.

    Returns
    -------
    tuple of Keyword
        The combined set.

    Raises
    ------
    ValueError
        If the set has no projection keyword.
    """
    at = next(
        (index for index, keyword in enumerate(keywords) if keyword.name in {"PROCESS", "STOP"}),
        None,
    )
    if at is None:
        raise ValueError("the keyword set has no PROCESS or STOP to insert before")
    return (*keywords[:at], *parameters, *keywords[at:])


def summarise_probe(
    rows: pd.DataFrame, *, by: Sequence[str] = ("candidate", "fold")
) -> pd.DataFrame:
    """Aggregate a probe's interval rows.

    Parameters
    ----------
    rows : pandas.DataFrame
        The rows with ``ba_error`` and ``tph_error``.
    by : sequence of str, optional
        The grouping columns.

    Returns
    -------
    pandas.DataFrame
        Count, bias, and MAE by group.

    Raises
    ------
    ValueError
        If an error column is missing.
    """
    missing = {"ba_error", "tph_error"} - set(rows.columns)
    if missing:
        raise ValueError(f"the probe rows lack {', '.join(sorted(missing))}")
    return (
        rows.groupby(list(by), sort=True)
        .agg(
            intervals=("ba_error", "size"),
            bias_ba=("ba_error", "mean"),
            mae_ba=("ba_error", lambda values: values.abs().mean()),
            bias_tph=("tph_error", "mean"),
            mae_tph=("tph_error", lambda values: values.abs().mean()),
        )
        .reset_index()
    )


def ingrowth_keyword(
    *,
    bec: str,
    years: float,
    rates: Mapping[str, Mapping[str, float]],
    scale: float = 1.0,
) -> Keyword | None:
    """Build an ``ESTAB`` natural-regeneration block from annual rates.

    Parameters
    ----------
    bec : str
        The BEC label that selects the rate row.
    years : float
        The projection interval length, in years.
    rates : Mapping of str to Mapping of str to float
        BEC label to species code to annual recruitment, in trees per hectare
        per year.
    scale : float, optional
        A multiplier on the annual rate, used for sensitivity.

    Returns
    -------
    Keyword or None
        An ``ESTAB`` block with one ``NATURAL`` line per species, or ``None``
        when the BEC has no positive rate.

    Raises
    ------
    ValueError
        If ``years`` or ``scale`` is negative.
    """
    if years < 0:
        raise ValueError("years must not be negative")
    if scale < 0:
        raise ValueError("scale must not be negative")
    lines: list[Keyword] = []
    for species, rate in rates.get(bec, {}).items():
        tph = float(rate) * years * scale
        tpa = tph * 0.404686
        if tpa < 0.05:
            continue
        # NATURAL reads trees per acre; 1 TPH = 0.404686 TPA.
        lines.append(Keyword("NATURAL", ("1", species, f"{tpa:.1f}", "100.0")))
    if not lines:
        return None
    return Keyword("ESTAB", nested=tuple(lines))
