#!/usr/bin/env python3
"""Smoke the installed surface end to end: bundles, recruitment, and the dataset writer.

This is the check that answers "does it work" rather than "do the pieces exist": it loads every
shipped bundle, runs one stand with a zone bundle and the recruitment model, and builds a two-stand
dataset with SQLite. It needs the built BC variant.

Command-line usage::

    python scripts/engine_smoke.py
    python scripts/engine_smoke.py --directory /tmp/smoke
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import pandas as pd

from fresh_fvsbc import DEFAULT_BUNDLES, Keyword, load_default_bundle, run_case
from fresh_fvsbc.dataset import build_dataset
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.treelist import TreeListFields

__all__ = ["EXIT_FAILED", "EXIT_OK", "main"]

EXIT_OK: int = 0
EXIT_FAILED: int = 1

TREES = [
    {
        "plot_id": 1,
        "tree_num": index,
        "tree_count": 1.5,
        "tree_history": 0,
        "species": "HW" if index % 2 else "FD",
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


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser."""
    parser = argparse.ArgumentParser(
        prog="engine_smoke",
        description="Exercise the shipped bundles, recruitment, and the dataset writer.",
    )
    parser.add_argument("--directory", type=Path, default=None, metavar="DIR")
    return parser


def _run(keywords: Sequence[Keyword], directory: Path) -> pd.DataFrame:
    records = cast("list[TreeListFields]", TREES)
    result = run_case(records, tuple(keywords), directory=directory)
    return read_table(result.database, "FVS_Summary_Metric").sort_values("Year")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the smoke and return the exit status.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments without the program name. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        ``0`` when every check passes, ``1`` when one fails.
    """
    args = _parser().parse_args(argv)
    if args.directory is not None:
        args.directory.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(dir=args.directory))
    else:
        root = Path(tempfile.mkdtemp(prefix="fresh-fvsbc-smoke-"))
    try:
        for name in DEFAULT_BUNDLES:
            bundle = load_default_bundle(name)
            assert bundle.bundle_id, name
            print(f"bundle {name:20s} {bundle.bundle_id}")

        cwh = load_default_bundle("cwh-v3")
        estab = load_default_bundle("recruitment-bc-v1").ingrowth_keyword(
            bec="CWHvm1/01", years=10, ba=45.0, cycles=2
        )
        assert estab is not None, "recruitment produced no ESTAB block"
        summary = _run(
            (
                Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
                Keyword("STDINFO", ("CAR", "CWHvm1/01", "0", "200", "35", "16")),
                Keyword("SITECODE", ("FD", "20")),
                Keyword("INVYEAR", ("1985",)),
                Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
                Keyword("TIMEINT", ("", "5")),
                Keyword("NUMCYCLE", ("2",)),
                Keyword("RANNSEED", ("1",)),
                *cwh.render(),
                estab,
                Keyword("TREELIST"),
                Keyword("PROCESS"),
                Keyword("STOP"),
            ),
            root / "run",
        )
        assert len(summary) == 3, f"expected three summary rows, got {len(summary)}"
        assert float(summary["Tph"].iloc[-1]) > float(summary["Tph"].iloc[0]), (
            "recruitment did not add trees over the two cycles"
        )
        print(
            f"run    cwh-v3 + recruitment  TPH {summary['Tph'].iloc[0]:.0f} -> "
            f"{summary['Tph'].iloc[-1]:.0f}"
        )

        stands = root / "stands"
        stands.mkdir()
        manifest: dict[str, object] = {
            "dataset_id": "smoke",
            "version": "0.1.0",
            "tables": ["FVS_CutList_Metric"],
            "stands": [],
        }
        records: list[dict[str, object]] = []
        for number in (1, 2):
            stand_id = f"S{number}"
            pd.DataFrame(TREES).to_csv(stands / f"{stand_id}.csv", index=False)
            records.append(
                {
                    "stand_id": stand_id,
                    "bec": "CWHvm1/01",
                    "neighbourhood": "smoke",
                    "trees": f"stands/{stand_id}.csv",
                    "keywords": [
                        {
                            "name": "DATABASE",
                            "lines": ["DSNOut", "FVSOut.db", "Summary", "TREELIDB"],
                        },
                        {"name": "STDINFO", "fields": ["CAR", "CWHvm1/01", "0", "200", "35", "16"]},
                        {"name": "SITECODE", "fields": ["FD", "20"]},
                        {"name": "INVYEAR", "fields": ["1985"]},
                        {"name": "DESIGN", "fields": ["0", "1", "999", "1", "0", "1", "1"]},
                        {"name": "TIMEINT", "fields": ["", "10"]},
                        {"name": "NUMCYCLE", "fields": ["1"]},
                        {"name": "TREELIST"},
                        {"name": "PROCESS"},
                        {"name": "STOP"},
                    ],
                }
            )
        manifest["stands"] = records
        (root / "manifest.json").write_text(__import__("json").dumps(manifest, indent=2))
        written = build_dataset(root / "manifest.json", root / "built")
        connection = sqlite3.connect(written["sqlite"])
        try:
            tables = {
                row[0]
                for row in connection.execute("select name from sqlite_master where type='table'")
            }
        finally:
            connection.close()
        assert {"runs", "stands", "trees", "events", "landscape", "dataset_meta"} <= tables, tables
        print(f"dataset 2 stands  sqlite tables {len(tables)}")
    except Exception as error:
        print(f"SMOKE FAILED: {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_FAILED
    print(f"OK ({root})")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
