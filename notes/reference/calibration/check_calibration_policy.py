"""Validate the candidate calibration policy against the frozen cards.

The check is intentionally narrow: it verifies the supported symmetric cases,
the not-frozen case, the minimums, and the audit deltas. It does not rerun any
model.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

POLICY = Path("notes/reference/calibration/calibration-policy.json")
AUDIT = Path("notes/reference/calibration/d9-symmetric-audit.csv")


def main() -> None:
    """Validate the policy and its evidence."""
    policy = json.loads(POLICY.read_text())
    if policy.get("default_rule") != "none":
        raise SystemExit("default rule must be none")
    minimums = policy.get("minimums", {})
    expected = {
        "calibration_sites": 20,
        "group_trees": 500,
        "trigger_points": 0.03,
        "bootstrap_splits": 40,
    }
    if minimums != expected:
        raise SystemExit(f"unexpected minimums: {minimums}")

    supported = policy.get("supported", {})
    if set(supported) != {"boundary", "mackenzie"}:
        raise SystemExit(f"unexpected supported cases: {sorted(supported)}")
    audit = {row["target"]: row for row in csv.DictReader(AUDIT.open())}
    for name, entry in supported.items():
        if entry.get("rule") != "symmetric":
            raise SystemExit(f"{name} is not marked symmetric")
        card_path = Path(entry["card"])
        if not card_path.is_file():
            raise SystemExit(f"missing card: {card_path}")
        card = json.loads(card_path.read_text())
        calibration = card.get("calibration", {})
        if calibration.get("mode") != "conditional-symmetric":
            raise SystemExit(f"{name} card mode is not conditional-symmetric")
        if calibration.get("recommended") is not True:
            raise SystemExit(f"{name} card does not mark the rule recommended")
        if float(audit[name]["delta_log_loss"]) >= 0:
            raise SystemExit(f"{name} has a non-negative audit delta")

    not_frozen = policy.get("not_frozen", {})
    if "invermere" not in not_frozen:
        raise SystemExit("invermere must be recorded as not frozen")
    if Path(not_frozen["invermere"]["card"]).exists():
        raise SystemExit("invermere card exists, but the policy says it is not frozen")

    excluded = " ".join(policy.get("excluded", []))
    for phrase in ("100 Mile", "IDFdk", "ICHmw2", "CWH", "SBPSmk"):
        if phrase not in excluded:
            raise SystemExit(f"excluded list is missing {phrase}")

    print(f"policy ok: {len(supported)} supported symmetric cases, invermere not frozen")


if __name__ == "__main__":
    main()
