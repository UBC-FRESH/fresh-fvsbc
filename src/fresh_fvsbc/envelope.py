"""The empirical basal-area envelope, and the flag it produces.

The envelope is a property of the PSP sample, not a biological maximum. For each
BEC the dataset carries the p99 and the observed maximum basal area. A run is
flagged when its BA is above the p99 or above the maximum; it is never clipped,
because a clipped number hides the disagreement the flag exists to show.

The envelope is built by :mod:`fresh_fvsbc.calibration` and published in
``notes/reference/calibration/bec_envelope.csv``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pandas as pd

__all__ = ["ENVELOPE_FLAGS", "envelope_flags", "load_envelope"]

#: The flag values, from best to worst. ``unknown`` is not a pass: the caller
#: must decide what to do when the BEC is outside the envelope table.
ENVELOPE_FLAGS: tuple[str, ...] = ("ok", "above_p99", "above_max", "unknown")


def load_envelope(path: str | Path) -> dict[str, dict[str, float]]:
    """Load the envelope table into a mapping by BEC.

    Parameters
    ----------
    path : str or Path
        The ``bec_envelope.csv`` file.

    Returns
    -------
    dict
        Each BEC mapped to ``{"ba_p99": ..., "ba_max": ...}``.

    Raises
    ------
    ValueError
        If the file lacks the two required columns.
    """
    frame = pd.read_csv(path)
    missing = {"BEC", "ba_p99", "ba_max"} - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing {', '.join(sorted(missing))}")
    return {
        str(row["BEC"]): {
            "ba_p99": float(row["ba_p99"]),
            "ba_max": float(row["ba_max"]),
        }
        for _, row in frame.iterrows()
    }


def envelope_flags(ba: float, bec: str, envelope: Mapping[str, Mapping[str, float]]) -> str:
    """Return the envelope flag for one basal-area value.

    Parameters
    ----------
    ba : float
        The basal area, in m2/ha.
    bec : str
        The BEC label, such as ``IDFdk3``.
    envelope : Mapping
        The mapping from :func:`load_envelope`.

    Returns
    -------
    str
        ``ok``, ``above_p99``, ``above_max``, or ``unknown``. A BEC outside the
        table is ``unknown`` rather than ``ok``.
    """
    row = envelope.get(bec)
    if row is None:
        return "unknown"
    if ba > row["ba_max"]:
        return "above_max"
    if ba > row["ba_p99"]:
        return "above_p99"
    return "ok"
