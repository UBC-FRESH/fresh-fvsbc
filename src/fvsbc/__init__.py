"""A Python wrapper for the BC variant of the Forest Vegetation Simulator.

This package is the public surface that ``fvsbc`` offers a caller. Its contracts are the
reference pages under ``docs/reference/``: the tree-list input, the keyword set, the outputs,
the provenance record, and the ``nemora`` ingestion.

The package is under construction, one bounded move at a time. Every module lands with its
tests in the same change set, and the gates configured in ``pyproject.toml`` cover it.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.0.0"
