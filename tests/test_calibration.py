"""Tests for the provincial calibration dataset builder.

The fixture is small enough to reason about by hand: two supported stands and
one unsupported stand, two visits for the supported ones, and one tree of each
end status (live, dead, missing). The test checks the tables, the aggregate
coverage, and the refusals without reading the 740 MB archive.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pandas as pd
import pytest

import build_calibration_dataset as cli
from fresh_fvsbc.calibration import (
    CalibrationDataError,
    build_dataset,
    species_crosswalk,
)


def _number(value: object) -> float:
    """Return a pandas scalar as a float.

    ``DataFrame.loc`` returns a union of every scalar pandas can hold; the
    cast names the one this fixture actually stores.
    """
    return cast(float, value)


def _write_archive(root: Path) -> Path:
    """Write a small archive and return its directory."""
    archive = root / "psp"
    archive.mkdir()
    header = pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": "S1",
                "BEC_ZONE": "IDF",
                "BEC_SBZ": "dk",
                "BEC_VAR": 3,
                "TSA_DESC": "Williams Lake TSA",
                "OWNER": "Crown",
            },
            {
                "SITE_IDENTIFIER": "S2",
                "BEC_ZONE": "SBS",
                "BEC_SBZ": "mc",
                "BEC_VAR": 2,
                "TSA_DESC": "Prince George TSA",
                "OWNER": "Crown",
            },
            {
                "SITE_IDENTIFIER": "S3",
                "BEC_ZONE": "CWH",
                "BEC_SBZ": "vm",
                "BEC_VAR": 1,
                "TSA_DESC": "North Island TSA",
                "OWNER": "Crown",
            },
        ]
    )
    header.to_csv(archive / "faib_header.csv", index=False)
    visits = pd.DataFrame(
        [
            ("S1", "S1-PSP1", 1, 2000),
            ("S1", "S1-PSP1", 2, 2010),
            ("S1", "S1-PSP2", 1, 2000),
            ("S1", "S1-PSP2", 2, 2010),
            ("S2", "S2-PSP1", 1, 2000),
            ("S2", "S2-PSP1", 2, 2010),
            ("S3", "S3-PSP1", 1, 2000),
        ],
        columns=["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER", "MEAS_YR"],
    )
    visits.to_csv(archive / "faib_sample_byvisit.csv", index=False)
    plots = visits[["SITE_IDENTIFIER", "CLSTR_ID", "VISIT_NUMBER"]].copy()
    plots["PLOT"] = [1, 1, 2, 2, 1, 1, 1]
    plots.to_csv(archive / "faib_plot_header.csv", index=False)
    trees = pd.DataFrame(
        [
            _tree("S1", "S1-PSP1", 1, 1, "FD", 20.0, 18.0, "L", damage="O"),
            _tree("S1", "S1-PSP1", 1, 2, "PL", 15.0, 14.0, "L"),
            _tree("S1", "S1-PSP1", 1, 3, "SE", 10.0, 9.0, "L"),
            _tree("S1", "S1-PSP1", 1, 4, "ZZ", 12.0, 11.0, "L"),
            _tree("S1", "S1-PSP1", 2, 1, "FD", 21.0, 19.0, "L"),
            _tree("S1", "S1-PSP1", 2, 2, "PL", 15.0, 14.0, "D"),
            _tree("S1", "S1-PSP1", 2, 4, "ZZ", 13.0, 12.0, "L"),
            _tree("S1", "S1-PSP2", 1, 1, "FD", 18.0, 17.0, "L", plot=2),
            _tree("S1", "S1-PSP2", 2, 1, "FD", 19.0, 18.0, "L", plot=2),
            _tree("S2", "S2-PSP1", 1, 1, "HW", 22.0, 20.0, "L"),
            _tree("S2", "S2-PSP1", 2, 1, "HW", 23.0, 21.0, "L"),
            _tree("S3", "S3-PSP1", 1, 1, "CW", 24.0, 22.0, "L"),
        ]
    )
    trees.to_csv(archive / "faib_tree_detail.csv", index=False)
    return archive


def _tree(
    site: str,
    cluster: str,
    visit: int,
    tree: int,
    species: str,
    dbh: float,
    height: float,
    status: str,
    *,
    plot: int = 1,
    damage: str | None = None,
) -> dict[str, object]:
    """Build one FAIB tree row with a ten-fold expansion factor."""
    ba_tree = 3.141592653589793 * (dbh / 200.0) ** 2
    return {
        "SITE_IDENTIFIER": site,
        "CLSTR_ID": cluster,
        "VISIT_NUMBER": visit,
        "PLOT": plot,
        "TREE_NO": tree,
        "SPECIES": species,
        "DBH": dbh,
        "HEIGHT": height,
        "LV_D": status,
        "PHF_TREE": 10.0,
        "TREE_WT": 1.0,
        "BA_TREE": ba_tree,
        "VOL_MER": 0.2,
        "DAM_AGNA": damage,
        "DAM_AGNB": None,
        "DAM_AGNC": None,
        "DAM_AGND": None,
        "DAM_AGNE": None,
    }


def test_build_writes_the_tables_and_the_manifest(tmp_path: Path) -> None:
    """The four inputs become the six tables, and the manifest counts them."""
    archive = _write_archive(tmp_path)
    dataset = build_dataset(archive, tmp_path / "out")

    for name in (
        "visits.csv",
        "intervals.csv",
        "tree_survival.csv",
        "bec_coverage.csv",
        "bec_envelope.csv",
        "bec_species_envelope.csv",
        "species_crosswalk.csv",
        "manifest.json",
    ):
        assert (dataset.directory / name).is_file()
    manifest = json.loads((dataset.directory / "manifest.json").read_text())
    assert manifest["rows"]["intervals"] == 3
    assert manifest["rows"]["tree_survival"] == 6
    assert manifest["rows"]["species_envelope"] > 0
    assert manifest["parameters"] == {
        "min_years": 2,
        "max_years": 40,
        "include_unsupported": False,
    }
    assert manifest["archive"] == "psp"


def test_coverage_counts_a_prototype_zone_without_tree_tables(tmp_path: Path) -> None:
    """CWH is supported now, and still contributes no interval without a tree table."""
    archive = _write_archive(tmp_path)
    dataset = build_dataset(archive, tmp_path / "out")
    coverage = dataset.coverage.set_index("BEC")

    assert bool(coverage.loc["IDFdk3", "supported"]) is True
    assert int(_number(coverage.loc["IDFdk3", "sites"])) == 1
    assert int(_number(coverage.loc["IDFdk3", "visits"])) == 4
    assert int(_number(coverage.loc["IDFdk3", "repeat_sites"])) == 1
    assert int(_number(coverage.loc["IDFdk3", "intervals"])) == 2
    assert int(_number(coverage.loc["IDFdk3", "damaged_trees"])) == 1
    assert bool(coverage.loc["CWHvm1", "supported"]) is True
    assert int(_number(coverage.loc["CWHvm1", "visits"])) == 1
    assert int(_number(coverage.loc["CWHvm1", "intervals"])) == 0


def test_intervals_separate_dead_from_missing(tmp_path: Path) -> None:
    """A tree seen dead is dead; a tree absent from the second visit is missing."""
    archive = _write_archive(tmp_path)
    dataset = build_dataset(archive, tmp_path / "out")
    survival = dataset.tree_survival
    statuses = survival["status"].value_counts().to_dict()

    assert statuses == {"live": 4, "dead": 1, "missing": 1}
    interval = dataset.intervals.set_index("interval_id")
    first = interval.loc["S1|1|2000|2010"]
    assert _number(first["dead_ba"]) > 0.0
    assert _number(first["dead_tph"]) == 10.0
    assert _number(first["years"]) == 10.0


def test_envelope_is_built_from_supported_visits(tmp_path: Path) -> None:
    """Every supported visit reaches the envelope, even when it has no tree table."""
    archive = _write_archive(tmp_path)
    dataset = build_dataset(archive, tmp_path / "out")
    assert set(dataset.envelope["BEC"]) == {"CWHvm1", "IDFdk3", "SBSmc2"}
    assert dataset.envelope["ba_p99"].notna().all()
    assert set(dataset.species_envelope["group"]) == {"FD", "HW", "PL", "SE", "UNKNOWN"}


def test_species_crosswalk_marks_an_unknown_code(tmp_path: Path) -> None:
    """A code outside BC's 15 is kept and marked unknown, not folded into another group."""
    archive = _write_archive(tmp_path)
    dataset = build_dataset(archive, tmp_path / "out")
    species = dataset.species.set_index("psp_species")
    assert bool(species.loc["FD", "known"]) is True
    assert bool(species.loc["ZZ", "known"]) is False
    assert species.loc["ZZ", "group"] == "UNKNOWN"


