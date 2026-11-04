"""Tests for the site-grouped probe harness.

They cover the full-visit tree read and the fold loop without running FVS.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import run_site_grouped_probe as grouped


def _intervals() -> pd.DataFrame:
    """Two eligible sites, each with one interval."""
    return pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "CLSTR_ID": "1-PSP",
                "visit0": 1,
                "visit1": 2,
                "PLOT": 1,
                "ba0": 25.0,
                "tph0": 900.0,
                "qmd": 18.0,
                "BEC": "SBPSmk",
                "TSA_DESC": "Quesnel TSA",
                "year0": 1990,
                "year1": 2000,
                "years": 10.0,
                "interval_id": "1|1|1990|2000",
                "dead_ba": 1.0,
            },
            {
                "SITE_IDENTIFIER": 2,
                "CLSTR_ID": "2-PSP",
                "visit0": 1,
                "visit1": 2,
                "PLOT": 1,
                "ba0": 30.0,
                "tph0": 800.0,
                "qmd": 20.0,
                "BEC": "SBPSmk",
                "TSA_DESC": "Quesnel TSA",
                "year0": 1990,
                "year1": 2000,
                "years": 10.0,
                "interval_id": "2|1|1990|2000",
                "dead_ba": 2.0,
            },
        ]
    )


def test_read_recruitment_trees_reads_both_visits(tmp_path: Path) -> None:
    """The harness must see end visits, not only the start tree list."""
    psp = tmp_path / "psp"
    psp.mkdir()
    pd.DataFrame(
        [
            {
                "SITE_IDENTIFIER": 1,
                "VISIT_NUMBER": 1,
                "PLOT": 1,
                "TREE_NO": 1,
                "SPECIES": "PL",
                "LV_D": "L",
                "PHF_TREE": 100.0,
            },
            {
                "SITE_IDENTIFIER": 1,
                "VISIT_NUMBER": 2,
                "PLOT": 1,
                "TREE_NO": 2,
                "SPECIES": "PL",
                "LV_D": "L",
                "PHF_TREE": 200.0,
            },
            {
                "SITE_IDENTIFIER": 99,
                "VISIT_NUMBER": 2,
                "PLOT": 1,
                "TREE_NO": 3,
                "SPECIES": "PL",
                "LV_D": "L",
                "PHF_TREE": 300.0,
            },
        ]
    ).to_csv(psp / "faib_tree_detail.csv", index=False)
    trees = grouped._read_recruitment_trees(psp, _intervals())
    assert trees["VISIT_NUMBER"].tolist() == [1, 2]


def test_main_runs_each_site_and_writes_a_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The fold loop writes both sites without invoking FVS."""
    data = tmp_path / "data"
    data.mkdir()
    _intervals().to_csv(data / "intervals.csv", index=False)
    pd.DataFrame(
        [
            {"SITE_IDENTIFIER": 1, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 30.0, "tph": 1000.0},
            {"SITE_IDENTIFIER": 2, "VISIT_NUMBER": 2, "PLOT": 1, "ba": 31.0, "tph": 900.0},
        ]
    ).to_csv(data / "visits.csv", index=False)
    candidates = tmp_path / "candidates.json"
    candidates.write_text(json.dumps([{"label": "base", "bamax": 75.0}]), encoding="utf-8")
    monkeypatch.setattr(
        grouped, "_read_recruitment_trees", lambda *_args, **_kwargs: pd.DataFrame({"x": [1]})
    )
    monkeypatch.setattr(grouped, "recruitment_table", lambda *_args, **_kwargs: pd.DataFrame())
    monkeypatch.setattr(
        grouped,
        "fit_rates",
        lambda *_args, **_kwargs: SimpleNamespace(rates=(SimpleNamespace(species="PL", rate=1.0),)),
    )

    def fake_run(command: list[str], **_kwargs: object) -> SimpleNamespace:
        out = Path(command[command.index("--out-dir") + 1])
        site = command[command.index("--test-sites") + 1]
        out.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "candidate": "base",
                    "fold": "test",
                    "interval_id": f"{site}|1|1990|2000",
                    "ba_error": 1.0,
                    "tph_error": 10.0,
                    "observed_ba1": 30.0,
                    "observed_tph1": 1000.0,
                }
            ]
        ).to_csv(out / "probe.csv", index=False)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    status = grouped.main(
        [
            "--data-dir",
            str(data),
            "--psp-dir",
            str(tmp_path / "psp"),
            "--out-dir",
            str(tmp_path / "out"),
            "--domain",
            "SBPSmk",
            "--min-qmd",
            "17",
            "--min-ba0",
            "20",
            "--candidates",
            str(candidates),
        ]
    )
    assert status == 0
    summary = pd.read_csv(tmp_path / "out" / "loso-summary.csv")
    assert summary.loc[0, "folds"] == 2
    assert summary.loc[0, "sites_pass"] == 2
    assert str(summary.loc[0, "data_checksum"]).startswith("sha256:")
