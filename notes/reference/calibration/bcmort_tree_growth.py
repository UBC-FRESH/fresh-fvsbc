"""Prototype BCMORT with individual-tree prior growth.

The D9.37 calibration dataset carries ``TREE_NO``, the prior live diameter, the
prior year, and per-year tree growth.  This script adds growth to the D9.35
crown plus height/DBH model and tests the same TSA holdouts.

The growth is measured before the survival interval starts, so it is not future
information.  This is a diagnostic prototype, not an FVS core change.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType

import bcmort_prototype as bm
import numpy as np
import pandas as pd

DATA = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4-growth/tree_survival.csv")
bm.DATA = str(DATA)


def _crown() -> ModuleType:
    """Import the crown module after the data path is set."""
    import bcmort_crown as bc

    return bc


def load() -> pd.DataFrame:
    """Load the growth dataset and add height/DBH plus growth."""
    frame = _crown().load()
    frame["hd"] = frame["HEIGHT"] / (frame["dbh"] / 100.0)
    for column in ("hd", "growth"):
        frame[column + "_missing"] = frame[column].isna().astype(float)
        frame[column] = frame[column].fillna(frame[column].median())
    return frame


def design(frame: pd.DataFrame, growth: bool = True) -> np.ndarray:
    """Build the crown plus height/DBH design, optionally with growth."""
    base = _crown().design(frame, crown=True)
    columns = [base, frame["hd"].to_numpy(), frame["hd_missing"].to_numpy()]
    if growth:
        columns.extend([frame["growth"].to_numpy(), frame["growth_missing"].to_numpy()])
    return np.column_stack(columns)


def _screen(
    frame: pd.DataFrame, bec: str, source: str, target: str, growth: bool
) -> dict[str, float]:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)]
    xtr = design(train, growth)
    xte = design(test, growth)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    pred = bm._predict(xte, test["exposure"].to_numpy(), beta)
    return bm._metrics(test["dead"].to_numpy(), pred)


def main() -> None:
    """Run the growth screen and write the summary."""
    frame = load()
    print(f"growth coverage: {1.0 - frame['growth_missing'].mean():.4f}")
    rows = []
    for bec, source, target in _crown().DIRECTIONS:
        height = _screen(frame, bec, source, target, growth=False)
        growth = _screen(frame, bec, source, target, growth=True)
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
                "growth_coverage": 1.0 - frame["growth_missing"].mean(),
            }
        )
    pd.DataFrame(rows).to_csv("notes/reference/calibration/d9-tree-growth-summary.csv", index=False)


if __name__ == "__main__":
    main()
