"""The oracle, as a test: this package's output against a standalone ``FVSbc``.

The comparison lives in ``scripts/oracle_compare.py`` and is a tool a person runs. This makes it a
check: it builds one run from a broad keyword set, compares every exposed table either build writes,
and fails on anything the module cannot explain.

It is skipped unless ``FVSBC_STANDALONE`` names the binary, which is how the suite stays runnable
without one — the binary is built from upstream ``main`` (ADR 0008) and is not in the repository.

What this proves is narrow and worth stating: **the two builds agree**, table by table, for one
case. It does not prove the numbers are right; that is what the official dump's four tables are for.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import oracle_compare as oc
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import to_tree_list
from fresh_fvsbc.run import run_case
from nemora_fixtures import synthetic_population


def _keywords() -> tuple[Keyword, ...]:
    """Return a keyword set that asks for as many exposed tables as one run can write.

    The recipes are in ``docs/reference/table-recipes.rst``. Every one of them needs a second
    thing beyond its ``DATABASE`` option, and the two easiest to get wrong are here: the
    fire-model block comes **before** ``INVYEAR``, or ``FUELOUT`` and ``POTFIRE`` switch their own
    reports off,
    and a removal is what makes the cut and after-treatment lists appear.

    Returns
    -------
    tuple of Keyword
        The set, in the order FVS reads it.
    """
    return (
        Keyword(
            "DATABASE",
            lines=(
                "DSNOut",
                "FVSOut.db",
                "Summary",
                "TREELIDB",
                "ComputDB",
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
        ),
        Keyword("STDIDENT", ("Oracle.1",)),
        Keyword("SITECODE", ("FD", "15")),
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
        ),
        Keyword("INVYEAR", ("2020",)),
        # Five plots, because the stand statistics are the distribution among sample points and a
        # one-plot stand has none.
        Keyword("DESIGN", ("0", "1", "999", "5", "0", "5", "1")),
        Keyword("NUMCYCLE", ("2",)),
        Keyword("STRCLASS"),
        Keyword("STATS"),
        Keyword("TREELIST"),
        Keyword("CUTLIST"),
        Keyword("ATRTLIST"),
        Keyword("THINBBA", ("1", "2")),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )


def test_this_package_agrees_with_a_standalone_fvsbc(tmp_path: Path) -> None:
    """Every exposed table either build writes agrees, or the disagreement is accounted for."""
    binary = os.environ.get(oc.ENV_BINARY)
    if not binary:
        pytest.skip(f"{oc.ENV_BINARY} is not set, so there is no standalone to compare against")

    records = to_tree_list(
        synthetic_population(stands=("S1", "S2", "S3", "S4", "S5"), trees_per_stand=20),
        species="FD",
        tree_age=21,
    )
    result = run_case(records, _keywords(), directory=tmp_path / "oracle")
    results = oc.compare_run(result.directory, Path(binary))

    unexplained = [record for record in results if record.status in {"differ", "stale"}]
    assert not unexplained, "\n".join(
        f"{record.table}: {record.status} ({record.detail})" for record in unexplained
    )

    # A comparison that silently compared nothing would pass the assertion above.
    compared = [record for record in results if record.status in {"match", "explained"}]
    assert len(compared) >= 20, [record.table for record in results]
