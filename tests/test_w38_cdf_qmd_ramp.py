"""W38 adds the CDF BA>60, QMD-dependent mortality ramp."""

from __future__ import annotations

import gzip
from pathlib import Path

_PATCH = (
    Path(__file__).resolve().parents[1] / "notes/reference/calibration/w38-cdf-qmd-ramp.patch.gz"
)


def test_w38_patch_carries_the_qmd_ramp() -> None:
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "50.0-QMDCM" in text
    assert "0.5000" in text
    assert "BAX .GT. 60.0" in text
    assert "CDF" in text
