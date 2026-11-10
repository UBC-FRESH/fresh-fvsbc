"""Evaluate one-sided and symmetric local rules for one TSA label.

The sweep records base, one-sided, and symmetric metrics for the same
target-excluded fit. It does not modify a frozen card or apply a rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd
from fit_candidate import _design, _local_metrics

REGISTRY = Path("notes/reference/calibration/candidate-registry.json")
MIN_TREES = 500
BOOTSTRAP = 40


def main() -> None:
    """Run one TSA and write its mode-comparison rows."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frame = bp.load()
    zones = sorted(frame["zone"].dropna().unique())
    registry = json.loads(REGISTRY.read_text())
    frozen = {entry["target_tsa"] for entry in registry["candidates"]}
    train = frame[frame["TSA_DESC"].astype(str) != args.target]
    target = frame[frame["TSA_DESC"].astype(str) == args.target].copy()
    if target.empty:
        raise SystemExit(f"no rows for {args.target}")
    y: list = []
    p: list = []
    target_rows: list[pd.DataFrame] = []
    for group in bp.GROUPS:
        part = train[train["group"] == group]
        test = target[target["group"] == group]
        if len(part) < 1000 or test.empty:
            continue
        x = _design(part, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, part["dead"].to_numpy(), part["exposure"].to_numpy())
        xt = _design(test, zones)
        xt[:, 1:] = (xt[:, 1:] - mean) / scale
        eta = xt @ beta
        pred = bm._predict(xt, test["exposure"].to_numpy(), beta)
        y.append(test["dead"].to_numpy())
        p.append(pred)
        target_rows.append(
            pd.DataFrame(
                {
                    "site": test["site"].to_numpy(),
                    "group": group,
                    "eta": eta,
                    "exposure": test["exposure"].to_numpy(),
                    "dead": test["dead"].to_numpy(),
                }
            )
        )
    if not y:
        raise SystemExit(f"no fitted groups for {args.target}")
    base = bp.metrics(np.concatenate(y), np.concatenate(p))
    sites = sorted(target["site"].astype(str).unique())
    k = min(20, len(sites) - 1) if len(sites) >= 2 else 0
    rows = [
        {
            "tsa": args.target,
            "mode": "base",
            "n": int(base["n"]),
            "event_rate": base["event_rate"],
            "mean_pred": base["mean_pred"],
            "auc": base["auc"],
            "brier": base["brier"],
            "log_loss": base["log_loss"],
            "calibration_sites": 0,
            "holdout_sites": 0,
            "target_sites": len(sites),
            "delta_log_loss": 0.0,
            "improved": False,
            "frozen_card": args.target in frozen,
        }
    ]
    if k:
        target_frame = pd.concat(target_rows, ignore_index=True)
        for mode, symmetric in (("one_sided", False), ("symmetric", True)):
            local = _local_metrics(
                target_frame,
                calibration_sites=k,
                bootstrap=BOOTSTRAP,
                symmetric=symmetric,
            )
            mean = local.get("mean_metrics")
            if not mean:
                continue
            rows.append(
                {
                    "tsa": args.target,
                    "mode": mode,
                    "n": int(float(mean["n"])),
                    "event_rate": float(mean["event_rate"]),
                    "mean_pred": float(mean["mean_pred"]),
                    "auc": float(mean["auc"]),
                    "brier": float(mean["brier"]),
                    "log_loss": float(mean["log_loss"]),
                    "calibration_sites": k,
                    "holdout_sites": int(local["holdout_sites"]),
                    "target_sites": len(sites),
                    "delta_log_loss": float(mean["log_loss"]) - float(base["log_loss"]),
                    "improved": bool(mean["log_loss"] < base["log_loss"]),
                    "frozen_card": args.target in frozen,
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"wrote {args.output} for {args.target}")


if __name__ == "__main__":
    main()
