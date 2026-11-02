#!/usr/bin/env python3
"""Run the uncalibrated FVS-BC baseline on a stratified PSP sample.

The command reads the calibration dataset and the raw FAIB tree rows, selects a
deterministic sample by BEC, grows each interval with no cut and no calibration,
and writes the comparison and the BEC summary. It does not fit a parameter.

Command-line usage::

    python scripts/run_baseline_backtest.py \
      --data-dir runtime/calibration \
      --psp-dir "$FAIB_PSP_DIR" \
      --out-dir runtime/baseline
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from fresh_fvsbc.backtest import run_backtest, select_intervals, summarise
from fresh_fvsbc.envelope import load_envelope

__all__ = ["EXIT_BAD_INPUT", "EXIT_OK", "main"]

EXIT_OK: int = 0
EXIT_BAD_INPUT: int = 2


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser."""
    parser = argparse.ArgumentParser(
        prog="run_baseline_backtest",
        description="Run the uncalibrated FVS-BC baseline on a stratified PSP sample.",
    )
    parser.add_argument("--data-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--psp-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--out-dir", required=True, type=Path, metavar="DIR")
    parser.add_argument("--per-bec", type=int, default=1, metavar="N")
    parser.add_argument("--tree-age", type=float, default=60.0, metavar="YEARS")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="write the sample and stop before any FVS run",
    )
    return parser


