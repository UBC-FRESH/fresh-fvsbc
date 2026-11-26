"""W17 puts PP on the V3 path with fitted FD and PY rows."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = Path(__file__).resolve().parents[1] / "notes/reference/calibration/w17-pp-v3.patch.gz"


def test_w17_patch_covers_the_five_files() -> None:
    """The condition, the branches, the DG rows, the height blocks, and mortality all name PP."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    for name in ("becset.f", "regent.f", "dgf.f", "htgf.f", "morts.f"):
        assert f"b/canada/bc/{name}" in text
    assert "INDEX(BEC%Zone,'PP')" in text
    assert "'PP/all         '" in text
    assert "PARAMETER (P_ZN = 61)" in text
    assert "PARAMETER (P_MD  = 73)" in text
    assert "! FD PP (fitted)" in text
    assert "! PY PP (fitted)" in text
    assert "! PP FD (fitted" in text
    assert "! PP PY (fitted" in text


def _stand() -> list[TreeListFields]:
    """Return one PP stand in the fitted size range."""
    return [
        {
            "plot_id": 1,
            "tree_num": index,
            "tree_count": 30.0,
            "tree_history": 0,
            "species": "FD" if index % 3 else "PY",
            "diam": 20.0 + index,
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
    os.environ.get("FVSBC_W17") != "1",
    reason="needs a build carrying w17-pp-v3; set FVSBC_W17=1 in that job",
)
def test_pp_runs_on_v3(tmp_path: Path) -> None:
    """A PP stand grows, records the V3 path, and is not rewritten to MSdk."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W17 PP TEST",)),
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
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    assert float(summary["QMD"].iloc[-1]) > float(summary["QMD"].iloc[0])
    assert result.provenance.bec_substitution is None
    assert all(record.path == "V3" for record in result.provenance.support)
