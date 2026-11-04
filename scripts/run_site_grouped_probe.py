#!/usr/bin/env python3
"""Run a leave-one-site-out calibration probe with fold-specific ingrowth.

This is the tracked version of the D7.19 evidence harness. For each eligible
site it fits the recruitment model on the other sites, runs the candidate on the
held-out site, and writes the combined interval and aggregate tables.

The probe does not fit the candidate parameters. They stay fixed in the
candidate JSON; only the ingrowth model is refit per fold.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from fresh_fvsbc.backtest import select_intervals
from fresh_fvsbc.calibration_probe import eligible_intervals, interval_checksum
from fresh_fvsbc.ingrowth import IngrowthModel, fit_rates, recruitment_table

__all__ = ["EXIT_BAD_INPUT", "EXIT_OK", "main"]

EXIT_OK: int = 0
EXIT_BAD_INPUT: int = 2


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser."""
    parser = argparse.ArgumentParser(
        prog="run_site_grouped_probe",
        description="Run a leave-one-site-out probe with fold-specific ingrowth.",
    )
    parser.add_argument("--data-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--psp-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--out-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--domain", required=True, help="BEC prefix, such as SBPSmk")
    parser.add_argument("--per-bec", type=int, default=1000, metavar="N")
    parser.add_argument("--min-ba0", type=float, default=15.0, metavar="M2HA")
    parser.add_argument("--max-mortality-fraction", type=float, default=0.4, metavar="FRACTION")
    parser.add_argument("--min-qmd", type=float, default=6.0, metavar="CM")
    parser.add_argument("--candidates", required=True, type=Path, metavar="FILE")
    parser.add_argument("--tree-age", type=float, default=60.0, metavar="YEARS")
    parser.add_argument("--max-rate", type=float, default=100.0, metavar="TPH/YR")
    return parser


def _read_recruitment_trees(psp_dir: Path, sample: pd.DataFrame) -> pd.DataFrame:
    """Read every tree visit for the sampled sites, not just the start visit."""
    sites = set(sample["SITE_IDENTIFIER"])
    columns = [
        "SITE_IDENTIFIER",
        "VISIT_NUMBER",
        "PLOT",
        "TREE_NO",
        "SPECIES",
        "LV_D",
        "PHF_TREE",
    ]
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(psp_dir / "faib_tree_detail.csv", usecols=columns, chunksize=500_000):
        chunk = chunk[chunk["SITE_IDENTIFIER"].isin(sites)]
        if not chunk.empty:
            chunks.append(chunk)
    if not chunks:
        return pd.DataFrame(columns=columns)
    return pd.concat(chunks, ignore_index=True)


def _rates_for_cli(model: IngrowthModel, bec: str) -> dict[str, object]:
    """Return the old CLI rate shape for one BEC."""
    return {"rates": {bec: {rate.species: rate.rate for rate in model.rates}}}


