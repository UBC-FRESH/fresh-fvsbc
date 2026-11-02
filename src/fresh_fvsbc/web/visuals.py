"""Schematic 2D and 3D stand payloads over a run's own per-tree tables.

The FVS tree tables carry **no x/y coordinates**. This module therefore computes a layout rather
than reading one: each plot (``PtIndex``) gets a square cell, and the trees in it are spaced on a
golden-angle spiral ordered by ``TreeIndex``. The arrangement is a presentation choice, not data.
Every value the browser shows — species, DBH, height, TPH, crown ratio, and whether a tree appears
in the cut list — is read from the run.

The reader is deliberately independent of FastAPI, like :mod:`fresh_fvsbc.web.runs`, so the layout
can be tested without the web extra installed.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Mapping
from typing import Any

import pandas as pd

from fresh_fvsbc.outputs import MissingOutputError, UnknownTableError, read_table
from fresh_fvsbc.web import runs as runstore

__all__ = [
    "CUT_TABLE",
    "MAX_TREES",
    "TREE_TABLE",
    "plot_layout",
    "visuals",
]

#: The per-tree table the 2D map and the 3D scene are built from.
TREE_TABLE: str = "FVS_TreeList_Metric"

#: The table that marks a tree as cut. A run writes it only when something was cut.
CUT_TABLE: str = "FVS_CutList_Metric"

#: The most trees one response carries. The cap is a safety valve for a very large run; a
#: truncated response says so rather than pretending it is the whole stand.
MAX_TREES: int = 8000

#: The golden angle, in radians. A sunflower spiral gives a stable, even scatter without random
#: state, so the same rows always produce the same picture.
_GOLDEN_ANGLE: float = math.pi * (3.0 - math.sqrt(5.0))

#: The smallest plot cell, in metres. A cell grows with the number of trees it holds.
_MIN_CELL_METERS: float = 36.0

#: What the layout is, said the same way in every response.
_LAYOUT_BASIS: str = (
    "Schematic: one cell per PtIndex, a stable spiral per plot ordered by TreeIndex. "
    "FVS writes no x/y coordinates, so this is not a stem map."
)


def _is_missing(value: object) -> bool:
    """Say whether a scalar is null or NaN.

    Parameters
    ----------
    value : object
        The value to test.

    Returns
    -------
    bool
        ``True`` for ``None``, ``NaN`` and pandas' missing markers.
    """
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if value is pd.NA or value is pd.NaT:
        return True
    try:
        return bool(value != value)
    except (TypeError, ValueError):
        return False


def _as_float(value: object) -> float | None:
    """Convert a scalar to a float, or ``None`` when it is missing or not numeric.

    Parameters
    ----------
    value : object
        The value to convert.

    Returns
    -------
    float or None
        The number, or ``None`` for a missing or non-numeric value.
    """
    if _is_missing(value):
        return None
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _as_int(value: object, default: int = 0) -> int:
    """Convert a scalar to an integer, or a default when it is missing.

    Parameters
    ----------
    value : object
        The value to convert.
    default : int, optional
        The value to return when conversion fails.

    Returns
    -------
    int
        The integer, or ``default``.
    """
    number = _as_float(value)
    return default if number is None else int(number)


def _as_text(value: object, default: str = "") -> str:
    """Convert a scalar to stripped text, or a default when it is missing.

    Parameters
    ----------
    value : object
        The value to convert.
    default : str, optional
        The value to return when the field is missing or empty.

    Returns
    -------
    str
        The text, or ``default``.
    """
    if _is_missing(value):
        return default
    text = str(value).strip()
    return text or default


def _record(row: Mapping[Hashable, Any], *, status: str) -> dict[str, Any]:
    """Turn one tree-table row into the record the browser draws.

    Parameters
    ----------
    row : mapping
        One row of ``FVS_TreeList_Metric`` or ``FVS_CutList_Metric``.
    status : str
        ``"live"`` for a tree-list row, ``"cut"`` for a cut-list row.

    Returns
    -------
    dict
        The values the browser needs, before a position is assigned.
    """
    plot = _as_int(row.get("PtIndex"), 1)
    tree_index = _as_int(row.get("TreeIndex"))
    return {
        "tree_id": _as_text(row.get("TreeId"), f"{plot}:{tree_index}"),
        "tree_index": tree_index,
        "plot": plot,
        "species": _as_text(row.get("SpeciesFVS"), "??"),
        "species_plants": _as_text(row.get("SpeciesPLANTS")) or None,
        "dbh_cm": _as_float(row.get("DBH")),
        "height_m": _as_float(row.get("Ht")),
        "tph": _as_float(row.get("TPH")),
        "crown_ratio": _as_float(row.get("PctCr")),
        "crown_width_m": _as_float(row.get("CrWidth")),
        "tree_age": _as_float(row.get("TreeAge")),
        "status": status,
        "x": 0.0,
        "y": 0.0,
    }


def _merge(tree_frame: pd.DataFrame, cut_frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Merge the tree list and the cut list into one record per tree.

    A tree that appears in both tables is one tree that was cut, not two trees. The tree list's
    values are kept because they carry the tree as it stood; the cut list contributes the status.

    Parameters
    ----------
    tree_frame : pandas.DataFrame
        The rows of ``FVS_TreeList_Metric`` for one year.
    cut_frame : pandas.DataFrame
        The rows of ``FVS_CutList_Metric`` for the same year, or an empty frame.

    Returns
    -------
    list of dict
        One record per tree, in tree-list order followed by cut-only trees.
    """
    records: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for row in tree_frame.to_dict(orient="records"):
        record = _record(row, status="live")
        key = record["tree_id"]
        if key not in records:
            order.append(key)
        records[key] = record
    for row in cut_frame.to_dict(orient="records"):
        record = _record(row, status="cut")
        key = record["tree_id"]
        if key in records:
            records[key]["status"] = "cut"
            continue
        order.append(key)
        records[key] = record
    return [records[key] for key in order]


