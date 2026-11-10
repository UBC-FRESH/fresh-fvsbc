"""Fit a target-excluded growth-free candidate and freeze its model card.

The target TSA is removed from training, the species-group model is fitted, the
target is scored, and the coefficients and aggregate metrics are written as a
model card. The script stores no site-level rows, so the same template can be
used for another TSA without changing the code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd

from fresh_fvsbc import __version__
from fresh_fvsbc.provenance import FVS_SOURCE_COMMIT, PYFVS_COMMIT

FEATURES = (
    "intercept",
    "log_dbh",
    "log_ba0",
    "log_qmd",
    "rel_dbh",
    "hd",
    "damage",
    "hd_missing",
    "crown",
    "crown_missing",
    "si",
    "si_missing",
)


def _digest(path: Path) -> str:
    """Return a SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _design(frame: pd.DataFrame, zones: list[str]) -> np.ndarray:
    """Return the growth-free provincial design."""
    return np.delete(bp.design(frame, zones), [6, 9], axis=1)


def _delta(eta: np.ndarray, dead: np.ndarray, exposure: np.ndarray) -> float:
    """Return the maximum-likelihood group intercept at fixed coefficients."""
    offset = np.log(exposure) + eta
    value = 0.0
    for _ in range(60):
        mu = np.exp(np.clip(value + offset, -20, 20))
        weight = np.clip(mu, 1e-8, None)
        z = value + offset + (dead - mu) / weight
        value = float(np.sum(weight * (z - offset)) / np.sum(weight))
    return value


def _local_metrics(
    frame: pd.DataFrame,
    *,
    calibration_sites: int,
    bootstrap: int,
    symmetric: bool = False,
    seed: int = 42,
) -> dict[str, object]:
    """Evaluate the 20-site conditional rule on held-out target sites.

    Parameters
    ----------
    frame : pandas.DataFrame
        One row per target tree, with ``site``, ``group``, ``eta``,
        ``exposure``, and ``dead``.
    calibration_sites : int
        Number of sites used to estimate the group intercepts.
    bootstrap : int
        Number of site splits.
    symmetric : bool, optional
        Apply an intercept when the group is over- or underpredicted by more
        than three points. The default is overprediction only.
    seed : int, optional
        Random seed for the splits.

    Returns
    -------
    dict
        The mean held-out metrics and the split design.
    """
    sites = sorted(frame["site"].astype(str).unique())
    if len(sites) <= calibration_sites:
        return {"evaluated": False, "reason": "not enough target sites"}
    rng = np.random.default_rng(seed)
    rows: list[dict[str, float]] = []
    for _ in range(bootstrap):
        shuffled = list(rng.permutation(sites))
        calibration = set(shuffled[:calibration_sites])
        cal = frame[frame["site"].isin(calibration)]
        hold = frame[~frame["site"].isin(calibration)]
        if cal.empty or hold.empty:
            continue
        offsets: dict[str, float] = {}
        for group, part in cal.groupby("group"):
            if len(part) < 500:
                continue
            eta = part["eta"].to_numpy()
            exposure = part["exposure"].to_numpy()
            base = 1.0 - np.exp(-exposure * np.exp(np.clip(eta, -20, 20)))
            gap = float(base.mean()) - float(part["dead"].mean())
            trigger = abs(gap) > 0.03 if symmetric else gap > 0.03
            if trigger:
                offsets[str(group)] = _delta(eta, part["dead"].to_numpy(), exposure)
        delta = hold["group"].map(offsets).fillna(0.0).to_numpy()
        pred = 1.0 - np.exp(
            -hold["exposure"].to_numpy() * np.exp(np.clip(hold["eta"].to_numpy() + delta, -20, 20))
        )
        rows.append(bp.metrics(hold["dead"].to_numpy(), pred))
    if not rows:
        return {"evaluated": False, "reason": "no usable splits"}
    return {
        "evaluated": True,
        "calibration_sites": calibration_sites,
        "holdout_sites": len(sites) - calibration_sites,
        "bootstrap": bootstrap,
        "mean_metrics": pd.DataFrame(rows).mean(numeric_only=True).to_dict(),
    }