def _read_trees(psp_dir: Path, sample: pd.DataFrame) -> pd.DataFrame:
    """Read the raw tree rows for the sampled intervals, in chunks."""
    keys = set(
        zip(
            sample["SITE_IDENTIFIER"],
            sample["CLSTR_ID"],
            sample["visit0"],
            sample["PLOT"],
            strict=True,
        )
    )
    sites = set(sample["SITE_IDENTIFIER"])
    columns = [
        "SITE_IDENTIFIER",
        "CLSTR_ID",
        "VISIT_NUMBER",
        "PLOT",
        "TREE_NO",
        "SPECIES",
        "DBH",
        "HEIGHT",
        "LV_D",
        "PHF_TREE",
        "CR_CL",
    ]
    rows: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        psp_dir / "faib_tree_detail.csv",
        usecols=columns,
        chunksize=500_000,
        low_memory=False,
    ):
        chunk = chunk[chunk["SITE_IDENTIFIER"].isin(sites)]
        if chunk.empty:
            continue
        index = pd.MultiIndex.from_frame(
            chunk[["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "PLOT"]]
        )
        hit = chunk[index.isin(keys)]
        if not hit.empty:
            rows.append(hit)
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.concat(rows, ignore_index=True)


def _markdown(frame: pd.DataFrame) -> str:
    """Render a small frame as a Markdown table without an optional dependency."""
    if frame.empty:
        return "No rows."
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def _report(summary: pd.DataFrame, skips: pd.DataFrame, rows: pd.DataFrame) -> str:
    """Return the Markdown baseline report."""
    skipped = skips[skips["reason"].fillna("") != ""] if "reason" in skips else skips.iloc[0:0]
    reasons = (
        skipped.groupby("reason").size().rename("intervals").reset_index()
        if not skipped.empty
        else pd.DataFrame(columns=["reason", "intervals"])
    )
    initial_bias = (
        rows["predicted_ba0"] - rows["observed_ba0"] if not rows.empty else pd.Series(dtype=float)
    )
    flags = (
        rows[rows["flag_predicted"] != "ok"][
            ["BEC", "observed_ba1", "predicted_ba1", "flag_predicted"]
        ]
        if not rows.empty
        else rows.iloc[0:0]
    )
    above_p99 = int((rows["flag_predicted"] == "above_p99").sum()) if not rows.empty else 0
    above_max = int((rows["flag_predicted"] == "above_max").sum()) if not rows.empty else 0
    lines = [
        "# Uncalibrated FVS-BC baseline",
        "",
        "This is the reference backtest, not a calibration. Each interval is grown",
        "from its first PSP measurement with no cut and no calibration.",
        "",
        f"Intervals compared: **{int(summary['intervals'].sum()) if not summary.empty else 0}**",
        f"Intervals skipped: **{len(skipped)}**",
        f"Intervals with skipped trees: **{int((skips['skipped'] > 0).sum())}**",
        "",
        "## Initial stand",
        "",
        f"Mean initial BA bias: **{float(initial_bias.mean()):.2f} m2/ha**",
        f"Median initial BA bias: **{float(initial_bias.median()):.2f} m2/ha**",
        f"Initial BA MAE: **{float(initial_bias.abs().mean()):.2f} m2/ha**",
        "",
        "## Envelope flags",
        "",
        f"Intervals above p99: **{above_p99}**",
        f"Intervals above max: **{above_max}**",
        "",
        _markdown(flags),
        "",
        "## By BEC",
        "",
        _markdown(summary),
        "",
        "## Skipped intervals",
        "",
        "The skipped BECs are listed in `baseline_skipped_becs.csv`.",
        "",
        _markdown(reasons),
        "",
        "## Limits",
        "",
        "- The site series is the diagnostic `/01`; the per-plot site series is not in the",
        "  extract.",
        "- `SITECODE` uses the placeholder `FD,20`; the PSP site index is not joined.",
        "- Tree age is the placeholder passed by `--tree-age`; a PSP interval has no single",
        "  age.",
        "- A tree whose species does not resolve to one of BC's 15 is skipped and counted.",
        "- The sample is BEC-stratified, not a random sample of BC stands.",
        "- Annual **net** change is the summary-level comparison; the gross mortality",
        "  table is not requested by this baseline.",
        "- The envelope flag is an empirical sample property, not a biological maximum.",
        "- The initial BA is reproduced closely; the end-of-interval BA is not. The",
        "  flagged cases are the finding, and a mean over one interval per BEC is not",
        "  a province-wide estimate.",
        "",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the baseline and write its tables.

    Parameters
    ----------
    argv : Sequence of str, optional
        The arguments, without the program name. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        ``0`` when the run completed, ``2`` when an input is missing.
    """
    args = _parser().parse_args(argv)
    data_dir = args.data_dir
    try:
        intervals = pd.read_csv(data_dir / "intervals.csv")
        visits = pd.read_csv(data_dir / "visits.csv")
        envelope = load_envelope(data_dir / "bec_envelope.csv")
    except (OSError, ValueError) as error:
        print(f"run_baseline_backtest: {error}", file=sys.stderr)
        return EXIT_BAD_INPUT
    sample = select_intervals(intervals, per_bec=args.per_bec)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        sample.to_csv(args.out_dir / "baseline_sample.csv", index=False)
        print(f"wrote {args.out_dir / 'baseline_sample.csv'} with {len(sample)} intervals")
        return EXIT_OK
    trees = _read_trees(args.psp_dir, sample)
    if trees.empty:
        print("run_baseline_backtest: no tree rows for the sample", file=sys.stderr)
        return EXIT_BAD_INPUT
    rows, summary, skips = run_backtest(
        sample,
        trees,
        visits,
        envelope,
        args.out_dir / "runs",
        per_bec=args.per_bec,
        tree_age=args.tree_age,
    )
    rows.to_csv(args.out_dir / "baseline_backtest.csv", index=False)
    summary.to_csv(args.out_dir / "baseline_summary.csv", index=False)
    for name, by in (
        ("baseline_by_tsa.csv", ("BEC", "TSA")),
        ("baseline_by_species.csv", ("BEC", "species_group")),
        ("baseline_by_dbh.csv", ("BEC", "dbh_class")),
        ("baseline_by_ba.csv", ("BEC", "ba_class")),
    ):
        summarise(rows, by).to_csv(args.out_dir / name, index=False)
    skips.to_csv(args.out_dir / "baseline_skips.csv", index=False)
    skipped = skips[skips["reason"].fillna("") != ""]
    skipped.groupby("reason").size().rename("intervals").reset_index().to_csv(
        args.out_dir / "baseline_skip_reasons.csv", index=False
    )
    skipped.groupby(["BEC", "reason"]).size().rename("intervals").reset_index().to_csv(
        args.out_dir / "baseline_skipped_becs.csv", index=False
    )
    (args.out_dir / "baseline_report.md").write_text(_report(summary, skips, rows))
    print(f"wrote {args.out_dir} with {len(rows)} compared intervals")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
