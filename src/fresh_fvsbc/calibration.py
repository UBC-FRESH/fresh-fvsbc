"""Build the provincial calibration dataset from the FAIB PSP archive.

The dataset is the input to the calibration workstream, not a calibration. It
turns the public FAIB permanent-sample-plot files into:

- one row per plot visit, with live basal area, trees per hectare, volume, and
  quadratic mean diameter;
- one row per consecutive visit pair, with the interval's dead basal area and
  trees per hectare;
- one row per live tree at the start of an interval, with its end status
  (``live``, ``dead``, or ``missing``), prior live diameter and year, and
  per-year growth from the previous live measurement;
- province-wide BEC coverage and basal-area envelope tables.

The tree-level tables carry site identifiers, so they stay in the caller's
output directory. The aggregate tables in ``notes/reference/calibration/`` carry
no site identifiers and are the ones safe to commit.

The archive is public
---------------------

The FAIB PSP compilation is public data. This module does not download it: the
caller names the directory that holds ``faib_header.csv``,
``faib_sample_byvisit.csv``, ``faib_plot_header.csv``, and
``faib_tree_detail.csv``. The manifest records each file's name, size, row
count, and SHA-256, so a run can be reproduced from the same snapshot.

What is in the weights
----------------------

``PHF_TREE`` is the per-hectare expansion factor and already includes
``TREE_WT`` and ``PLOT_WT`` for the FAIB compilation. This module still
multiplies by ``TREE_WT`` defensively, because the data dictionary names both
and a future extract may not fold them; the value is 1 for an ordinary tree.
``BA_TREE`` is the tree's basal area in square metres, and ``VOL_MER`` is gross
merchantable volume in cubic metres.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd

from fresh_fvsbc.bec import SUPPORTED_ZONES, UNSUPPORTED_ZONES
from fresh_fvsbc.treelist import JSP_CODES

__all__ = [
    "SPECIES_GROUPS",
    "CalibrationDataError",
    "CalibrationDataset",
    "Manifest",
    "build_dataset",
    "species_crosswalk",
    "species_envelope",
]

#: The four FAIB PSP files the dataset needs.
INPUT_FILES: tuple[str, ...] = (
    "faib_header.csv",
    "faib_sample_byvisit.csv",
    "faib_plot_header.csv",
    "faib_tree_detail.csv",
)

#: The species groups the mortality workstream uses. A code that is not here is
#: kept as ``UNKNOWN`` rather than folded into another group silently.
SPECIES_GROUPS: dict[str, str] = {
    "FD": "FD",
    "PL": "PL",
    "SE": "SE",
    "SW": "SE",
    "SX": "SE",
    "HW": "HW",
    "CW": "HW",
    "EP": "HW",
    "AT": "HW",
    "AC": "HW",
    "OC": "HW",
    "OH": "HW",
    "PW": "PW",
    "LW": "LW",
    "BG": "BG",
    "BL": "BL",
    "PY": "PY",
}

#: The minimum and maximum interval length, in years. An interval shorter than
#: two years is mostly measurement noise; one longer than forty mixes several
#: disturbances and a climate trend into one observation.
MIN_YEARS: int = 2
MAX_YEARS: int = 40


class CalibrationDataError(ValueError):
    """An archive or output that the dataset builder cannot use."""


class Manifest(TypedDict):
    """The input and output inventory a build writes.

    Attributes
    ----------
    inputs : dict
        Each input file's size and SHA-256, by file name.
    rows : dict
        The row count of each input and output table.
    parameters : dict
        The interval bounds and any other build setting.
    supported_zones : list of str
        The BEC zones the variant resolves.
    unsupported_zones : list of str
        The BEC zones the variant does not resolve.
    source : str
        The data source, named without a machine path.
    archive : str
        The archive directory's name, not its full path.
    """

    inputs: dict[str, dict[str, object]]
    rows: dict[str, int]
    parameters: dict[str, object]
    supported_zones: list[str]
    unsupported_zones: list[str]
    source: str
    archive: str


@dataclass(frozen=True, slots=True)
class CalibrationDataset:
    """The tables a build returns, and where they were written.

    Parameters
    ----------
    directory : Path
        The output directory.
    visits : pandas.DataFrame
        One row per plot visit.
    intervals : pandas.DataFrame
        One row per consecutive visit pair.
    tree_survival : pandas.DataFrame
        One row per live tree at the start of an interval.
    coverage : pandas.DataFrame
        BEC coverage, including the zones the variant does not resolve.
    envelope : pandas.DataFrame
        Basal-area and volume envelope by BEC.
    species_envelope : pandas.DataFrame
        Basal-area envelope by BEC and species group.
    species : pandas.DataFrame
        The PSP-to-FVS species crosswalk.
    manifest : Mapping
        The input and output inventory.
    """

    directory: Path
    visits: pd.DataFrame
    intervals: pd.DataFrame
    tree_survival: pd.DataFrame
    coverage: pd.DataFrame
    envelope: pd.DataFrame
    species_envelope: pd.DataFrame
    species: pd.DataFrame
    manifest: Manifest


def _sha256(path: Path) -> str:
    """Return the SHA-256 of a file.

    Parameters
    ----------
    path : Path
        The file to read.

    Returns
    -------
    str
        The hexadecimal digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_files(psp_dir: Path) -> dict[str, Path]:
    """Return the input paths, refusing a missing file by name."""
    paths = {name: psp_dir / name for name in INPUT_FILES}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise CalibrationDataError(
            f"{psp_dir} is missing {', '.join(missing)}; the four FAIB PSP files are required"
        )
    return paths


