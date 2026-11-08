#!/usr/bin/env python3
"""Summarise non-PSP external probes by calibration domain.

The non-PSP repeated cohort is an independent validation sample, not training data. This script
turns one or more ``probe.csv`` files into the domain table the tiered calibration surface uses.
It applies the pre-registered thresholds in ``full-domain-design.md``:

- BA bias within ±3 m2/ha or ±10 percent;
- TPH bias within ±15 percent.

A site passes only when its own aggregate error is inside the same band. The domain verdict is
``insufficient`` below five intervals, because a one-interval domain cannot support a claim.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

#: The tracked BEC-to-domain crosswalk. It maps every BC BGC unit the design names.
DEFAULT_GAP = Path(__file__).with_name("w2-bec-gap.csv")

#: Zones the original W2 design called unsupported but which now have their own domain row.
ZONE_FALLBACK: dict[str, str] = {
    "CWH": "CWH",
    "BWBS": "BWBS",
    "MH": "MH",
    "CDF": "CDF",
    "CMA": "CMA",
    "PP": "PP",
}

#: Fixed seed for the site bootstrap, so a rerun reports the same interval.
BOOTSTRAP_SEED: int = 20261108

#: The number of site-bootstrap resamples.
BOOTSTRAP_REPS: int = 2000

#: The zones are matched longest-first because SBPS must not read as SBS.
ZONES: tuple[str, ...] = (
    "SBPS",
    "ESSF",
    "CWH",
    "BWBS",
    "ICH",
    "IDF",
    "SBS",
    "MS",
    "MH",
    "CDF",
    "PP",
)


def _zone(bec: str) -> str:
    """Return the BEC zone from a label such as ``IDFdk3`` or ``CWHDM``."""
    letters = "".join(character for character in bec if character.isalpha())
    for zone in ZONES:
        if letters.startswith(zone):
            return zone
    return letters[:4]


def _domain(bec: str, mapping: dict[str, str]) -> str:
    """Return the calibration domain for a BEC, with an explicit zone fallback."""
    mapped = mapping.get(bec)
    if isinstance(mapped, str) and mapped:
        return mapped
    return ZONE_FALLBACK.get(_zone(bec), _zone(bec))


def _site_bootstrap(by_site: pd.DataFrame, measure: str) -> tuple[float, float]:
    """Return the 2.5 and 97.5 percent site-bootstrap bounds for one relative bias.

    Parameters
    ----------
    by_site : pandas.DataFrame
        Per-site sums of observed and predicted BA or TPH.
    measure : str
        ``"ba"`` or ``"tph"``.

    Returns
    -------
    tuple of float
        The lower and upper percentage bounds.
    """
    observed = by_site[f"observed_{measure}1"].to_numpy(dtype=float)
    predicted = by_site[f"predicted_{measure}1"].to_numpy(dtype=float)
    if len(observed) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.integers(0, len(observed), size=(BOOTSTRAP_REPS, len(observed)))
    observed_draws = observed[draws].sum(axis=1)
    predicted_draws = predicted[draws].sum(axis=1)
    valid = observed_draws > 0
    percentages = (predicted_draws[valid] - observed_draws[valid]) / observed_draws[valid] * 100.0
    if percentages.size == 0:
        return float("nan"), float("nan")
    low, high = np.percentile(percentages, [2.5, 97.5])
    return float(low), float(high)


def _verdict(row: Any) -> str:  # noqa: ANN401 - itertuples returns a synthetic named tuple
    """Classify a domain from its point estimate and site-bootstrap interval."""
    if int(row.intervals) < 5:
        return "insufficient"
    ba_point = bool(row.ba_within)
    tph_point = bool(row.tph_within)
    if not (ba_point and tph_point):
        return "fails"
    ba_low = float(row.ba_pct_low)
    ba_high = float(row.ba_pct_high)
    tph_low = float(row.tph_pct_low)
    tph_high = float(row.tph_pct_high)
    ba_ci = not np.isfinite(ba_low) or (ba_low > -10.0 and ba_high < 10.0)
    tph_ci = not np.isfinite(tph_low) or (tph_low > -15.0 and tph_high < 15.0)
    return "passes" if ba_ci and tph_ci else "leans-pass"


def summarise(frame: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Aggregate probe rows by domain and apply the pre-registered bands.

    Parameters
    ----------
    frame : pandas.DataFrame
        Rows from one or more ``probe.csv`` files.
    mapping : dict
        BEC label to calibration-domain name.

    Returns
    -------
    pandas.DataFrame
        One row per domain with counts, bias, percentage bias, MAE, site-pass counts, and a verdict.
    """
    frame = frame.copy()
    frame["BEC"] = frame["BEC"].astype(str).str.upper().str.replace("/", "", regex=False)
    frame["domain"] = [_domain(bec, mapping) for bec in frame["BEC"]]
    frame["site"] = frame["interval_id"].astype(str).str.split("|").str[0]
    rows: list[dict[str, Any]] = []
    for domain, group in frame.groupby("domain", sort=True):
        by_site = group.groupby("site")[
            ["observed_ba1", "predicted_ba1", "observed_tph1", "predicted_tph1"]
        ].sum()
        site_ba = (
            (by_site["predicted_ba1"] - by_site["observed_ba1"])
            / by_site["observed_ba1"].clip(lower=1e-6)
            * 100.0
        ).abs()
        site_tph = (
            (by_site["predicted_tph1"] - by_site["observed_tph1"])
            / by_site["observed_tph1"].clip(lower=1e-6)
            * 100.0
        ).abs()
        n_sites = int(group["site"].nunique())
        observed_ba = float(group["observed_ba1"].mean())
        observed_tph = float(group["observed_tph1"].mean())
        ba_bias = float(group["ba_error"].mean())
        tph_bias = float(group["tph_error"].mean())
        ba_pct = ba_bias / observed_ba * 100.0 if observed_ba else float("nan")
        tph_pct = tph_bias / observed_tph * 100.0 if observed_tph else float("nan")
        ba_low, ba_high = _site_bootstrap(by_site, "ba")
        tph_low, tph_high = _site_bootstrap(by_site, "tph")
        rows.append(
            {
                "domain": domain,
                "intervals": len(group),
                "sites": n_sites,
                "ba_bias": ba_bias,
                "ba_pct": ba_pct,
                "ba_pct_low": ba_low,
                "ba_pct_high": ba_high,
                "ba_mae": group["ba_error"].abs().mean(),
                "ba_within": abs(ba_bias) <= 3.0 or abs(ba_pct) <= 10.0,
                "ba_sites_pass": f"{int((site_ba <= 10.0).sum())}/{n_sites}",
                "tph_bias": tph_bias,
                "tph_pct": tph_pct,
                "tph_pct_low": tph_low,
                "tph_pct_high": tph_high,
                "tph_mae": group["tph_error"].abs().mean(),
                "tph_within": abs(tph_pct) <= 15.0,
                "tph_sites_pass": f"{int((site_tph <= 15.0).sum())}/{n_sites}",
            }
        )
    summary = pd.DataFrame(rows)
    summary["verdict"] = [_verdict(row) for row in summary.itertuples()]
    return summary


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="nonpsp_domain_baseline",
        description="Summarise non-PSP probe.csv files by calibration domain.",
    )
    parser.add_argument(
        "--probe",
        action="append",
        required=True,
        type=Path,
        metavar="FILE",
        help="a probe.csv; repeat for each zone",
    )
    parser.add_argument(
        "--gap",
        type=Path,
        default=DEFAULT_GAP,
        metavar="FILE",
        help="the BEC-to-domain crosswalk (default: w2-bec-gap.csv beside this script)",
    )
    parser.add_argument("--out", type=Path, required=True, metavar="FILE")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Write the domain summary and print it.

    Parameters
    ----------
    argv : list of str or None, optional
        Arguments without the program name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` on success.
    """
    args = _parser().parse_args(argv)
    gap = pd.read_csv(args.gap)
    gap["bgc"] = gap["bgc"].astype(str).str.upper()
    mapping = dict(zip(gap["bgc"], gap["domain"], strict=True))
    frames = [pd.read_csv(path) for path in args.probe]
    summary = summarise(pd.concat(frames, ignore_index=True), mapping)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.out, index=False)
    print(summary.round(2).to_string(index=False))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
