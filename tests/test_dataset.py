"""The manifest-driven multi-scale dataset builder."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import pytest

from fresh_fvsbc.dataset import DatasetError, build_dataset


def _trees(path: Path, species: str) -> None:
    pd.DataFrame(
        [
            {
                "plot_id": 1,
                "tree_num": 1,
                "tree_count": 200.0,
                "tree_history": 0,
                "species": species,
                "diam": 14.0,
                "dg_incr": 0.0,
                "live_ht": 13.0,
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": 5,
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
                "tree_age": 50.0,
            },
            {
                "plot_id": 1,
                "tree_num": 2,
                "tree_count": 150.0,
                "tree_history": 0,
                "species": species,
                "diam": 22.0,
                "dg_incr": 0.0,
                "live_ht": 18.0,
                "trunc_ht": 0.0,
                "htg_incr": 0.0,
                "crown_ratio": 5,
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
                "tree_age": 50.0,
            },
        ]
    ).to_csv(path, index=False)


def _keywords(bec: str) -> list[dict[str, object]]:
    return [
        {"name": "DATABASE", "lines": ["DSNOut", "FVSOut.db", "Summary", "TREELIDB"]},
        {"name": "STDIDENT", "fields": ["DATASET TEST"]},
        {"name": "STDINFO", "fields": ["CAR", bec, "0", "200", "35", "16"]},
        {"name": "SITECODE", "fields": ["SE", "15"]},
        {"name": "INVYEAR", "fields": ["1985"]},
        {"name": "DESIGN", "fields": ["0", "1", "999", "1", "0", "1", "1"]},
        {"name": "TIMEINT", "fields": ["", "10"]},
        {"name": "NUMCYCLE", "fields": ["1"]},
        {"name": "TREELIST"},
        {"name": "PROCESS"},
        {"name": "STOP"},
    ]


def _manifest(tmp: Path) -> Path:
    (tmp / "trees").mkdir()
    _trees(tmp / "trees" / "bwbs.csv", "AT")
    _trees(tmp / "trees" / "sbs.csv", "PL")
    manifest = {
        "dataset_id": "pilot",
        "version": "0.1.0",
        "stands": [
            {
                "stand_id": "B1",
                "bec": "BWBSmw/01",
                "neighbourhood": "N1",
                "tsa": "Dawson Creek TSA",
                "trees": "trees/bwbs.csv",
                "keywords": _keywords("BWBSmw/01"),
            },
            {
                "stand_id": "S1",
                "bec": "SBSmw/01",
                "neighbourhood": "N1",
                "tsa": "Dawson Creek TSA",
                "trees": "trees/sbs.csv",
                "keywords": _keywords("SBSmw/01"),
            },
        ],
    }
    path = tmp / "manifest.json"
    path.write_text(json.dumps(manifest))
    return path


def test_manifest_without_stands_is_refused(tmp_path: Path) -> None:
    """An empty dataset is a manifest error, not an empty table."""
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"dataset_id": "empty", "stands": []}))
    with pytest.raises(DatasetError, match="stands"):
        build_dataset(path, tmp_path / "out")


@pytest.mark.skipif(
    os.environ.get("FVSBC_W5") != "1",
    reason="needs a BWBS/SBS V3 build; set FVSBC_W5=1 in that job",
)
def test_build_dataset_writes_the_schema(tmp_path: Path) -> None:
    """Two stands produce runs, stands, trees, and a BEC landscape."""
    written = build_dataset(_manifest(tmp_path), tmp_path / "out")
    for name in ("runs", "stands", "trees", "neighbourhoods", "landscape", "dataset"):
        assert name in written
        assert written[name].exists()
    runs = pd.read_csv(written["runs"])
    assert set(runs["bec"]) == {"BWBSmw/01", "SBSmw/01"}
    support = json.loads(runs.iloc[0]["support"])
    assert support
    assert {"tier", "species"} <= set(support[0])
    landscape = pd.read_csv(written["landscape"])
    assert set(landscape["bec"]) == {"BWBSmw/01", "SBSmw/01"}
    assert (landscape["n_stands"] == 1).all()
    neighbourhoods = pd.read_csv(written["neighbourhoods"])
    assert set(neighbourhoods["neighbourhood"]) == {"N1"}
    assert set(neighbourhoods["bec"]) == {"BWBSmw/01", "SBSmw/01"}
    trees = pd.read_csv(written["trees"])
    assert {"run_id", "stand_id", "bec"} <= set(trees.columns)
    schema = json.loads(written["dataset"].read_text())["schema"]
    assert "BA" in schema["stands"]
    assert "DBH" in schema["trees"]


def test_keyword_and_manifest_validation(tmp_path: Path) -> None:
    """Bad keywords and a bad manifest are named errors, not silent runs."""
    from fresh_fvsbc.dataset import _keyword, _manifest

    with pytest.raises(DatasetError, match="name"):
        _keyword({})
    with pytest.raises(DatasetError, match="fields"):
        _keyword({"name": "X", "fields": "bad"})
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    with pytest.raises(DatasetError, match="cannot be read"):
        _manifest(bad)
    missing = tmp_path / "missing.json"
    missing.write_text(json.dumps({"stands": [{"stand_id": "x"}]}))
    with pytest.raises(DatasetError, match="missing"):
        _manifest(missing)


def test_build_dataset_with_a_stub_runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The builder normalises tables and the BEC scales without the extension."""
    import fresh_fvsbc.dataset as dataset

    class _Prov:
        def as_record(self) -> dict[str, object]:
            return {
                "variant": "bc",
                "pyfvs_commit": "p",
                "fvs_source_commit": "f",
                "keyword_set_hash": "sha256:k",
                "treelist_hash": "sha256:t",
                "case_id": "case",
                "calibration_id": "",
                "support": [{"species": "AT", "tier": "C", "reason": "x", "evidence": "y"}],
            }

    class _Result:
        database = tmp_path / "stub.db"
        provenance = _Prov()

    def fake_run(*_args: object, **_kwargs: object) -> _Result:
        return _Result()

    def fake_read(_db: object, table: str) -> pd.DataFrame:
        if table == "FVS_Summary_Metric":
            return pd.DataFrame(
                [
                    {"Year": 1985, "BA": 20.0, "Tph": 500.0, "QMD": 8.0, "TCuM": 100.0},
                    {"Year": 1995, "BA": 24.0, "Tph": 520.0, "QMD": 9.0, "TCuM": 120.0},
                ]
            )
        return pd.DataFrame(
            [
                {
                    "Year": 1985,
                    "TreeIndex": 1,
                    "PtIndex": 1,
                    "SpeciesFVS": "AT",
                    "DBH": 10.0,
                    "DG": 0.1,
                    "Ht": 10.0,
                    "HtG": 0.1,
                    "TPH": 500.0,
                    "MortPH": 0.0,
                }
            ]
        )

    monkeypatch.setattr(dataset, "run_case", fake_run)
    monkeypatch.setattr(dataset, "read_table", fake_read)
    written = build_dataset(_manifest(tmp_path), tmp_path / "out")
    runs = pd.read_csv(written["runs"])
    assert list(runs["neighbourhood"]) == ["N1", "N1"]
    landscape = pd.read_csv(written["landscape"])
    assert landscape["mean_BA"].tolist() == [24.0, 24.0]
    assert landscape["n_stands"].tolist() == [1, 1]
