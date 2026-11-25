"""A manifest-driven multi-scale dataset from FVS-BC runs.

The unit is the BEC: a stand carries its BEC label, and the landscape table aggregates by BEC,
never by TSA. The builder writes normalised CSVs for runs, stands, trees, each requested output
table, and a BEC-level landscape summary, plus the manifest and schema that produced them.

A manifest is a JSON object::

    {
      "dataset_id": "pilot-2026-11-25",
      "version": "0.1.0",
      "stands": [
        {"stand_id": "S1", "bec": "BWBSmw/01", "neighbourhood": "N1", "tsa": "Dawson Creek TSA",
         "trees": "stands/S1.csv", "calibration": null,
         "keywords": [{"name": "DATABASE", "lines": ["DSNOut", "FVSOut.db", "Summary", "TREELIDB"]},
                      {"name": "INVYEAR", "fields": ["1985"]},
                      {"name": "PROCESS"}, {"name": "STOP"}]}
      ]
    }

``trees`` is a CSV with the tree-list columns. Paths are relative to the manifest.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pandas as pd

from fresh_fvsbc.bundle import load_bundle
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import run_case
from fresh_fvsbc.treelist import TreeListFields

__all__ = ["DatasetError", "build_dataset"]

#: The normalised tables the builder always writes.
_TABLES = ("runs", "stands", "trees", "neighbourhoods", "landscape")


class DatasetError(Exception):
    """A manifest that cannot produce a dataset."""


def _keyword(record: Mapping[str, object]) -> Keyword:
    name = record.get("name")
    if not isinstance(name, str) or not name:
        raise DatasetError("every keyword needs a name")
    fields = record.get("fields", [])
    lines = record.get("lines", [])
    if not isinstance(fields, list) or not isinstance(lines, list):
        raise DatasetError(f"keyword {name} needs list fields and lines")
    return Keyword(name, tuple(str(v) for v in fields), tuple(str(v) for v in lines))


def _manifest(path: Path) -> dict[str, object]:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DatasetError(f"the manifest cannot be read: {error}") from error
    if not isinstance(record, dict):
        raise DatasetError("the manifest must be an object")
    stands = record.get("stands")
    if not isinstance(stands, list) or not stands:
        raise DatasetError("the manifest needs a non-empty stands list")
    for stand in stands:
        if not isinstance(stand, dict):
            raise DatasetError("every stand must be an object")
        for key in ("stand_id", "bec", "trees", "keywords"):
            if key not in stand:
                raise DatasetError(f"a stand is missing {key}")
    return record


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_dataset(manifest_path: str | Path, out_dir: str | Path) -> dict[str, Path]:
    """Build a multi-scale dataset from a manifest.

    Parameters
    ----------
    manifest_path : str or Path
        The manifest JSON.
    out_dir : str or Path
        Where the dataset is written.

    Returns
    -------
    dict of str to Path
        The table name to the file written.

    Raises
    ------
    DatasetError
        If the manifest is invalid or a stand cannot be run.
    """
    manifest_file = Path(manifest_path)
    manifest = _manifest(manifest_file)
    base = manifest_file.parent
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dataset_id = str(manifest.get("dataset_id", "dataset"))
    version = str(manifest.get("version", "0.0.0"))

    runs: list[dict[str, object]] = []
    stands: list[pd.DataFrame] = []
    trees: list[pd.DataFrame] = []
    written: dict[str, Path] = {}

    raw_stands = manifest.get("stands")
    if not isinstance(raw_stands, list):
        raise DatasetError("the manifest needs a stands list")
    for spec in raw_stands:
        if not isinstance(spec, dict):
            raise DatasetError("every stand must be an object")
        stand_id = str(spec["stand_id"])
        bec = str(spec["bec"])
        neighbourhood = str(spec.get("neighbourhood", bec))
        tsa = spec.get("tsa")
        tree_file = base / str(spec["trees"])
        tree_frame = pd.read_csv(tree_file)
        # `to_dict` returns the tree-list contract's keys.
        records = cast(list[TreeListFields], tree_frame.to_dict("records"))
        raw_keywords = spec.get("keywords")
        if not isinstance(raw_keywords, list):
            raise DatasetError(f"stand {stand_id} needs a keywords list")
        keywords = tuple(_keyword(record) for record in raw_keywords if isinstance(record, dict))
        calibration = (
            load_bundle(base / str(spec["calibration"])) if spec.get("calibration") else None
        )
        result = run_case(
            records,
            keywords,
            directory=out / "runs" / stand_id,
            calibration=calibration,
            tsa=str(tsa) if tsa else None,
        )
        provenance = result.provenance.as_record()
        run_id = f"{dataset_id}:{stand_id}"
        runs.append(
            {
                "dataset_id": dataset_id,
                "run_id": run_id,
                "stand_id": stand_id,
                "bec": bec,
                "neighbourhood": neighbourhood,
                "tsa": tsa,
                "tree_file_sha256": _hash(tree_file),
                "support": json.dumps(provenance.get("support", [])),
                "variant": provenance.get("variant"),
                "pyfvs_commit": provenance.get("pyfvs_commit"),
                "fvs_source_commit": provenance.get("fvs_source_commit"),
                "keyword_set_hash": provenance.get("keyword_set_hash"),
                "treelist_hash": provenance.get("treelist_hash"),
                "case_id": provenance.get("case_id"),
                "calibration_id": provenance.get("calibration_id"),
            }
        )
        summary = read_table(result.database, "FVS_Summary_Metric").copy()
        summary.insert(0, "bec", bec)
        summary.insert(0, "neighbourhood", neighbourhood)
        summary.insert(0, "stand_id", stand_id)
        summary.insert(0, "run_id", run_id)
        stands.append(summary)
        tree_table = read_table(result.database, "FVS_TreeList_Metric").copy()
        if not tree_table.empty:
            tree_table.insert(0, "bec", bec)
            tree_table.insert(0, "stand_id", stand_id)
            tree_table.insert(0, "run_id", run_id)
            trees.append(tree_table)

    runs_frame = pd.DataFrame(runs)
    stands_frame = pd.concat(stands, ignore_index=True)
    trees_frame = pd.concat(trees, ignore_index=True) if trees else pd.DataFrame()

    latest = stands_frame.sort_values(["run_id", "Year"]).groupby("run_id").tail(1)
    landscape = (
        latest.groupby("bec", as_index=False)[["BA", "Tph", "QMD", "TCuM"]]
        .mean()
        .rename(
            columns={"BA": "mean_BA", "Tph": "mean_Tph", "QMD": "mean_QMD", "TCuM": "mean_TCuM"}
        )
    )
    landscape["n_stands"] = latest.groupby("bec").size().to_numpy()
    neighbourhoods = (
        latest.groupby(["neighbourhood", "bec"], as_index=False)[["BA", "Tph", "QMD", "TCuM"]]
        .mean()
        .rename(
            columns={"BA": "mean_BA", "Tph": "mean_Tph", "QMD": "mean_QMD", "TCuM": "mean_TCuM"}
        )
    )
    neighbourhoods["n_stands"] = latest.groupby(["neighbourhood", "bec"]).size().to_numpy()

    for name, frame in (
        ("runs", runs_frame),
        ("stands", stands_frame),
        ("trees", trees_frame),
        ("neighbourhoods", neighbourhoods),
        ("landscape", landscape),
    ):
        path = out / f"{name}.csv"
        frame.to_csv(path, index=False)
        written[name] = path

    (out / "dataset.json").write_text(
        json.dumps(
            {
                "dataset_id": dataset_id,
                "version": version,
                "source_manifest": manifest,
                "manifest_sha256": _hash(manifest_file),
                "tables": list(_TABLES),
                "schema": {
                    name: list(frame.columns)
                    for name, frame in (
                        ("runs", runs_frame),
                        ("stands", stands_frame),
                        ("trees", trees_frame),
                        ("landscape", landscape),
                    )
                },
            },
            indent=2,
        )
        + "\n"
    )
    written["dataset"] = out / "dataset.json"
    return written
