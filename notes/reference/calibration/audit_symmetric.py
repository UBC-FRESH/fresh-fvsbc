"""Audit the symmetric local rule across the candidate set.

The audit fits each target-excluded growth-free model, then compares the base
metrics with the symmetric 20-site local rule. It writes aggregate rows only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd
from fit_candidate import _design, _local_metrics

TARGETS = (
    ("north-island", "North Island TSA"),
    ("kamloops", "Kamloops TSA"),
    ("prince-george", "Prince George TSA"),
    ("cranbrook", "Cranbrook TSA"),
    ("arrow", "Arrow TSA"),
    ("fraser", "Fraser TSA"),
    ("mackenzie", "MacKenzie TSA"),
    ("haida-gwaii", "Haida Gwaii TSA"),
    ("kootenay-lake", "Kootenay Lake TSA"),
    ("boundary", "Boundary TSA"),
)
MIN_TARGET_TREES = 500


def main() -> None:
    """Run the audit and write one aggregate row per target."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notes/reference/calibration/d9-symmetric-audit.csv"),
    )
    args = parser.parse_args()

    frame = bp.load()
    zones = sorted(frame["zone"].dropna().unique())
    rows = []
    for label, target_name in TARGETS:
        train = frame[frame["TSA_DESC"].astype(str) != target_name]
        target = frame[frame["TSA_DESC"].astype(str) == target_name].copy()
        if target.empty:
            continue
        y: list[np.ndarray] = []
        p: list[np.ndarray] = []
        target_rows: list[pd.DataFrame] = []
        for group in bp.GROUPS:
            part = train[train["group"] == group]
            test = target[target["group"] == group]
            if len(part) < 1000 or test.empty or len(test) < MIN_TARGET_TREES:
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
            y.append(test["dead"].to_numpy())
            p.append(pred)
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
        if not y:
            continue
        base = bp.metrics(np.concatenate(y), np.concatenate(p))
        local = _local_metrics(
            pd.concat(target_rows, ignore_index=True),
            calibration_sites=20,
            bootstrap=40,
            symmetric=True,
        )
        local_mean = local.get("mean_metrics", {})
        rows.append(
            {
                "target": label,
                "n": base["n"],
                "base_mean_pred": base["mean_pred"],
                "base_event_rate": base["event_rate"],
                "base_auc": base["auc"],
                "base_log_loss": base["log_loss"],
                "symmetric_mean_pred": local_mean.get("mean_pred"),
                "symmetric_auc": local_mean.get("auc"),
                "symmetric_log_loss": local_mean.get("log_loss"),
                "delta_log_loss": (
                    local_mean.get("log_loss", np.nan) - base["log_loss"] if local_mean else np.nan
                ),
            }
        )
        local_loss = local_mean.get("log_loss", float("nan"))
        print(f"{label:16s} base_ll={base['log_loss']:.3f} local_ll={local_loss:.3f}")
    result = pd.DataFrame(rows).sort_values("target")
    args.output.write_text(result.to_csv(index=False))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
