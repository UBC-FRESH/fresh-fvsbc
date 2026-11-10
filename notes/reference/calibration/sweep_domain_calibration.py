"""Estimate BEC-domain offsets from training TSAs and apply them to a holdout.

The target TSA contributes no calibration rows. Offsets are learned from the
remaining TSAs at BEC unit, parent zone, and global group levels.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd
from bec_units import assign_units
from fit_candidate import _delta, _design

PRIOR_TREES = 500
MIN_TREES = 500


def _offsets(
    frame: pd.DataFrame,
    key: str,
    *,
    symmetric: bool,
) -> dict[tuple[str, str], float]:
    """Return shrunk offsets for one hierarchy key."""
    result: dict[tuple[str, str], float] = {}
    for (level, group), part in frame.groupby([key, "group"]):
        if len(part) < MIN_TREES:
            continue
        eta = part["eta"].to_numpy(dtype=float)
        exposure = part["exposure"].to_numpy(dtype=float)
        dead = part["dead"].to_numpy(dtype=float)
        base = 1.0 - np.exp(-exposure * np.exp(np.clip(eta, -20, 20)))
        gap = float(base.mean()) - float(dead.mean())
        trigger = abs(gap) > 0.03 if symmetric else gap > 0.03
        if trigger:
            shrink = len(part) / (len(part) + PRIOR_TREES)
            result[(str(level), str(group))] = shrink * _delta(eta, dead, exposure)
    return result


def main() -> None:
    """Run one TSA and write base plus domain-calibration rows."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frame = assign_units(bp.load())
    zones = sorted(frame["zone"].dropna().unique())
    train = frame[frame["TSA_DESC"].astype(str) != args.target]
    target = frame[frame["TSA_DESC"].astype(str) == args.target].copy()
    if target.empty:
        raise SystemExit(f"no rows for {args.target}")
    y: list = []
    p: list = []
    train_rows: list[pd.DataFrame] = []
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
        pred = bm._predict(xt, test["exposure"].to_numpy(), beta)
        y.append(test["dead"].to_numpy())
        p.append(pred)
        train_rows.append(
            pd.DataFrame(
                {
                    "group": group,
                    "eta": x @ beta,
                    "exposure": part["exposure"].to_numpy(),
                    "dead": part["dead"].to_numpy(),
                    "unit": part["unit"].to_numpy(),
                    "bec_zone": part["bec_zone"].to_numpy(),
                }
            )
        )
        target_rows.append(
            pd.DataFrame(
                {
                    "group": group,
                    "eta": xt @ beta,
                    "exposure": test["exposure"].to_numpy(),
                    "dead": test["dead"].to_numpy(),
                    "unit": test["unit"].to_numpy(),
                    "bec_zone": test["bec_zone"].to_numpy(),
                }
            )
        )
    if not y:
        raise SystemExit(f"no fitted groups for {args.target}")
    base = bp.metrics(np.concatenate(y), np.concatenate(p))
    train_frame = pd.concat(train_rows, ignore_index=True)
    target_frame = pd.concat(target_rows, ignore_index=True)
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
            "delta_log_loss": 0.0,
            "improved": False,
        }
    ]
    for mode, symmetric in (("domain_one_sided", False), ("domain_symmetric", True)):
        unit = _offsets(train_frame, "unit", symmetric=symmetric)
        zone = _offsets(train_frame, "bec_zone", symmetric=symmetric)
        global_offsets = _offsets(
            train_frame.assign(global_level="global"), "global_level", symmetric=symmetric
        )
        delta = np.array(
            [
                unit.get(
                    (unit_name, group),
                    zone.get((zone_name, group), global_offsets.get(("global", group), 0.0)),
                )
                for unit_name, zone_name, group in zip(
                    target_frame["unit"].astype(str),
                    target_frame["bec_zone"].astype(str),
                    target_frame["group"],
                    strict=True,
                )
            ]
        )
        pred = 1.0 - np.exp(
            -target_frame["exposure"].to_numpy()
            * np.exp(np.clip(target_frame["eta"].to_numpy() + delta, -20, 20))
        )
        metric = bp.metrics(target_frame["dead"].to_numpy(), pred)
        rows.append(
            {
                "tsa": args.target,
                "mode": mode,
                "n": int(metric["n"]),
                "event_rate": metric["event_rate"],
                "mean_pred": metric["mean_pred"],
                "auc": metric["auc"],
                "brier": metric["brier"],
                "log_loss": metric["log_loss"],
                "delta_log_loss": float(metric["log_loss"]) - float(base["log_loss"]),
                "improved": bool(metric["log_loss"] < base["log_loss"]),
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"wrote {args.output} for {args.target}")


if __name__ == "__main__":
    main()