def main(argv: Sequence[str] | None = None) -> int:
    """Run every site fold and write the combined evidence.

    Parameters
    ----------
    argv : sequence of str or None, optional
        The arguments, without the program name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        :data:`EXIT_OK` on success, or :data:`EXIT_BAD_INPUT` for a bad input.
    """
    args = _parser().parse_args(argv)
    try:
        intervals = pd.read_csv(args.data_dir / "intervals.csv")
        visits = pd.read_csv(args.data_dir / "visits.csv")
        json.loads(args.candidates.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"run_site_grouped_probe: {error}")
        return EXIT_BAD_INPUT
    domain = intervals[intervals["BEC"].astype(str).str.startswith(args.domain)].copy()
    if domain.empty:
        print(f"run_site_grouped_probe: no intervals for {args.domain}")
        return EXIT_BAD_INPUT
    try:
        eligible = eligible_intervals(
            domain,
            min_ba0=args.min_ba0,
            max_mortality_fraction=args.max_mortality_fraction,
            min_qmd=args.min_qmd,
        )
    except ValueError as error:
        print(f"run_site_grouped_probe: {error}")
        return EXIT_BAD_INPUT
    sample = select_intervals(eligible, per_bec=args.per_bec)
    trees = _read_recruitment_trees(args.psp_dir, sample)
    if trees.empty:
        print("run_site_grouped_probe: no tree rows for the eligible sample")
        return EXIT_BAD_INPUT
    args.out_dir.mkdir(parents=True, exist_ok=True)
    probe_script = Path(__file__).with_name("run_calibration_probe.py")
    rows: list[pd.DataFrame] = []
    for site in sorted(sample["SITE_IDENTIFIER"].astype(str).unique()):
        fold = args.out_dir / "folds" / site
        data = fold / "data"
        data.mkdir(parents=True, exist_ok=True)
        train = sample[sample["SITE_IDENTIFIER"].astype(str) != site]
        test = sample[sample["SITE_IDENTIFIER"].astype(str) == site]
        table = recruitment_table(train, trees)
        model = fit_rates(
            table,
            model_id=f"{args.domain}-loso-{site}",
            version="0.1.0",
            statistic="mean",
            max_rate=args.max_rate,
        )
        bec = str(test["BEC"].iloc[0])
        (fold / "rates.json").write_text(
            json.dumps(_rates_for_cli(model, bec), indent=2) + "\n", encoding="utf-8"
        )
        test.to_csv(data / "intervals.csv", index=False)
        visits[visits["SITE_IDENTIFIER"].astype(str) == site].to_csv(
            data / "visits.csv", index=False
        )
        command = [
            sys.executable,
            str(probe_script),
            "--data-dir",
            str(data),
            "--psp-dir",
            str(args.psp_dir),
            "--out-dir",
            str(fold / "probe"),
            "--domain",
            args.domain,
            "--per-bec",
            str(args.per_bec),
            "--min-ba0",
            str(args.min_ba0),
            "--max-mortality-fraction",
            str(args.max_mortality_fraction),
            "--min-qmd",
            str(args.min_qmd),
            "--candidates",
            str(args.candidates),
            "--ingrowth",
            str(fold / "rates.json"),
            "--test-sites",
            site,
            "--tree-age",
            str(args.tree_age),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"run_site_grouped_probe: fold {site} failed\n{result.stdout}\n{result.stderr}")
            return EXIT_BAD_INPUT
        frame = pd.read_csv(fold / "probe" / "probe.csv")
        frame["fold_site"] = site
        rows.append(frame)
    if not rows:
        print("run_site_grouped_probe: no fold produced a comparison")
        return EXIT_BAD_INPUT
    combined = pd.concat(rows, ignore_index=True)
    combined.to_csv(args.out_dir / "loso-probe.csv", index=False)
    site_groups = combined.groupby("fold_site")
    summary = pd.DataFrame(
        [
            {
                "folds": combined["fold_site"].nunique(),
                "intervals": len(combined),
                "data_checksum": interval_checksum(sample),
                "ba_percent": 100 * combined["ba_error"].mean() / combined["observed_ba1"].mean(),
                "tph_percent": 100
                * combined["tph_error"].mean()
                / combined["observed_tph1"].mean(),
                "worst_site_ba_percent": max(
                    abs(100 * group["ba_error"].mean() / group["observed_ba1"].mean())
                    for _, group in site_groups
                ),
                "worst_site_tph_percent": max(
                    abs(100 * group["tph_error"].mean() / group["observed_tph1"].mean())
                    for _, group in site_groups
                ),
                "sites_pass": sum(
                    abs(100 * group["ba_error"].mean() / group["observed_ba1"].mean()) <= 10
                    and abs(100 * group["tph_error"].mean() / group["observed_tph1"].mean()) <= 15
                    for _, group in site_groups
                ),
            }
        ]
    )
    summary.to_csv(args.out_dir / "loso-summary.csv", index=False)
    print(summary.round(2).to_string(index=False))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
