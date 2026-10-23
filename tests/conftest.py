"""Make ``scripts/`` and the ``fresh-fvsbc`` package importable from the tests.

``scripts/`` holds the repository's own tooling, and ``src/`` holds the package this project
ships. Neither is installed, so the suite puts both on the import path.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]
SCRIPTS: Path = ROOT / "scripts"
SRC: Path = ROOT / "src"

for path in (SCRIPTS, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
