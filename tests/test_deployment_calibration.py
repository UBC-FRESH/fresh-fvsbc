"""Tests for the deployment calibration helper."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "notes/reference/calibration/deployment_calibration.py"
POLICY = ROOT / "notes/reference/calibration/calibration-policy.json"
BOUNDARY = ROOT / "notes/reference/calibration/boundary-candidate/model-card.json"
QUESNEL = ROOT / "notes/reference/calibration/quesnel-candidate/model-card.json"


def _scored(path: Path, sites: int = 20) -> Path:
    """Write a synthetic scored table with one under- and one overpredicted group."""
    rows = []
    for index in range(1, sites + 1):
        for _ in range(50):
            rows.append(
                {
                    "site": f"s{index:02d}",
                    "group": "FD",
                    "eta": -2.0,
                    "exposure": 1.0,
                    "dead": 1,
                }
            )
            rows.append(
                {
                    "site": f"s{index:02d}",
                    "group": "HW",
                    "eta": 0.0,
                    "exposure": 1.0,
                    "dead": 0,
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(path, index=False)
    return path


def _run(card: Path, scored: Path, output: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    """Run the helper as the deployment CLI."""
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--card",
            str(card),
            "--scored",
            str(scored),
            "--policy",
            str(POLICY),
            "--output",
            str(output),
            *extra,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_symmetric_rule_applies_both_directions(tmp_path: Path) -> None:
    """Boundary uses the symmetric rule and corrects both groups."""
    scored = _scored(tmp_path / "scored.csv")
    output = tmp_path / "offsets.json"
    completed = _run(BOUNDARY, scored, output, "--apply", str(tmp_path / "applied.csv"))
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text())
    assert payload["rule"] == "symmetric"
    assert payload["calibration_sites"] == 20
    assert payload["applied_groups"] == ["FD", "HW"]
    assert payload["groups"]["FD"]["offset"] > 0
    assert payload["groups"]["HW"]["offset"] < 0
    applied = pd.read_csv(tmp_path / "applied.csv")
    assert (applied["calibrated_prediction"] != applied["base_prediction"]).any()
    assert "site" in applied.columns


def test_one_sided_rule_skips_underprediction(tmp_path: Path) -> None:
    """Quesnel uses the one-sided rule and leaves the underpredicted group alone."""
    scored = _scored(tmp_path / "scored.csv")
    output = tmp_path / "offsets.json"
    completed = _run(QUESNEL, scored, output)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output.read_text())
    assert payload["rule"] == "one_sided"
    assert payload["applied_groups"] == ["HW"]
    assert payload["groups"]["FD"]["offset"] == 0.0
    assert payload["groups"]["HW"]["offset"] < 0


def test_the_helper_rejects_too_few_sites(tmp_path: Path) -> None:
    """A deployment calibration needs the policy minimum site count."""
    scored = _scored(tmp_path / "scored.csv", sites=10)
    completed = _run(BOUNDARY, scored, tmp_path / "offsets.json")
    assert completed.returncode != 0
    assert "need at least 20 sites" in completed.stderr


def test_the_helper_requires_a_policy_rule(tmp_path: Path) -> None:
    """An unmapped optional card needs an explicit rule."""
    card = tmp_path / "card.json"
    card.write_text('{"model_id": "unknown-model"}')
    scored = _scored(tmp_path / "scored.csv")
    completed = _run(card, scored, tmp_path / "offsets.json")
    assert completed.returncode != 0
    assert "no policy rule" in completed.stderr
