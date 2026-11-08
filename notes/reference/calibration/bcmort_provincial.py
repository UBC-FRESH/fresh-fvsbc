"""Provincial species-group mortality fit on all PSP tree intervals.

This is the first model that uses the whole BC tree-survival table instead of
two BEC-specific TSAs.  It fits a species-group logistic hazard with BEC-zone
effects and tests four held-out TSAs at once.

It is a prototype, not an FVS integration.
"""

from __future__ import annotations

from pathlib import Path

import bcmort_prototype as bm
import numpy as np
import pandas as pd

DATA = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4-growth/tree_survival.csv")
INTERVALS = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4-growth/intervals.csv")
RAW = Path("/srv/shared-data/gep/ws4/tmp/inv01-data/psp/faib_tree_detail.csv")
CROWN = {"D": 1.0, "C": 2.0, "I": 3.0, "S": 4.0}
TARGETS = ("Okanagan TSA", "Quesnel TSA")
GROUPS = ("FD", "PL", "SE", "HW", "OTHER")


def load() -> pd.DataFrame:
    """Load and prepare the provincial tree-survival table."""
    frame = pd.read_csv(
        DATA,
        usecols=[
            "interval_id",
            "BEC",
            "TSA_DESC",
            "PLOT",
            "TREE_NO",
            "group",
            "dbh",
            "ba0",
            "tph0",
            "damage",
            "dead",
            "known",
            "exposure",
            "HEIGHT",
            "growth",
        ],
    )
    frame = frame[(frame["known"] == 1) & (frame["exposure"] > 0)].copy()
    frame["group"] = frame["group"].astype(str).str.upper()
    frame.loc[~frame["group"].isin(GROUPS[:-1]), "group"] = "OTHER"
    parts = frame["interval_id"].str.split("|", expand=True)
    frame["site"] = parts[0].astype(str)
    intervals = pd.read_csv(INTERVALS, usecols=["interval_id", "visit0"])
    frame = frame.merge(intervals, on="interval_id", how="left")
    raw = pd.read_csv(
        RAW,
        usecols=["SITE_IDENTIFIER", "VISIT_NUMBER", "PLOT", "TREE_NO", "CR_CL", "SI_TREE"],
    )
    raw["site"] = raw["SITE_IDENTIFIER"].astype(str)
    raw["visit0"] = raw["VISIT_NUMBER"].astype(int)
    raw["TREE_NO"] = raw["TREE_NO"].astype(float)
    raw["crown"] = raw["CR_CL"].astype(str).str.upper().map(CROWN)
    raw["si"] = pd.to_numeric(raw["SI_TREE"], errors="coerce")
    raw = raw.groupby(["site", "visit0", "PLOT", "TREE_NO"], as_index=False)[["crown", "si"]].mean()
    frame = frame.merge(raw, on=["site", "visit0", "PLOT", "TREE_NO"], how="left")
    for column in ("crown", "si"):
        frame[column + "_missing"] = frame[column].isna().astype(float)
        frame[column] = frame[column].fillna(frame[column].median())
    frame["qmd"] = 100.0 * np.sqrt(4.0 * frame["ba0"] / (np.pi * frame["tph0"]))
    frame["rel_dbh"] = frame["dbh"] / frame.groupby(["interval_id", "PLOT"])["dbh"].transform("max")
    frame["hd"] = frame["HEIGHT"] / (frame["dbh"] / 100.0)
    for column in ("hd", "growth"):
        frame[column + "_missing"] = frame[column].isna().astype(float)
        frame[column] = frame[column].fillna(frame[column].median())
    frame["zone"] = frame["BEC"].astype(str).str.extract(r"^([A-Za-z]+)")[0].str.upper()
    return frame


def design(frame: pd.DataFrame, zones: list[str]) -> np.ndarray:
    """Build the species-group design with BEC-zone effects."""
    cols = [
        np.ones(len(frame)),
        np.log(frame["dbh"].clip(lower=0.1)),
        np.log1p(frame["ba0"].clip(lower=0)),
        np.log1p(frame["qmd"].clip(lower=0)),
        frame["rel_dbh"].to_numpy(),
        frame["hd"].to_numpy(),
        frame["growth"].to_numpy(),
        frame["damage"].astype(float).to_numpy(),
        frame["hd_missing"].to_numpy(),
        frame["growth_missing"].to_numpy(),
        frame["crown"].to_numpy(),
        frame["crown_missing"].to_numpy(),
        frame["si"].to_numpy(),
        frame["si_missing"].to_numpy(),
    ]
    zone = frame["zone"].to_numpy()
    cols.extend([(zone == value).astype(float) for value in zones])
    return np.column_stack(cols)


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    """Return discrimination and calibration metrics."""
    eps = 1e-6
    p = np.clip(p, eps, 1 - eps)
    order = np.argsort(p)
    ranks = np.empty(len(p), dtype=float)
    ranks[order] = np.arange(1, len(p) + 1)
    pos = y == 1
    n_pos = pos.sum()
    n_neg = len(y) - n_pos
    auc = (
        (ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
        if n_pos and n_neg
        else np.nan
    )
    return {
        "n": float(len(y)),
        "event_rate": float(y.mean()),
        "mean_pred": float(p.mean()),
        "auc": float(auc),
        "brier": float(np.mean((p - y) ** 2)),
        "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
    }


def main() -> None:
    """Fit the provincial model and test the held-out TSAs."""
    frame = load()
    train = frame[~frame["TSA_DESC"].astype(str).isin(TARGETS)]
    zones = sorted(frame["zone"].dropna().unique())
    rows = []
    all_y: dict[str, list[np.ndarray]] = {target: [] for target in TARGETS}
    all_p: dict[str, list[np.ndarray]] = {target: [] for target in TARGETS}
    for group in GROUPS:
        tr = train[train["group"] == group]
        if len(tr) < 1000:
            continue
        x = design(tr, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, tr["dead"].to_numpy(), tr["exposure"].to_numpy())
        for target in TARGETS:
            test = frame[(frame["TSA_DESC"].astype(str) == target) & (frame["group"] == group)]
            if test.empty:
                continue
            xt = design(test, zones)
            xt[:, 1:] = (xt[:, 1:] - mean) / scale
            pred = bm._predict(xt, test["exposure"].to_numpy(), beta)
            metric = metrics(test["dead"].to_numpy(), pred)
            rows.append({"group": group, "target_tsa": target, **metric})
            all_y[target].append(test["dead"].to_numpy())
            all_p[target].append(pred)
            print(
                f"{group:5s} {target:20s} n={metric['n']:7.0f} "
                f"auc={metric['auc']:.3f} mean={metric['mean_pred']:.3f} "
                f"obs={metric['event_rate']:.3f} ll={metric['log_loss']:.3f}"
            )
    for target in TARGETS:
        if not all_y[target]:
            continue
        metric = metrics(np.concatenate(all_y[target]), np.concatenate(all_p[target]))
        rows.append({"group": "ALL", "target_tsa": target, **metric})
        print(
            f"ALL   {target:20s} n={metric['n']:7.0f} "
            f"auc={metric['auc']:.3f} mean={metric['mean_pred']:.3f} "
            f"obs={metric['event_rate']:.3f} ll={metric['log_loss']:.3f}"
        )
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-provincial-crown-si-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
