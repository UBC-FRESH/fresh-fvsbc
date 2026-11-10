"""Fit one target-excluded hierarchical BEC model.

The model uses parent BEC zone fixed effects plus partial-pooled subzone
intercepts. Subzone offsets are shrunken by ``n / (n + 500)`` and updated by
backfitting. TSA is not in the predictor.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd
from fit_candidate import _delta, _design

PRIOR_TREES = 500
PASSES = 2


def main() -> None:
    """Fit one TSA holdout and write group and aggregate metrics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frame = bp.load()
    frame["subzone"] = frame["zone"]
    frame["zone"] = frame["zone"].str.extract(r"^([A-Z]+)")[0]
    parent_zones = sorted(frame["zone"].dropna().unique())
    train = frame[frame["TSA_DESC"].astype(str) != args.target]
    target = frame[frame["TSA_DESC"].astype(str) == args.target].copy()
    if target.empty:
        raise SystemExit(f"no rows for {args.target}")
    rows = []
    y_all: list[np.ndarray] = []
    p_all: list[np.ndarray] = []
    for group in bp.GROUPS:
        part = train[train["group"] == group]
        test = target[target["group"] == group]
        if len(part) < 1000 or test.empty:
            continue
        x = _design(part, parent_zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        xt = _design(test, parent_zones)
        xt[:, 1:] = (xt[:, 1:] - mean) / scale
        beta = bm._fit(x, part["dead"].to_numpy(), part["exposure"].to_numpy())
        offsets: dict[str, float] = {}
        part_subzone = part["subzone"].astype(str).to_numpy()
        for _ in range(PASSES):
            train_offset = np.array([offsets.get(value, 0.0) for value in part_subzone])
            beta = bm._fit(
                x,
                part["dead"].to_numpy(),
                part["exposure"].to_numpy(),
                offset=train_offset,
            )
            fixed = x @ beta
            updated: dict[str, float] = {}
            for subzone in np.unique(part_subzone):
                mask = part_subzone == subzone
                count = int(mask.sum())
                delta = _delta(
                    fixed[mask],
                    part["dead"].to_numpy()[mask],
                    part["exposure"].to_numpy()[mask],
                )
                updated[str(subzone)] = count / (count + PRIOR_TREES) * delta
            offsets = updated
        train_offset = np.array([offsets.get(value, 0.0) for value in part_subzone])
        beta = bm._fit(
            x,
            part["dead"].to_numpy(),
            part["exposure"].to_numpy(),
            offset=train_offset,
        )
        target_offset = target.loc[test.index, "subzone"].astype(str).map(offsets).fillna(0.0)
        pred = 1.0 - np.exp(
            -test["exposure"].to_numpy()
            * np.exp(np.clip(xt @ beta + target_offset.to_numpy(dtype=float), -20, 20))
        )
        metric = bp.metrics(test["dead"].to_numpy(), pred)
        rows.append({"target": args.target, "group": group, **metric})
        y_all.append(test["dead"].to_numpy())
        p_all.append(pred)
    if not y_all:
        raise SystemExit(f"no fitted groups for {args.target}")
    all_metric = bp.metrics(np.concatenate(y_all), np.concatenate(p_all))
    rows.append({"target": args.target, "group": "ALL", **all_metric})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"wrote {args.output} for {args.target}")


if __name__ == "__main__":
    main()
