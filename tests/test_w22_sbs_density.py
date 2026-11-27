"""W22 adds the SBS BL stand-density term used to fix the SBSmc2 cell."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc import Keyword, load_default_bundle, run_case
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.treelist import TreeListFields

_PATCH = (
    Path(__file__).resolve().parents[1] / "notes/reference/calibration/w22-sbs-bl-density.patch.gz"
)


def test_w22_patch_sets_the_bl_density_coefficient() -> None:
    """The BL row's CCF coefficient moves from zero to the fitted density term."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "-0.350000" in text
    assert "SBS BL high-density term" in text


def _stand(large_trees_per_plot: float) -> list[TreeListFields]:
    """Return an SBSmc2 stand with large BL plus a fixed 10-20 cm BL component."""
    trees: list[TreeListFields] = []
    for index in range(1, 11):
        trees.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": large_trees_per_plot,
                "tree_history": 0,
                "species": "BL",
                "diam": 28.0 + 2.0 * index,
                "dg_incr": 0.0,
                "live_ht": 22.0 + 0.5 * index,
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
                "tree_age": 70.0,
            }
        )
    for index in range(1, 17):
        trees.append(
            {
                "plot_id": 1,
                "tree_num": 100 + index,
                "tree_count": 20.0,
                "tree_history": 0,
                "species": "BL",
                "diam": 10.5 + 0.6 * index,
                "dg_incr": 0.0,
                "live_ht": 8.0 + 0.5 * (10.5 + 0.6 * index),
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
        )
    return trees


def _mid_tree_growth(tmp_path: Path, large_trees_per_plot: float) -> tuple[float, float]:
    """Run five years and return (stand CCF, mean 10-20 cm BL growth)."""
    bundle = load_default_bundle("sbs-v3")
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDINFO", ("CAR", "SBSmc2/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("PL", "18")),
        Keyword("INVYEAR", ("1995",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "5")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        *bundle.render(),
        Keyword("TREELIST"),
        Keyword("PROCESS"),
        Keyword("TREELIST"),
        Keyword("STOP"),
    )
    result = run_case(_stand(large_trees_per_plot), keywords, directory=tmp_path)
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    trees = read_table(result.database, "FVS_TreeList_Metric")
    mid = trees[(trees.DBH >= 10.0) & (trees.DBH <= 20.0)].groupby("Year").DBH.mean()
    years = sorted(mid.index)
    growth = (mid.loc[years[-1]] - mid.loc[years[0]]) / (years[-1] - years[0])
    return float(summary.CCF.iloc[0]), float(growth)


@pytest.mark.skipif(
    os.environ.get("FVSBC_W22") != "1",
    reason="needs a build carrying w22-sbs-bl-density; set FVSBC_W22=1 in that job",
)
def test_sbs_bl_10_20_grows_slower_in_a_denser_stand(tmp_path: Path) -> None:
    """The W22 BL density term reduces 10-20 cm growth as CCF rises."""
    low_ccf, low_growth = _mid_tree_growth(tmp_path / "low", 2.0)
    high_ccf, high_growth = _mid_tree_growth(tmp_path / "high", 30.0)
    assert high_ccf > low_ccf + 100.0
    assert high_growth < 0.8 * low_growth, (
        f"BL 10-20 growth {low_growth:.3f} at CCF {low_ccf:.0f} vs "
        f"{high_growth:.3f} at CCF {high_ccf:.0f}"
    )
