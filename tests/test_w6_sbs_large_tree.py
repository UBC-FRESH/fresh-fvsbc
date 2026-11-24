"""W6 gives SBS large trees a non-zero diameter increment."""

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
    Path(__file__).resolve().parents[1]
    / "notes/reference/calibration/w6-sbs-sbps-large-tree.patch.gz"
)


def test_w6_patch_carries_sbs_and_sbps() -> None:
    """The banked patch adds both site-series tokens to the zonal row."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "SBS/all" in text
    assert "SBPS/all" in text
    assert "SSKONST" in text


def _large_sbs_stand() -> list[TreeListFields]:
    """Return a stand entirely above the small-tree threshold."""
    records: list[TreeListFields] = []
    for index, diam in enumerate(
        (15.0, 18.0, 20.0, 22.0, 25.0, 28.0, 30.0, 32.0, 35.0, 40.0), start=1
    ):
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": 70.0,
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
    os.environ.get("FVSBC_W6") != "1",
    reason="needs a build carrying w6-sbs-sbps-large-tree; set FVSBC_W6=1 in that job",
)
def test_sbs_large_trees_grow(tmp_path: Path) -> None:
    """A stand above 10 cm gains basal area instead of standing still.

    Parameters
    ----------
    tmp_path : Path
        The run directory.
    """
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W6 SBS LARGE TREE",)),
        Keyword("STDINFO", ("CAR", "SBSmw/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("FD", "20")),
        Keyword("INVYEAR", ("1985",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(_large_sbs_stand(), keywords, directory=tmp_path / "sbs")
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    assert float(summary["Tph"].iloc[-1]) > 0.0
    assert float(summary["BA"].iloc[-1]) > float(summary["BA"].iloc[0]) * 1.01
