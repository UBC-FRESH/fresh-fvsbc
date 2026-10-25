"""The child process that drives one projection.

FVS keeps its state in the process rather than in the working directory: a case run after
another projection produces different numbers, even in a fresh directory (ADR 0010). So a run is
driven in a process of its own, and this module is that process.

It is private. The only supported way to reach it is :func:`fresh_fvsbc.run.run_case`, which
spawns it, reads what it writes, and turns its failure into an exception a caller can catch.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path

from fresh_fvsbc.run import (
    EXTENSION_UNAVAILABLE_CODE,
    SUMMARY_FILE_NAME,
    VARIANTS_FILE_NAME,
    ExtensionUnavailableError,
    _drive_here,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Drive one projection and write what the parent needs.

    Parameters
    ----------
    argv : sequence of str or None, optional
        ``directory``, ``key_name`` and ``variant``. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` when the projection ran, and :data:`fresh_fvsbc.run.EXTENSION_UNAVAILABLE_CODE` when
        PyFVS is not importable or the variant did not load. Any other failure propagates and the
        interpreter exits non-zero with the traceback on standard error.
    """
    arguments = list(sys.argv[1:] if argv is None else argv)
    directory, key_name, variant = Path(arguments[0]), arguments[1], arguments[2]
    try:
        summary, variants = _drive_here(key_name, variant=variant, directory=directory)
    except ExtensionUnavailableError as error:
        print(f"fresh-fvsbc: {error}", file=sys.stderr)
        return EXTENSION_UNAVAILABLE_CODE
    summary.to_csv(directory / SUMMARY_FILE_NAME, index=False)
    (directory / VARIANTS_FILE_NAME).write_text(json.dumps(list(variants)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
