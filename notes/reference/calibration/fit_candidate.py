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


def main() -> None:
    """Fit the target-excluded model and write metrics and the model card."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-tsa", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--model-card", type=Path, required=True)
    parser.add_argument("--calibration", choices=("none", "conditional"), default="none")
    parser.add_argument(
        "--min-target-trees",
        type=int,
        default=0,
        help="Omit species groups with fewer target trees than this.",
    )
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
        pred = bm._predict(xt, test["exposure"].to_numpy(), beta)
        metric = bp.metrics(test["dead"].to_numpy(), pred)
        rows.append({"group": group, **metric})
        all_y.append(test["dead"].to_numpy())
        all_p.append(pred)
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

    calibration = (
        {
            "applied": False,
            "rule": (
                "Fit target-excluded species-group intercepts only when a group has at least 500 "
                "target trees and overpredicts by more than 3 points."
            ),
            "evaluated": args.calibration == "conditional",
        }
        if args.calibration == "conditional"
        else {
            "applied": False,
            "rule": "No local calibration; the target-excluded layer is used directly.",
            "evaluated": False,
        }
    )
    card = {
        "model_id": args.model_id,
        "status": "frozen_candidate_layer",
        "target_tsa": target_name,
        "excluded_from_training": [target_name],
        "features": feature_names,
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
