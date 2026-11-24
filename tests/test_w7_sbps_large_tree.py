"""W7 gives SBPS large trees a finite, non-zero diameter increment."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = (
    Path(__file__).resolve().parents[1] / "notes/reference/calibration/w7-sbps-large-tree.patch.gz"
)


def test_w7_patch_replaces_the_sbps_rows() -> None:
    """The banked patch enables SBPS and carries a fitted PL intercept."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "SBPS/all" in text
    assert "ZNKONST" in text
    assert "-2.204670" in text


def _large_sbps_stand() -> list[TreeListFields]:
    """Return an SBPS PL stand entirely above the small-tree threshold."""
    records: list[TreeListFields] = []
    for index, diam in enumerate(
        (15.0, 17.0, 19.0, 21.0, 23.0, 25.0, 27.0, 29.0, 31.0, 33.0), start=1
    ):
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": 60.0,
                "tree_history": 0,
                "species": "PL",
                "diam": diam,
                "dg_incr": 0.0,
                "live_ht": 8.0 + 0.5 * diam,
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
    return records


@pytest.mark.skipif(
    os.environ.get("FVSBC_W7") != "1",
    reason="needs a build carrying w7-sbps-large-tree; set FVSBC_W7=1 in that job",
)
def test_sbps_large_trees_grow_without_overflow(tmp_path: Path) -> None:
    """A large SBPS stand gains basal area and stays in physical bounds.

    Parameters
    ----------
    tmp_path : Path
        The run directory.
    """
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDIDENT", ("W7 SBPS LARGE TREE",)),
        Keyword("STDINFO", ("CAR", "SBPSmk/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("FD", "20")),
        Keyword("INVYEAR", ("1985",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("TREELIST"),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(_large_sbps_stand(), keywords, directory=tmp_path / "sbps")
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    assert float(summary["Tph"].iloc[-1]) > 0.0
    assert float(summary["BA"].iloc[-1]) < 200.0
    assert float(summary["QMD"].iloc[-1]) < 100.0
    trees = read_table(result.database, "FVS_TreeList_Metric")
    first = float(trees[trees["Year"] == trees["Year"].min()]["DBH"].mean())
    last = float(trees[trees["Year"] == trees["Year"].max()]["DBH"].mean())
    assert last > first + 0.01
