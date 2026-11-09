"""Build the candidate-review manifest.

The manifest pins the tracked candidate artifacts, workflows, and scripts by
SHA-256. It contains no site-level rows. The script fails when an expected model
card or boundary card is missing or no longer carries its frozen identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from fresh_fvsbc import __version__
from fresh_fvsbc.provenance import FVS_SOURCE_COMMIT, PYFVS_COMMIT

ARTIFACTS = (
    "notes/reference/calibration/d9-candidate-review-package.md",
    "notes/reference/calibration/REVIEW-INSTRUCTIONS.md",
    "notes/reports/d9-candidate-review-template.md",
    "notes/reference/calibration/quesnel-candidate/README.md",
    "notes/reference/calibration/quesnel-candidate/JOINT-REPORT.md",
    "notes/reference/calibration/quesnel-candidate/metrics.csv",
    "notes/reference/calibration/quesnel-candidate/model-card.json",
    "notes/reference/calibration/quesnel-candidate/small-tree-boundary.json",
    "notes/reference/calibration/okanagan-candidate/README.md",
    "notes/reference/calibration/okanagan-candidate/metrics.csv",
    "notes/reference/calibration/okanagan-candidate/model-card.json",
    "notes/reference/calibration/d9-small-tree-panel-summary.csv",
    "notes/reference/calibration/d9-provincial-crown-si-summary.csv",
    "notes/reference/calibration/d9-provincial-calibration-summary.csv",
    "notes/reference/calibration/d9-okanagan-candidate-summary.csv",
    "workflows/freshforge/quesnel_background.yaml",
    "workflows/freshforge/quesnel_mpb_segment.yaml",
    "workflows/freshforge/okanagan_background.yaml",
    "notes/reference/calibration/bcmort_provincial.py",
    "notes/reference/calibration/bcmort_provincial_calibration.py",
    "notes/reference/calibration/freeze_model.py",
    "notes/reference/calibration/fit_candidate.py",
    "notes/reference/calibration/mpb_segment.py",
    "notes/reference/calibration/freeze_boundary.py",
    "notes/reference/calibration/d9-freshforge-workflow.md",
    "notes/reference/calibration/d9-freshforge-mpb.md",
    "notes/reference/calibration/d9-freshforge-boundary.md",
    "notes/reference/calibration/d9-freshforge-okanagan.md",
    "notes/reference/calibration/d9-okanagan-candidate.md",
    "notes/reference/calibration/d9-quesnel-mpb-segment.md",
    "notes/reference/calibration/d9-small-tree-panel.md",
)


def _digest(path: Path) -> str:
    """Return a SHA-256 digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _check_cards() -> None:
    """Fail when the frozen cards no longer carry their expected identity."""
    quesnel = json.loads(
        Path("notes/reference/calibration/quesnel-candidate/model-card.json").read_text()
    )
    okanagan = json.loads(
        Path("notes/reference/calibration/okanagan-candidate/model-card.json").read_text()
    )
    boundary = json.loads(
        Path("notes/reference/calibration/quesnel-candidate/small-tree-boundary.json").read_text()
    )
    if quesnel.get("model_id") != "quesnel-sbsmw-background-v0":
        raise SystemExit("Quesnel model card has an unexpected model_id")
    if okanagan.get("model_id") != "okanagan-background-v0":
        raise SystemExit("Okanagan model card has an unexpected model_id")
    if boundary.get("boundary_id") != "quesnel-pl-small-tree-v0":
        raise SystemExit("small-tree boundary card has an unexpected boundary_id")
    if boundary.get("checks", {}).get("passed") is not True:
        raise SystemExit("small-tree boundary card does not pass its checks")


def main() -> None:
    """Write the review manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notes/reference/calibration/review-manifest.json"),
    )
    args = parser.parse_args()

    _check_cards()
    entries = {}
    for name in ARTIFACTS:
        path = Path(name)
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {name}")
        entries[name] = {
            "sha256": _digest(path),
            "bytes": path.stat().st_size,
        }
    manifest = {
        "package_id": "d9-candidate-review-v0",
        "status": "published_for_review",
        "decision": "pending",
        "scope": {
            "quesnel": [
                "quesnel-sbsmw-background-v0",
                "quesnel large-tree MPB segment",
                "quesnel small-tree PL boundary",
            ],
            "okanagan": ["okanagan-background-v0"],
            "excluded": [
                "100 Mile (retracted)",
                "IDFdk (no bundle)",
                "ICHmw2 (unsigned)",
                "CWH volume question",
                "SBPSmk mature",
                "new TSAs and global screens",
            ],
        },
        "pins": {
            "pyfvs_commit": PYFVS_COMMIT,
            "fvs_source_commit": FVS_SOURCE_COMMIT,
            "variant": "bc",
            "wrapper_version": __version__,
        },
        "artifacts": entries,
        "instructions": "notes/reference/calibration/REVIEW-INSTRUCTIONS.md",
        "claim": (
            "Review package only. No bundle, certificate, yield, AAC, legal, or whole-block claim."
        ),
    }
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output} with {len(entries)} artifacts")


if __name__ == "__main__":
    main()