def main() -> None:
    """Fit the target-excluded model and write metrics and the model card."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-tsa", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--model-card", type=Path, required=True)
    parser.add_argument(
        "--calibration",
        choices=("none", "conditional", "symmetric"),
        default="none",
    )
    parser.add_argument(
        "--min-target-trees",
        type=int,
        default=0,
        help="Omit species groups with fewer target trees than this.",
    )
    parser.add_argument(
        "--evaluate-local",
        action="store_true",
        help="Evaluate the conditional 20-site rule on held-out target sites.",
    )
    parser.add_argument("--calibration-sites", type=int, default=20)
    parser.add_argument("--bootstrap", type=int, default=40)
    args = parser.parse_args()

    frame = bp.load()
    target_name = str(args.target_tsa)
    train = frame[frame["TSA_DESC"].astype(str) != target_name]
    target = frame[frame["TSA_DESC"].astype(str) == target_name].copy()
    if target.empty:
        raise SystemExit(f"no rows for target TSA: {target_name}")
    zones = sorted(frame["zone"].dropna().unique())
    feature_names = list(FEATURES) + [f"zone_{zone}" for zone in zones]
    groups: dict[str, object] = {}
    rows: list[dict[str, object]] = []
    omitted: list[dict[str, object]] = []
    all_y: list[np.ndarray] = []
    all_p: list[np.ndarray] = []
    target_rows: list[pd.DataFrame] = []
    for group in bp.GROUPS:
        part = train[train["group"] == group]
        test = target[target["group"] == group]
        if len(part) < 1000 or test.empty:
            continue
        if len(test) < args.min_target_trees:
            omitted.append({"group": group, "n": len(test)})
            continue
        x = _design(part, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, part["dead"].to_numpy(), part["exposure"].to_numpy())
        xt = _design(test, zones)
        xt[:, 1:] = (xt[:, 1:] - mean) / scale
        eta = xt @ beta
        pred = bm._predict(xt, test["exposure"].to_numpy(), beta)
        metric = bp.metrics(test["dead"].to_numpy(), pred)
        rows.append({"group": group, **metric})
        all_y.append(test["dead"].to_numpy())
        all_p.append(pred)
        target_rows.append(
            pd.DataFrame(
                {
                    "site": test["site"].to_numpy(),
                    "group": group,
                    "eta": eta,
                    "exposure": test["exposure"].to_numpy(),
                    "dead": test["dead"].to_numpy(),
                }
            )
        )
        groups[group] = {
            "beta": [float(value) for value in beta],
            "mean": [float(value) for value in mean],
            "scale": [float(value) for value in scale],
            "n": len(part),
        }
    overall = bp.metrics(np.concatenate(all_y), np.concatenate(all_p))
    rows.append({"group": "ALL", **overall})
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.metrics, index=False)

    if args.calibration == "conditional":
        calibration: dict[str, object] = {
            "applied": False,
            "mode": "conditional-one-sided",
            "rule": (
                "Fit target-excluded species-group intercepts only when a group has at least 500 "
                "target trees and overpredicts by more than 3 points."
            ),
            "evaluated": True,
            "recommended": False,
        }
    elif args.calibration == "symmetric":
        calibration = {
            "applied": False,
            "mode": "conditional-symmetric",
            "rule": (
                "Fit target-excluded species-group intercepts when a group has at least 500 target "
                "trees and is over- or underpredicted by more than 3 points."
            ),
            "evaluated": True,
            "recommended": True,
        }
    else:
        calibration = {
            "applied": False,
            "mode": "none",
            "rule": "No local calibration; the target-excluded layer is used directly.",
            "evaluated": False,
            "recommended": False,
        }
    if args.evaluate_local:
        calibration["local_metrics"] = _local_metrics(
            pd.concat(target_rows, ignore_index=True),
            calibration_sites=args.calibration_sites,
            bootstrap=args.bootstrap,
            symmetric=args.calibration == "symmetric",
        )
    card = {
        "model_id": args.model_id,
        "status": "frozen_candidate_layer",
        "target_tsa": target_name,
        "excluded_from_training": [target_name],
        "features": feature_names,
        "preprocessing": frame.attrs.get("preprocessing", {}),
        "species_groups": groups,
        "metrics": rows,
        "calibration": calibration,
        "pins": {
            "pyfvs_commit": PYFVS_COMMIT,
            "fvs_source_commit": FVS_SOURCE_COMMIT,
            "variant": "bc",
            "wrapper_version": __version__,
        },
        "data_checksums": {
            "tree_survival.csv": _digest(bp.DATA),
            "intervals.csv": _digest(bp.INTERVALS),
            "faib_tree_detail.csv": _digest(bp.RAW),
        },
        "limitations": [
            f"Only {target_name} is held out; no production temporal validation.",
            "The layer is background mortality; local MPB and small-tree terms stay separate.",
            "The card contains aggregate metrics and coefficients, not site rows.",
        ],
        "claim": (
            "Frozen diagnostic candidate layer. Not a yield, AAC, legal, whole-block, or "
            "certificate claim."
        ),
    }
    args.model_card.parent.mkdir(parents=True, exist_ok=True)
    if omitted:
        card["target_groups_below_minimum"] = omitted
        card["limitations"].append(
            "Groups below the target-support minimum are omitted: "
            + ", ".join(f"{item['group']} ({item['n']})" for item in omitted)
        )
    args.model_card.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.metrics} and {args.model_card}")


if __name__ == "__main__":
    main()
