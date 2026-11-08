"""Temporal target calibration curve for the BCMORT growth model.

Fit on intervals ending by 2000, test on intervals starting in 2000 or later.
Use k post-2000 sites to estimate one target intercept and test the remaining
post-2000 sites.  This tests whether a single target intercept can repair the
post-2000 level shift; it is not a full hierarchical model or an FVS change.
"""

from __future__ import annotations

import bcmort_prototype as bm
import bcmort_tree_growth as bg
import numpy as np
import pandas as pd

KS = (1, 2, 3, 5, 10, 20)


def _split(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach start and end years parsed from the interval id."""
    parts = frame["interval_id"].str.split("|", expand=True)
    frame = frame.copy()
    frame["year0"] = parts[2].astype(int)
    frame["year1"] = parts[3].astype(int)
    return frame


def _run(frame: pd.DataFrame, bec: str, repeats: int = 40) -> list[dict[str, float | str]]:
    """Run the temporal calibration curve for one BEC."""
    train = frame[(frame["BEC"] == bec) & (frame["year1"] <= 2000)]
    test = frame[(frame["BEC"] == bec) & (frame["year0"] >= 2000)].copy()
    test["site"] = test["interval_id"].str.split("|").str[0]
    xtr = bg.design(train, True)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    xte = bg.design(test, True)
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    base = bm._metrics(test["dead"].to_numpy(), bm._predict(xte, test["exposure"].to_numpy(), beta))
    sites = sorted(test["site"].unique())
    rng = np.random.default_rng(42)
    rows: list[dict[str, float | str]] = []
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
            xc = bg.design(calibration, True)
            xh = bg.design(holdout, True)
            xc[:, 1:] = (xc[:, 1:] - mean) / scale
            xh[:, 1:] = (xh[:, 1:] - mean) / scale
            delta = bg._crown()._delta(
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
                "k": float(k),
                "n_test_sites": float(len(sites) - k),
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
            f"{bec}: k={k:2d}  log loss {base['log_loss']:.3f} -> {value['log_loss']:.3f}; "
            f"mean {value['mean_pred']:.3f} vs {value['event_rate']:.3f}"
        )
    return rows


def main() -> None:
    """Run the temporal calibration curve and write the summary."""
    frame = _split(bg.load())
    rows: list[dict[str, float | str]] = []
    for bec in ("MSdm1", "SBSmw"):
        rows.extend(_run(frame, bec))
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-bcmort-temporal-calibration-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
