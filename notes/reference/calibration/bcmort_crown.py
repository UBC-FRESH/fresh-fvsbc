"""Prototype BCMORT with a crown-class covariate.

The base BCMORT prototype has DBH, BAL, BA, QMD, relative DBH, damage, and
species.  This screen adds the raw tree crown class (D/C/I/S) from the PSP tree
detail and tests the same TSA holdouts.  It also tests a local target intercept
on top of the crown model.

This is a diagnostic prototype, not an FVS core change.
"""

from __future__ import annotations

from pathlib import Path

import bcmort_prototype as bm
import numpy as np
import pandas as pd

RAW = Path("/srv/shared-data/gep/ws4/tmp/inv01-data/psp/faib_tree_detail.csv")
INTERVALS = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4/intervals.csv")
CROWN = {"D": 1.0, "C": 2.0, "I": 3.0, "S": 4.0}
DIRECTIONS = (
    ("MSdm1", "Okanagan TSA", "Boundary TSA"),
    ("MSdm1", "Boundary TSA", "Okanagan TSA"),
    ("SBSmw", "Quesnel TSA", "Prince George TSA"),
    ("SBSmw", "Prince George TSA", "Quesnel TSA"),
)


def load() -> pd.DataFrame:
    """Load the survival frame and merge crown class at the start visit."""
    frame = bm._load()
    intervals = pd.read_csv(INTERVALS, usecols=["interval_id", "visit0"])
    frame = frame.merge(intervals, on="interval_id", how="left")
    clusters = set(frame["CLSTR_ID"].astype(str))
    chunks = []
    for chunk in pd.read_csv(
        RAW, usecols=["CLSTR_ID", "VISIT_NUMBER", "PLOT", "DBH", "CR_CL"], chunksize=500_000
    ):
        chunk = chunk[chunk["CLSTR_ID"].astype(str).isin(clusters)]
        if not chunk.empty:
            chunks.append(chunk)
    raw = pd.concat(chunks)
    raw["crown"] = raw["CR_CL"].astype(str).str.upper().map(CROWN)
    raw = raw.groupby(["CLSTR_ID", "VISIT_NUMBER", "PLOT", "DBH"], as_index=False)["crown"].mean()
    frame = frame.merge(
        raw,
        left_on=["CLSTR_ID", "visit0", "PLOT", "dbh"],
        right_on=["CLSTR_ID", "VISIT_NUMBER", "PLOT", "DBH"],
        how="left",
    )
    frame["crown_missing"] = frame["crown"].isna().astype(float)
    frame["crown"] = frame["crown"].fillna(frame["crown"].median())
    return frame


def design(frame: pd.DataFrame, crown: bool = True) -> np.ndarray:
    """Build the base design, optionally with crown class and its missing flag."""
    base = bm._design(frame)
    if not crown:
        return base
    return np.column_stack([base, frame["crown"].to_numpy(), frame["crown_missing"].to_numpy()])


def _scaled(train: pd.DataFrame, test: pd.DataFrame, crown: bool) -> tuple[np.ndarray, np.ndarray]:
    xtr = design(train, crown)
    xte = design(test, crown)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    return xtr, xte


def _delta(eta: np.ndarray, y: np.ndarray, exposure: np.ndarray) -> float:
    offset = np.log(exposure) + eta
    delta = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(delta + offset, -20, 20))
        weight = np.clip(mu, 1e-8, None)
        z = delta + offset + (y - mu) / weight
        delta = float(np.sum(weight * (z - offset)) / np.sum(weight))
    return delta


def _screen(
    frame: pd.DataFrame, bec: str, source: str, target: str, crown: bool
) -> dict[str, float]:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)]
    xtr, xte = _scaled(train, test, crown)
    beta = bm._fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    pred = bm._predict(xte, test["exposure"].to_numpy(), beta)
    return bm._metrics(test["dead"].to_numpy(), pred)


def _local(
    frame: pd.DataFrame, bec: str, source: str, target: str, repeats: int = 40
) -> dict[str, float]:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == source)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == target)].copy()
    test["site"] = test["interval_id"].str.split("|").str[0]
    xtr, _ = _scaled(train, test, crown=True)
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
        mean = design(train)[:, 1:].mean(axis=0)
        scale = design(train)[:, 1:].std(axis=0)
        scale[scale == 0] = 1
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
    """Run the crown screen and the crown-plus-local calibration."""
    frame = load()
    print(f"crown coverage: {1.0 - frame['crown_missing'].mean():.4f}")
    rows = []
    for bec, source, target in DIRECTIONS:
        base = _screen(frame, bec, source, target, crown=False)
        crown = _screen(frame, bec, source, target, crown=True)
        local = _local(frame, bec, source, target)
        print(
            f"{bec}: {source} -> {target}  "
            f"AUC {base['auc']:.3f} -> {crown['auc']:.3f}; "
            f"log loss {base['log_loss']:.3f} -> {crown['log_loss']:.3f}; "
            f"local log loss {local['local_log_loss']:.3f}"
        )
        rows.append(
            {
                "bec": bec,
                "source_tsa": source,
                "target_tsa": target,
                "auc_base": base["auc"],
                "auc_crown": crown["auc"],
                "logloss_base": base["log_loss"],
                "logloss_crown": crown["log_loss"],
                "brier_base": base["brier"],
                "brier_crown": crown["brier"],
                "mean_base": base["mean_pred"],
                "mean_crown": crown["mean_pred"],
                "mean_local": local["local_mean"],
                "logloss_local": local["local_log_loss"],
                "brier_local": local["local_brier"],
            }
        )
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-bcmort-crown-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
