"""W15 puts MS on the V3 path with fitted large-tree and height rows."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = Path(__file__).resolve().parents[1] / "notes/reference/calibration/w15-ms-v3.patch.gz"


def test_w15_patch_covers_the_five_files() -> None:
    """The condition, the branches, the DG rows, the height blocks, and mortality all name MS."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    for name in ("becset.f", "regent.f", "dgf.f", "htgf.f", "morts.f"):
        assert f"b/canada/bc/{name}" in text
    assert "INDEX(BEC%Zone,'MS')" in text
    assert "'MS/all         '" in text
    assert "PARAMETER (P_ZN = 54)" in text
    assert "PARAMETER (P_MD  = 68)" in text
    for species in ("! AT MS", "! BL MS", "! FD MS", "! LW MS", "! PL MS", "! PY MS", "! SE MS"):
        assert species in text
    for label in (
        "! MS BL (fitted",
        "! MS FD (fitted",
        "! MS LW (fitted",
        "! MS PL (fitted",
        "! MS SE (fitted",
    ):
        assert label in text


def _stand() -> list[TreeListFields]:
    """Return one MS stand in the fitted size range."""
    return [
        {
            "plot_id": 1,
            "tree_num": index,
            "tree_count": 30.0,
            "tree_history": 0,
            "species": "PL" if index % 3 else "FD",
            "diam": 18.0 + index,
            "dg_incr": 0.0,
            "live_ht": 12.0 + 0.5 * index,
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
    os.environ.get("FVSBC_W15") != "1",
    reason="needs a build carrying w15-ms-v3; set FVSBC_W15=1 in that job",
)
def test_ms_runs_on_v3(tmp_path: Path) -> None:
    """An MS stand runs, grows, and records the V3 path."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W15 MS TEST",)),
        Keyword("STDINFO", ("KAM", "MSdm1/01", "0", "200", "35", "16")),
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
    result = run_case(_stand(), keywords, directory=tmp_path / "ms")
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    assert float(summary["BA"].iloc[-1]) > 0.0
    assert float(summary["QMD"].iloc[-1]) > float(summary["QMD"].iloc[0])
    assert all(record.path == "V3" for record in result.provenance.support)
