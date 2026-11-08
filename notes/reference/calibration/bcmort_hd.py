"""Prototype BCMORT with crown class and height-DBH ratio.

Adds the tree height at the start visit to the D9.34 crown-class prototype and
tests the same TSA holdouts.  Height/DBH is a coarse vigor and stability proxy;
it is not a continuous crown ratio.

This is a diagnostic prototype, not an FVS core change.
"""

from __future__ import annotations

from pathlib import Path

import bcmort_crown as bc
import bcmort_prototype as bm
import numpy as np
import pandas as pd

RAW = Path("/srv/shared-data/gep/ws4/tmp/inv01-data/psp/faib_tree_detail.csv")
DIRECTIONS = bc.DIRECTIONS


def load() -> pd.DataFrame:
    """Load the crown frame and merge height at the start visit."""
    frame = bc.load()
    clusters = set(frame["CLSTR_ID"].astype(str))
    chunks = []
    for chunk in pd.read_csv(
        RAW, usecols=["CLSTR_ID", "VISIT_NUMBER", "PLOT", "DBH", "HEIGHT"], chunksize=500_000
    ):
        chunk = chunk[chunk["CLSTR_ID"].astype(str).isin(clusters)]
        if not chunk.empty:
            chunks.append(chunk)
    raw = pd.concat(chunks)
    raw = raw.groupby(["CLSTR_ID", "VISIT_NUMBER", "PLOT", "DBH"], as_index=False)["HEIGHT"].mean()
    frame = frame.merge(
        raw,
        left_on=["CLSTR_ID", "visit0", "PLOT", "dbh"],
        right_on=["CLSTR_ID", "VISIT_NUMBER", "PLOT", "DBH"],
        how="left",
    )
    frame["hd"] = frame["HEIGHT"] / (frame["dbh"] / 100.0)
    frame["hd_missing"] = frame["hd"].isna().astype(float)
    frame["hd"] = frame["hd"].fillna(frame["hd"].median())
    return frame


def design(frame: pd.DataFrame) -> np.ndarray:
    """Add height/DBH and its missing flag to the crown design."""
    return np.column_stack(
        [bc.design(frame, crown=True), frame["hd"].to_numpy(), frame["hd_missing"].to_numpy()]
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


def _delta(eta: np.ndarray, y: np.ndarray, exposure: np.ndarray) -> float:
    offset = np.log(exposure) + eta
    delta = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(delta + offset, -20, 20))
        weight = np.clip(mu, 1e-8, None)
        z = delta + offset + (y - mu) / weight
        delta = float(np.sum(weight * (z - offset)) / np.sum(weight))
    return delta


def _local(
    frame: pd.DataFrame, bec: str, source: str, target: str, repeats: int = 40
) -> dict[str, float]:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)].copy()
    test["site"] = test["interval_id"].str.split("|").str[0]
    xtr = design(train)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    sites = sorted(test["site"].unique())
    rng = np.random.default_rng(42)
    rows: list[dict[str, float]] = []
    for _ in range(repeats):
        rng.shuffle(sites)
        cut = max(1, len(sites) // 2)
        calibration = test[test["site"].isin(set(sites[:cut]))]
        holdout = test[test["site"].isin(set(sites[cut:]))]
        if calibration.empty or holdout.empty:
            continue
        xc = design(calibration)
        xh = design(holdout)
        xc[:, 1:] = (xc[:, 1:] - mean) / scale
        xh[:, 1:] = (xh[:, 1:] - mean) / scale
        delta = _delta(
            xc @ beta, calibration["dead"].to_numpy(), calibration["exposure"].to_numpy()
        )
        base = bm._predict(xh, holdout["exposure"].to_numpy(), beta)
        local = 1.0 - np.exp(
            -holdout["exposure"].to_numpy() * np.exp(np.clip(xh @ beta + delta, -20, 20))
        )
        mb = bm._metrics(holdout["dead"].to_numpy(), base)
        ml = bm._metrics(holdout["dead"].to_numpy(), local)
        rows.append(
            {
                "delta": delta,
                "event_rate": ml["event_rate"],
                "base_mean": mb["mean_pred"],
                "local_mean": ml["mean_pred"],
                "base_log_loss": mb["log_loss"],
                "local_log_loss": ml["log_loss"],
                "base_brier": mb["brier"],
                "local_brier": ml["brier"],
            }
        )
    return pd.DataFrame(rows).mean().to_dict()


def main() -> None:
    """Run the height/DBH screen and the local target intercept."""
    frame = load()
    print(f"height/DBH coverage: {1.0 - frame['hd_missing'].mean():.4f}")
    rows = []
    for bec, source, target in DIRECTIONS:
        crown = bc._screen(frame, bec, source, target, crown=True)
        height = _screen(frame, bec, source, target)
        local = _local(frame, bec, source, target)
        print(
            f"{bec}: {source} -> {target}  "
            f"AUC {crown['auc']:.3f} -> {height['auc']:.3f}; "
            f"log loss {crown['log_loss']:.3f} -> {height['log_loss']:.3f}; "
            f"local log loss {local['local_log_loss']:.3f}"
        )
        rows.append(
            {
                "bec": bec,
                "source_tsa": source,
                "target_tsa": target,
                "auc_crown": crown["auc"],
                "auc_hd": height["auc"],
                "logloss_crown": crown["log_loss"],
                "logloss_hd": height["log_loss"],
                "brier_crown": crown["brier"],
                "brier_hd": height["brier"],
                "mean_crown": crown["mean_pred"],
                "mean_hd": height["mean_pred"],
                "mean_local": local["local_mean"],
                "logloss_local": local["local_log_loss"],
                "brier_local": local["local_brier"],
            }
        )
    pd.DataFrame(rows).to_csv("notes/reference/calibration/d9-bcmort-hd-summary.csv", index=False)


if __name__ == "__main__":
    main()
