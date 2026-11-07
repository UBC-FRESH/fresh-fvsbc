"""Prototype hurdle recruitment model for IDFdk PSP intervals.

Not a package module. Fits a two-part model on tree-derived recruitment counts and
prints train/100 Mile House validation metrics. No scipy/statsmodels dependency.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fresh_fvsbc.calibration import SPECIES_GROUPS
from fresh_fvsbc.ingrowth import recruitment_table

INTERVALS = "runtime/calibration/intervals.csv"
TREES = "/srv/shared-data/gep/ws4/tmp/inv01-data/psp/faib_tree_detail.csv"
GROUPS = ("FD", "PL", "SE", "HW")


def _design(frame: pd.DataFrame) -> np.ndarray:
    cols = [
        np.ones(len(frame)),
        np.log1p(frame["ba0"].to_numpy()),
        np.log1p(frame["qmd"].to_numpy()),
        np.log1p(frame["years"].to_numpy()),
        np.log1p(frame["ba_FD"].to_numpy()),
        np.log1p(frame["ba_PL"].to_numpy()),
        np.log1p(frame["ba_SE"].to_numpy()),
        np.log1p(frame["ba_HW"].to_numpy()),
    ]
    for bec in ("IDFdk1", "IDFdk2", "IDFdk3", "IDFdk4", "IDFdk5"):
        cols.append((frame["BEC"].astype(str).to_numpy() == bec).astype(float))
    return np.column_stack(cols)


def _logit_fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta = np.zeros(x.shape[1])
    for _ in range(60):
        eta = np.clip(x @ beta, -20, 20)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1 - p), 1e-8, None)
        z = eta + (y - p) / w
        lhs = x.T @ (w[:, None] * x) + np.eye(x.shape[1]) * 1.0
        beta = np.linalg.solve(lhs, x.T @ (w * z))
    return beta


def _loglinear_fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Ordinary least squares on log positive rate; a robust hurdle count proxy."""
    return np.linalg.lstsq(x, np.log(y + 0.05), rcond=None)[0]


def _prepare() -> tuple[pd.DataFrame, pd.DataFrame]:
    intervals = pd.read_csv(INTERVALS)
    intervals = intervals[intervals["BEC"].astype(str).str.startswith("IDFdk")].copy()
    sites = set(intervals["SITE_IDENTIFIER"].astype(str))
    cols = [
        "SITE_IDENTIFIER",
        "CLSTR_ID",
        "VISIT_NUMBER",
        "PLOT",
        "TREE_NO",
        "SPECIES",
        "DBH",
        "LV_D",
        "PHF_TREE",
        "TREE_WT",
        "BA_TREE",
    ]
    frames = []
    for chunk in pd.read_csv(TREES, usecols=cols, chunksize=500_000):
        chunk = chunk[chunk["SITE_IDENTIFIER"].astype(str).isin(sites)]
        if not chunk.empty:
            frames.append(chunk)
    trees = pd.concat(frames, ignore_index=True)
    table = recruitment_table(intervals, trees)
    meta = intervals.set_index("interval_id")[["SITE_IDENTIFIER", "visit0", "PLOT"]]
    table = table.join(meta, on="interval_id")
    # Parent BA by group at the start visit.
    live = trees[(trees["LV_D"] == "L") & (trees["PHF_TREE"] > 0)].copy()
    live["phf"] = live["PHF_TREE"] * live["TREE_WT"].fillna(1)
    live["ba"] = live["BA_TREE"].fillna(0) * live["phf"]
    live["group"] = live["SPECIES"].astype(str).str.upper().map(SPECIES_GROUPS).fillna("UNKNOWN")
    start = (
        live.groupby(["SITE_IDENTIFIER", "VISIT_NUMBER", "PLOT", "group"])["ba"]
        .sum()
        .unstack(fill_value=0)
    )
    start.columns = [f"ba_{c}" for c in start.columns]
    start = start.reset_index().rename(columns={"VISIT_NUMBER": "visit0"})
    table = table.merge(start, on=["SITE_IDENTIFIER", "visit0", "PLOT"], how="left")
    for g in GROUPS:
        if f"ba_{g}" not in table:
            table[f"ba_{g}"] = 0.0
        table[f"ba_{g}"] = table[f"ba_{g}"].fillna(0.0)
    table = table[table["years"] > 0].reset_index(drop=True)
    return table, intervals


def _metrics(obs: np.ndarray, pred: np.ndarray, years: np.ndarray) -> dict[str, float]:
    obs_rate = obs / years
    pred_rate = pred / years
    return {
        "n": float(len(obs)),
        "obs_mean_tph": float(obs_rate.mean()),
        "pred_mean_tph": float(pred_rate.mean()),
        "obs_zero": float((obs == 0).mean()),
        "pred_zero": float((pred < 0.5).mean()),
        "rmse": float(np.sqrt(np.mean((pred_rate - obs_rate) ** 2))),
        "corr": float(np.corrcoef(obs_rate, pred_rate)[0, 1]) if len(obs) > 2 else float("nan"),
    }


def main() -> None:
    """Fit the prototype and print train/test metrics."""
    table, _intervals = _prepare()
    table["test"] = table["TSA_DESC"].astype(str).eq("100 Mile House TSA")
    train = table[~table["test"]].copy()
    test = table[table["test"]].copy()
    xtr = _design(train)
    xte = _design(test)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1.0
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    ytr = train["new_total"].to_numpy()
    yte = test["new_total"].to_numpy()
    ytr_rate = train["years"].to_numpy()
    yte_rate = test["years"].to_numpy()
    present = (ytr > 0).astype(float)
    beta_p = _logit_fit(xtr, present)
    pos = ytr > 0
    beta_c = _loglinear_fit(xtr[pos], ytr[pos] / ytr_rate[pos])
    resid = np.log(ytr[pos] / ytr_rate[pos] + 0.05) - xtr[pos] @ beta_c
    smear = float(np.mean(np.exp(resid)))

    def predict(x: np.ndarray, years: np.ndarray) -> np.ndarray:
        p = 1.0 / (1.0 + np.exp(-(x @ beta_p)))
        rate = np.exp(np.clip(x @ beta_c, -20, 20)) * smear
        return p * rate * years

    pred_tr = predict(xtr, ytr_rate)
    pred_te = predict(xte, yte_rate)
    print("train", _metrics(ytr, pred_tr, ytr_rate))
    print("test ", _metrics(yte, pred_te, yte_rate))
    print("coefficients presence", np.round(beta_p, 3).tolist())
    print("coefficients count   ", np.round(beta_c, 3).tolist())
    # Zero/positive decomposition on test.
    print("test observed zeros", int((yte == 0).sum()), "of", len(yte))
    print("test predicted zeros", int((pred_te < 0.5).sum()))


if __name__ == "__main__":
    main()
