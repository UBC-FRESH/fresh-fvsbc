#!/usr/bin/env python3
"""Compare the wrapper's zone-path registry with the variant's ``LV2ATV`` list.

The variant decides V3 with one hard-coded list in ``canada/bc/becset.f``. If a zone is added
there and not to :data:`fresh_fvsbc.support.ZONE_PATH` (or the other way round), the support
record claims a path the engine does not run. This check fails on that divergence.

Command-line usage::

    python scripts/check_zone_paths.py --source path/to/fvs/canada/bc/becset.f
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from pathlib import Path

from fresh_fvsbc.support import ZONE_PATH

__all__ = ["EXIT_DIVERGED", "EXIT_OK", "main"]

EXIT_OK: int = 0
EXIT_DIVERGED: int = 1


def _parser() -> argparse.ArgumentParser:
    """Return the command's parser."""
    parser = argparse.ArgumentParser(
        prog="check_zone_paths",
        description="Compare ZONE_PATH with the V3 zone list in becset.f.",
    )
    parser.add_argument("--source", required=True, type=Path, metavar="FILE")
    return parser


def engine_v3_zones(path: Path) -> set[str]:
    """Return the zones the variant's ``LV2ATV`` list names.

    Parameters
    ----------
    path : Path
        ``canada/bc/becset.f``.

    Returns
    -------
    set of str
        The zone tokens in the ``IF`` that clears ``LV2ATV``.
    """
    text = path.read_text(encoding="latin-1")
    at = text.index("LV2ATV = .TRUE.")
    block = text[at : text.index("ENDIF", at)]
    return set(re.findall(r"INDEX\(BEC%Zone,'([A-Z]+)'\)", block))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the check and return the exit status.

    Parameters
    ----------
    argv : sequence of str, optional
        Command-line arguments, without the program name. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    int
        ``0`` when the registry and the source agree, ``1`` when they diverge.
    """
    args = _parser().parse_args(argv)
    engine = engine_v3_zones(args.source)
    declared_v3 = {zone for zone, path in ZONE_PATH.items() if path == "V3"}
    problems: list[str] = []
    for zone in sorted(engine - declared_v3):
        problems.append(f"{zone}: the engine runs V3 and ZONE_PATH does not say so")
    for zone in sorted(declared_v3 - engine):
        problems.append(f"{zone}: ZONE_PATH says V3 and the engine runs V2")
    if problems:
        for problem in problems:
            print(f"DIVERGED: {problem}")
        return EXIT_DIVERGED
    print(f"ok: {len(engine)} V3 zones agree with the engine: {' '.join(sorted(engine))}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