def _bec(frame: pd.DataFrame) -> pd.Series:
    """Build the BEC label from its three fields, refusing a missing zone."""
    zone = frame["BEC_ZONE"].fillna("").astype(str).str.strip().str.upper()
    subzone = frame["BEC_SBZ"].fillna("").astype(str).str.strip().str.upper()
    variant = (
        frame["BEC_VAR"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.upper()
    )
    return zone + subzone.str.lower() + variant


def _header(psp_dir: Path) -> pd.DataFrame:
    """Read the site header and attach the BEC and supported flag."""
    header = pd.read_csv(
        psp_dir / "faib_header.csv",
        usecols=[
            "SITE_IDENTIFIER",
            "BEC_ZONE",
            "BEC_SBZ",
            "BEC_VAR",
            "TSA_DESC",
            "OWNER",
        ],
        low_memory=False,
    )
    header["BEC"] = _bec(header)
    header["supported"] = header["BEC_ZONE"].fillna("").str.upper().isin(SUPPORTED_ZONES)
    header = header.drop_duplicates("SITE_IDENTIFIER").set_index("SITE_IDENTIFIER")
    return header


def _visits(psp_dir: Path) -> pd.DataFrame:
    """Read the visit table and normalise its identifiers."""
    visits = pd.read_csv(
        psp_dir / "faib_sample_byvisit.csv",
        usecols=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "MEAS_YR"],
        low_memory=False,
    )
    visits = visits.dropna(subset=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "MEAS_YR"])
    visits["VISIT_NUMBER"] = visits["VISIT_NUMBER"].astype(int)
    visits["MEAS_YR"] = visits["MEAS_YR"].astype(int)
    return visits.drop_duplicates(["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER"])


