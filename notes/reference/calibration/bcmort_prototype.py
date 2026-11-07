"""Prototype tree-level survival model for MSdm1 and SBSmw.

Fits a Poisson piecewise-exponential hazard with offset log(exposure), then
reports TSA holdout discrimination and calibration. Not a package module.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DATA = "/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4/tree_survival.csv"
GROUPS = ("FD", "PL", "SE", "HW", "OTHER")


def _load() -> pd.DataFrame:
    frame = pd.read_csv(DATA)
    frame = frame[(frame["known"] == 1) & (frame["exposure"] > 0)].copy()
    frame["damage"] = frame["damage"].astype(bool)
    frame["group"] = frame["group"].astype(str).str.upper()
    frame.loc[~frame["group"].isin(GROUPS[:-1]), "group"] = "OTHER"
    frame["qmd"] = 100.0 * np.sqrt(4.0 * frame["ba0"] / (np.pi * frame["tph0"]))
    # BAL: basal area of trees larger than the subject within the plot.
    bal = []
    for _, g in frame.groupby(["interval_id", "PLOT"], sort=False):
        g = g.sort_values("dbh", ascending=False)
        cum = g["ba"].cumsum()
        bal.append((cum - g["ba"]).reindex(g.index))
    frame["bal"] = pd.concat(bal).sort_index()
    frame["rel_dbh"] = frame["dbh"] / frame.groupby(["interval_id", "PLOT"])["dbh"].transform("max")
    return frame


def _design(frame: pd.DataFrame) -> np.ndarray:
    cols = [
        np.ones(len(frame)),
        np.log(frame["dbh"].clip(lower=0.1)),
        np.log1p(frame["bal"].clip(lower=0)),
        np.log1p(frame["ba0"].clip(lower=0)),
        np.log1p(frame["qmd"].clip(lower=0)),
        frame["rel_dbh"].to_numpy(),
        frame["damage"].astype(float).to_numpy(),
    ]
    for group in GROUPS[:-1]:
        cols.append((frame["group"].to_numpy() == group).astype(float))
    return np.column_stack(cols)


def _fit(x: np.ndarray, y: np.ndarray, exposure: np.ndarray) -> np.ndarray:
    beta = np.zeros(x.shape[1])
    offset = np.log(exposure)
    for _ in range(60):
        eta = np.clip(x @ beta + offset, -20, 20)
        mu = np.exp(eta)
        w = np.clip(mu, 1e-8, None)
        z = eta + (y - mu) / w
        lhs = x.T @ (w[:, None] * x) + np.eye(x.shape[1]) * 1.0
        beta = np.linalg.solve(lhs, x.T @ (w * (z - offset)))
    return beta


def _predict(x: np.ndarray, exposure: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return 1.0 - np.exp(-exposure * np.exp(np.clip(x @ beta, -20, 20)))


def _auc(y: np.ndarray, p: np.ndarray) -> float:
    order = np.argsort(p)
    ranks = np.empty(len(p), dtype=float)
    ranks[order] = np.arange(1, len(p) + 1)
    pos = y == 1
    n_pos = pos.sum()
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def _metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    eps = 1e-6
    p = np.clip(p, eps, 1 - eps)
    return {
        "n": float(len(y)),
        "events": float(y.sum()),
        "event_rate": float(y.mean()),
        "mean_pred": float(p.mean()),
        "auc": _auc(y, p),
        "brier": float(np.mean((p - y) ** 2)),
        "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
    }


def _run(bec: str, train_tsa: str, test_tsa: str, frame: pd.DataFrame) -> None:
    train = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == train_tsa)]
    test = frame[(frame["BEC"] == bec) & (frame["TSA_DESC"] == test_tsa)]
    xtr = _design(train)
    xte = _design(test)
    mean = xtr[:, 1:].mean(axis=0)
    scale = xtr[:, 1:].std(axis=0)
    scale[scale == 0] = 1
    xtr[:, 1:] = (xtr[:, 1:] - mean) / scale
    xte[:, 1:] = (xte[:, 1:] - mean) / scale
    beta = _fit(xtr, train["dead"].to_numpy(), train["exposure"].to_numpy())
    ptr = _predict(xtr, train["exposure"].to_numpy(), beta)
    pte = _predict(xte, test["exposure"].to_numpy(), beta)
    # Intercept-only baseline.
    base = np.full(len(test), train["dead"].sum() / train["exposure"].sum())
    pbase = 1 - np.exp(-test["exposure"].to_numpy() * base)
    print(f"\n{bec}: train {train_tsa} -> test {test_tsa}")
    print(" train", _metrics(train["dead"].to_numpy(), ptr))
    print(" test ", _metrics(test["dead"].to_numpy(), pte))
    print(" base ", _metrics(test["dead"].to_numpy(), pbase))
    print(" beta ", np.round(beta, 4).tolist())


def main() -> None:
    """Run the TSA-transfer prototypes."""
    frame = _load()
    _run("MSdm1", "Okanagan TSA", "Boundary TSA", frame)
    _run("MSdm1", "Boundary TSA", "Okanagan TSA", frame)
    _run("SBSmw", "Quesnel TSA", "Prince George TSA", frame)
    _run("SBSmw", "Prince George TSA", "Quesnel TSA", frame)


if __name__ == "__main__":
    main()
