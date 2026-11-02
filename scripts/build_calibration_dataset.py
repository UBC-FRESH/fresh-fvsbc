#!/usr/bin/env python3
"""Build the provincial calibration dataset from the FAIB PSP archive.

The command is a thin shell over :func:`fresh_fvsbc.calibration.build_dataset`.
It takes the directory that holds the four FAIB files and an output directory.
The tree-level tables stay in the output directory; the aggregate tables are the
ones that can be committed.

Command-line usage::

    python scripts/build_calibration_dataset.py --psp-dir PATH --out-dir PATH
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from fresh_fvsbc.calibration import CalibrationDataError, build_dataset

__all__ = ["EXIT_BAD_INPUT", "EXIT_OK", "main"]

#: The build completed and wrote its tables.
EXIT_OK: int = 0

#: The input was wrong before any table was written.
EXIT_BAD_INPUT: int = 2


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser."""
    parser = argparse.ArgumentParser(
        prog="build_calibration_dataset",
        description="Build the BC calibration dataset from the FAIB PSP archive.",
    )
    parser.add_argument(
        "--psp-dir",
        required=True,
        type=Path,
        metavar="DIR",
        help="the directory holding the four FAIB PSP CSV files",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        metavar="DIR",
        help="where the tables and manifest are written",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the build and report what was written.

    Parameters
    ----------
    argv : Sequence of str, optional
        The command-line arguments, without the program name. Defaults to
        ``sys.argv[1:]``.

    Returns
    -------
    int
        ``0`` when the build completed, ``2`` when the input was refused.
    """
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        dataset = build_dataset(args.psp_dir, args.out_dir)
    except CalibrationDataError as error:
        print(f"build_calibration_dataset: {error}", file=sys.stderr)
        return EXIT_BAD_INPUT
    print(f"wrote {dataset.directory}")
    for name, count in dataset.manifest["rows"].items():
        print(f"{name}: {count}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