def test_a_missing_input_is_refused(tmp_path: Path) -> None:
    """A missing file is named before any output is written."""
    archive = _write_archive(tmp_path)
    (archive / "faib_tree_detail.csv").unlink()
    with pytest.raises(CalibrationDataError, match=r"faib_tree_detail\.csv"):
        build_dataset(archive, tmp_path / "out")


def test_the_command_writes_the_dataset(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The command is a shell over the builder, and it reports the counts."""
    archive = _write_archive(tmp_path)
    code = cli.main(["--psp-dir", str(archive), "--out-dir", str(tmp_path / "out")])
    captured = capsys.readouterr()
    assert code == cli.EXIT_OK
    assert "intervals: 3" in captured.out
    assert (tmp_path / "out" / "manifest.json").is_file()


def test_the_command_refuses_a_missing_archive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing archive is bad input, not a traceback."""
    code = cli.main(["--psp-dir", str(tmp_path / "absent"), "--out-dir", str(tmp_path / "out")])
    assert code == cli.EXIT_BAD_INPUT
    assert "faib_header.csv" in capsys.readouterr().err


def test_all_zones_adds_the_unsupported_zone_to_the_tree_tables(tmp_path: Path) -> None:
    """The all-zone build reads CWH trees, visits, and envelope rows, not only the counts."""
    archive = _write_archive(tmp_path)
    dataset = build_dataset(archive, tmp_path / "out", include_unsupported=True)

    assert "CWHvm1" in set(dataset.visits["BEC"])
    assert "CWHvm1" in set(dataset.envelope["BEC"])
    assert dataset.manifest["parameters"]["include_unsupported"] is True


def test_the_command_accepts_the_all_zones_flag(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The command exposes the all-zone path."""
    archive = _write_archive(tmp_path)
    code = cli.main(["--psp-dir", str(archive), "--out-dir", str(tmp_path / "out"), "--all-zones"])
    assert code == cli.EXIT_OK
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text())
    assert manifest["parameters"]["include_unsupported"] is True
    assert "all" not in capsys.readouterr().err.lower()


def test_species_crosswalk_accepts_a_frame_with_one_known_code() -> None:
    """The crosswalk function is usable on its own, without a full build."""
    frame = pd.DataFrame({"species": ["FD", "ZZ"]})
    crosswalk = species_crosswalk(frame).set_index("psp_species")
    assert crosswalk.loc["FD", "fvs_species"] == "FD"
    assert crosswalk.loc["ZZ", "fvs_species"] == ""
