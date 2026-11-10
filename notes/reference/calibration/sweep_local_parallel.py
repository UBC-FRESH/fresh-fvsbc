"""Run the local-rule sweep in parallel.

Each target runs ``sweep_local.py --target`` in a separate process. The driver
combines the per-target mode tables into one aggregate CSV.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import bcmort_provincial as bp
import pandas as pd

SCRIPT = Path("notes/reference/calibration/sweep_local.py")


def main() -> None:
    """Run every target and combine the parts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notes/reference/calibration/d9-tsa-local-sweep.csv"),
    )
    parser.add_argument("--jobs", type=int, default=12)
    args = parser.parse_args()

    frame = bp.load()
    targets = sorted(frame["TSA_DESC"].dropna().astype(str).unique())
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tsa-local-sweep-") as directory:
        root = Path(directory)
        parts = [root / f"part-{index:02d}.csv" for index in range(len(targets))]

        def run(target: str, part: Path) -> None:
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
            )
            if completed.returncode != 0:
                failures.append(f"{target}: {completed.stderr[-400:]}")

        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            list(pool.map(run, targets, parts))
        if failures:
            raise SystemExit("local sweep failures:\n" + "\n".join(failures))
        frames = [pd.read_csv(part) for part in parts if part.stat().st_size]
    result = pd.concat(frames, ignore_index=True)
    mode_order = {"base": 0, "one_sided": 1, "symmetric": 2}
    result["_mode"] = result["mode"].map(mode_order).fillna(9).astype(int)
    result = result.sort_values(["tsa", "_mode"]).drop(columns="_mode")
    args.output.write_text(result.to_csv(index=False))
    print(f"wrote {args.output} with {len(result)} rows")


if __name__ == "__main__":
    main()
