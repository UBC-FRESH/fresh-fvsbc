#!/usr/bin/env python3
"""Select a fixed candidate from the training fold of a probe.

The probe itself only evaluates fixed candidates. This script applies the selection rule written
before a direct-calibration run: keep candidates inside the training BA/TPH bands, minimise the
larger normalized absolute bias, then break ties by site-pass counts. The test fold is reported but
never used to choose.

The output is ``selection.json`` next to ``--out``; the selected label is the frozen candidate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

#: The bands the calibration design pre-registers.
BA_ABS: float = 3.0
BA_PCT: float = 10.0
TPH_PCT: float = 15.0


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="select_probe_candidate",
        description="Choose a fixed candidate on the training fold of one probe.",
    )
    parser.add_argument("--probe", required=True, type=Path, metavar="FILE")
    parser.add_argument("--out", required=True, type=Path, metavar="FILE")
    parser.add_argument("--train-label", default="train", metavar="LABEL")
    parser.add_argument("--test-label", default="test", metavar="LABEL")
    return parser


def _metrics(frame: pd.DataFrame) -> dict[str, Any]:
    """Return one candidate/fold row with bias, percentage bias, and site-pass counts.

    Parameters
    ----------
    frame : pandas.DataFrame
        The rows for one candidate and one fold.

    Returns
    -------
    dict
        The metrics used by the selection rule.
    """
    observed_ba = float(frame["observed_ba1"].mean())
    observed_tph = float(frame["observed_tph1"].mean())
    ba_bias = float(frame["ba_error"].mean())
    tph_bias = float(frame["tph_error"].mean())
    by_site = frame.groupby(frame["interval_id"].astype(str).str.split("|").str[0])[
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
    return {
        "intervals": len(frame),
        "sites": len(by_site),
        "ba_bias": ba_bias,
        "ba_pct": ba_bias / observed_ba * 100.0 if observed_ba else float("nan"),
        "tph_bias": tph_bias,
        "tph_pct": tph_bias / observed_tph * 100.0 if observed_tph else float("nan"),
        "ba_sites_pass": int((site_ba <= BA_PCT).sum()),
        "tph_sites_pass": int((site_tph <= TPH_PCT).sum()),
    }


def _passes(row: dict[str, Any]) -> bool:
    """Say whether a candidate is inside both training bands."""
    return (abs(float(row["ba_bias"])) <= BA_ABS or abs(float(row["ba_pct"])) <= BA_PCT) and abs(
        float(row["tph_pct"])
    ) <= TPH_PCT


def _score(row: dict[str, Any]) -> tuple[float, int, int]:
    """Return the pre-registered ordering key, smallest first."""
    return (
        max(abs(float(row["ba_pct"])) / BA_PCT, abs(float(row["tph_pct"])) / TPH_PCT),
        -int(row["ba_sites_pass"]),
        -int(row["tph_sites_pass"]),
    )


def main(argv: list[str] | None = None) -> int:
    """Apply the selection rule and write the frozen candidate.

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
    frame = pd.read_csv(args.probe)
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for (candidate, fold), group in frame.groupby(["candidate", "fold"], sort=True):
        rows[(str(candidate), str(fold))] = _metrics(group)
    train = {
        candidate: metrics
        for (candidate, fold), metrics in rows.items()
        if fold == args.train_label
    }
    passing = {candidate: metrics for candidate, metrics in train.items() if _passes(metrics)}
    selected = min(passing, key=lambda candidate: _score(passing[candidate])) if passing else None
    payload = {
        "selected": selected,
        "training_candidates": train,
        "training_passing": sorted(passing),
        "test": {} if selected is None else rows.get((selected, args.test_label), {}),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"selected: {selected}")
    for candidate, metrics in sorted(train.items()):
        marker = " *" if candidate == selected else ""
        print(
            f"{candidate:12s} BA {metrics['ba_pct']:7.2f}% "
            f"TPH {metrics['tph_pct']:7.2f}% "
            f"sites {metrics['ba_sites_pass']:3d}/{metrics['tph_sites_pass']:3d}{marker}"
        )
    if selected is not None:
        test = rows[(selected, args.test_label)]
        print(
            f"test {selected}: BA {test['ba_pct']:.2f}% TPH {test['tph_pct']:.2f}% "
            f"sites {test['ba_sites_pass']}/{test['tph_sites_pass']}"
        )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
