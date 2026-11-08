"""Target-TSA intercept calibration curve for the BCMORT prototype.

Fits the D9.35 height/DBH model on a source TSA, then uses k target sites to
estimate one target intercept and tests the remaining target sites.  This is a
deployment-calibration diagnostic, not a hierarchical model or an FVS change.
"""

from __future__ import annotations

from pathlib import Path

import bcmort_hd as bh
import bcmort_prototype as bm
import numpy as np
import pandas as pd

KS = (1, 2, 3, 5, 10, 20)


def _run(
    frame: pd.DataFrame, bec: str, source: str, target: str, repeats: int = 40
) -> list[dict[str, float]]:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)].copy()
    test["site"] = test["interval_id"].str.split("|").str[0]
    xtr = bh.design(train)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    xte = bh.design(test)
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    base = bm._metrics(test["dead"].to_numpy(), bm._predict(xte, test["exposure"].to_numpy(), beta))
    sites = sorted(test["site"].unique())
    rng = np.random.default_rng(42)
    rows = []
    for k in KS:
        if k >= len(sites):
            continue
        values = []
        for _ in range(repeats):
            rng.shuffle(sites)
            calibration = test[test["site"].isin(set(sites[:k]))]
            holdout = test[test["site"].isin(set(sites[k:]))]
            if calibration.empty or holdout.empty:
                continue
            xc = bh.design(calibration)
            xh = bh.design(holdout)
            xc[:, 1:] = (xc[:, 1:] - mean) / scale
            xh[:, 1:] = (xh[:, 1:] - mean) / scale
            delta = bh._delta(
                xc @ beta, calibration["dead"].to_numpy(), calibration["exposure"].to_numpy()
            )
            pred = 1.0 - np.exp(
                -holdout["exposure"].to_numpy() * np.exp(np.clip(xh @ beta + delta, -20, 20))
            )
            metric = bm._metrics(holdout["dead"].to_numpy(), pred)
            values.append(
                {
                    "delta": delta,
                    "event_rate": metric["event_rate"],
                    "mean_pred": metric["mean_pred"],
                    "log_loss": metric["log_loss"],
                    "brier": metric["brier"],
                    "auc": metric["auc"],
                }
            )
        value = pd.DataFrame(values).mean()
        rows.append(
            {
                "bec": bec,
                "source_tsa": source,
                "target_tsa": target,
                "k": float(k),
                "base_mean": base["mean_pred"],
                "base_log_loss": base["log_loss"],
                "base_brier": base["brier"],
                "base_auc": base["auc"],
                "local_mean": value["mean_pred"],
                "local_log_loss": value["log_loss"],
                "local_brier": value["brier"],
                "local_auc": value["auc"],
                "delta": value["delta"],
                "event_rate": value["event_rate"],
            }
        )
        print(
            f"{bec}: {source} -> {target}  k={k:2d}  "
            f"log loss {base['log_loss']:.3f} -> {value['log_loss']:.3f}; "
            f"mean {value['mean_pred']:.3f} vs {value['event_rate']:.3f}"
        )
    return rows


def main() -> None:
    """Run the target calibration curve and write the summary."""
    frame = bh.load()
    rows: list[dict[str, float]] = []
    for bec, source, target in bh.DIRECTIONS:
        rows.extend(_run(frame, bec, source, target))
    pd.DataFrame(rows).to_csv(
        Path("notes/reference/calibration/d9-bcmort-calibration-curve-summary.csv"), index=False
    )


if __name__ == "__main__":
    main()
