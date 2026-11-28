#!/usr/bin/env python3
"""Validate observed BC disturbance events against the PSP interval table.

The harness is ready before the data: point ``--observations`` at a CSV with
the documented columns and it reports coverage; add ``--predictions`` once
engine runs exist and it reports BA/TPH bias and MAE by type and severity.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from fresh_fvsbc.disturbance import (
    EXIT_BAD_INPUT,
    EXIT_OK,
    DisturbanceError,
    coverage,
    load_observations,
    summarise,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_disturbance",
        description="Check and score observed disturbance events.",
    )
    parser.add_argument("--observations", required=True, type=Path, metavar="CSV")
    parser.add_argument(
        "--intervals",
        required=True,
        type=Path,
        metavar="DIR",
        help="calibration directory containing intervals.csv",
    )
    parser.add_argument("--predictions", type=Path, default=None, metavar="CSV")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the coverage check and optional score, and return an exit code.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments without the program name, or ``None`` to read ``sys.argv``.

    Returns
    -------
    int
        :data:`EXIT_OK` on success, or :data:`EXIT_BAD_INPUT` for bad input.
    """
    args = _parser().parse_args(argv)
    try:
        intervals = pd.read_csv(args.intervals / "intervals.csv")
        observations = load_observations(args.observations)
    except (OSError, DisturbanceError) as error:
        print(f"validate_disturbance: {error}")
        return EXIT_BAD_INPUT
    print(json.dumps(coverage(observations, intervals), indent=2, sort_keys=True))
    if args.predictions is None:
        print("validate_disturbance: no predictions supplied; coverage only")
        return EXIT_OK
    try:
        predictions = pd.read_csv(args.predictions)
        summary = summarise(predictions)
    except (OSError, DisturbanceError) as error:
        print(f"validate_disturbance: {error}")
        return EXIT_BAD_INPUT
    print(summary.round(3).to_string(index=False))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
