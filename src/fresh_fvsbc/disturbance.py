"""Load and score observed BC disturbance events against calibration intervals.

The engine can already run fire and removal schedules; this module is the
observed-data side of a future calibration.  It validates the input contract,
checks which events can be matched to the PSP interval table, and scores
post-disturbance BA/TPH predictions when they exist.  No observations ship
with the package: the BC fire/severity and harvested-block data are external.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

EXIT_OK: int = 0
EXIT_BAD_INPUT: int = 2

REQUIRED_COLUMNS: tuple[str, ...] = (
    "SITE_IDENTIFIER",
    "DISTURBANCE_YEAR",
    "DISTURBANCE_TYPE",
    "SEVERITY",
)

DISTURBANCE_TYPES: frozenset[str] = frozenset({"fire", "harvest", "mpb", "windthrow"})

PREDICTION_COLUMNS: tuple[str, ...] = (
    "DISTURBANCE_TYPE",
    "SEVERITY",
    "observed_ba1",
    "predicted_ba1",
    "observed_tph1",
    "predicted_tph1",
)


class DisturbanceError(ValueError):
    """An observed-disturbance table does not match the contract."""


def load_observations(path: str | Path) -> pd.DataFrame:
    """Read and validate an observed-disturbance table.

    Parameters
    ----------
    path : str or Path
        A CSV with :data:`REQUIRED_COLUMNS`.  ``SEVERITY`` is a 0-1 fraction;
        ``DISTURBANCE_TYPE`` is one of :data:`DISTURBANCE_TYPES`.

    Returns
    -------
    pandas.DataFrame
        The table, with year as an integer, severity as a float, and type
        lower-cased.

    Raises
    ------
    DisturbanceError
        If a required column is missing or a value is outside the contract.
    """
    frame = pd.read_csv(path)
    missing = [name for name in REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise DisturbanceError(f"missing columns: {', '.join(missing)}")
    if frame.empty:
        return frame
    frame = frame.copy()
    try:
        frame["DISTURBANCE_YEAR"] = pd.to_numeric(frame["DISTURBANCE_YEAR"], errors="raise").astype(
            int
        )
        frame["SEVERITY"] = pd.to_numeric(frame["SEVERITY"], errors="raise")
    except (TypeError, ValueError) as error:
        raise DisturbanceError(f"non-numeric year or severity: {error}") from error
    if ((frame["SEVERITY"] < 0.0) | (frame["SEVERITY"] > 1.0)).any():
        raise DisturbanceError("severity must be between 0 and 1")
    frame["DISTURBANCE_TYPE"] = frame["DISTURBANCE_TYPE"].astype(str).str.lower()
    unknown = sorted(set(frame["DISTURBANCE_TYPE"]) - DISTURBANCE_TYPES)
    if unknown:
        raise DisturbanceError(f"unknown disturbance type: {', '.join(unknown)}")
    return frame


def coverage(observations: pd.DataFrame, intervals: pd.DataFrame) -> dict[str, object]:
    """Summarise how many observed events match the PSP interval sites.

    Parameters
    ----------
    observations : pandas.DataFrame
        A table returned by :func:`load_observations`.
    intervals : pandas.DataFrame
        The calibration interval table, with ``SITE_IDENTIFIER``.

    Returns
    -------
    dict
        Counts of observations and sites, the matched and unmatched site ids,
        the event counts by type, and the severity range.
    """
    interval_sites = set(intervals["SITE_IDENTIFIER"].astype(str))
    observed_sites = set(observations["SITE_IDENTIFIER"].astype(str))
    matched = observed_sites & interval_sites
    by_type = (
        observations["DISTURBANCE_TYPE"].value_counts().to_dict() if not observations.empty else {}
    )
    return {
        "observations": len(observations),
        "sites": len(observed_sites),
        "matched_sites": len(matched),
        "unmatched_sites": sorted(observed_sites - interval_sites),
        "by_type": {str(key): int(value) for key, value in by_type.items()},
        "severity_min": float(observations["SEVERITY"].min()) if not observations.empty else None,
        "severity_max": float(observations["SEVERITY"].max()) if not observations.empty else None,
    }


def summarise(predictions: pd.DataFrame) -> pd.DataFrame:
    """Return BA/TPH bias and MAE by disturbance type and severity class.

    Parameters
    ----------
    predictions : pandas.DataFrame
        One row per event with :data:`PREDICTION_COLUMNS`.

    Returns
    -------
    pandas.DataFrame
        Columns ``DISTURBANCE_TYPE``, ``SEVERITY``, ``intervals``,
        ``bias_ba``, ``mae_ba``, ``bias_tph``, ``mae_tph``.
    """
    missing = [name for name in PREDICTION_COLUMNS if name not in predictions.columns]
    if missing:
        raise DisturbanceError(f"missing prediction columns: {', '.join(missing)}")
    if predictions.empty:
        return pd.DataFrame(
            columns=[
                "DISTURBANCE_TYPE",
                "SEVERITY",
                "intervals",
                "bias_ba",
                "mae_ba",
                "bias_tph",
                "mae_tph",
            ]
        )
    frame = predictions.copy()
    frame["ba_error"] = frame["predicted_ba1"] - frame["observed_ba1"]
    frame["tph_error"] = frame["predicted_tph1"] - frame["observed_tph1"]
    summary = (
        frame.groupby(["DISTURBANCE_TYPE", "SEVERITY"])
        .agg(
            intervals=("ba_error", "size"),
            bias_ba=("ba_error", "mean"),
            mae_ba=("ba_error", lambda values: float(values.abs().mean())),
            bias_tph=("tph_error", "mean"),
            mae_tph=("tph_error", lambda values: float(values.abs().mean())),
        )
        .reset_index()
    )
    return summary
