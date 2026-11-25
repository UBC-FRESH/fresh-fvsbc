"""W11 fits CWH large-tree height growth for six species and keeps the CW donor."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = Path(__file__).resolve().parents[1] / "notes/reference/calibration/w11-cwh-height.patch.gz"


def test_w11_patch_is_six_blocks_ahead_of_the_donor() -> None:
    """Six single-species CWH blocks lead the table, and CW keeps its donor row."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "PARAMETER (P_MD  = 63)" in text
    for label in (
        "! CWH HW (fitted CWH height growth)",
        "! CWH FD (fitted CWH height growth)",
        "! CWH BG (fitted CWH height growth)",
        "! CWH SE (fitted CWH height growth, new model)",
        "! CWH AT (fitted CWH height growth, new model)",
        "! CWH PL (fitted CWH height growth, new model)",
    ):
        assert label in text
    assert "! CWH CW (" not in text
    assert text.index("! CWH HW (fitted") < text.index("! ICH+IDF PW 21m")


def _stand() -> list[TreeListFields]:
    """Return one CWH stand in the size range the height row was fitted on."""
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
                "species": "HW",
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


def _height_growth(tmp: Path, bec: str) -> float:
    """Run a CWH stand for ten years and return its mean height gain in feet."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary", "TREELIDB")),
        Keyword("STDIDENT", ("W11 HEIGHT TEST",)),
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
    result = run_case(_stand(), keywords, directory=tmp / bec.replace("/", "_"))
    trees = read_table(result.database, "FVS_TreeList_Metric")
    means = trees.groupby("Year")["Ht"].mean()
    return float(means.iloc[-1] - means.iloc[0])


@pytest.mark.skipif(
    os.environ.get("FVSBC_W11") != "1",
    reason="needs a build carrying w11-cwh-height; set FVSBC_W11=1 in that job",
)
def test_cwh_hemlock_gains_height(tmp_path: Path) -> None:
    """The fitted CWH hemlock row produces a decade of height growth."""
    growth = _height_growth(tmp_path, "CWHvm1/01")
    assert 0.5 < growth < 3.0
