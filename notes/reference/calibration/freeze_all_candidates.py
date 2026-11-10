"""Freeze a base card for every TSA label that lacks one.

Each target runs ``fit_candidate.py`` in a separate process with the current
growth-free recipe, no local calibration, and zero target-support minimum. The
driver writes no site-level rows.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import bcmort_provincial as bp

ROOT = Path("notes/reference/calibration")
SCRIPT = ROOT / "fit_candidate.py"
REGISTRY = ROOT / "candidate-registry.json"


def _slug(tsa: str) -> str:
    """Return a candidate directory slug for a TSA label."""
    base = tsa.removesuffix(" TSA").lower()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def main() -> None:
    """Run the missing targets and report failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=12)
    args = parser.parse_args()

    frame = bp.load()
    all_targets = sorted(frame["TSA_DESC"].dropna().astype(str).unique())
    registry = json.loads(REGISTRY.read_text())
    frozen = {entry["target_tsa"] for entry in registry["candidates"]}
    missing = [target for target in all_targets if target not in frozen]
    failures: list[str] = []

    def run(target: str) -> None:
        slug = _slug(target)
        directory = ROOT / f"{slug}-candidate"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--target-tsa",
                target,
                "--model-id",
                f"{slug}-background-v0",
                "--calibration",
                "none",
                "--min-target-trees",
                "0",
                "--metrics",
                str(directory / "metrics.csv"),
                "--model-card",
                str(directory / "model-card.json"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            failures.append(f"{target}: {completed.stderr[-400:]}")
        else:
            print(f"froze {target}")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        list(pool.map(run, missing))
    if failures:
        raise SystemExit("card failures:\n" + "\n".join(failures))
    print(f"froze {len(missing)} cards")


if __name__ == "__main__":
    main()
