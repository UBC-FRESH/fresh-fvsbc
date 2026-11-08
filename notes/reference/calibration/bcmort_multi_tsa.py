"""Multi-TSA calibration backtest for the provincial mortality model.

Fits the D9.42 provincial model without seven target TSAs, then applies a
species-group local intercept from k target sites to each target.  This tests
whether the Quesnel calibration result generalizes.

This is a prototype, not an FVS integration.
"""

from __future__ import annotations

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd

TARGETS = (
    "Okanagan TSA",
    "Quesnel TSA",
    "Arrowsmith TSA",
    "MacKenzie TSA",
    "Merritt TSA",
    "Haida Gwaii TSA",
    "Morice TSA",
)
KS = (10, 20)


def _delta(eta: np.ndarray, y: np.ndarray, exposure: np.ndarray) -> float:
    offset = np.log(exposure) + eta
    value = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(value + offset, -20, 20))
        weight = np.clip(mu, 1e-8, None)
        z = value + offset + (y - mu) / weight
        value = float(np.sum(weight * (z - offset)) / np.sum(weight))
    return value


def _calibrate(target: pd.DataFrame, k: int) -> dict[str, float]:
    sites = sorted(target["site"].unique())
    if k >= len(sites):
        return {}
    rng = np.random.default_rng(42)
    values = []
    for _ in range(30):
        rng.shuffle(sites)
        calibration = target[target["site"].isin(set(sites[:k]))]
        holdout = target[target["site"].isin(set(sites[k:]))]
        if calibration.empty or holdout.empty:
            continue
        global_delta = _delta(
            calibration["eta"].to_numpy(),
            calibration["dead"].to_numpy(),
            calibration["exposure"].to_numpy(),
        )
        deltas = {}
        for group, part in calibration.groupby("group"):
            if len(part) >= 50:
                deltas[group] = _delta(
                    part["eta"].to_numpy(), part["dead"].to_numpy(), part["exposure"].to_numpy()
                )
            else:
                deltas[group] = global_delta
        delta = holdout["group"].map(deltas).fillna(global_delta).to_numpy()
        pred = 1.0 - np.exp(
            -holdout["exposure"].to_numpy()
            * np.exp(np.clip(holdout["eta"].to_numpy() + delta, -20, 20))
        )
        values.append(bp.metrics(holdout["dead"].to_numpy(), pred))
    return pd.DataFrame(values).mean().to_dict()


def _adaptive(target: pd.DataFrame, k: int, threshold: float = 0.03) -> dict[str, float]:
    """Apply local offsets only when calibration sites show bias above threshold."""
    sites = sorted(target["site"].unique())
    if k >= len(sites):
        return {}
    rng = np.random.default_rng(42)
    values = []
    for _ in range(30):
        rng.shuffle(sites)
        calibration = target[target["site"].isin(set(sites[:k]))]
        holdout = target[target["site"].isin(set(sites[k:]))]
        if calibration.empty or holdout.empty:
            continue
        base_cal = 1.0 - np.exp(
            -calibration["exposure"].to_numpy()
            * np.exp(np.clip(calibration["eta"].to_numpy(), -20, 20))
        )
        base_hold = 1.0 - np.exp(
            -holdout["exposure"].to_numpy() * np.exp(np.clip(holdout["eta"].to_numpy(), -20, 20))
        )
        if float(base_cal.mean()) <= float(calibration["dead"].mean()) + threshold:
            values.append(bp.metrics(holdout["dead"].to_numpy(), base_hold))
            continue
        global_delta = _delta(
            calibration["eta"].to_numpy(),
            calibration["dead"].to_numpy(),
            calibration["exposure"].to_numpy(),
        )
        deltas = {}
        for group, part in calibration.groupby("group"):
            if len(part) >= 50:
                deltas[group] = _delta(
                    part["eta"].to_numpy(), part["dead"].to_numpy(), part["exposure"].to_numpy()
                )
            else:
                deltas[group] = global_delta
        delta = holdout["group"].map(deltas).fillna(global_delta).to_numpy()
        pred = 1.0 - np.exp(
            -holdout["exposure"].to_numpy()
            * np.exp(np.clip(holdout["eta"].to_numpy() + delta, -20, 20))
        )
        values.append(bp.metrics(holdout["dead"].to_numpy(), pred))
    return pd.DataFrame(values).mean().to_dict()


