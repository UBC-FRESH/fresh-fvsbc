"""Run the command with ``python -m fresh_fvsbc``.

The package is not installed in CI or in the docs, so this is the entry point those use. An
installed package gets the same function as the ``fresh-fvsbc`` console script.
"""

from __future__ import annotations

import sys

from fresh_fvsbc.cli import main

if __name__ == "__main__":
    sys.exit(main())
