"""W9 puts MH and CDF on the V3 path with the coastal donor rows."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = Path(__file__).resolve().parents[1] / "notes/reference/calibration/w9-mh-cdf-v3.patch.gz"


def test_w9_patch_carries_mh_and_cdf() -> None:
    """The banked patch names both zones in every table it touches."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "MH/all" in text
    assert "CDF/all" in text
    assert "INDEX(BEC%Zone,'MH')" in text
    assert "INDEX(BEC%Zone,'CDF')" in text


def _stand(species: str) -> list[TreeListFields]:
    """Return a large-tree stand for a zone test."""
    records: list[TreeListFields] = []
    for index, diam in enumerate(
        (20.0, 23.0, 26.0, 29.0, 32.0, 35.0, 38.0, 41.0, 45.0, 50.0), start=1
    ):
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": 70.0,
                "tree_history": 0,
                "species": species,
                "diam": diam,
                "dg_incr": 0.0,
                "live_ht": 12.0 + 0.6 * diam,
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


def _run(tmp: Path, bec: str, species: str) -> list[float]:
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDIDENT", ("W9 ZONE TEST",)),
        Keyword("STDINFO", ("CAR", bec, "0", "200", "35", "16")),
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
    result = run_case(_stand(species), keywords, directory=tmp / bec.replace("/", "_"))
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    trees = read_table(result.database, "FVS_TreeList_Metric")
    first = float(trees[trees["Year"] == trees["Year"].min()]["DBH"].mean())
    last = float(trees[trees["Year"] == trees["Year"].max()]["DBH"].mean())
    assert float(summary["Tph"].iloc[-1]) > 0.0
    assert float(summary["BA"].iloc[-1]) < 300.0
    assert float(summary["QMD"].iloc[-1]) < 100.0
    return [first, last]


@pytest.mark.skipif(
    os.environ.get("FVSBC_W9") != "1",
    reason="needs a build carrying w9-mh-cdf-v3; set FVSBC_W9=1 in that job",
)
@pytest.mark.parametrize(("bec", "species"), [("MHmm1/01", "HW"), ("CDFmm/01", "FD")])
def test_mh_and_cdf_large_trees_grow(tmp_path: Path, bec: str, species: str) -> None:
    """Both zones gain diameter without an overflow.

    Parameters
    ----------
    tmp_path : Path
        The run directory.
    bec : str
        The zone label under test.
    species : str
        The species code under test.
    """
    first, last = _run(tmp_path, bec, species)
    assert last > first + 0.01
