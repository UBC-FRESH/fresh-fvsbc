"""Prototype BCMORT with prior stand growth and mortality rates.

Adds the previous interval's stand-level rates to the D9.35 height/DBH model.
The previous interval ends at the current start visit, so the rates are known
at prediction time.  This is a diagnostic prototype, not an FVS core change.
"""

from __future__ import annotations

from pathlib import Path

import bcmort_hd as bh
import bcmort_prototype as bm
import numpy as np
import pandas as pd

INTERVALS = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4/intervals.csv")
RATES = ("net_ba_rate", "gross_ba_rate", "ba_mortality", "tph_mortality", "years")


def load() -> pd.DataFrame:
    """Load the height/DBH frame and merge prior-interval stand rates."""
    frame = bh.load()
    intervals = pd.read_csv(
        INTERVALS,
        usecols=["interval_id", "SITE_IDENTIFIER", "PLOT", "year0", *RATES],
    )
    intervals = intervals.sort_values(["SITE_IDENTIFIER", "PLOT", "year0"])
    grouped = intervals.groupby(["SITE_IDENTIFIER", "PLOT"], sort=False)
    for column in RATES:
        intervals["prior_" + column] = grouped[column].shift(1)
    prior = ["prior_" + column for column in RATES]
    frame = frame.merge(intervals[["interval_id", *prior]], on="interval_id", how="left")
    for column in prior:
        frame[column + "_missing"] = frame[column].isna().astype(float)
        frame[column] = frame[column].fillna(frame[column].median())
    return frame


def design(frame: pd.DataFrame) -> np.ndarray:
    """Add the prior stand rates and their missing flags to the height/DBH design."""
    prior = ["prior_" + column for column in RATES]
    return np.column_stack(
        [
            bh.design(frame),
            *[frame[column].to_numpy() for column in prior],
            *[frame[column + "_missing"].to_numpy() for column in prior],
        ]
    )


def _screen(frame: pd.DataFrame, bec: str, source: str, target: str) -> dict[str, float]:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)]
    xtr = design(train)
    xte = design(test)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    pred = bm._predict(xte, test["exposure"].to_numpy(), beta)
    return bm._metrics(test["dead"].to_numpy(), pred)


def main() -> None:
    """Run the prior stand-rate screen and write the summary."""
    frame = load()
    print(f"prior-rate coverage: {1.0 - frame['prior_years_missing'].mean():.4f}")
    rows = []
    for bec, source, target in bh.DIRECTIONS:
        height = bh._screen(frame, bec, source, target)
        growth = _screen(frame, bec, source, target)
        print(
            f"{bec}: {source} -> {target}  "
            f"AUC {height['auc']:.3f} -> {growth['auc']:.3f}; "
            f"log loss {height['log_loss']:.3f} -> {growth['log_loss']:.3f}; "
            f"Brier {height['brier']:.4f} -> {growth['brier']:.4f}"
        )
        rows.append(
            {
                "bec": bec,
                "source_tsa": source,
                "target_tsa": target,
                "auc_hd": height["auc"],
                "auc_growth": growth["auc"],
                "logloss_hd": height["log_loss"],
                "logloss_growth": growth["log_loss"],
                "brier_hd": height["brier"],
                "brier_growth": growth["brier"],
                "mean_hd": height["mean_pred"],
                "mean_growth": growth["mean_pred"],
            }
        )
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-bcmort-growth-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