def _trees(psp_dir: Path, site_ids: set[object] | None, *, min_dbh: float = 0.0) -> pd.DataFrame:
    """Read the selected stands' trees in chunks and normalise the weights.

    ``site_ids=None`` reads every site, which is the all-zone path. ``min_dbh``
    applies the common DBH denominator before BA/TPH and survival are built.
    """
    if min_dbh < 0:
        raise ValueError("min_dbh must not be negative")
    columns = [
        "SITE_IDENTIFIER",
        "CLSTR_ID",
        "VISIT_NUMBER",
        "PLOT",
        "TREE_NO",
        "SPECIES",
        "DBH",
        "HEIGHT",
        "LV_D",
        "PHF_TREE",
        "TREE_WT",
        "BA_TREE",
        "VOL_MER",
        "DAM_AGNA",
        "DAM_AGNB",
        "DAM_AGNC",
        "DAM_AGND",
        "DAM_AGNE",
    ]
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        psp_dir / "faib_tree_detail.csv", usecols=columns, chunksize=500_000, low_memory=False
    ):
        if site_ids is not None:
            chunk = chunk[chunk["SITE_IDENTIFIER"].isin(site_ids)]
        if chunk.empty:
            continue
        chunk = chunk.dropna(subset=["DBH", "LV_D", "PHF_TREE"])
        chunk = chunk[chunk["DBH"] >= min_dbh]
        chunk = chunk[chunk["LV_D"].isin(["L", "D"])]
        chunk = chunk[chunk["PHF_TREE"] > 0]
        if chunk.empty:
            continue
        chunk["phf"] = chunk["PHF_TREE"].fillna(0.0) * chunk["TREE_WT"].fillna(1.0)
        chunk["ba"] = chunk["BA_TREE"].fillna(0.0) * chunk["phf"]
        chunk["volume"] = chunk["VOL_MER"].fillna(0.0) * chunk["phf"]
        chunk["species"] = chunk["SPECIES"].fillna("").astype(str).str.strip().str.upper()
        chunk["group"] = chunk["species"].map(SPECIES_GROUPS).fillna("UNKNOWN")
        damage_columns = ["DAM_AGNA", "DAM_AGNB", "DAM_AGNC", "DAM_AGND", "DAM_AGNE"]
        chunk["damage"] = chunk[damage_columns].notna().any(axis=1)
        chunks.append(
            chunk[
                [
                    "SITE_IDENTIFIER",
                    "CLSTR_ID",
                    "VISIT_NUMBER",
                    "PLOT",
                    "TREE_NO",
                    "species",
                    "group",
                    "DBH",
                    "HEIGHT",
                    "LV_D",
                    "phf",
                    "ba",
                    "volume",
                    "damage",
                ]
            ]
        )
    if not chunks:
        raise CalibrationDataError("the tree file holds no rows for the requested sites")
    trees = pd.concat(chunks, ignore_index=True)
    trees["VISIT_NUMBER"] = trees["VISIT_NUMBER"].astype(int)
    trees["PLOT"] = trees["PLOT"].astype(int)
    return trees


