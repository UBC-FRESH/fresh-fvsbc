"""Run the hierarchical BEC holdout in parallel."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import bcmort_provincial as bp
import pandas as pd

SCRIPT = Path("notes/reference/calibration/fit_bec_hierarchy.py")


def main() -> None:
    """Run every target and combine the parts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notes/reference/calibration/d9-bec-hierarchy-holdout.csv"),
    )
    parser.add_argument("--jobs", type=int, default=12)
    args = parser.parse_args()

    frame = bp.load()
    targets = sorted(frame["TSA_DESC"].dropna().astype(str).unique())
    failures: list[str] = []
    root = Path("runtime/bec-hierarchy-parts")
    root.mkdir(parents=True, exist_ok=True)
    parts = [root / f"part-{index:02d}.csv" for index in range(len(targets))]

    def run(target: str, part: Path) -> None:
        if part.is_file() and part.stat().st_size:
            return
        environment = os.environ.copy()
        environment["OMP_NUM_THREADS"] = "1"
        environment["OPENBLAS_NUM_THREADS"] = "1"
        environment["MKL_NUM_THREADS"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--target",
                target,
                "--output",
                str(part),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        if completed.returncode != 0:
            failures.append(f"{target}: {completed.stderr[-400:]}")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(run, targets, parts))
    if failures:
        raise SystemExit("hierarchy failures:\n" + "\n".join(failures))
    frames = [pd.read_csv(part) for part in parts if part.stat().st_size]
    result = pd.concat(frames, ignore_index=True)
    order = {"ALL": 0, "FD": 1, "PL": 2, "SE": 3, "HW": 4, "OTHER": 5}
    result["_order"] = result["group"].map(order).fillna(9).astype(int)
    result = result.sort_values(["target", "_order"]).drop(columns="_order")
    args.output.write_text(result.to_csv(index=False))
    print(f"wrote {args.output} with {len(result)} rows")


if __name__ == "__main__":
    main()
