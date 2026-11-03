"""The D6 SBPS small-tree path stays finite.

The pre-fix BC build selected the exponential IDF/ICH small-tree height form for
``SBPS`` because the zone token does not contain ``SBS``.  Its SBS-form
coefficients overflowed, and the summary carried DBHs in the hundreds of
centimetres.  This test grows a small-tree PL stand in ``SBPSmc`` and refuses
that failure mode.  It needs the built extension and skips without it; the CI
extension job runs it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields


def _small_pl_stand() -> list[TreeListFields]:
    """Return a dense PL stand below the 4.5-inch small-tree threshold."""
    records: list[TreeListFields] = []
    for index, diam in enumerate((3.2, 3.8, 4.4, 4.9, 5.3, 5.8, 6.1, 6.5, 6.9, 7.2), start=1):
        records.append(
            {
                "plot_id": 1,
                "tree_num": index,
                "tree_count": 250.0,
                "tree_history": 0,
                "species": "PL",
                "diam": diam,
                "dg_incr": 0.0,
                "live_ht": 1.3 + 1.1 * diam,
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": 2,
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
                "tree_age": 60.0,
            }
        )
    return records


def test_sbps_small_trees_do_not_overflow(tmp_path: Path) -> None:
    """A small-tree SBPS stand stays in physical BA/QMD bounds.

    Parameters
    ----------
    tmp_path : Path
        The run directory.
    """
    pytest.importorskip(
        "pyfvs", reason="the BC extension is not built in this environment; ADR 0004 is the recipe"
    )
    records = _small_pl_stand()
    keywords = (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", ("D6 SBPS SMALL TREE",)),
        Keyword("STDINFO", ("CAR", "SBPSmc/01", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "20")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(records, keywords, directory=tmp_path / "sbpsmc")
    report = (result.directory / "run.out").read_text(encoding="latin-1")
    assert "Infinity" not in report
    summary = read_table(result.database, "FVS_Summary_Metric")
    assert summary["BA"].max() < 200.0
    assert summary["QMD"].max() < 100.0
