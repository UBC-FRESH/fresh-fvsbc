"""W12 gives SBS a per-subzone maximum basal area instead of a flat 55 m2/ha."""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_PATCH = Path(__file__).resolve().parents[1] / "notes/reference/calibration/w12-sbs-bamax.patch.gz"


def test_w12_patch_carries_the_subzone_caps() -> None:
    """The patch replaces the flat SBS cap with the measured p99 values."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    for marker in (
        'CASE ("mc2")',
        "BAMAX = 68.",
        'CASE ("wk")',
        "BAMAX = 71.",
        'CASE ("dh1")',
        "BAMAX = 75.",
    ):
        assert marker in text
    assert text.count('CASE ("dw1","dw2")') == 1, "the flat dw pair case is gone"


def _stand() -> list[TreeListFields]:
    """Return a 65 m2/ha SBS stand: above the old flat cap and below SBSmc2's p99."""
    records: list[TreeListFields] = []
    for index in range(24):
        diam = 28.0 + 0.5 * index
        records.append(
            {
                "plot_id": 1,
                "tree_num": index + 1,
                "tree_count": 30.0,
                "tree_history": 0,
                "species": "PL" if index % 3 else "FD",
                "diam": diam,
                "dg_incr": 0.0,
                "live_ht": 14.0 + 0.5 * diam,
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


def _summary(tmp: Path) -> list[tuple[float, float]]:
    """Run the stand for ten years and return (BA, TPH) at each end."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W12 CAP TEST",)),
        Keyword("STDINFO", ("CAR", "SBSmc2/01", "0", "200", "35", "16")),
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
    result = run_case(_stand(), keywords, directory=tmp)
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    return [
        (float(summary["BA"].iloc[0]), float(summary["Tph"].iloc[0])),
        (float(summary["BA"].iloc[-1]), float(summary["Tph"].iloc[-1])),
    ]


@pytest.mark.skipif(
    os.environ.get("FVSBC_W12") != "1",
    reason="needs a build carrying w12-sbs-bamax; set FVSBC_W12=1 in that job",
)
def test_sbs_stand_above_the_old_cap_holds_its_basal_area(tmp_path: Path) -> None:
    """At 65 m2/ha an SBSmc2 stand no longer loses basal area to the cap."""
    (start_ba, start_tph), (end_ba, end_tph) = _summary(tmp_path / "run")
    assert start_ba > 55.0
    assert end_ba >= start_ba, "the flat 55 cap would have cut this stand's BA"
    assert 0.0 < end_tph < start_tph
