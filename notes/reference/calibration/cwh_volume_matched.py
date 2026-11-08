"""Recompute CWH observed volume with the FVS merchantability limits.

The CWH 4 cm validation compared FVS ``MCuM`` with all observed ``VOL_MER``
trees.  FVS only counts trees above ``DBHMIN`` (17.5 cm, or 12.5 cm for
lodgepole pine), so this script filters the observed trees to the same limit.
It is an audit, not a calibration.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode")
VALIDATION = Path("runtime/d9-cwh-4cm-validation/validation-rows.csv")
PSP_RAW = Path("/srv/shared-data/gep/ws4/tmp/inv01-data/psp/faib_tree_detail.csv")
NONPSP_RAW = ROOT / "faib-audit/nonpsp-rep/faib_tree_detail.csv"
DATASETS = {
    "Arrowsmith": ("psp4", PSP_RAW),
    "Fraser": ("psp4", PSP_RAW),
    "Haida Gwaii": ("psp4", PSP_RAW),
    "temporal >=2000": ("psp4-temporal-2000", PSP_RAW),
    "non-PSP external": ("nonpsp4", NONPSP_RAW),
}
COLUMNS = [
    "SITE_IDENTIFIER",
    "VISIT_NUMBER",
    "PLOT",
    "SPECIES",
    "DBH",
    "LV_D",
    "PHF_TREE",
    "TREE_WT",
    "VOL_MER",
]


def _observed(interval: pd.Series, raw: pd.DataFrame) -> float:
    trees = raw[
        (raw["SITE_IDENTIFIER"].astype(str) == str(interval["SITE_IDENTIFIER"]))
        & (raw["VISIT_NUMBER"].astype(int) == int(interval["visit1"]))
        & (raw["PLOT"].astype(float) == float(interval["PLOT"]))
        & (raw["LV_D"] == "L")
    ].copy()
    if trees.empty:
        return float("nan")
    trees["phf"] = trees["PHF_TREE"] * trees["TREE_WT"].fillna(1)
    trees["volume"] = trees["VOL_MER"].fillna(0) * trees["phf"]
    min_dbh = trees["SPECIES"].astype(str).str.upper().eq("PL").map({True: 12.5, False: 17.5})
    return float(trees.loc[trees["DBH"] >= min_dbh, "volume"].sum())


def main() -> None:
    """Recompute matched observed volume and write the summary CSV."""
    validation = pd.read_csv(VALIDATION)
    raw_cache: dict[Path, pd.DataFrame] = {}
    rows: list[dict[str, object]] = []
    for holdout, group in validation.groupby("holdout"):
        dataset, raw_path = DATASETS[holdout]
        intervals = pd.read_csv(ROOT / dataset / "intervals.csv").set_index("interval_id")
        if raw_path not in raw_cache:
            raw_cache[raw_path] = pd.read_csv(raw_path, usecols=COLUMNS)
        raw = raw_cache[raw_path]
        for row in group.to_dict("records"):
            interval_id = str(row["interval_id"])
            if interval_id not in intervals.index:
                continue
            observed = _observed(intervals.loc[interval_id], raw)
            if pd.isna(observed):
                continue
            rows.append(
                {
                    "holdout": holdout,
                    "predicted": float(row["predicted_volume"]),
                    "obs_all": float(row["observed_volume"]),
                    "obs_matched": observed,
                }
            )
    result = pd.DataFrame(rows)
    summary = []
    for holdout, group in [*result.groupby("holdout"), ("all", result)]:
        matched = (
            100 * (group["predicted"] - group["obs_matched"]).sum() / group["obs_matched"].sum()
        )
        all_trees = 100 * (group["predicted"] - group["obs_all"]).sum() / group["obs_all"].sum()
        summary.append(
            {
                "holdout": holdout,
                "n": len(group),
                "matched_percent": matched,
                "all_percent": all_trees,
            }
        )
        print(f"{holdout:20s} n={len(group):3d}  matched={matched:6.2f}%  all={all_trees:6.2f}%")
    pd.DataFrame(summary).to_csv(
        "notes/reference/calibration/d9-cwh-volume-matched-summary.csv", index=False
    )


if __name__ == "__main__":
    main()
