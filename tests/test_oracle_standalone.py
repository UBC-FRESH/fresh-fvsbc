"""The oracle, as a test: this package's output against a standalone ``FVSbc``.

The comparison lives in ``scripts/oracle_compare.py`` and is a tool a person runs. This makes it a
check: it builds a handful of runs from the recipes in ``docs/reference/table-recipes.rst``,
compares every exposed table either build writes, and fails on anything the module cannot explain.

Four cases, not one, because the tables need different things to appear: a **removal** for the cut
and after-treatment lists, a **fire** for mortality and consumption, an **infection** through the
damage columns for the four dwarf-mistletoe tables, an ``RDIN`` block for root disease, and a
``PLANT`` line for the regeneration tally. One run cannot produce them all.

It is skipped unless ``FVSBC_STANDALONE`` names the binary, which is how the suite stays runnable
without one — the binary is built from upstream ``main`` (ADR 0008) and is not in the repository.

What this proves is narrow and worth stating: **the two builds agree**, table by table, for these
cases. It does not prove the numbers are right; that is what the official dump's four tables are
for.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

import oracle_compare as oc
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import to_tree_list
from fresh_fvsbc.outputs import STANDALONE_VERIFIED
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields
from nemora_fixtures import synthetic_population

#: Five plots, because ``FVS_Stats_Stand`` is the distribution among sample points and a one-plot
#: stand has none.
STANDS = ("S1", "S2", "S3", "S4", "S5")

#: The trees per stand. Enough that a thinning to BA 2 actually removes something.
TREES = 20


def _database(*options: str) -> Keyword:
    """Return the ``DATABASE`` block that asks for the tables a case is about."""
    return Keyword("DATABASE", lines=("DSNOut", "FVSOut.db", *options))


def _common() -> tuple[Keyword, ...]:
    """Return the keywords every case needs, in the order FVS reads them."""
    return (
        Keyword("STDIDENT", ("Oracle.1",)),
        Keyword("SITECODE", ("FD", "15")),
        Keyword("INVYEAR", ("2020",)),
        Keyword("DESIGN", ("0", "1", "999", "5", "0", "5", "1")),
        Keyword("NUMCYCLE", ("2",)),
    )


def _tail() -> tuple[Keyword, ...]:
    """Return the keywords that end a case."""
    return (Keyword("PROCESS"), Keyword("STOP"))


def _main_case() -> tuple[list[TreeListFields], tuple[Keyword, ...]]:
    """The fire, the removal and the statistics: the largest single case.

    The fire-model block comes **before** ``INVYEAR``, or ``FUELOUT`` and ``POTFIRE`` capture
    the inventory year and switch their own reports off.
    """
    records = to_tree_list(
        synthetic_population(stands=STANDS, trees_per_stand=TREES), species="FD", tree_age=21
    )
    keywords = (
        _database(
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
        *_common()[:1],
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
                Keyword("CANFPROF", ("1",)),
                Keyword("SIMFIRE", ("1", "20", "1", "21", "1", "100", "1")),
            ),
        ),
        *_common()[2:],
        Keyword("STRCLASS"),
        Keyword("STATS"),
        Keyword("TREELIST"),
        Keyword("CUTLIST"),
        Keyword("ATRTLIST"),
        Keyword("THINBBA", ("1", "2")),
        Keyword("COMPUTE", lines=("0", "BigVol = spmcdbh(3,0,0, 20.0, 999.0, 0,999,0)")),
        *_tail(),
    )
    return list(records), keywords


def _mistletoe_case() -> tuple[list[TreeListFields], tuple[Keyword, ...]]:
    """Dwarf mistletoe: the rating enters through the damage columns, code 30 with the severity."""
    records = to_tree_list(
        synthetic_population(stands=STANDS, trees_per_stand=TREES), species="FD", tree_age=21
    )
    infected: list[TreeListFields] = [
        {**record, "damage1": 30, "severity1": 2} for record in records
    ]
    keywords = (
        _database("Summary", "TREELIDB", "ComputDB", "MISRPTS"),
        *_common(),
        Keyword(
            "MISTOE",
            nested=(
                Keyword("MISTPINF", ("0", "3", "0.5")),
                Keyword("MISTPRT", ("1",)),
                Keyword("NEWSPRED", ("1",)),
            ),
        ),
        Keyword("TREELIST"),
        *_tail(),
    )
    return infected, keywords


def _root_disease_case() -> tuple[list[TreeListFields], tuple[Keyword, ...]]:
    """Root disease: ``RDIN`` refuses the whole set at its ``END`` without ``RRINIT``."""
    records = to_tree_list(
        synthetic_population(stands=STANDS, trees_per_stand=TREES), species="FD", tree_age=21
    )
    keywords = (
        _database("Summary", "TREELIDB", "ComputDB", "RDSUM", "RDDETAIL"),
        *_common(),
        Keyword("RDIN", nested=(Keyword("RRINIT"), Keyword("RRDOUT"))),
        Keyword("TREELIST"),
        *_tail(),
    )
    return list(records), keywords


def _regeneration_case() -> tuple[list[TreeListFields], tuple[Keyword, ...]]:
    """Regeneration: the ``PLANT`` line needs stems per acre, or ``esin.f`` refuses the set."""
    records = to_tree_list(
        synthetic_population(stands=STANDS, trees_per_stand=TREES), species="FD", tree_age=21
    )
    keywords = (
        _database("Summary", "TREELIDB", "ComputDB", "REGREPTS"),
        *_common(),
        Keyword("ESTAB", nested=(Keyword("PLANT", ("0", "FD", "3680", "90")),)),
        Keyword("TREELIST"),
        *_tail(),
    )
    return list(records), keywords


def _binary() -> str:
    """Return the standalone binary's path, or skip the test.

    Two things have to be present and neither is in a default install: the built extension, and a
    standalone ``FVSbc`` built from a different source revision. The quality job has neither, and
    this is how the suite stays runnable there.

    Returns
    -------
    str
        The path to the binary.
    """
    if importlib.util.find_spec("pyfvs") is None:
        pytest.skip("the extension is not installed, so there is nothing to compare")
    binary = os.environ.get(oc.ENV_BINARY)
    if not binary:
        pytest.skip(f"{oc.ENV_BINARY} is not set, so there is no standalone to compare against")
    return binary


#: One case per family of tables, because no single run writes them all.
CASES = {
    "main": _main_case,
    "mistletoe": _mistletoe_case,
    "root-disease": _root_disease_case,
    "regeneration": _regeneration_case,
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_this_package_agrees_with_a_standalone_fvsbc(name: str, tmp_path: Path) -> None:
    """Every exposed table either build writes agrees, or the disagreement is accounted for."""
    binary = _binary()
    records, keywords = CASES[name]()
    result = run_case(records, keywords, directory=tmp_path / name)
    results = oc.compare_run(result.directory, Path(binary))

    unexplained = [record for record in results if record.status in {"differ", "stale"}]
    assert not unexplained, "\n".join(
        f"{name}/{record.table}: {record.status} ({record.detail})" for record in unexplained
    )

    # A comparison that silently compared nothing would pass the assertion above.
    compared = [record for record in results if record.status in {"match", "explained"}]
    assert compared, [record.table for record in results]


def test_every_verified_table_is_checked(tmp_path: Path) -> None:
    """The tables the project claims are verified are the tables these cases compare.

    Without this, a table can be added to :data:`STANDALONE_VERIFIED` — and so to the documentation
    and the web badge — with no case that would notice it breaking.
    """
    binary = _binary()
    checked: set[str] = set()
    for name, build in sorted(CASES.items()):
        records, keywords = build()
        result = run_case(records, keywords, directory=tmp_path / f"coverage-{name}")
        checked |= {
            record.table
            for record in oc.compare_run(result.directory, Path(binary))
            if record.status in {"match", "explained"}
        }
    missing = sorted(set(STANDALONE_VERIFIED) - checked)
    assert not missing, f"verified but no case compares them: {missing}"
