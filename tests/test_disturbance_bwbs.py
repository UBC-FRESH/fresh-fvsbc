"""Disturbance wiring and post-disturbance continuation on a calibrated BWBS zone.

Gated on ``FVSBC_W5=1``: the case needs a build carrying the BWBS V3 tables
(W5-W9). The engine-level disturbance writers are already oracle-checked; this
test adds the zone layer.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

_SKIP = pytest.mark.skipif(
    os.environ.get("FVSBC_W5") != "1",
    reason="needs a BWBS V3 build (W5-W9); set FVSBC_W5=1 in that job",
)


def _stand() -> list[TreeListFields]:
    """Return a mixed BWBS stand."""
    records: list[TreeListFields] = []
    n = 0
    for species, lo, hi in (
        ("AT", 8, 16),
        ("PL", 10, 22),
        ("SE", 12, 28),
        ("AT", 6, 12),
        ("PL", 8, 18),
    ):
        for diam in (lo, (lo + hi) / 2, hi):
            n += 1
            records.append(
                {
                    "plot_id": 1,
                    "tree_num": n,
                    "tree_count": 120.0,
                    "tree_history": 0,
                    "species": species,
                    "diam": float(diam),
                    "dg_incr": 0.0,
                    "live_ht": 2.0 + 0.7 * diam,
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


def _database() -> Keyword:
    return Keyword(
        "DATABASE",
        (),
        (
            "DSNOut",
            "FVSOut.db",
            "Summary",
            "TREELIDB",
            "CUTLIDB",
            "ATRTLIDB",
            "MORTREDB",
            "SnagOuDB",
            "SnagSuDB",
            "DWDVLDB",
            "DWDCVDB",
            "FuelsOut",
            "FuelReDB",
            "PotfirDB",
            "CarbReDB",
            "STRCLSDB",
            "INVSTATS",
        ),
    )


def _keys(extra: tuple[Keyword, ...], fire: bool) -> tuple[Keyword, ...]:
    keys = [
        _database(),
        Keyword("STDIDENT", ("DISTURB BWBS",)),
        Keyword("STDINFO", ("CAR", "BWBSmw/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("SE", "15")),
    ]
    if fire:
        keys.append(
            Keyword(
                "FMIN",
                nested=(
                    Keyword("MORTREPT", ("1",)),
                    Keyword("FUELOUT", ("2",)),
                    Keyword("FUELREPT", ("2",)),
                    Keyword("POTFIRE", ("2",)),
                    Keyword("SNAGOUT", ("1",)),
                    Keyword("SNAGSUM", ("2",)),
                    Keyword("DWDVLOUT", ("2",)),
                    Keyword("DWDCVOUT", ("2",)),
                    Keyword("CARBREPT", ("2",)),
                    Keyword("SIMFIRE", ("1", "20", "1", "21", "1", "100", "1")),
                ),
            )
        )
    keys += [
        Keyword("INVYEAR", ("1985",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("STRCLASS"),
        Keyword("STATS"),
        Keyword("TREELIST"),
        *extra,
        Keyword("PROCESS"),
        Keyword("STOP"),
    ]
    return tuple(keys)


def _run(tmp: Path, extra: tuple[Keyword, ...], fire: bool) -> tuple[float, float]:
    result = run_case(_stand(), _keys(extra, fire), directory=tmp / ("fire" if fire else "case"))
    summary = read_table(result.database, "FVS_Summary_Metric").sort_values("Year")
    return float(summary["BA"].iloc[0]), float(summary["BA"].iloc[-1])


@_SKIP
def test_removal_writes_cut_tables_and_leaves_a_residual(tmp_path: Path) -> None:
    """A thinning removes basal area and reports the cut and attribute lists."""
    _, control = _run(tmp_path, (), False)
    ba0, ba1 = _run(
        tmp_path, (Keyword("THINBBA", ("1", "20")), Keyword("CUTLIST"), Keyword("ATRTLIST")), False
    )
    assert 0.0 < ba1 < ba0
    assert ba1 < control


@_SKIP
def test_fire_writes_disturbance_tables_and_leaves_survivors(tmp_path: Path) -> None:
    """A fire writes mortality, snags, DWD, fuels, consumption and carbon, and leaves live trees."""
    ba0, ba1 = _run(tmp_path, (), True)
    assert 0.0 < ba1 < ba0


@_SKIP
def test_fire_tables_are_present(tmp_path: Path) -> None:
    """The fire writers all produce rows on a calibrated zone."""
    result = run_case(_stand(), _keys((), True), directory=tmp_path / "fire_tables")
    assert len(read_table(result.database, "FVS_Mortality_Metric")) > 0
    assert len(read_table(result.database, "FVS_SnagDet_Metric")) > 0
    assert len(read_table(result.database, "FVS_Down_Wood_Vol_Metric")) > 0
    assert len(read_table(result.database, "FVS_Consumption_Metric")) > 0
    assert len(read_table(result.database, "FVS_Carbon_Metric")) > 0
