"""Support-aware calibration policy with nested site cross-validation.

For each TSA, outer site folds measure policy performance. Inner site folds
choose between base, TSA partial symmetric, and BEC-unit partial symmetric.
No outer holdout row chooses the mode.
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

MIN_TREES = 500
PRIOR_TREES = 500
MODES = ("base", "tsa_partial_symmetric", "bec_partial_symmetric")


def _tsa_offsets(frame: pd.DataFrame) -> dict[str, float]:
    """Return shrunk TSA group offsets."""
    result: dict[str, float] = {}
    for group, part in frame.groupby("group"):
        if len(part) < MIN_TREES:
            continue
        eta = part["eta"].to_numpy(dtype=float)
        exposure = part["exposure"].to_numpy(dtype=float)
        dead = part["dead"].to_numpy(dtype=float)
        base = 1.0 - np.exp(-exposure * np.exp(np.clip(eta, -20, 20)))
        if abs(float(base.mean()) - float(dead.mean())) <= 0.03:
            continue
        shrink = len(part) / (len(part) + PRIOR_TREES)
        result[str(group)] = shrink * _delta(eta, dead, exposure)
    return result


def _bec_offsets(
    frame: pd.DataFrame,
) -> tuple[dict[tuple[str, str], float], dict[tuple[str, str], float]]:
    """Return unit and parent-zone offsets."""
    unit: dict[tuple[str, str], float] = {}
    zone: dict[tuple[str, str], float] = {}
    for key, target in (("unit", unit), ("bec_zone", zone)):
        for (level, group), part in frame.groupby([key, "group"]):
            if len(part) < MIN_TREES:
                continue
            eta = part["eta"].to_numpy(dtype=float)
            exposure = part["exposure"].to_numpy(dtype=float)
            dead = part["dead"].to_numpy(dtype=float)
            base = 1.0 - np.exp(-exposure * np.exp(np.clip(eta, -20, 20)))
            if abs(float(base.mean()) - float(dead.mean())) <= 0.03:
                continue
            shrink = len(part) / (len(part) + PRIOR_TREES)
            target[(str(level), str(group))] = shrink * _delta(eta, dead, exposure)
    return unit, zone


def _predict(frame: pd.DataFrame, calibration: pd.DataFrame, mode: str) -> np.ndarray:
    """Predict with one calibration mode."""
    exposure = frame["exposure"].to_numpy(dtype=float)
    eta = frame["eta"].to_numpy(dtype=float)
    if mode == "base":
        delta = np.zeros(len(frame))
    elif mode == "tsa_partial_symmetric":
        offsets = _tsa_offsets(calibration)
        delta = frame["group"].astype(str).map(offsets).fillna(0.0).to_numpy()
    else:
        unit, zone = _bec_offsets(calibration)
        delta = np.array(
            [
                unit.get((unit_name, group), zone.get((zone_name, group), 0.0))
                for unit_name, zone_name, group in zip(
                    frame["unit"].astype(str),
                    frame["bec_zone"].astype(str),
                    frame["group"].astype(str),
                    strict=True,
                )
            ]
        )
    return 1.0 - np.exp(-exposure * np.exp(np.clip(eta + delta, -20, 20)))


def _log_loss(frame: pd.DataFrame, calibration: pd.DataFrame, mode: str) -> float:
    """Return log loss for one mode."""
    pred = _predict(frame, calibration, mode)
    return bp.metrics(frame["dead"].to_numpy(), pred)["log_loss"]


def _folds(sites: list[str], n_folds: int, rng: np.random.Generator) -> list[set[str]]:
    """Return site folds."""
    if n_folds >= len(sites):
        return [{site} for site in sites]
    shuffled = list(rng.permutation(sites))
    return [set(shuffled[index::n_folds]) for index in range(n_folds)]


def _choose_mode(frame: pd.DataFrame, rng: np.random.Generator) -> str:
    """Choose a mode by inner site cross-validation."""
    sites = sorted(frame["site"].astype(str).unique())
    inner_folds = _folds(sites, min(3, len(sites)), rng)
    scores: dict[str, list[float]] = {mode: [] for mode in MODES}
    for hold_sites in inner_folds:
        hold = frame[frame["site"].astype(str).isin(hold_sites)]
        calibration = frame[~frame["site"].astype(str).isin(hold_sites)]
        if calibration.empty or hold.empty:
            continue
        for mode in MODES:
            scores[mode].append(_log_loss(hold, calibration, mode))
    means = {
        mode: float(np.mean(values)) if values else float("inf") for mode, values in scores.items()
    }
    return min(MODES, key=lambda mode: means[mode])


def main() -> None:
    """Run nested policy evaluation for one TSA."""
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
        target_rows.append(
            pd.DataFrame(
                {
                    "site": test["site"].to_numpy(),
                    "group": group,
                    "eta": xt @ beta,
                    "exposure": test["exposure"].to_numpy(),
                    "dead": test["dead"].to_numpy(),
                    "unit": test["unit"].to_numpy(),
                    "bec_zone": test["bec_zone"].to_numpy(),
                }
            )
        )
    if not target_rows:
        raise SystemExit(f"no fitted groups for {args.target}")
    target_frame = pd.concat(target_rows, ignore_index=True)
    sites = sorted(target_frame["site"].astype(str).unique())
    rng = np.random.default_rng(42)
    outer_folds = _folds(sites, min(5, len(sites)), rng)
    policy_pred: list[np.ndarray] = []
    base_pred: list[np.ndarray] = []
    observed: list[np.ndarray] = []
    selected: dict[str, int] = dict.fromkeys(MODES, 0)
    for hold_sites in outer_folds:
        hold = target_frame[target_frame["site"].astype(str).isin(hold_sites)]
        calibration = target_frame[~target_frame["site"].astype(str).isin(hold_sites)]
        if calibration.empty or hold.empty:
            continue
        mode = _choose_mode(calibration, rng)
        selected[mode] += 1
        policy_pred.append(_predict(hold, calibration, mode))
        base_pred.append(_predict(hold, calibration, "base"))
        observed.append(hold["dead"].to_numpy())
    if not observed:
        raise SystemExit(f"no outer folds for {args.target}")
    y = np.concatenate(observed)
    policy = bp.metrics(y, np.concatenate(policy_pred))
    base = bp.metrics(y, np.concatenate(base_pred))
    row = {
        "tsa": args.target,
        "n": int(policy["n"]),
        "target_sites": len(sites),
        "outer_folds": len(observed),
        "policy_mode": max(selected, key=selected.get),
        "base_log_loss": base["log_loss"],
        "policy_log_loss": policy["log_loss"],
        "delta_log_loss": policy["log_loss"] - base["log_loss"],
        "policy_auc": policy["auc"],
        "base_auc": base["auc"],
        "selected_base": selected["base"],
        "selected_tsa": selected["tsa_partial_symmetric"],
        "selected_bec": selected["bec_partial_symmetric"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row]).to_csv(args.output, index=False)
    print(f"wrote {args.output} for {args.target}")


if __name__ == "__main__":
    main()
