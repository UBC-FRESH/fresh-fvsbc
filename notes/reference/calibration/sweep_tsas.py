"""Run the current target-excluded recipe on every TSA with PSP data.

The sweep is evidence: it records base aggregate and per-group calibration
metrics for every TSA label, including small groups. It does not freeze cards,
apply local calibration, or make a review decision.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd

REGISTRY = Path("notes/reference/calibration/candidate-registry.json")


def _design(frame: pd.DataFrame, zones: list[str]) -> np.ndarray:
    """Return the growth-free design."""
    return np.delete(bp.design(frame, zones), [6, 9], axis=1)


def main() -> None:
    """Fit every TSA and write the long-form sweep table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notes/reference/calibration/d9-tsa-calibration-sweep.csv"),
    )
    parser.add_argument("--target", default=None, help="Run one TSA label only.")
    args = parser.parse_args()

    frame = bp.load()
    zones = sorted(frame["zone"].dropna().unique())
    registry = json.loads(REGISTRY.read_text())
    frozen = {entry["target_tsa"] for entry in registry["candidates"]}
    rows = []
    targets = (
        [args.target] if args.target else sorted(frame["TSA_DESC"].dropna().astype(str).unique())
    )
    for tsa in targets:
        train = frame[frame["TSA_DESC"].astype(str) != tsa]
        target = frame[frame["TSA_DESC"].astype(str) == tsa]
        if target.empty:
            continue
        y: list[np.ndarray] = []
        p: list[np.ndarray] = []
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
            pred = bm._predict(xt, test["exposure"].to_numpy(), beta)
            metric = bp.metrics(test["dead"].to_numpy(), pred)
            rows.append(
                {
                    "tsa": tsa,
                    "group": group,
                    "n": int(metric["n"]),
                    "event_rate": metric["event_rate"],
                    "mean_pred": metric["mean_pred"],
                    "auc": metric["auc"],
                    "brier": metric["brier"],
                    "log_loss": metric["log_loss"],
                    "target_support": len(test) >= 500,
                    "frozen_card": tsa in frozen,
                    "target_sites": target["site"].nunique(),
                    "target_intervals": target["interval_id"].nunique(),
                }
            )
            y.append(test["dead"].to_numpy())
            p.append(pred)
        if not y:
            continue
        metric = bp.metrics(np.concatenate(y), np.concatenate(p))
        rows.append(
            {
                "tsa": tsa,
                "group": "ALL",
                "n": int(metric["n"]),
                "event_rate": metric["event_rate"],
                "mean_pred": metric["mean_pred"],
                "auc": metric["auc"],
                "brier": metric["brier"],
                "log_loss": metric["log_loss"],
                "target_support": True,
                "frozen_card": tsa in frozen,
                "target_sites": target["site"].nunique(),
                "target_intervals": target["interval_id"].nunique(),
            }
        )
        order = {"ALL": 0, **{group: index + 1 for index, group in enumerate(bp.GROUPS)}}
        rows.sort(key=lambda row: (row["tsa"], order[str(row["group"])]))
        print(
            f"{tsa:24s} n={int(metric['n']):7d} auc={metric['auc']:.3f} ll={metric['log_loss']:.3f}"
        )
    result = pd.DataFrame(rows)
    result.to_csv(args.output, index=False)
    print(f"wrote {args.output} with {len(result)} rows")


if __name__ == "__main__":
    main()
