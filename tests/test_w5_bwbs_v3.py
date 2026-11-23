"""The W5 BWBS V3 patch and its provenance-only base bundle.

The banked patch is checked for the five tables it must touch, and the bundle is checked against the
package pin. The behavioural test needs a build that carries W5; it is gated on ``FVSBC_W5`` so the
published build is not asked to pass a test for code it does not contain.
"""

from __future__ import annotations

import gzip
import os
from pathlib import Path

import pytest

from fresh_fvsbc.bundle import load_bundle
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_ROOT = Path(__file__).resolve().parents[1]
_PATCH = _ROOT / "notes/reference/calibration/w5-bwbs-v3.patch.gz"
_BUNDLE = _ROOT / "notes/reference/calibration/bwbs-v3-bundle.json"


def test_w5_patch_touches_the_five_tables() -> None:
    """The banked patch is readable and names every table BWBS needs."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    for name in ("becset.f", "regent.f", "dgf.f", "htgf.f", "morts.f"):
        assert f"/{name}" in text
    assert "BWBS/all" in text
    assert "LMRT(1)" in text or "'BWBS/all       ', '               '," in text


def test_w5_bundle_is_provenance_only() -> None:
    """The V3 base bundle carries no growth or mortality multiplier."""
    bundle = load_bundle(_BUNDLE)
    assert bundle.bundle_id == "bwbs-v3-base-2026-11-23"
    assert "BWBS" in bundle.domain.becs
    assert bundle.parameters == ()


def _aspen_stand() -> list[TreeListFields]:
    """Return a young BWBS aspen stand above and below the small-tree threshold."""
    records: list[TreeListFields] = []
    for index, diam in enumerate(
        (8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 18.0), start=1
    ):
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": 200.0,
                "tree_history": 0,
                "species": "AT",
                "diam": diam,
                "dg_incr": 0.0,
                "live_ht": 1.3 + 0.9 * diam,
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
    return records


@pytest.mark.skipif(
    os.environ.get("FVSBC_W5") != "1",
    reason="needs a build carrying w5-bwbs-v3; set FVSBC_W5=1 in that job",
)
def test_bwbs_aspen_survives_and_grows(tmp_path: Path) -> None:
    """A BWBS aspen stand neither dies wholesale nor stands still.

    Before W5 the missing ``LMRT`` entry set ``RIP=99`` and every aspen died; the missing ``DGF``
    entry left large-tree DG at zero. Both failures are visible in this one run.

    Parameters
    ----------
    tmp_path : Path
        The run directory.
    """
    records = _aspen_stand()
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W5 BWBS ASPEN",)),
        Keyword("STDINFO", ("CAR", "BWBSmw/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("SE", "20")),
        Keyword("INVYEAR", ("1985",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(records, keywords, directory=tmp_path / "bwbs")
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    start = float(summary["BA"].iloc[0])
    end = float(summary["BA"].iloc[-1])
    assert float(summary["Tph"].iloc[-1]) > 0.0, "the stand was killed wholesale"
    assert end > start, "large-tree diameter growth was zero"
    assert float(summary["QMD"].iloc[-1]) < 100.0
