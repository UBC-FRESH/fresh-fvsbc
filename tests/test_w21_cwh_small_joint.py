"""W21 adds the CWH small-tree density response to diameter and mortality."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc import Keyword, run_case
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.treelist import TreeListFields

_PATCH = (
    Path(__file__).resolve().parents[1] / "notes/reference/calibration/w21-cwh-small-joint.patch.gz"
)


def test_w21_patch_carries_both_terms() -> None:
    """The patch changes the diameter increment and the small-tree mortality."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "EXP(-0.45 * (RELDEN*0.01 - 1.66))" in text
    assert "EXP(0.45 * MIN(RELDEN*0.01 - 1.66, 1.8))" in text
    assert "regent.f" in text
    assert "morts.f" in text


def _stand(large_trees_per_plot: float) -> list[TreeListFields]:
    """Return a CWH stand with large trees plus a fixed small-tree component."""
    trees: list[TreeListFields] = []
    for index in range(1, 11):
        trees.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": large_trees_per_plot,
                "tree_history": 0,
                "species": "HW",
                "diam": 30.0 + 2.0 * index,
                "dg_incr": 0.0,
                "live_ht": 25.0 + 0.5 * index,
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
        )
    for index in range(1, 33):
        trees.append(
            {
                "plot_id": 1,
                "tree_num": 100 + index,
                "tree_count": 5.0,
                "tree_history": 0,
                "species": "HW",
                "diam": 2.0 + 0.25 * index,
                "dg_incr": 0.0,
                "live_ht": 5.0 + 0.9 * (2.0 + 0.25 * index),
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
                "tree_age": 30.0,
            }
        )
    return trees


def _small_tree_growth(tmp_path: Path, large_trees_per_plot: float) -> tuple[float, float]:
    """Run five years and return (stand CCF, mean small-tree diameter growth)."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDINFO", ("CAR", "CWHvm1/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("HW", "25")),
        Keyword("INVYEAR", ("2000",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "5")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST"),
        Keyword("PROCESS"),
        Keyword("TREELIST"),
        Keyword("STOP"),
    )
    result = run_case(_stand(large_trees_per_plot), keywords, directory=tmp_path)
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    trees = read_table(result.database, "FVS_TreeList_Metric")
    small = trees[trees.DBH < 10.0].groupby("Year").DBH.mean()
    years = sorted(small.index)
    growth = (small.loc[years[-1]] - small.loc[years[0]]) / (years[-1] - years[0])
    return float(summary.CCF.iloc[0]), float(growth)


@pytest.mark.skipif(
    os.environ.get("FVSBC_W21") != "1",
    reason="needs a build carrying w21-cwh-small-joint; set FVSBC_W21=1 in that job",
)
def test_small_trees_grow_slower_in_a_denser_cwh_stand(tmp_path: Path) -> None:
    """The W21 density term makes small-tree growth fall as CCF rises."""
    low_ccf, low_growth = _small_tree_growth(tmp_path / "low", 2.0)
    high_ccf, high_growth = _small_tree_growth(tmp_path / "high", 30.0)
    assert high_ccf > low_ccf + 50.0
    assert high_growth < 0.85 * low_growth, (
        f"small-tree growth {low_growth:.3f} at CCF {low_ccf:.0f} vs "
        f"{high_growth:.3f} at CCF {high_ccf:.0f}"
    )