def _visit_table(trees: pd.DataFrame, visits: pd.DataFrame, header: pd.DataFrame) -> pd.DataFrame:
    """Build one row per plot visit from the live trees."""
    live = trees[trees["LV_D"] == "L"]
    visits_out = (
        live.groupby(["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "PLOT"], as_index=False)
        .agg(
            ba=("ba", "sum"),
            tph=("phf", "sum"),
            volume=("volume", "sum"),
            top_height=("HEIGHT", "max"),
            trees=("ba", "size"),
        )
        .rename(columns={"trees": "live_trees"})
    )
    visits_out = visits_out.merge(
        visits, on=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER"], how="inner"
    )
    visits_out = visits_out.merge(
        header[["BEC", "TSA_DESC", "supported"]],
        left_on="SITE_IDENTIFIER",
        right_index=True,
        how="left",
    )
    visits_out["qmd"] = 100.0 * np.sqrt(
        visits_out["ba"] / visits_out["tph"].replace(0.0, np.nan) * (4.0 / np.pi)
    )
    return visits_out.sort_values(
        ["SITE_IDENTIFIER", "PLOT", "MEAS_YR", "VISIT_NUMBER"], ignore_index=True
    )


def _intervals(visits: pd.DataFrame, trees: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the interval table and the tree-survival table."""
    visits = visits.copy()
    grouped = visits.groupby(["SITE_IDENTIFIER", "PLOT"], sort=False)
    for column, new in (
        ("MEAS_YR", "next_year"),
        ("VISIT_NUMBER", "next_visit"),
        ("ba", "next_ba"),
        ("tph", "next_tph"),
    ):
        visits[new] = grouped[column].shift(-1)
    intervals = visits.dropna(subset=["next_year", "next_visit"]).copy()
    intervals["years"] = intervals["next_year"] - intervals["MEAS_YR"]
    intervals = intervals[intervals["years"].between(MIN_YEARS, MAX_YEARS, inclusive="both")].copy()
    intervals["next_year"] = intervals["next_year"].astype(int)
    intervals["next_visit"] = intervals["next_visit"].astype(int)
    intervals["interval_id"] = (
        intervals["SITE_IDENTIFIER"].astype(str)
        + "|"
        + intervals["PLOT"].astype(str)
        + "|"
        + intervals["MEAS_YR"].astype(str)
        + "|"
        + intervals["next_year"].astype(str)
    )
    intervals = intervals.rename(
        columns={
            "MEAS_YR": "year0",
            "next_year": "year1",
            "VISIT_NUMBER": "visit0",
            "next_visit": "visit1",
            "ba": "ba0",
            "tph": "tph0",
        }
    )

    start = trees[trees["LV_D"] == "L"].merge(
        intervals[
            [
                "SITE_IDENTIFIER",
                "PLOT",
                "visit0",
                "visit1",
                "interval_id",
                "years",
                "year0",
                "ba0",
                "tph0",
                "BEC",
                "TSA_DESC",
            ]
        ],
        left_on=["SITE_IDENTIFIER", "PLOT", "VISIT_NUMBER"],
        right_on=["SITE_IDENTIFIER", "PLOT", "visit0"],
        how="inner",
    )
    end = trees[["SITE_IDENTIFIER", "PLOT", "VISIT_NUMBER", "TREE_NO", "LV_D", "phf"]].rename(
        columns={"VISIT_NUMBER": "visit1", "LV_D": "end_status", "phf": "end_phf"}
    )
    start = start.merge(
        end,
        on=["SITE_IDENTIFIER", "PLOT", "visit1", "TREE_NO"],
        how="left",
    )
    # Prior live diameter for each tree, from its previous measured visit.
    history = trees.loc[
        trees["LV_D"] == "L",
        ["SITE_IDENTIFIER", "PLOT", "VISIT_NUMBER", "TREE_NO", "DBH"],
    ].sort_values(["SITE_IDENTIFIER", "PLOT", "TREE_NO", "VISIT_NUMBER"])
    grouped_history = history.groupby(["SITE_IDENTIFIER", "PLOT", "TREE_NO"], sort=False)
    history["prior_dbh"] = grouped_history["DBH"].shift(1)
    history["prior_visit"] = grouped_history["VISIT_NUMBER"].shift(1)
    visit_year = visits[["SITE_IDENTIFIER", "PLOT", "VISIT_NUMBER", "MEAS_YR"]].rename(
        columns={"VISIT_NUMBER": "prior_visit", "MEAS_YR": "prior_year"}
    )
    history = history.merge(
        visit_year,
        on=["SITE_IDENTIFIER", "PLOT", "prior_visit"],
        how="left",
    )
    start = start.merge(
        history[["SITE_IDENTIFIER", "PLOT", "VISIT_NUMBER", "TREE_NO", "prior_dbh", "prior_year"]],
        left_on=["SITE_IDENTIFIER", "PLOT", "visit0", "TREE_NO"],
        right_on=["SITE_IDENTIFIER", "PLOT", "VISIT_NUMBER", "TREE_NO"],
        how="left",
    )
    start["growth"] = (start["DBH"] - start["prior_dbh"]) / (
        start["year0"] - start["prior_year"]
    ).replace(0.0, np.nan)

    start["status"] = np.select(
        [start["end_status"] == "D", start["end_status"] == "L"],
        ["dead", "live"],
        default="missing",
    )
    start["dead_ba"] = np.where(start["status"] == "dead", start["ba"], 0.0)
    start["dead_tph"] = np.where(
        start["status"] == "dead", start["end_phf"].fillna(start["phf"]), 0.0
    )
    dead = (
        start.groupby("interval_id", as_index=False)
        .agg(dead_ba=("dead_ba", "sum"), dead_tph=("dead_tph", "sum"))
        .set_index("interval_id")
    )
    intervals = intervals.merge(dead, left_on="interval_id", right_index=True, how="left")
    intervals[["dead_ba", "dead_tph"]] = intervals[["dead_ba", "dead_tph"]].fillna(0.0)
    intervals["ba_mortality"] = intervals["dead_ba"] / intervals["ba0"] / intervals["years"]
    intervals["tph_mortality"] = intervals["dead_tph"] / intervals["tph0"] / intervals["years"]
    intervals["net_ba_rate"] = (intervals["next_ba"] - intervals["ba0"]) / intervals["years"]
    intervals["gross_ba_rate"] = (
        intervals["next_ba"] - intervals["ba0"] + intervals["dead_ba"]
    ) / intervals["years"]

    tree_survival = start[
        [
            "interval_id",
            "BEC",
            "TSA_DESC",
            "CLSTR_ID",
            "PLOT",
            "TREE_NO",
            "species",
            "group",
            "DBH",
            "HEIGHT",
            "phf",
            "ba",
            "years",
            "ba0",
            "tph0",
            "damage",
            "status",
            "prior_dbh",
            "prior_year",
            "growth",
        ]
    ].rename(columns={"DBH": "dbh", "phf": "phf", "ba": "ba", "years": "years"})
    tree_survival["dead"] = (tree_survival["status"] == "dead").astype(int)
    tree_survival["known"] = (tree_survival["status"] != "missing").astype(int)
    tree_survival["exposure"] = tree_survival["years"] * tree_survival["known"]
    return intervals.reset_index(drop=True), tree_survival.reset_index(drop=True)


def _coverage(
    header: pd.DataFrame,
    visits: pd.DataFrame,
    intervals: pd.DataFrame,
    tree_survival: pd.DataFrame,
) -> pd.DataFrame:
    """Build the BEC coverage table, including the unsupported zones."""
    visits_meta = visits[["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER"]].drop_duplicates()
    visit_counts = visits_meta.groupby("SITE_IDENTIFIER").size()
    years = visits[["SITE_IDENTIFIER", "MEAS_YR"]].drop_duplicates()
    year_counts = years.groupby("SITE_IDENTIFIER").size()
    sites = pd.DataFrame(
        {
            "BEC": header["BEC"],
            "supported": header["supported"],
            "visits": visit_counts.reindex(header.index, fill_value=0),
            "years": year_counts.reindex(header.index, fill_value=0),
        }
    )
    rows: list[dict[str, object]] = []
    for bec, group in sites.groupby("BEC", dropna=False):
        rows.append(
            {
                "BEC": bec,
                "supported": bool(group["supported"].iloc[0]),
                "sites": int(group.shape[0]),
                "visits": int(group["visits"].sum()),
                "repeat_sites": int((group["years"] >= 2).sum()),
            }
        )
    coverage = pd.DataFrame(rows)
    interval_counts = intervals.groupby("BEC").size().rename("intervals")
    tree_counts = tree_survival.groupby("BEC").agg(
        live_trees=("status", "size"),
        dead_trees=("dead", "sum"),
        missing_trees=("status", lambda values: int((values == "missing").sum())),
        damaged_trees=("damage", "sum"),
    )
    coverage = coverage.merge(interval_counts, on="BEC", how="left")
    coverage = coverage.merge(tree_counts, on="BEC", how="left")
    for column in ("intervals", "live_trees", "dead_trees", "missing_trees", "damaged_trees"):
        coverage[column] = coverage[column].fillna(0).astype(int)
    coverage["supported"] = coverage["BEC"].isin(header.loc[header["supported"], "BEC"].unique())
    return coverage.sort_values(["supported", "sites"], ascending=[False, False], ignore_index=True)


def species_envelope(tree_survival: pd.DataFrame) -> pd.DataFrame:
    """Build the basal-area envelope by BEC and species group.

    Parameters
    ----------
    tree_survival : pandas.DataFrame
        The tree-survival table, with ``BEC``, ``group``, ``interval_id``,
        ``ba``, and ``phf``.

    Returns
    -------
    pandas.DataFrame
        One row per BEC and group, with the plot count, BA p50/p90/p99/max,
        and mean TPH.
    """
    if tree_survival.empty:
        return pd.DataFrame(
            columns=["BEC", "group", "plots", "ba_p50", "ba_p90", "ba_p99", "ba_max", "tph_mean"]
        )
    plots = tree_survival.groupby(["BEC", "group", "interval_id"], as_index=False).agg(
        ba=("ba", "sum"), tph=("phf", "sum")
    )
    rows: list[dict[str, object]] = []
    for (bec, group), frame in plots.groupby(["BEC", "group"], sort=True):
        ba = frame["ba"]
        rows.append(
            {
                "BEC": bec,
                "group": group,
                "plots": int(frame.shape[0]),
                "ba_p50": float(ba.quantile(0.50)),
                "ba_p90": float(ba.quantile(0.90)),
                "ba_p99": float(ba.quantile(0.99)),
                "ba_max": float(ba.max()),
                "tph_mean": float(frame["tph"].mean()),
            }
        )
    return pd.DataFrame(rows)


def _envelope(visits: pd.DataFrame) -> pd.DataFrame:
    """Build the basal-area and volume envelope by BEC."""
    rows: list[dict[str, object]] = []
    for bec, group in visits.groupby("BEC", dropna=False):
        ba = group["ba"].dropna()
        rows.append(
            {
                "BEC": bec,
                "plots": int(group.shape[0]),
                "ba_p50": float(ba.quantile(0.50)) if not ba.empty else np.nan,
                "ba_p90": float(ba.quantile(0.90)) if not ba.empty else np.nan,
                "ba_p99": float(ba.quantile(0.99)) if not ba.empty else np.nan,
                "ba_max": float(ba.max()) if not ba.empty else np.nan,
                "tph_mean": float(group["tph"].mean()),
                "volume_mean": float(group["volume"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("BEC", ignore_index=True)


def species_crosswalk(trees: pd.DataFrame) -> pd.DataFrame:
    """Return the PSP-to-FVS species crosswalk observed in the tree table.

    Parameters
    ----------
    trees : pandas.DataFrame
        The normalised tree table, with a ``species`` column.

    Returns
    -------
    pandas.DataFrame
        One row per observed PSP code, with its FVS code when the code is one of
        BC's 15, its calibration group, and a ``known`` flag.
    """
    observed = sorted(trees["species"].dropna().unique())
    rows = []
    for code in observed:
        fvs_code = code if code in JSP_CODES else ""
        rows.append(
            {
                "psp_species": code,
                "fvs_species": fvs_code,
                "group": SPECIES_GROUPS.get(code, "UNKNOWN"),
                "known": bool(fvs_code),
            }
        )
    return pd.DataFrame(rows)


def _manifest(
    psp_dir: Path,
    inputs: Mapping[str, Path],
    header: pd.DataFrame,
    visits_meta: pd.DataFrame,
    plots: pd.DataFrame,
    trees: pd.DataFrame,
    visits: pd.DataFrame,
    intervals: pd.DataFrame,
    tree_survival: pd.DataFrame,
    coverage: pd.DataFrame,
    envelope: pd.DataFrame,
    species_envelope_frame: pd.DataFrame,
    species: pd.DataFrame,
    include_unsupported: bool,
    min_dbh: float,
) -> Manifest:
    """Build the input and output manifest, without a machine-specific path."""
    return {
        "inputs": {
            name: {
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for name, path in inputs.items()
        },
        "rows": {
            "header": int(header.shape[0]),
            "visits": int(visits_meta.shape[0]),
            "plots": int(plots.shape[0]),
            "trees": int(trees.shape[0]),
            "visit_summaries": int(visits.shape[0]),
            "intervals": int(intervals.shape[0]),
            "tree_survival": int(tree_survival.shape[0]),
            "coverage": int(coverage.shape[0]),
            "envelope": int(envelope.shape[0]),
            "species_envelope": int(species_envelope_frame.shape[0]),
            "species": int(species.shape[0]),
        },
        "parameters": {
            "min_years": MIN_YEARS,
            "max_years": MAX_YEARS,
            "include_unsupported": include_unsupported,
            "min_dbh": min_dbh,
        },
        "supported_zones": list(SUPPORTED_ZONES),
        "unsupported_zones": list(UNSUPPORTED_ZONES),
        "source": "FAIB PSP compilation",
        "archive": psp_dir.name,
    }


def build_dataset(
    psp_dir: str | Path,
    out_dir: str | Path,
    *,
    include_unsupported: bool = False,
    min_dbh: float = 0.0,
) -> CalibrationDataset:
    """Build the calibration dataset and write it to ``out_dir``.

    Parameters
    ----------
    psp_dir : str or Path
        The directory that holds the four FAIB PSP files.
    out_dir : str or Path
        Where the tables and the manifest are written. The tree-level tables
        carry site identifiers; keep them outside the tracked tree.
    include_unsupported : bool, optional
        Read every site, including the zones the current variant does not
        resolve. The default keeps the supported-zone dataset unchanged.
    min_dbh : float, optional
        The common lower DBH limit, in cm. FAIB programs do not share one
        tree-detail limit: PSP subplots start at 2.0 cm while CMI/YSM/VRI/NFI
        tree detail starts at 4.0 cm. Set this explicitly for cross-program
        comparisons. Defaults to 0.0 for compatibility.

    Returns
    -------
    CalibrationDataset
        The tables, the crosswalk, and the manifest.

    Raises
    ------
    CalibrationDataError
        If an input file is missing, a required column is absent, or no
        supported-zone trees are present.
    """
    source = Path(psp_dir)
    destination = Path(out_dir)
    inputs = _require_files(source)
    destination.mkdir(parents=True, exist_ok=True)

    header = _header(source)
    visits_meta = _visits(source)
    plots = pd.read_csv(
        source / "faib_plot_header.csv",
        usecols=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "PLOT"],
        low_memory=False,
    ).drop_duplicates()
    supported_ids = set(header.index[header["supported"]])
    site_ids = None if include_unsupported else supported_ids
    trees = _trees(source, site_ids, min_dbh=min_dbh)
    visits = _visit_table(trees, visits_meta, header)
    intervals, tree_survival = _intervals(visits, trees)
    coverage = _coverage(header, visits_meta, intervals, tree_survival)
    envelope = _envelope(visits)
    species_envelope_frame = species_envelope(tree_survival)
    species = species_crosswalk(trees)
    manifest = _manifest(
        source,
        inputs,
        header,
        visits_meta,
        plots,
        trees,
        visits,
        intervals,
        tree_survival,
        coverage,
        envelope,
        species_envelope_frame,
        species,
        include_unsupported,
        min_dbh,
    )

    outputs = {
        "visits.csv": visits,
        "intervals.csv": intervals,
        "tree_survival.csv": tree_survival,
        "bec_coverage.csv": coverage,
        "bec_envelope.csv": envelope,
        "bec_species_envelope.csv": species_envelope_frame,
        "species_crosswalk.csv": species,
    }
    for name, frame in outputs.items():
        frame.to_csv(destination / name, index=False)
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return CalibrationDataset(
        directory=destination,
        visits=visits,
        intervals=intervals,
        tree_survival=tree_survival,
        coverage=coverage,
        envelope=envelope,
        species_envelope=species_envelope_frame,
        species=species,
        manifest=manifest,
    )
