"""Evaluate BEC-unit local calibration for one TSA holdout.

Unit-by-group offsets are estimated from calibration sites and fall back to
parent-zone-by-group offsets when a unit has too little support. Both are
shrunk by ``n / (n + 500)``.
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

BOOTSTRAP = 40
PRIOR_TREES = 500
MIN_TREES = 500


def _offsets(
    calibration: pd.DataFrame,
    *,
    key: str,
    symmetric: bool,
) -> dict[tuple[str, str], float]:
    """Estimate shrunk offsets at one hierarchy key (unit or zone)."""
    values: dict[tuple[str, str], float] = {}
    for (level, group), part in calibration.groupby([key, "group"]):
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
            values[(str(level), str(group))] = shrink * _delta(eta, dead, exposure)
    return values


def _metrics(
    frame: pd.DataFrame,
    *,
    calibration_sites: int,
    bootstrap: int,
    symmetric: bool,
) -> dict[str, object]:
    """Evaluate unit-to-zone fallback offsets on held-out sites."""
    sites = sorted(frame["site"].astype(str).unique())
    if len(sites) <= calibration_sites:
        return {"evaluated": False, "reason": "not enough target sites"}
    rng = np.random.default_rng(42)
    rows: list[dict[str, float]] = []
    for _ in range(bootstrap):
        shuffled = list(rng.permutation(sites))
        calibration = set(shuffled[:calibration_sites])
        cal = frame[frame["site"].isin(calibration)]
        hold = frame[~frame["site"].isin(calibration)]
        if cal.empty or hold.empty:
            continue
        unit = _offsets(cal, key="unit", symmetric=symmetric)
        zone = _offsets(cal, key="bec_zone", symmetric=symmetric)
        hold_unit = hold["unit"].astype(str)
        hold_zone = hold["bec_zone"].astype(str)
        delta = np.array(
            [
                unit.get((unit_name, group), zone.get((zone_name, group), 0.0))
                for unit_name, zone_name, group in zip(
                    hold_unit, hold_zone, hold["group"], strict=True
                )
            ]
        )
        pred = 1.0 - np.exp(
            -hold["exposure"].to_numpy() * np.exp(np.clip(hold["eta"].to_numpy() + delta, -20, 20))
        )
        rows.append(bp.metrics(hold["dead"].to_numpy(), pred))
    if not rows:
        return {"evaluated": False, "reason": "no usable splits"}
    return {
        "evaluated": True,
        "calibration_sites": calibration_sites,
        "holdout_sites": len(sites) - calibration_sites,
        "bootstrap": bootstrap,
        "mean_metrics": pd.DataFrame(rows).mean(numeric_only=True).to_dict(),
    }


def main() -> None:
    """Run one TSA and write base plus BEC-unit rows."""
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
                    "unit": test["unit"].to_numpy(),
                    "bec_zone": test["bec_zone"].to_numpy(),
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
        }
    ]
    if k:
        target_frame = pd.concat(target_rows, ignore_index=True)
        for mode, symmetric in (("bec_one_sided", False), ("bec_symmetric", True)):
            local = _metrics(
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
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"wrote {args.output} for {args.target}")


if __name__ == "__main__":
    main()
