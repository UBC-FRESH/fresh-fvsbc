"""W10 gives MH and CDF their own large-tree rows for the species that have pairs."""

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
    Path(__file__).resolve().parents[1] / "notes/reference/calibration/w10-mh-cdf-own-dg.patch.gz"
)


def test_w10_patch_is_zone_rows_ahead_of_the_donor() -> None:
    """Four zone rows precede the CWH rows, and the model count moves with them."""
    text = gzip.decompress(_PATCH.read_bytes()).decode("utf-8")
    assert "PARAMETER (P_ZN = 47)" in text
    assert "! HW MH (fitted from MH pairs)" in text
    assert "! BG MH (fitted from MH pairs)" in text
    assert "! FD CDF (fitted from CDF pairs; OC still coastal)" in text
    assert "! AT CDF (fitted; includes DR)" in text
    # The zone rows are added before the coastal donor rows they replace.
    assert text.index("! HW MH (fitted") < text.index("! HW CWH (fitted")


def _stand(species: str) -> list[TreeListFields]:
    """Return one large-tree stand for the zone comparison."""
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


def _closing_qmd(tmp: Path, bec: str, species: str) -> float:
    """Run the stand for ten years and return its closing quadratic mean diameter."""
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("W10 ZONE TEST",)),
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
    closing = float(summary["QMD"].iloc[-1])
    assert 0.0 < closing < 100.0
    return closing


@pytest.mark.skipif(
    os.environ.get("FVSBC_W10") != "1",
    reason="needs a build carrying w10-mh-cdf-own-dg; set FVSBC_W10=1 in that job",
)
def test_mh_grows_slower_than_the_coastal_donor(tmp_path: Path) -> None:
    """Mountain hemlock's own row is slower than the CWH hemlock donor."""
    mh = _closing_qmd(tmp_path, "MHmm1/01", "HW")
    cwh = _closing_qmd(tmp_path, "CWHvm1/01", "HW")
    assert mh < cwh


@pytest.mark.skipif(
    os.environ.get("FVSBC_W10") != "1",
    reason="needs a build carrying w10-mh-cdf-own-dg; set FVSBC_W10=1 in that job",
)
def test_cdf_grows_faster_than_the_coastal_donor(tmp_path: Path) -> None:
    """Coastal Douglas-fir's own row is faster than the CWH Douglas-fir donor."""
    cdf = _closing_qmd(tmp_path, "CDFmm/01", "FD")
    cwh = _closing_qmd(tmp_path, "CWHvm1/01", "FD")
    assert cdf > cwh
