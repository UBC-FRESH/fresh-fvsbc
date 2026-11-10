"""Tests for raw inventory scoring with a frozen candidate card."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "notes/reference/calibration/score_inventory.py"
BOUNDARY = ROOT / "notes/reference/calibration/boundary-candidate/model-card.json"
QUESNEL = ROOT / "notes/reference/calibration/quesnel-candidate/model-card.json"


def _inventory(path: Path, *, species: bool = False) -> Path:
    """Write a small synthetic feature table."""
    rows = [
        {
            "site": "s1",
            "plot": 1,
            "group": "FD",
            "species": "FD",
            "dbh": 20.0,
            "ba0": 20.0,
            "tph0": 500.0,
            "height": 18.0,
            "damage": 0,
            "growth": 0.1,
            "crown": 2.0,
            "si": 18.0,
            "zone": "ICHmk",
        },
        {
            "site": "s1",
            "plot": 1,
            "group": "FD",
            "species": "FD",
            "dbh": 10.0,
            "ba0": 20.0,
            "tph0": 500.0,
            "height": 9.0,
            "damage": 1,
            "growth": 0.0,
            "crown": None,
            "si": None,
            "zone": "ICHmk",
        },
        {
            "site": "s2",
            "plot": 1,
            "group": "HW",
            "species": "AC",
            "dbh": 15.0,
            "ba0": 15.0,
            "tph0": 400.0,
            "height": 14.0,
            "damage": 0,
            "growth": 0.2,
            "crown": 3.0,
            "si": 20.0,
            "zone": "IDFdm",
        },
    ]
    frame = pd.DataFrame(rows)
    if species:
        frame = frame.drop(columns=["group"])
    frame.to_csv(path, index=False)
    return path


def _run(card: Path, source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    """Run the raw scorer."""
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--card",
            str(card),
            "--input",
            str(source),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_scorer_writes_finite_eta(tmp_path: Path) -> None:
    """A card with preprocessing metadata scores raw rows."""
    source = _inventory(tmp_path / "inventory.csv")
    output = tmp_path / "scored.csv"
    completed = _run(BOUNDARY, source, output)
    assert completed.returncode == 0, completed.stderr
    scored = pd.read_csv(output)
    assert list(scored.columns) == ["site", "plot", "group", "eta"]
    assert len(scored) == 3
    assert scored["eta"].notna().all()
    assert set(scored["group"]) == {"FD", "HW"}


def test_the_scorer_maps_species_codes(tmp_path: Path) -> None:
    """A species column is mapped through the card's species groups."""
    source = _inventory(tmp_path / "inventory.csv", species=True)
    output = tmp_path / "scored.csv"
    completed = _run(BOUNDARY, source, output)
    assert completed.returncode == 0, completed.stderr
    scored = pd.read_csv(output)
    assert set(scored["group"]) == {"FD", "HW"}


def test_the_scorer_requires_preprocessing_metadata(tmp_path: Path) -> None:
    """An older card without medians fails instead of guessing."""
    source = _inventory(tmp_path / "inventory.csv")
    completed = _run(QUESNEL, source, tmp_path / "scored.csv")
    assert completed.returncode != 0
    assert "no preprocessing" in completed.stderr