def plot_layout(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[float], float]:
    """Assign schematic positions to tree records, one cell per plot.

    Parameters
    ----------
    records : list of dict
        Tree records carrying ``plot``, ``tree_index`` and ``tree_id``. The function sets ``x``
        and ``y`` on each record in place.

    Returns
    -------
    plots : list of dict
        One record per plot with its centre, cell count and tree count.
    bounds : list of float
        ``[min_x, min_y, max_x, max_y]``, padded by half a cell so the outermost trees are not on
        the edge.
    cell : float
        The plot cell size in metres.
    """
    if not records:
        return [], [0.0, 0.0, 1.0, 1.0], _MIN_CELL_METERS
    plots = sorted({int(record["plot"]) for record in records})
    groups: dict[int, list[dict[str, Any]]] = {plot: [] for plot in plots}
    for record in records:
        groups[int(record["plot"])].append(record)
    largest = max(len(group) for group in groups.values())
    cell = max(_MIN_CELL_METERS, 2.2 * math.sqrt(largest))
    columns = max(1, math.ceil(math.sqrt(len(plots))))
    centers: dict[int, tuple[float, float]] = {}
    for index, plot in enumerate(plots):
        column = index % columns
        row = index // columns
        centers[plot] = (column * cell, row * cell)
    for plot in plots:
        group = groups[plot]
        group.sort(key=lambda record: (record["tree_index"], record["tree_id"]))
        center_x, center_y = centers[plot]
        radius = cell * 0.45
        count = len(group)
        for rank, record in enumerate(group):
            if count == 1:
                x, y = center_x, center_y
            else:
                angle = rank * _GOLDEN_ANGLE
                distance = radius * math.sqrt((rank + 0.5) / count)
                x = center_x + distance * math.cos(angle)
                y = center_y + distance * math.sin(angle)
            record["x"] = round(x, 3)
            record["y"] = round(y, 3)
    plot_records = [
        {
            "id": plot,
            "x": round(centers[plot][0], 3),
            "y": round(centers[plot][1], 3),
            "count": len(groups[plot]),
        }
        for plot in plots
    ]
    pad = cell * 0.5
    bounds = [
        round(min(record["x"] for record in records) - pad, 3),
        round(min(record["y"] for record in records) - pad, 3),
        round(max(record["x"] for record in records) + pad, 3),
        round(max(record["y"] for record in records) + pad, 3),
    ]
    return plot_records, bounds, cell


