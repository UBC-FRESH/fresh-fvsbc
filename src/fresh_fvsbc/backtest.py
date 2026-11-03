"""The uncalibrated FVS-BC baseline backtest.

An interval is two consecutive PSP measurements of one plot. The baseline grows
the first measurement's tree list through FVS-BC, with no cut and no calibration,
and compares the result with the second measurement. The comparison is the
reference the calibration is judged against; it is not a calibration.

The sample is stratified by BEC, because a province-wide mean would hide the
variants where the model fails. The tree list is built from the raw FAIB tree
rows: ``PHF_TREE`` is the per-hectare expansion factor, and a tree whose species
does not resolve to one of BC's 15 is skipped and counted rather than mapped to
a species it is not.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from fresh_fvsbc.bec import BecCode, BecCodeError
from fresh_fvsbc.calibration import SPECIES_GROUPS
from fresh_fvsbc.envelope import envelope_flags
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import (
    DONOR_SPECIES,
    SpeciesError,
    TreeListFields,
    resolve_species,
)

__all__ = [
    "CROWN_BY_CLASS",
    "SPECIES_ALIASES",
    "classes_for",
    "compare_rows",
    "keywords_for",
    "psp_tree_records",
    "run_backtest",
    "select_intervals",
    "summarise",
    "summary_for_year",
]

#: A crown-class letter in the FAIB tree table mapped to FVS's 1-to-9 class.
CROWN_BY_CLASS: dict[str, int] = {"D": 8, "C": 6, "I": 4, "S": 2}

#: PSP species spellings that are aliases of one of BC's 15. A code outside
#: this map and outside the 15 is skipped rather than forced into a group. The
#: donor aliases are the same layer the tree-list writer uses, so a baseline
#: and a run of the same stand resolve ``Ba``, ``Hm``, ``Yc``, ``Dr``, and
#: ``Mb`` the same way.
SPECIES_ALIASES: dict[str, str] = {
    "SX": "SE",
    "SW": "SE",
    "W": "OH",
    **DONOR_SPECIES,
}


def select_intervals(intervals: pd.DataFrame, per_bec: int = 1) -> pd.DataFrame:
    """Select a deterministic, BEC-stratified sample of intervals.

    Parameters
    ----------
    intervals : pandas.DataFrame
        The interval table from the calibration dataset. It needs ``BEC``,
        ``TSA_DESC``, ``SITE_IDENTIFIER``, ``PLOT``, and ``year0``.
    per_bec : int, optional
        The number of intervals to take from each BEC, spread across TSAs.
        Defaults to one.

    Returns
    -------
    pandas.DataFrame
        The sample, sorted by BEC and TSA.
    """
    if per_bec < 1:
        raise ValueError("per_bec must be at least one")
    ordered = intervals.sort_values(
        ["BEC", "TSA_DESC", "SITE_IDENTIFIER", "PLOT", "year0"], kind="stable"
    )
    return ordered.groupby("BEC", sort=True).head(per_bec).reset_index(drop=True)


def _number(value: object) -> float:
    """Return a value as a float, refusing a non-numeric one."""
    try:
        return float(str(value))
    except (TypeError, ValueError) as error:
        raise ValueError(f"{value!r} is not numeric") from error


def _integer(value: object) -> int:
    """Return a value as an integer through :func:`_number`."""
    return int(_number(value))


def _dbh_class(dbh: float) -> str:
    """Return the DBH class of the median tree."""
    if dbh < 10:
        return "<10"
    if dbh < 25:
        return "10-25"
    if dbh < 40:
        return "25-40"
    return "40+"


def _ba_class(ba: float) -> str:
    """Return the stand BA class."""
    if ba < 20:
        return "<20"
    if ba < 30:
        return "20-30"
    if ba < 40:
        return "30-40"
    if ba < 50:
        return "40-50"
    return "50+"


def classes_for(records: list[TreeListFields], ba0: float) -> dict[str, str]:
    """Return the dominant species group, median DBH class, and BA class.

    Parameters
    ----------
    records : list of TreeListFields
        The start tree list.
    ba0 : float
        The observed initial basal area, in m2/ha.

    Returns
    -------
    dict
        ``species_group``, ``dbh_class``, and ``ba_class``.
    """
    weights: dict[str, float] = {}
    dbhs: list[float] = []
    for record in records:
        group = SPECIES_GROUPS.get(str(record["species"]), "UNKNOWN")
        weights[group] = weights.get(group, 0.0) + float(record["tree_count"])
        dbhs.append(float(record["diam"]))
    dominant = max(weights, key=lambda key: weights[key]) if weights else "UNKNOWN"
    median_dbh = sorted(dbhs)[len(dbhs) // 2] if dbhs else 0.0
    return {
        "species_group": dominant,
        "dbh_class": _dbh_class(median_dbh),
        "ba_class": _ba_class(ba0),
    }


def _region(tsa: object) -> str:
    """Return a BC region token from the TSA name, defaulting to ``CAR``."""
    name = str(tsa)
    if "Kamloops" in name or "Merritt" in name:
        return "KAM"
    if "Nelson" in name:
        return "NEL"
    return "CAR"


def psp_tree_records(
    trees: pd.DataFrame,
    interval: Mapping[str, object],
    *,
    tree_age: float = 60.0,
) -> tuple[list[TreeListFields], int]:
    """Build one interval's start tree list from the raw FAIB rows.

    Parameters
    ----------
    trees : pandas.DataFrame
        The raw tree rows, with ``SITE_IDENTIFIER``, ``CLSTR_ID``,
        ``VISIT_NUMBER``, ``PLOT``, ``TREE_NO``, ``SPECIES``, ``DBH``,
        ``HEIGHT``, ``CR_CL``, ``LV_D``, and ``PHF_TREE``.
    interval : Mapping
        One row from the interval table, with ``SITE_IDENTIFIER``,
        ``CLSTR_ID``, ``PLOT``, and ``visit0``.
    tree_age : float, optional
        The age at breast height to write. The PSP interval does not carry a
        single age; the default is a stated placeholder.

    Returns
    -------
    tuple of (list of TreeListFields, int)
        The records and the number of trees skipped because their species did
        not resolve to one of BC's 15.
    """
    mask = (
        (trees["SITE_IDENTIFIER"] == interval["SITE_IDENTIFIER"])
        & (trees["CLSTR_ID"] == interval["CLSTR_ID"])
        & (trees["VISIT_NUMBER"] == interval["visit0"])
        & (trees["PLOT"] == interval["PLOT"])
        & (trees["LV_D"] == "L")
        & (trees["PHF_TREE"] > 0)
    )
    start = trees[mask]
    records: list[TreeListFields] = []
    skipped = 0
    for tree_number, row in enumerate(start.itertuples(index=False), start=1):
        code = SPECIES_ALIASES.get(str(row.SPECIES).upper(), str(row.SPECIES).upper())
        try:
            species = resolve_species(code)
        except SpeciesError:
            skipped += 1
            continue
        dbh = _number(row.DBH)
        height = _number(row.HEIGHT)
        if not math.isfinite(height) or height <= 1.3:
            height = 1.3 + 0.5 * dbh
        records.append(
            {
                "plot_id": _integer(row.PLOT),
                "tree_num": tree_number,
                "tree_count": _number(row.PHF_TREE),
                "tree_history": 0,
                "species": species,
                "diam": dbh,
                "dg_incr": 0.0,
                "live_ht": height,
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": CROWN_BY_CLASS.get(str(row.CR_CL).upper(), 5),
                "damage1": 0,
                "severity1": 0,
                "damage2": 0,
                "severity2": 0,
                "damage3": 0,
                "severity3": 0,
                "tree_val": 0,
                "tree_rx": 0,
                "plot_slope": 0,
                "plot_aspect": 0,
                "plot_habitat": 0,
                "plot_topo_pos": 0,
                "plot_site_prep": 0,
                "tree_age": tree_age,
            }
        )
    return records, skipped


def keywords_for(interval: Mapping[str, object]) -> tuple[Keyword, ...]:
    """Build the uncalibrated keyword set for one interval.

    Parameters
    ----------
    interval : Mapping
        One row from the interval table.

    Returns
    -------
    tuple of Keyword
        A ``DATABASE`` request for the metric summary, the stand setup, one
        growth cycle of the interval's length, and the terminator.
    """
    bec = str(interval["BEC"])
    region = _region(interval["TSA_DESC"])
    return (
        Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")),
        Keyword("STDIDENT", (f"BASELINE {interval['interval_id']}",)),
        Keyword("STDINFO", (region, f"{bec}/01", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "20")),
        Keyword("INVYEAR", (str(_integer(interval["year0"])),)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", str(_integer(interval["years"])))),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )


def summary_for_year(database: str | Path, year: int) -> dict[str, float]:
    """Return the metric summary row for a year.

    Parameters
    ----------
    database : str or Path
        The run's SQLite database.
    year : int
        The year to read. The last row is used when the year is absent.

    Returns
    -------
    dict
        ``ba``, ``tph``, ``qmd``, ``top_height``, and ``volume``. ``volume`` is
        the metric merchantable volume (``MCuM``).
    """
    frame = read_table(database, "FVS_Summary_Metric")
    match = frame[frame["Year"] == year]
    row = match.iloc[-1] if not match.empty else frame.iloc[-1]
    return {
        "ba": float(row["BA"]),
        "tph": float(row["Tph"]),
        "qmd": float(row["QMD"]),
        "top_height": float(row["TopHt"]),
        "volume": float(row["MCuM"]),
    }


def compare_rows(
    interval: Mapping[str, object],
    observed_next: Mapping[str, float],
    predicted_start: Mapping[str, float],
    predicted_end: Mapping[str, float],
    envelope: Mapping[str, Mapping[str, float]],
) -> dict[str, object]:
    """Build one comparison row from the observed and predicted summaries.

    Parameters
    ----------
    interval : Mapping
        One interval row, with its BEC, TSA, BA0, TPH0, and years.
    observed_next : Mapping
        The second measurement: ``ba``, ``tph``, ``qmd``, ``top_height``, and
        ``volume``.
    predicted_start : Mapping
        The FVS metric summary at the start year.
    predicted_end : Mapping
        The FVS metric summary at the end year.
    envelope : Mapping
        The envelope mapping, from :func:`fresh_fvsbc.envelope.load_envelope`.

    Returns
    -------
    dict
        The observed, predicted, bias, and flag fields for one interval.
    """
    bec = str(interval["BEC"])
    observed_ba = _number(interval["ba0"])
    observed_next_ba = _number(observed_next["ba"])
    observed_next_tph = _number(observed_next["tph"])
    years = _number(interval["years"])
    observed_net_ba = (observed_next_ba - observed_ba) / years
    predicted_net_ba = (predicted_end["ba"] - predicted_start["ba"]) / years
    observed_net_tph = (observed_next_tph - _number(interval["tph0"])) / years
    predicted_net_tph = (predicted_end["tph"] - predicted_start["tph"]) / years
    return {
        "interval_id": interval["interval_id"],
        "BEC": bec,
        "TSA": interval["TSA_DESC"],
        "species_group": interval.get("species_group", ""),
        "dbh_class": interval.get("dbh_class", ""),
        "ba_class": interval.get("ba_class", ""),
        "years": _number(interval["years"]),
        "observed_ba0": observed_ba,
        "predicted_ba0": predicted_start["ba"],
        "observed_ba1": observed_next_ba,
        "predicted_ba1": predicted_end["ba"],
        "bias_ba": predicted_end["ba"] - observed_next_ba,
        "observed_net_ba_rate": observed_net_ba,
        "predicted_net_ba_rate": predicted_net_ba,
        "bias_net_ba_rate": predicted_net_ba - observed_net_ba,
        "observed_net_tph_rate": observed_net_tph,
        "predicted_net_tph_rate": predicted_net_tph,
        "bias_net_tph_rate": predicted_net_tph - observed_net_tph,
        "observed_tph1": observed_next_tph,
        "predicted_tph1": predicted_end["tph"],
        "bias_tph": predicted_end["tph"] - observed_next_tph,
        "observed_qmd1": _number(observed_next["qmd"]),
        "predicted_qmd1": predicted_end["qmd"],
        "bias_qmd": predicted_end["qmd"] - _number(observed_next["qmd"]),
        "observed_top_height1": _number(observed_next["top_height"]),
        "predicted_top_height1": predicted_end["top_height"],
        "bias_top_height": predicted_end["top_height"] - _number(observed_next["top_height"]),
        "observed_volume1": _number(observed_next["volume"]),
        "predicted_volume1": predicted_end["volume"],
        "bias_volume": predicted_end["volume"] - _number(observed_next["volume"]),
        "flag_observed": envelope_flags(observed_next_ba, bec, envelope),
        "flag_predicted": envelope_flags(predicted_end["ba"], bec, envelope),
    }


def summarise(rows: pd.DataFrame, by: tuple[str, ...] = ("BEC",)) -> pd.DataFrame:
    """Aggregate the comparison rows by BEC.

    Parameters
    ----------
    rows : pandas.DataFrame
        The rows from :func:`compare_rows`.
    by : tuple of str, optional
        The columns to group by. Defaults to ``("BEC",)``.

    Returns
    -------
    pandas.DataFrame
        Count, mean bias, and mean absolute error for BA, TPH, QMD, top height,
        and volume, by BEC.
    """
    if rows.empty:
        return rows.copy()
    grouped = rows.groupby(list(by), sort=True)
    summary = grouped.agg(
        intervals=("interval_id", "size"),
        bias_ba=("bias_ba", "mean"),
        mae_ba=("bias_ba", lambda values: float(values.abs().mean())),
        bias_tph=("bias_tph", "mean"),
        mae_tph=("bias_tph", lambda values: float(values.abs().mean())),
        bias_net_ba_rate=("bias_net_ba_rate", "mean"),
        mae_net_ba_rate=("bias_net_ba_rate", lambda values: float(values.abs().mean())),
        bias_net_tph_rate=("bias_net_tph_rate", "mean"),
        mae_net_tph_rate=("bias_net_tph_rate", lambda values: float(values.abs().mean())),
        bias_qmd=("bias_qmd", "mean"),
        mae_qmd=("bias_qmd", lambda values: float(values.abs().mean())),
        bias_top_height=("bias_top_height", "mean"),
        mae_top_height=("bias_top_height", lambda values: float(values.abs().mean())),
        bias_volume=("bias_volume", "mean"),
        mae_volume=("bias_volume", lambda values: float(values.abs().mean())),
        above_p99=("flag_predicted", lambda values: int((values == "above_p99").sum())),
        above_max=("flag_predicted", lambda values: int((values == "above_max").sum())),
    )
    return summary.reset_index()


def run_backtest(
    intervals: pd.DataFrame,
    trees: pd.DataFrame,
    visits: pd.DataFrame,
    envelope: Mapping[str, Mapping[str, float]],
    directory: str | Path,
    *,
    per_bec: int = 1,
    tree_age: float = 60.0,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the baseline sample and return the rows, the summary, and the skips.

    Parameters
    ----------
    intervals : pandas.DataFrame
        The interval table.
    trees : pandas.DataFrame
        The raw tree rows for the sampled intervals.
    visits : pandas.DataFrame
        The visit table, used for the second measurement's QMD, top height, and
        volume.
    envelope : Mapping
        The envelope from :func:`fresh_fvsbc.envelope.load_envelope`.
    directory : str or Path
        Where each run writes. One subdirectory per interval.
    per_bec : int, optional
        The sample size per BEC. Defaults to one.
    tree_age : float, optional
        The age placeholder written to the tree list. Defaults to 60.

    Returns
    -------
    tuple of (pandas.DataFrame, pandas.DataFrame, pandas.DataFrame)
        The comparison rows, the BEC summary, and one row per interval with the
        number of skipped trees.
    """
    sample = select_intervals(intervals, per_bec=per_bec)
    root = Path(directory)
    rows: list[dict[str, object]] = []
    skips: list[dict[str, object]] = []
    for raw in sample.to_dict("records"):
        interval = {str(key): value for key, value in raw.items()}
        try:
            BecCode.parse(f"{_region(interval['TSA_DESC'])}{interval['BEC']}/01")
        except BecCodeError:
            skips.append(
                {
                    "interval_id": interval["interval_id"],
                    "BEC": interval["BEC"],
                    "trees": 0,
                    "skipped": 0,
                    "reason": "BEC not resolved by the variant",
                }
            )
            continue
        records, skipped = psp_tree_records(trees, interval, tree_age=tree_age)
        if not records:
            skips.append(
                {
                    "interval_id": interval["interval_id"],
                    "BEC": interval["BEC"],
                    "trees": 0,
                    "skipped": skipped,
                    "reason": "no tree resolved to one of BC's 15 species",
                }
            )
            continue
        interval = {**interval, **classes_for(records, _number(interval["ba0"]))}
        skips.append(
            {
                "interval_id": interval["interval_id"],
                "BEC": interval["BEC"],
                "trees": len(records),
                "skipped": skipped,
                "reason": "",
            }
        )
        run_dir = root / str(interval["interval_id"]).replace("|", "_")
        result = run_case(records, keywords_for(interval), directory=run_dir)
        predicted_start = summary_for_year(result.database, _integer(interval["year0"]))
        predicted_end = summary_for_year(result.database, _integer(interval["year1"]))
        observed_rows = visits[
            (visits["SITE_IDENTIFIER"] == interval["SITE_IDENTIFIER"])
            & (visits["VISIT_NUMBER"] == interval["visit1"])
            & (visits["PLOT"] == interval["PLOT"])
        ]
        observed = observed_rows.iloc[0]
        observed_next = {
            "ba": _number(observed["ba"]),
            "tph": _number(observed["tph"]),
            "qmd": _number(observed["qmd"]),
            "top_height": _number(observed["top_height"]),
            "volume": _number(observed["volume"]),
        }
        rows.append(
            compare_rows(
                interval,
                observed_next,
                predicted_start,
                predicted_end,
                envelope,
            )
        )
    frame = pd.DataFrame(rows)
    return frame, summarise(frame), pd.DataFrame(skips)
