"""W18 refits the SBS BL large-tree growth row instead of masking it."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = Path(__file__).resolve().parents[1] / "notes/reference/calibration/w18-sbs-bl-dg.patch.gz"


def test_w18_patch_refits_the_bl_row() -> None:
    """The patch replaces the BL row's coefficients and drops the crown term."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "11005" in text
    assert "-2.344304" in text
    assert "-0.025885" in text
    assert "3.1925" in text, "the patch shows the old crown coefficient being removed"
    assert "+     >  0.0000,               ! crown" in text


def _stand() -> list[TreeListFields]:
    """Return a dense small-tree BL stand."""
    return [
        {
            "plot_id": 1,
            "tree_num": index,
            "tree_count": 4.0,
            "tree_history": 0,
            "species": "BL",
            "diam": 10.0 + 0.5 * index,
            "dg_incr": 0.0,
            "live_ht": 7.0 + 0.4 * index,
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
            "tree_age": 60.0,
        }
        for index in range(1, 21)
    ]


@pytest.mark.skipif(
    os.environ.get("FVSBC_W18") != "1",
    reason="needs a build carrying w18-sbs-bl-dg; set FVSBC_W18=1 in that job",
)
def test_a_dense_bl_stand_grows_at_the_refit_rate(tmp_path: Path) -> None:
    """Ten years of growth on a 10-20 cm BL stand stays near the measured 0.2 cm/yr."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W18 BL TEST",)),
        Keyword("STDINFO", ("CAR", "SBSmc2/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("PL", "18")),
        Keyword("INVYEAR", ("1995",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST"),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(_stand(), keywords, directory=tmp_path / "bl")
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    qmd0 = float(summary["QMD"].iloc[0])
    qmd1 = float(summary["QMD"].iloc[-1])
    growth = (qmd1 - qmd0) / 10.0
    assert 0.0 < growth < 0.5, f"BL grew {growth:.3f} cm/yr; the refit should keep it near 0.2"
