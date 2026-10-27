"""Compare a run's database against the standalone ``FVSbc``'s own output.

The package's own runs come from the **pinned** source; the standalone binary is built from
**upstream
``main``** (ADR 0008), because the pin's tree-regeneration routines depend on PyFVS's API. So a
difference
between the two is not automatically a defect — it can be source drift. What the comparison proves
is the
other direction: **where the two agree, this project's keyword rendering, tree list and build
reproduce
FVS's own writer**, table by table, for the tables that have no other oracle.

Four of the 31 exposed tables are checked against FVS's own database dump. This is how the rest get
a check.

The binary is not in the repository. Point at it with ``--binary`` or ``FVSBC_STANDALONE``; without
it the
command reports that and exits 2, and the test suite skips.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from fresh_fvsbc.outputs import EXPOSED_TABLES, read_table
from fresh_fvsbc.run import DATABASE_NAME, KEYWORD_FILE_NAME, tree_file_name

__all__ = [
    "ENV_BINARY",
    "Comparison",
    "compare",
    "main",
    "standalone_key",
]

#: The environment variable naming the standalone binary.
ENV_BINARY: str = "FVSBC_STANDALONE"

#: The line that ends a tree-data block, as ``intree.f`` reads it.
TREE_END: str = "-999"

#: The keyword that begins the inline tree records in a standalone keyword file.
TREE_DATA_KEYWORD: str = "TREEDATA"

#: The keyword file name the standalone is given.
STANDALONE_KEY: str = "case.key"


@dataclass(frozen=True)
class Comparison:
    """What happened to one table.

    Attributes
    ----------
    table : str
        The table's name.
    status : str
        ``match``, ``differ``, ``missing`` (absent from the standalone's database) or ``extra``
        (present
        there and not in ours).
    detail : str
        A short explanation, empty for a match.
    """

    table: str
    status: str
    detail: str


def standalone_key(run_key: str, tree_text: str) -> str:
    """Build a keyword file the standalone binary can read from a run's keyword file and tree list.

    The standalone reads the tree records **inline**, between ``TREEDATA`` and the next keyword. A
    run
    directory keeps them in a separate file, because the package drives FVS through PyFVS's step
    API.

    Parameters
    ----------
    run_key : str
        The contents of ``run.key``.
    tree_text : str
        The contents of ``run.tre``, which ends with the ``-999`` terminator.

    Returns
    -------
    str
        A keyword file with the tree records inlined.

    Raises
    ------
    ValueError
        If the keyword file carries no ``TREEDATA`` line, because then there is nowhere to put them.
    """
    lines = run_key.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == TREE_DATA_KEYWORD:
            body = tree_text if tree_text.endswith("\n") else tree_text + "\n"
            return (
                "\n".join(lines[: index + 1]) + "\n" + body + "\n".join(lines[index + 1 :]) + "\n"
            )
    raise ValueError(
        f"the keyword file has no {TREE_DATA_KEYWORD} line to put the tree records after"
    )


def _canonical(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a frame whose row order cannot affect equality.

    Parameters
    ----------
    frame : pandas.DataFrame
        The table.

    Returns
    -------
    pandas.DataFrame
        The same values as strings, sorted by every column, with a fresh index.
    """
    text = frame.astype(str)
    return text.sort_values(by=list(text.columns)).reset_index(drop=True)


def compare(ours: Path, theirs: Path) -> tuple[Comparison, ...]:
    """Compare every exposed table in two run databases.

    Parameters
    ----------
    ours : Path
        This package's database.
    theirs : Path
        The standalone binary's database.

    Returns
    -------
    tuple of Comparison
        One record per table either database holds, ordered by table name.
    """
    mine = {name for name in EXPOSED_TABLES if _has_table(ours, name)}
    other = {name for name in EXPOSED_TABLES if _has_table(theirs, name)}
    results: list[Comparison] = []
    for name in sorted(mine | other):
        if name not in other:
            results.append(Comparison(name, "missing", "the standalone wrote no such table"))
            continue
        if name not in mine:
            results.append(Comparison(name, "extra", "only the standalone wrote it"))
            continue
        left = _canonical(read_table(ours, name))
        right = _canonical(read_table(theirs, name))
        if list(left.columns) != list(right.columns):
            results.append(Comparison(name, "differ", "the column lists differ"))
            continue
        if left.shape != right.shape:
            results.append(
                Comparison(name, "differ", f"{left.shape[0]} rows here, {right.shape[0]} there")
            )
            continue
        if left.equals(right):
            results.append(Comparison(name, "match", ""))
            continue
        differing = int((left != right).any(axis=1).sum())
        results.append(Comparison(name, "differ", f"{differing} row(s) differ"))
    return tuple(results)


def _has_table(database: Path, name: str) -> bool:
    """Say whether a database holds a table.

    Parameters
    ----------
    database : Path
        The database to look in.
    name : str
        The table.

    Returns
    -------
    bool
        ``True`` when the table is there and the database exists.
    """
    if not database.is_file():
        return False
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        row = connection.execute(
            "select count(*) from sqlite_master where type='table' and name = ?", (name,)
        ).fetchone()
        return bool(row and row[0])
    finally:
        connection.close()


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns
    -------
    argparse.ArgumentParser
        The parser for ``oracle_compare.py``.
    """
    parser = argparse.ArgumentParser(
        prog="oracle_compare.py",
        description=(
            "Compare a run's database against the standalone FVSbc's output for the same case."
        ),
    )
    parser.add_argument(
        "--run",
        type=Path,
        required=True,
        metavar="DIR",
        help="a run directory holding run.key, run.tre and the output database",
    )
    parser.add_argument(
        "--binary",
        type=Path,
        default=None,
        metavar="PATH",
        help=f"the standalone FVSbc, default from ${ENV_BINARY}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the comparison.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments to parse. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when every table present in both agrees, ``1`` when any differs, ``2`` when the binary
        or an
        input is missing.
    """
    args = _parser().parse_args(argv)
    binary = args.binary or (Path(os.environ[ENV_BINARY]) if ENV_BINARY in os.environ else None)
    if binary is None or not Path(binary).is_file():
        print(
            f"oracle_compare: no standalone binary; pass --binary or set ${ENV_BINARY}",
            file=sys.stderr,
        )
        return 2
    run = args.run
    key_path = run / KEYWORD_FILE_NAME
    tree_path = tree_file_name(key_path)
    database = run / DATABASE_NAME
    for required in (key_path, tree_path, database):
        if not required.is_file():
            print(f"oracle_compare: {required} is missing", file=sys.stderr)
            return 2

    workdir = Path(tempfile.mkdtemp(prefix="oracle-compare-"))
    try:
        (workdir / STANDALONE_KEY).write_text(
            standalone_key(
                key_path.read_text(encoding="utf-8"),
                tree_path.read_text(encoding="utf-8"),
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [str(binary), f"--keywordfile={STANDALONE_KEY}"],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            print(
                f"oracle_compare: the standalone exited {completed.returncode}\n"
                f"{completed.stdout[-2000:]}\n{completed.stderr[-2000:]}",
                file=sys.stderr,
            )
            return 2
        results = compare(database, workdir / DATABASE_NAME)
        width = max((len(result.table) for result in results), default=10)
        for result in results:
            line = f"  {result.table:<{width}}  {result.status}"
            print(line + (f"  ({result.detail})" if result.detail else ""))
        differing = [result for result in results if result.status != "match"]
        agreed = len(results) - len(differing)
        print(f"\n  {agreed} of {len(results)} tables agree; {len(differing)} do not.")
        return 0 if not differing else 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
