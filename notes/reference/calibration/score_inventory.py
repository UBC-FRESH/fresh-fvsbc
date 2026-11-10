"""Score raw inventory rows with a frozen candidate card.

The input is a feature table with ``site``, ``plot``, ``dbh``, ``ba0``, ``tph0``,
``height``, ``damage``, ``growth``, ``crown``, ``si``, and ``zone``, plus either
``group`` or ``species``. The card supplies the species-group coefficients,
scalers, zones, and preprocessing medians. The output is a scored table with
``site,plot,group,eta``.

The card's medians are the frozen full-frame values; the candidate review
package flags that imputation concern. This script does not fit or tune a model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

GROUPS = ("FD", "PL", "SE", "HW", "OTHER")
BASE_FEATURES = (
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


def _group_name(group: str) -> str:
    """Normalize a species group."""
    value = str(group).upper()
    return value if value in GROUPS[:-1] else "OTHER"


def _design(frame: pd.DataFrame, zones: list[str]) -> np.ndarray:
    """Build the growth-free design from the prepared feature table."""
    zone = frame["zone"].to_numpy()
    columns = [
        np.ones(len(frame)),
        np.log(frame["dbh"].clip(lower=0.1)),
        np.log1p(frame["ba0"].clip(lower=0)),
        np.log1p(frame["qmd"].clip(lower=0)),
        frame["rel_dbh"].to_numpy(),
        frame["hd"].to_numpy(),
        frame["damage"].astype(float).to_numpy(),
        frame["hd_missing"].to_numpy(),
        frame["crown"].to_numpy(),
        frame["crown_missing"].to_numpy(),
        frame["si"].to_numpy(),
        frame["si_missing"].to_numpy(),
    ]
    columns.extend([(zone == value).astype(float) for value in zones])
    return np.column_stack(columns)


def main() -> None:
    """Score raw feature rows and write ``eta``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    card = json.loads(args.card.read_text())
    preprocessing = card.get("preprocessing", {})
    medians = preprocessing.get("medians")
    zones = preprocessing.get("zones")
    if not medians or not zones:
        raise SystemExit("card has no preprocessing medians/zones; regenerate it first")
    frame = pd.read_csv(args.input)
    if "group" in frame.columns:
        frame["group"] = frame["group"].map(_group_name)
    elif "species" in frame.columns:
        species_map = preprocessing.get("species_groups", {})
        frame["group"] = frame["species"].astype(str).str.upper().map(species_map).map(_group_name)
    else:
        raise SystemExit("input needs group or species")
    required = (
        "site",
        "plot",
        "dbh",
        "ba0",
        "tph0",
        "height",
        "damage",
        "growth",
        "crown",
        "si",
        "zone",
    )
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise SystemExit(f"input is missing columns: {', '.join(missing)}")
    if frame["group"].isna().any():
        raise SystemExit("some species did not map to a group")

    frame["zone"] = frame["zone"].astype(str).str.extract(r"^([A-Za-z]+)")[0].str.upper()
    if frame["zone"].isna().any():
        raise SystemExit("zone is missing")
    for column in ("crown", "si"):
        frame[column + "_missing"] = frame[column].isna().astype(float)
        frame[column] = frame[column].fillna(float(medians[column]))
    frame["qmd"] = 100.0 * np.sqrt(4.0 * frame["ba0"] / (np.pi * frame["tph0"]))
    frame["rel_dbh"] = frame["dbh"] / frame.groupby(["site", "plot"])["dbh"].transform("max")
    frame["hd"] = frame["height"] / (frame["dbh"] / 100.0)
    for column in ("hd", "growth"):
        frame[column + "_missing"] = frame[column].isna().astype(float)
        frame[column] = frame[column].fillna(float(medians[column]))
    frame["damage"] = frame["damage"].fillna(0.0)

    design = _design(frame, zones)
    outputs = []
    for group in GROUPS:
        part = frame["group"] == group
        if not part.any():
            continue
        coefficients = card.get("species_groups", {}).get(group)
        if not coefficients:
            raise SystemExit(f"card has no coefficients for {group}")
        beta = np.asarray(coefficients["beta"], dtype=float)
        mean = np.asarray(coefficients["mean"], dtype=float)
        scale = np.asarray(coefficients["scale"], dtype=float)
        if len(beta) != design.shape[1] or len(mean) != design.shape[1] - 1:
            raise SystemExit(f"feature count mismatch for {group}")
        x = design[part.to_numpy()].copy()
        x[:, 1:] = (x[:, 1:] - mean) / scale
        outputs.append(
            pd.DataFrame(
                {
                    "site": frame.loc[part, "site"].to_numpy(),
                    "plot": frame.loc[part, "plot"].to_numpy(),
                    "group": group,
                    "eta": x @ beta,
                }
            )
        )
    scored = pd.concat(outputs, ignore_index=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(args.output, index=False)
    print(f"wrote {args.output} with {len(scored)} rows")


if __name__ == "__main__":
    main()