def _species_counts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Count the trees by FVS species code.

    Parameters
    ----------
    records : list of dict
        The tree records for one year.

    Returns
    -------
    list of dict
        ``code`` and ``count`` records, most frequent first.
    """
    counts: dict[str, int] = {}
    for record in records:
        code = str(record["species"])
        counts[code] = counts.get(code, 0) + 1
    return [
        {"code": code, "count": count}
        for code, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _summary_row(run: runstore.Run, year: int) -> dict[str, Any] | None:
    """Return the summary row for one year, when the run wrote one.

    Parameters
    ----------
    run : fresh_fvsbc.web.runs.Run
        The run to read.
    year : int
        The year to find.

    Returns
    -------
    dict or None
        The row from ``summary.csv``, or ``None`` when the summary is absent or has no such year.
    """
    try:
        rows = runstore.summary(run)
    except runstore.RunError:
        return None
    for row in rows:
        if _as_int(row.get("year")) == year:
            return row
    return None


def _unavailable(reason: str) -> dict[str, Any]:
    """Build the response for a run that has nothing to draw.

    Parameters
    ----------
    reason : str
        Why the run has no visual payload.

    Returns
    -------
    dict
        A payload with ``available`` false and the same keys as a successful one.
    """
    return {
        "available": False,
        "reason": reason,
        "year": None,
        "years": [],
        "layout": {"kind": "schematic", "basis": _LAYOUT_BASIS, "cell_m": _MIN_CELL_METERS},
        "plots": [],
        "species": [],
        "trees": [],
        "cut_trees": [],
        "bounds": [0.0, 0.0, 1.0, 1.0],
        "counts": {"trees": 0, "cut": 0, "plots": 0, "shown": 0, "total": 0},
        "truncated": False,
        "summary": None,
    }


def _year_rows(frame: pd.DataFrame, year: int) -> pd.DataFrame:
    """Return the rows of a frame for one year.

    Parameters
    ----------
    frame : pandas.DataFrame
        A per-tree frame with a numeric ``Year`` column.
    year : int
        The year to keep.

    Returns
    -------
    pandas.DataFrame
        The matching rows.
    """
    numeric = pd.to_numeric(frame["Year"], errors="coerce")
    return frame[numeric == year]


def visuals(run: runstore.Run, year: int | None = None) -> dict[str, Any]:
    """Build the 2D and 3D payload for one run and one year.

    Parameters
    ----------
    run : fresh_fvsbc.web.runs.Run
        The run to read.
    year : int, optional
        The year to draw. The first year in the tree list is used when this is omitted or names
        a year the run did not write.

    Returns
    -------
    dict
        ``available``, ``reason``, ``year``, ``years``, ``layout``, ``plots``, ``species``,
        ``trees``, ``cut_trees``, ``bounds``, ``counts``, ``truncated`` and ``summary``. A run
        without a tree list answers with ``available`` false and a reason, not an exception.

    Raises
    ------
    fresh_fvsbc.web.runs.RunError
        If the run directory has gone away.
    """
    if not run.path.is_dir():
        raise runstore.RunError(f"the run directory {run.path} is no longer there")
    if not run.database.is_file():
        return _unavailable(f"the run {run.id} has no FVSOut.db")
    try:
        tree_frame = read_table(run.database, TREE_TABLE)
    except (MissingOutputError, UnknownTableError) as error:
        return _unavailable(str(error))
    if tree_frame.empty or "Year" not in tree_frame.columns:
        return _unavailable(f"the run {run.id} wrote no rows in {TREE_TABLE}")
    numeric_years = pd.to_numeric(tree_frame["Year"], errors="coerce").dropna()
    years = sorted({int(value) for value in numeric_years})
    if not years:
        return _unavailable(f"the run {run.id} wrote no dated rows in {TREE_TABLE}")
    selected = year if year is not None and int(year) in years else years[0]
    tree_rows = _year_rows(tree_frame, selected)
    try:
        cut_frame = read_table(run.database, CUT_TABLE)
    except (MissingOutputError, UnknownTableError):
        cut_frame = pd.DataFrame()
    cut_rows = _year_rows(cut_frame, selected) if not cut_frame.empty else pd.DataFrame()
    records = _merge(tree_rows, cut_rows)
    total = len(records)
    truncated = total > MAX_TREES
    shown = records[:MAX_TREES]
    plots, bounds, cell = plot_layout(shown)
    live = sum(1 for record in shown if record["status"] == "live")
    cut = sum(1 for record in shown if record["status"] == "cut")
    return {
        "available": True,
        "reason": None,
        "year": selected,
        "years": years,
        "layout": {
            "kind": "schematic",
            "basis": _LAYOUT_BASIS,
            "cell_m": round(cell, 2),
        },
        "plots": plots,
        "species": _species_counts(shown),
        "trees": [record for record in shown if record["status"] == "live"],
        "cut_trees": [record for record in shown if record["status"] == "cut"],
        "bounds": bounds,
        "counts": {
            "trees": live,
            "cut": cut,
            "plots": len(plots),
            "shown": len(shown),
            "total": total,
        },
        "truncated": truncated,
        "summary": _summary_row(run, selected),
    }
