"""Post-2000 temporal validation of the provincial mortality model.

Train on intervals ending by 2000, test on intervals starting in 2000 or later.
The result isolates the PL/MPB temporal failure from the rest of the model.

This is a diagnostic prototype, not an FVS integration.
"""

from __future__ import annotations

import bcmort_prototype as bm
import bcmort_provincial as bp
import numpy as np
import pandas as pd


def main() -> None:
    """Fit pre-2000 species-group models and report the post-2000 test."""
    frame = bp.load()
    parts = frame["interval_id"].str.split("|", expand=True)
    frame["year0"] = parts[2].astype(int)
    frame["year1"] = parts[3].astype(int)
    train = frame[frame["year1"] <= 2000]
    test = frame[frame["year0"] >= 2000].copy()
    zones = sorted(frame["zone"].dropna().unique())
    rows = []
    all_y = []
    all_p = []
    for group in bp.GROUPS:
        tr = train[train["group"] == group]
        te = test[test["group"] == group]
        if len(tr) < 1000 or te.empty:
            continue
        x = bp.design(tr, zones)
        mean = x[:, 1:].mean(axis=0)
        scale = x[:, 1:].std(axis=0)
        scale[scale == 0] = 1
        x[:, 1:] = (x[:, 1:] - mean) / scale
        beta = bm._fit(x, tr["dead"].to_numpy(), tr["exposure"].to_numpy())
        xt = bp.design(te, zones)
        xt[:, 1:] = (xt[:, 1:] - mean) / scale
        pred = bm._predict(xt, te["exposure"].to_numpy(), beta)
        metric = bp.metrics(te["dead"].to_numpy(), pred)
        rows.append({"group": group, **metric})
        all_y.append(te["dead"].to_numpy())
        all_p.append(pred)
        print(
            f"{group:5s} n={metric['n']:7.0f} auc={metric['auc']:.3f} "
            f"mean={metric['mean_pred']:.3f} obs={metric['event_rate']:.3f} "
            f"ll={metric['log_loss']:.3f}"
        )
    overall = bp.metrics(np.concatenate(all_y), np.concatenate(all_p))
    rows.append({"group": "ALL", **overall})
    print(
        f"ALL   n={overall['n']:7.0f} auc={overall['auc']:.3f} "
        f"mean={overall['mean_pred']:.3f} obs={overall['event_rate']:.3f} "
        f"ll={overall['log_loss']:.3f}"
    )
    pd.DataFrame(rows).to_csv(
        "notes/reference/calibration/d9-provincial-temporal-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
