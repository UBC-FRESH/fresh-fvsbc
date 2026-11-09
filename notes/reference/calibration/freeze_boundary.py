"""Freeze the small-tree PL residual as a checked model boundary.

The panel table is aggregate: one row per external case, with no site key. The
script checks the boundary claim, then writes a JSON card with the panel
summary, checksum, pins, and the rule that MPB is not tuned for small trees.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from fresh_fvsbc import __version__
from fresh_fvsbc.provenance import FVS_SOURCE_COMMIT, PYFVS_COMMIT

PANEL = Path("notes/reference/calibration/d9-small-tree-panel-summary.csv")
OUTPUT = Path("notes/reference/calibration/quesnel-candidate/small-tree-boundary.json")
COLUMNS = ("case_index", "final_live_pl_tpa", "max_live_dbh_cm", "live_pl_above_15_tpa")
THRESHOLD_CM = 15.0
ABOVE_LIMIT_TPA = 1.0
DBH_LIMIT_CM = 20.0


def _digest(path: Path) -> str:
    """Return a SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _check(panel: pd.DataFrame) -> None:
    """Raise when the panel no longer supports the small-tree boundary.

    Parameters
    ----------
    panel : pandas.DataFrame
        The aggregate panel table.

    Raises
    ------
    SystemExit
        If a required column is missing, a value is negative, or the residual
        includes material live PL above the small-tree threshold.
    """
    missing = [column for column in COLUMNS if column not in panel.columns]
    if missing:
        raise SystemExit(f"panel is missing columns: {', '.join(missing)}")
    if panel[list(COLUMNS)].isna().any().any():
        raise SystemExit("panel contains missing values")
    numeric = panel[["final_live_pl_tpa", "max_live_dbh_cm", "live_pl_above_15_tpa"]]
    if (numeric < 0).any().any():
        raise SystemExit("panel contains negative values")
    above = float(panel["live_pl_above_15_tpa"].sum())
    if above > ABOVE_LIMIT_TPA:
        raise SystemExit(f"live PL above {THRESHOLD_CM:g} cm is {above:g}/ac, above the boundary")
    dbh = float(panel["max_live_dbh_cm"].max())
    if dbh > DBH_LIMIT_CM:
        raise SystemExit(f"maximum live PL DBH is {dbh:g} cm, above the boundary")


def main() -> None:
    """Check the panel and write the frozen boundary card."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=PANEL)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    panel = pd.read_csv(args.panel)
    _check(panel)
    card = {
        "boundary_id": "quesnel-pl-small-tree-v0",
        "status": "frozen_boundary",
        "boundary": {
            "threshold_cm": THRESHOLD_CM,
            "rule": (
                "MPB handles the large-tree PL collapse. Do not tune INITMORT for small PL; "
                "report the sub-threshold residual as a separate mortality gap."
            ),
        },
        "panel": {
            "cases": len(panel),
            "mean_final_live_pl_tpa": float(panel["final_live_pl_tpa"].mean()),
            "max_final_live_pl_tpa": float(panel["final_live_pl_tpa"].max()),
            "max_live_dbh_cm": float(panel["max_live_dbh_cm"].max()),
            "live_pl_above_15_tpa": float(panel["live_pl_above_15_tpa"].sum()),
        },
        "checks": {
            "above_threshold_limit_tpa": ABOVE_LIMIT_TPA,
            "max_dbh_limit_cm": DBH_LIMIT_CM,
            "passed": True,
        },
        "evidence": {
            "note": "notes/reference/calibration/d9-small-tree-panel.md",
            "panel": str(args.panel),
            "panel_checksum": _digest(args.panel),
        },
        "pins": {
            "pyfvs_commit": PYFVS_COMMIT,
            "fvs_source_commit": FVS_SOURCE_COMMIT,
            "variant": "bc",
            "wrapper_version": __version__,
        },
        "claim": (
            "Frozen diagnostic boundary for sub-threshold PL after MPB. Not a yield, AAC, legal, "
            "whole-block, or certificate claim."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
