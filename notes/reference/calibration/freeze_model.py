"""Freeze the Quesnel non-PL candidate as a model card.

The card stores the fitted species-group coefficients, feature scaling, data
checksums, pins, and the conditional calibration rule. It stores no site-level
rows. The card is the durable artifact behind the FreshForge workflow.
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

TARGET = "Quesnel TSA"
TREE = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4-growth/tree_survival.csv")
INTERVALS = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4-growth/intervals.csv")
RAW = Path("/srv/shared-data/gep/ws4/tmp/inv01-data/psp/faib_tree_detail.csv")
METRICS = Path("notes/reference/calibration/d9-quesnel-nonpl-summary.csv")
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
    base = bp.design(frame, zones)
    return np.delete(base, [6, 9], axis=1)


def main() -> None:
    """Fit the candidate and write the model card."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frame = bp.load()
    train = frame[frame["TSA_DESC"].astype(str) != TARGET]
    zones = sorted(frame["zone"].dropna().unique())
    feature_names = list(FEATURES) + [f"zone_{zone}" for zone in zones]
    groups: dict[str, object] = {}
    for group in bp.GROUPS:
        part = train[train["group"] == group]
        if len(part) < 1000:
            continue
        x = _design(part, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, part["dead"].to_numpy(), part["exposure"].to_numpy())
        groups[group] = {
            "beta": [float(value) for value in beta],
            "mean": [float(value) for value in mean],
            "scale": [float(value) for value in scale],
            "n": len(part),
        }

    metrics = pd.read_csv(METRICS).to_dict("records") if METRICS.exists() else []
    card = {
        "model_id": "quesnel-sbsmw-background-v0",
        "status": "frozen_candidate_layer",
        "target_tsa": TARGET,
        "excluded_from_training": [TARGET],
        "features": feature_names,
        "species_groups": groups,
        "calibration": {
            "target_tsa": TARGET,
            "calibration_sites": 20,
            "overprediction_threshold": 0.03,
            "minimum_group_trees": 500,
            "rule": (
                "Estimate one species-group intercept on target sites; apply it only when the "
                "calibrated group has at least 500 trees and overpredicts by more than 3 points."
            ),
        },
        "metrics": metrics,
        "pins": {
            "pyfvs_commit": PYFVS_COMMIT,
            "fvs_source_commit": FVS_SOURCE_COMMIT,
            "variant": "bc",
            "wrapper_version": __version__,
        },
        "data_checksums": {
            "tree_survival.csv": _digest(TREE),
            "intervals.csv": _digest(INTERVALS),
            "faib_tree_detail.csv": _digest(RAW),
        },
        "limitations": [
            "PL is excluded; the candidate is non-PL background only.",
            "Small-tree PL residual is documented separately, not modeled.",
            "Only one target TSA; no production temporal validation.",
            "The MPB layer is separate and local.",
        ],
        "claim": (
            "Frozen diagnostic candidate layer for Quesnel non-PL background mortality. "
            "Not a yield, AAC, legal, whole-block, or certificate claim."
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
