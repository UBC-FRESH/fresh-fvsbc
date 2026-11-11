"""Build and check the full-BC review-bundle manifest.

The manifest pins all 40 cards, their metrics, and the policy/evidence files by
SHA-256. It also verifies that every card carries preprocessing metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path("notes/reference/calibration")
REGISTRY = ROOT / "candidate-registry.json"
OUTPUT = ROOT / "full-bc-review-manifest.json"
STATIC = (
    "candidate-registry.json",
    "CANDIDATE-REGISTRY.md",
    "calibration-policy.json",
    "CALIBRATION-POLICY.md",
    "support-policy.json",
    "d9-support-policy.csv",
    "d9-support-policy.md",
    "d9-bec-stratification.csv",
    "d9-bec-strata.csv",
    "d9-bec-stratification.md",
    "d9-bec-hierarchy.md",
    "d9-tsa-calibration-sweep.csv",
    "d9-tsa-local-sweep.csv",
    "d9-tsa-partial-sweep.csv",
    "d9-bec-calibration.csv",
    "d9-domain-calibration.csv",
    "d9-imputation-sensitivity.md",
    "d9-candidate-review-package.md",
    "review-manifest.json",
    "d9-full-bc-review-bundle.md",
    "FULL-BC-REVIEW-INSTRUCTIONS.md",
    "REVIEW-INSTRUCTIONS.md",
    "d9-review-addendum-1.md",
    "d9-deployment-calibration.md",
    "d9-raw-scoring.md",
    "deployment_calibration.py",
    "score_inventory.py",
    "sweep_support_policy.py",
)


def _digest(path: Path) -> str:
    """Return a SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _payload() -> dict[str, object]:
    """Return the bundle manifest."""
    registry = json.loads(REGISTRY.read_text())
    cards = registry["candidates"]
    if len(cards) != 40:
        raise SystemExit(f"expected 40 cards, found {len(cards)}")
    if len({card["model_id"] for card in cards}) != 40:
        raise SystemExit("duplicate model_id in registry")
    artifacts: dict[str, dict[str, object]] = {}
    for card in cards:
        card_path = Path(card["card"])
        metrics_path = Path(card["metrics"]) if card["metrics"] else None
        data = json.loads(card_path.read_text())
        preprocessing = data.get("preprocessing", {})
        if not preprocessing.get("medians") or not preprocessing.get("zones"):
            raise SystemExit(f"card lacks preprocessing metadata: {card_path}")
        artifacts[str(card_path)] = {
            "sha256": _digest(card_path),
            "bytes": card_path.stat().st_size,
        }
        if metrics_path and metrics_path.is_file():
            artifacts[str(metrics_path)] = {
                "sha256": _digest(metrics_path),
                "bytes": metrics_path.stat().st_size,
            }
    for name in STATIC:
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"missing bundle artifact: {path}")
        artifacts[str(path)] = {"sha256": _digest(path), "bytes": path.stat().st_size}
    return {
        "bundle_id": "d9-full-bc-review-v0",
        "status": "published_for_review",
        "decision": "pending",
        "scope": {
            "cards": 40,
            "review_pending": registry["counts"].get("review_pending", 0),
            "not_in_current_review": registry["counts"].get("not_in_current_review", 0),
            "evidence_only": ["invermere", "100-mile-house"],
        },
        "instructions": "notes/reference/calibration/FULL-BC-REVIEW-INSTRUCTIONS.md",
        "bundle": "notes/reference/calibration/d9-full-bc-review-bundle.md",
        "artifacts": artifacts,
        "claim": (
            "Full-BC review bundle only. No production bundle, certificate, yield, AAC, "
            "legal, or whole-block claim."
        ),
    }


def main() -> None:
    """Write or check the full-BC review manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    text = json.dumps(_payload(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit(f"stale full-BC review manifest: {args.output}")
        print("full-BC review bundle ok: 40 cards")
        return
    args.output.write_text(text)
    print(f"wrote {args.output} with 40 cards")


if __name__ == "__main__":
    main()
