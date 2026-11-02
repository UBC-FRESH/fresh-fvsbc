#!/usr/bin/env python3
"""Build the W1.6 coverage and power tables from the aggregate calibration tables.

The command applies the pre-registered sample-size rule in
:mod:`fresh_fvsbc.calibration_domains`. It writes one row per BEC variant and one row per BEC zone.

Command-line usage::

    python scripts/build_calibration_domains.py \
      --coverage notes/reference/calibration/bec_coverage.csv \
      --baseline notes/reference/calibration/baseline_summary.csv \
      --out-dir notes/reference/calibration
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from fresh_fvsbc.calibration_domains import DomainError, write_domain_tables

__all__ = ["EXIT_BAD_INPUT", "EXIT_OK", "main"]

#: The tables were written.
EXIT_OK: int = 0

#: The input was wrong before any table was written.
EXIT_BAD_INPUT: int = 2


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser.

    Returns
    -------
    argparse.ArgumentParser
        The parser for the domain build.
    """
    parser = argparse.ArgumentParser(
        prog="build_calibration_domains",
        description="Build the W1.6 domain coverage and power tables.",
    )
    parser.add_argument(
        "--coverage",
        required=True,
        type=Path,
        metavar="CSV",
        help="the aggregate bec_coverage.csv",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        metavar="CSV",
        help="the baseline summary, used for the envelope flags",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        metavar="DIR",
        help="where domain_power.csv and domain_summary.csv are written",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the domain build and report what was written.

    Parameters
    ----------
    argv : sequence of str or None, optional
        The command-line arguments without the program name. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when the tables were written, ``2`` when the input was refused.
    """
    args = _parser().parse_args(argv)
    try:
        tables = write_domain_tables(args.coverage, args.baseline, args.out_dir)
    except (DomainError, OSError, ValueError) as error:
        print(f"build_calibration_domains: {error}", file=sys.stderr)
        return EXIT_BAD_INPUT
    print(f"wrote {tables.power_path}")
    print(f"wrote {tables.summary_path}")
    print(
        f"{tables.variants} variants: {tables.calibration} calibration, "
        f"{tables.validation_only} validation-only, "
        f"{tables.insufficient} insufficient, {tables.upstream} upstream"
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
