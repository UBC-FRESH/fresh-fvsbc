"""Prototype target-TSA intercept calibration for BCMORT.

Fit fixed effects on a source TSA, estimate a target intercept on half the
target sites, and test on the other half. This tests local calibration, not a
new FVS implementation.
"""

from __future__ import annotations

import bcmort_prototype as bm
import numpy as np
import pandas as pd


def _delta_fit(eta: np.ndarray, y: np.ndarray, exposure: np.ndarray) -> float:
    offset = np.log(exposure) + eta
    delta = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(delta + offset, -20, 20))
        w = np.clip(mu, 1e-8, None)
        z = delta + offset + (y - mu) / w
        delta = float(np.sum(w * (z - offset)) / np.sum(w))
    return delta


def _run(frame: pd.DataFrame, bec: str, source: str, target: str, repeats: int = 40) -> None:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)].copy()
    test["site"] = test["interval_id"].str.split("|").str[0]
    xtr = bm._design(train)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    sites = sorted(test["site"].unique())
    rng = np.random.default_rng(42)
    rows = []
    for _ in range(repeats):
        rng.shuffle(sites)
        cut = max(1, len(sites) // 2)
        cal = set(sites[:cut])
        hold = set(sites[cut:])
        cal_frame = test[test["site"].isin(cal)]
        hold_frame = test[test["site"].isin(hold)]
        if cal_frame.empty or hold_frame.empty:
            continue
        xc = bm._design(cal_frame)
        xc[:, 1:] = (xc[:, 1:] - mean) / scale
        xh = bm._design(hold_frame)
        xh[:, 1:] = (xh[:, 1:] - mean) / scale
        eta_c = xc @ beta
        eta_h = xh @ beta
        delta = _delta_fit(eta_c, cal_frame["dead"].to_numpy(), cal_frame["exposure"].to_numpy())
        base = bm._predict(xh, hold_frame["exposure"].to_numpy(), beta)
        local = 1.0 - np.exp(
            -hold_frame["exposure"].to_numpy() * np.exp(np.clip(eta_h + delta, -20, 20))
        )
        y = hold_frame["dead"].to_numpy()
        mb = bm._metrics(y, base)
        ml = bm._metrics(y, local)
        rows.append(
            {
                "delta": delta,
                "base_logloss": mb["log_loss"],
                "local_logloss": ml["log_loss"],
                "base_brier": mb["brier"],
                "local_brier": ml["brier"],
                "base_mean": mb["mean_pred"],
                "local_mean": ml["mean_pred"],
                "event_rate": float(y.mean()),
                "cal_sites": len(cal),
                "test_sites": len(hold),
            }
        )
    d = pd.DataFrame(rows)
    print(f"{bec}: {source} -> {target}  repeats={len(d)} cal_sites={d.cal_sites.mean():.1f}")
    print(
        d[
            [
                "delta",
                "event_rate",
                "base_mean",
                "local_mean",
                "base_logloss",
                "local_logloss",
                "base_brier",
                "local_brier",
            ]
        ]
        .mean()
        .round(4)
        .to_dict()
    )


def main() -> None:
    """Run the target-TSA intercept prototype."""
    frame = bm._load()
    _run(frame, "MSdm1", "Okanagan TSA", "Boundary TSA")
    _run(frame, "MSdm1", "Boundary TSA", "Okanagan TSA")
    _run(frame, "SBSmw", "Quesnel TSA", "Prince George TSA")
    _run(frame, "SBSmw", "Prince George TSA", "Quesnel TSA")


if __name__ == "__main__":
    main()
