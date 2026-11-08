"""Target-TSA calibration for the provincial mortality model.

Fit the D9.42 provincial model without Quesnel, then use k Quesnel sites to
estimate species-group intercept offsets and test the remaining Quesnel sites.
This is a local calibration layer, not a new provincial fit or an FVS change.
"""

from __future__ import annotations

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd

TARGET = "Quesnel TSA"
KS = (1, 2, 3, 5, 10, 20)


def _delta(eta: np.ndarray, y: np.ndarray, exposure: np.ndarray) -> float:
    offset = np.log(exposure) + eta
    value = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(value + offset, -20, 20))
        weight = np.clip(mu, 1e-8, None)
        z = value + offset + (y - mu) / weight
        value = float(np.sum(weight * (z - offset)) / np.sum(weight))
    return value


def main() -> None:
    """Fit the source model, then run the Quesnel site-split calibration curve."""
    frame = bp.load()
    train = frame[frame["TSA_DESC"].astype(str) != TARGET]
    target = frame[frame["TSA_DESC"].astype(str) == TARGET].copy()
    target["site"] = target["interval_id"].str.split("|").str[0]
    zones = sorted(frame["zone"].dropna().unique())
    pieces = []
    for group in bp.GROUPS:
        tr = train[train["group"] == group]
        te = target[target["group"] == group]
        if len(tr) < 1000 or te.empty:
            continue
        x = bp.design(tr, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, tr["dead"].to_numpy(), tr["exposure"].to_numpy())
        xt = bp.design(te, zones)
        xt[:, 1:] = (xt[:, 1:] - mean) / scale
        pieces.append(
            pd.DataFrame(
                {
                    "site": te["site"].to_numpy(),
                    "group": group,
                    "eta": xt @ beta,
                    "exposure": te["exposure"].to_numpy(),
                    "dead": te["dead"].to_numpy(),
                }
            )
        )
    target = pd.concat(pieces, ignore_index=True)
    sites = sorted(target["site"].unique())
    rng = np.random.default_rng(42)
    rows = []
    for k in KS:
        if k >= len(sites):
            continue
        values = []
        for _ in range(40):
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
        if not values:
            continue
        mean = pd.DataFrame(values).mean()
        rows.append(
            {
                "k": float(k),
                "n_test_sites": float(len(sites) - k),
                "mean": mean["mean_pred"],
                "event_rate": mean["event_rate"],
                "auc": mean["auc"],
                "brier": mean["brier"],
                "log_loss": mean["log_loss"],
            }
        )
        print(
            f"k={k:2d} mean={mean['mean_pred']:.3f} obs={mean['event_rate']:.3f} "
            f"auc={mean['auc']:.3f} ll={mean['log_loss']:.3f} brier={mean['brier']:.3f}"
        )
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-provincial-calibration-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
