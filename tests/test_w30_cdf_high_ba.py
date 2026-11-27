"""W30 adds the CDF high-BA mortality interaction."""

from __future__ import annotations

import gzip
from pathlib import Path

_PATCH = (
    Path(__file__).resolve().parents[1]
    / "notes/reference/calibration/w30-cdf-high-ba-mort.patch.gz"
)


def test_w30_patch_carries_the_high_ba_term() -> None:
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "0.2500" in text
    assert "90.0" in text
    assert "CDF" in text
