"""W13/W14 make PP resolve as PP and give it the measured caps."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_NOTES = Path(__file__).resolve().parents[1] / "notes/reference/calibration"


def test_w14_patch_maps_the_pp_series() -> None:
    """The missing PP series are listed with the PP habitat, not the default."""
    text = gzip.decompress((_NOTES / "w14-pp-site-series.patch.gz").read_bytes()).decode("utf-8")
    assert "'PPxh2/01'" in text
    assert "'PPxh/01'" in text
    assert "IBEC = 130" in text


def test_w13_patch_sets_the_measured_caps() -> None:
    """PPxh gets 30 and PPxh2 series 1-4 gets 48, the measured p99 values."""
    text = gzip.decompress((_NOTES / "w13-pp-bamax.patch.gz").read_bytes()).decode("utf-8")
    assert 'CASE ("xh")' in text
    assert "BAMAX = 30." in text
    assert "BAMAX = 48." in text


def _stand() -> list[TreeListFields]:
    """Return a small PP stand."""
    return [
        {
            "plot_id": 1,
            "tree_num": index,
            "tree_count": 25.0,
            "tree_history": 0,
            "species": "PL" if index % 4 else "FD",
            "diam": 26.0 + index,
            "dg_incr": 0.0,
            "live_ht": 20.0 + 0.4 * index,
            "trunc_ht": 0.0,
            "htg_incr": 0.0,
            "crown_ratio": 5,
            "damage1": 0,
            "severity1": 0,
            "damage2": 0,
            "severity2": 0,
            "damage3": 0,
            "severity3": 0,
            "tree_val": 0,
            "tree_rx": 0,
            "plot_slope": 0,
            "plot_aspect": 0,
            "plot_habitat": 0,
            "plot_topo_pos": 0,
            "plot_site_prep": 0,
            "tree_age": 80.0,
        }
        for index in range(1, 13)
    ]


@pytest.mark.skipif(
    os.environ.get("FVSBC_W14") != "1",
    reason="needs a build carrying the PP series mapping; set FVSBC_W14=1 in that job",
)
def test_pp_keeps_its_bec(tmp_path: Path) -> None:
    """A PPxh2 run records no substitution and reports the PP cap."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W14 PP TEST",)),
        Keyword("STDINFO", ("KAM", "PPxh2/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("PL", "18")),
        Keyword("INVYEAR", ("1985",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST"),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(_stand(), keywords, directory=tmp_path / "pp")
    assert result.provenance.bec_substitution is None
    report = (tmp_path / "pp" / "run.out").read_text(encoding="latin-1")
    assert "MAXIMUM BASAL AREA FOR PPxh2/01" in report
    assert "48.0" in report
