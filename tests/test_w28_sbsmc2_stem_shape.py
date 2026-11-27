"""W28 adds the SBSmc2 two-sided stem-shape mortality term."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc import Keyword, load_default_bundle, run_case
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.treelist import TreeListFields

_PATCH = (
    Path(__file__).resolve().parents[1]
    / "notes/reference/calibration/w28-sbsmc2-stem-shape.patch.gz"
)


def test_w28_patch_carries_the_two_sided_term() -> None:
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "0.5000" in text
    assert "2.5000" in text
    assert "SBSmc2" in text


def _stand(dbh_low: float, dbh_high: float, count: float) -> list[TreeListFields]:
    return [
        {
            "plot_id": 1,
            "tree_num": index,
            "tree_count": count,
            "tree_history": 0,
            "species": "BL",
            "diam": dbh_low + (dbh_high - dbh_low) * (index - 1) / 9.0,
            "dg_incr": 0.0,
            "live_ht": 5.0 + 0.9 * (dbh_low + (dbh_high - dbh_low) * (index - 1) / 9.0),
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
            "tree_age": 40.0,
        }
        for index in range(1, 11)
    ]


def _retention(tmp_path: Path, dbh_low: float, dbh_high: float, count: float) -> float:
    bundle = load_default_bundle("sbsmc2-v3")
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDINFO", ("CAR", "SBSmc2/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("PL", "18")),
        Keyword("INVYEAR", ("1995",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("3",)),
        Keyword("RANNSEED", ("1",)),
        *bundle.render(),
        Keyword("TREELIST"),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(_stand(dbh_low, dbh_high, count), keywords, directory=tmp_path)
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    return float(summary.Tph.iloc[-1]) / float(summary.Tph.iloc[0])


@pytest.mark.skipif(
    os.environ.get("FVSBC_W28") != "1",
    reason="needs a build carrying w28-sbsmc2-stem-shape; set FVSBC_W28=1 in that job",
)
def test_small_stems_survive_better_than_large_stems(tmp_path: Path) -> None:
    small = _retention(tmp_path / "small", 4.0, 8.0, 100.0)
    large = _retention(tmp_path / "large", 25.0, 40.0, 50.0)
    assert small > 0.9
    assert large < small - 0.02