def main() -> None:
    """Fit once, then backtest base and local calibration for each target TSA."""
    frame = bp.load()
    train = frame[~frame["TSA_DESC"].astype(str).isin(TARGETS)]
    target = frame[frame["TSA_DESC"].astype(str).isin(TARGETS)].copy()
    target["site"] = target["interval_id"].str.split("|").str[0]
    zones = sorted(frame["zone"].dropna().unique())
    pieces = []
    for group in bp.GROUPS:
        tr = train[train["group"] == group]
        if len(tr) < 1000:
            continue
        x = bp.design(tr, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, tr["dead"].to_numpy(), tr["exposure"].to_numpy())
        te = target[target["group"] == group]
        if te.empty:
            continue
        xt = bp.design(te, zones)
        xt[:, 1:] = (xt[:, 1:] - mean) / scale
        pieces.append(
            pd.DataFrame(
                {
                    "tsa": te["TSA_DESC"].astype(str).to_numpy(),
                    "site": te["site"].to_numpy(),
                    "group": group,
                    "eta": xt @ beta,
                    "exposure": te["exposure"].to_numpy(),
                    "dead": te["dead"].to_numpy(),
                }
            )
        )
    predictions = pd.concat(pieces, ignore_index=True)
    rows = []
    for tsa in TARGETS:
        part = predictions[predictions["tsa"] == tsa]
        if part.empty:
            continue
        base = bp.metrics(
            part["dead"].to_numpy(),
            1.0 - np.exp(-part["exposure"].to_numpy() * np.exp(np.clip(part["eta"], -20, 20))),
        )
        print(
            f"{tsa:20s} base mean={base['mean_pred']:.3f} obs={base['event_rate']:.3f} "
            f"auc={base['auc']:.3f} ll={base['log_loss']:.3f}"
        )
        for k in KS:
            local = _calibrate(part, k)
            if not local:
                continue
            rows.append(
                {
                    "tsa": tsa,
                    "k": k,
                    "n_sites": part["site"].nunique(),
                    "base_mean": base["mean_pred"],
                    "base_auc": base["auc"],
                    "base_log_loss": base["log_loss"],
                    "base_brier": base["brier"],
                    "local_mean": local["mean_pred"],
                    "local_auc": local["auc"],
                    "local_log_loss": local["log_loss"],
                    "local_brier": local["brier"],
                    "event_rate": base["event_rate"],
                }
            )
            print(
                f"  k={k:2d} mean={local['mean_pred']:.3f} auc={local['auc']:.3f} "
                f"ll={local['log_loss']:.3f} brier={local['brier']:.3f}"
            )
        adaptive = _adaptive(part, 20)
        if adaptive:
            rows.append(
                {
                    "tsa": tsa,
                    "k": "adaptive20",
                    "n_sites": part["site"].nunique(),
                    "base_mean": base["mean_pred"],
                    "base_auc": base["auc"],
                    "base_log_loss": base["log_loss"],
                    "base_brier": base["brier"],
                    "local_mean": adaptive["mean_pred"],
                    "local_auc": adaptive["auc"],
                    "local_log_loss": adaptive["log_loss"],
                    "local_brier": adaptive["brier"],
                    "event_rate": base["event_rate"],
                }
            )
            print(
                f"  adaptive20 mean={adaptive['mean_pred']:.3f} auc={adaptive['auc']:.3f} "
                f"ll={adaptive['log_loss']:.3f} brier={adaptive['brier']:.3f}"
            )
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-multi-tsa-calibration-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
