"""Temporal holdout for the BCMORT growth model.

Train on intervals that end by 2000 and test on intervals that start in 2000 or
later.  The split keeps the growth covariate on the same footing as the TSA
holdout: growth is prior information at the start of each interval.

This is a diagnostic prototype, not an FVS core change.
"""

from __future__ import annotations

import bcmort_prototype as bm
import bcmort_tree_growth as bg
import pandas as pd


def _split(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach start and end years parsed from the interval id."""
    parts = frame["interval_id"].str.split("|", expand=True)
    frame = frame.copy()
    frame["year0"] = parts[2].astype(int)
    frame["year1"] = parts[3].astype(int)
    return frame


def _run(frame: pd.DataFrame, bec: str) -> dict[str, float | str]:
    """Fit a pre-2000 model and test on post-2000 intervals."""
    train = frame[(frame["BEC"] == bec) & (frame["year1"] <= 2000)]
    test = frame[(frame["BEC"] == bec) & (frame["year0"] >= 2000)]
    values: dict[str, float | str] = {
        "bec": bec,
        "train_n": float(len(train)),
        "test_n": float(len(test)),
    }
    for growth, suffix in ((False, "hd"), (True, "growth")):
        xtr = bg.design(train, growth)
        xte = bg.design(test, growth)
        mean = xtr[:, 1:].mean(axis=0)
        scale = xtr[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
        xte[:, 1:] = (xte[:, 1:] - mean) / scale
        beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
        metric = bm._metrics(
            test["dead"].to_numpy(),
            bm._predict(xte, test["exposure"].to_numpy(), beta),
        )
        values[f"auc_{suffix}"] = metric["auc"]
        values[f"logloss_{suffix}"] = metric["log_loss"]
        values[f"brier_{suffix}"] = metric["brier"]
        values[f"mean_{suffix}"] = metric["mean_pred"]
        values["event_rate"] = metric["event_rate"]
    print(
        f"{bec}: train {len(train)} -> test {len(test)}  "
        f"AUC {values['auc_hd']:.3f} -> {values['auc_growth']:.3f}; "
        f"log loss {values['logloss_hd']:.3f} -> {values['logloss_growth']:.3f}; "
        f"mean {values['mean_growth']:.3f} vs {values['event_rate']:.3f}"
    )
    return values


def main() -> None:
    """Run the temporal holdouts and write the summary."""
    frame = _split(bg.load())
    rows = [_run(frame, bec) for bec in ("MSdm1", "SBSmw")]
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-bcmort-temporal-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
