"""The W1.6 domain classifier: the sample-size rule, the summaries, and the command."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

import build_calibration_domains as cli
from fresh_fvsbc.calibration_domains import (
    DomainError,
    _integer,
    classify_variant,
    prepare_coverage,
    summarise_domains,
    write_domain_tables,
)


def _coverage_frame() -> pd.DataFrame:
    """Return a coverage table that exercises every status and verdict."""
    return pd.DataFrame(
        [
            _row("ICHmw2", True, repeat=225, intervals=978, dead=15357),
            _row("ESSFwc2", True, repeat=52, intervals=119, dead=889),
            _row("MSdm1", True, repeat=133, intervals=591, dead=5981),
            _row("MSdm3", True, repeat=18, intervals=57, dead=859),
            _row("IDFdk3", True, repeat=161, intervals=298, dead=5652),
            _row("SBPSdc", True, repeat=17, intervals=49, dead=1411),
            _row("PPxh", True, repeat=2, intervals=6, dead=25),
            _row("SBSxx", True, repeat=10, intervals=50, dead=2000),
            _row("CWHvm1", False, repeat=100, intervals=0, dead=0),
        ]
    )


def _row(bec: str, supported: bool, *, repeat: int, intervals: int, dead: int) -> dict[str, object]:
    """Build one aggregate coverage row.

    Parameters
    ----------
    bec : str
        The BEC variant.
    supported : bool
        Whether the variant resolves the zone.
    repeat : int
        Repeat sites.
    intervals : int
        Measurement intervals.
    dead : int
        Dead-tree rows.

    Returns
    -------
    dict
        One row in the coverage table's shape.
    """
    return {
        "BEC": bec,
        "supported": supported,
        "sites": repeat * 2,
        "visits": repeat * 3,
        "repeat_sites": repeat,
        "intervals": intervals,
        "live_trees": repeat * 100,
        "dead_trees": dead,
        "missing_trees": 0,
        "damaged_trees": 0,
    }


@pytest.mark.parametrize(
    ("supported", "repeat", "intervals", "expected"),
    [
        (False, 100, 100, "upstream"),
        (True, 15, 50, "calibration"),
        (True, 14, 50, "validation-only"),
        (True, 15, 49, "validation-only"),
        (True, 5, 10, "validation-only"),
        (True, 4, 9, "insufficient"),
    ],
)
def test_classify_variant(supported: bool, repeat: int, intervals: int, expected: str) -> None:
    """The rule has four outcomes and the boundaries are inclusive."""
    assert (
        classify_variant(supported=supported, repeat_sites=repeat, intervals=intervals) == expected
    )


def test_prepare_coverage_adds_status_readiness_and_mde() -> None:
    """The prepared table carries the status, the three readiness flags, and both MDEs."""
    prepared = prepare_coverage(_coverage_frame())
    status = dict(zip(prepared["BEC"], prepared["status"], strict=True))
    assert status["ICHmw2"] == "calibration"
    assert status["ESSFwc2"] == "calibration"
    assert status["SBPSdc"] == "validation-only"
    assert status["PPxh"] == "insufficient"
    assert status["CWHvm1"] == "upstream"
    row = prepared.set_index("BEC").loc["MSdm3"]
    assert bool(row["capacity_ready"]) is True
    assert bool(row["mortality_ready"]) is False
    assert bool(row["growth_ready"]) is False
    ich = prepared.set_index("BEC").loc["ICHmw2"]
    assert ich["mortality_mde_pct"] == pytest.approx(round(100.0 * 2.8 / math.sqrt(15357), 2))
    assert ich["ba_mde_m2ha"] == pytest.approx(round(2.8 * 10 / math.sqrt(978), 2))
    upstream = prepared.set_index("BEC").loc["CWHvm1"]
    assert str(upstream["mortality_mde_pct"]) == "nan"
    assert str(upstream["ba_mde_m2ha"]) == "nan"


def test_prepare_coverage_accepts_string_booleans() -> None:
    """The CSV's ``True``/``False`` text is parsed, not treated as truthy strings."""
    frame = _coverage_frame()
    frame["supported"] = frame["supported"].map({True: "True", False: "False"})
    prepared = prepare_coverage(frame)
    assert prepared.set_index("BEC").loc["CWHvm1", "status"] == "upstream"
    assert prepared.set_index("BEC").loc["ICHmw2", "status"] == "calibration"


def test_prepare_coverage_refuses_a_missing_column() -> None:
    """A table that is not the coverage table names the missing column."""
    frame = _coverage_frame().drop(columns=["dead_trees"])
    with pytest.raises(DomainError, match="dead_trees"):
        prepare_coverage(frame)


def test_prepare_coverage_refuses_an_unknown_zone() -> None:
    """A BEC code outside the twelve zones is refused rather than silently dropped."""
    frame = _coverage_frame()
    frame.loc[0, "BEC"] = "XYZ01"
    with pytest.raises(DomainError, match="XYZ01"):
        prepare_coverage(frame)


def test_summarise_domains_verdicts_and_claims() -> None:
    """Each zone gets the verdict its counts support, and a baseline flag count."""
    prepared = prepare_coverage(_coverage_frame())
    baseline = pd.DataFrame(
        [
            {"BEC": "ICHmw2", "above_p99": 1, "above_max": 0},
            {"BEC": "SBPSdc", "above_p99": 0, "above_max": 1},
        ]
    )
    summary = summarise_domains(prepared, baseline).set_index("zone")
    assert summary.loc["ICH", "verdict"] == "calibration"
    assert summary.loc["ESSF", "verdict"] == "partial"
    assert summary.loc["SBPS", "verdict"] == "validation-only"
    assert summary.loc["PP", "verdict"] == "insufficient"
    assert summary.loc["CWH", "verdict"] == "upstream"
    assert summary.loc["ICH", "baseline_flags"] == 1
    assert summary.loc["SBPS", "baseline_flags"] == 1
    assert "leave-one-variant-out" in str(summary.loc["ICH", "claim"])
    assert "W2" in str(summary.loc["CWH", "claim"])
    assert "validation" in str(summary.loc["SBPS", "claim"])
    assert "Not enough" in str(summary.loc["PP", "claim"])
    assert "ready parameters" in str(summary.loc["ESSF", "claim"])


def test_summarise_domains_without_a_baseline() -> None:
    """The baseline is optional, and the flag column is zero when it is absent."""
    summary = summarise_domains(prepare_coverage(_coverage_frame()))
    assert set(summary["baseline_flags"]) == {0}


def test_summarise_domains_refuses_an_unknown_baseline_zone() -> None:
    """A baseline BEC outside the zones is refused by name."""
    prepared = prepare_coverage(_coverage_frame())
    baseline = pd.DataFrame([{"BEC": "XYZ01", "above_p99": 1, "above_max": 0}])
    with pytest.raises(DomainError, match="XYZ01"):
        summarise_domains(prepared, baseline)


def test_write_domain_tables_writes_both_csvs(tmp_path: Path) -> None:
    """The command writes the per-variant and per-zone tables with the expected counts."""
    coverage = tmp_path / "coverage.csv"
    _coverage_frame().to_csv(coverage, index=False)
    baseline = tmp_path / "baseline.csv"
    pd.DataFrame([{"BEC": "ICHmw2", "above_p99": 1, "above_max": 0}]).to_csv(baseline, index=False)
    tables = write_domain_tables(coverage, baseline, tmp_path / "out")
    power = pd.read_csv(tables.power_path)
    summary = pd.read_csv(tables.summary_path)
    assert len(power) == 9
    assert "status" in power.columns
    assert "verdict" in summary.columns
    assert tables.calibration == 5
    assert tables.validation_only == 2
    assert tables.insufficient == 1
    assert tables.upstream == 1
    assert tables.variants == 9


def test_write_domain_tables_without_a_baseline(tmp_path: Path) -> None:
    """The optional baseline is not required."""
    coverage = tmp_path / "coverage.csv"
    _coverage_frame().to_csv(coverage, index=False)
    tables = write_domain_tables(coverage, None, tmp_path / "out")
    assert tables.summary_path.is_file()


def test_the_command_reports_what_it_wrote(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The CLI prints both paths and the status counts."""
    coverage = tmp_path / "coverage.csv"
    _coverage_frame().to_csv(coverage, index=False)
    out = tmp_path / "out"
    assert cli.main(["--coverage", str(coverage), "--out-dir", str(out)]) == 0
    captured = capsys.readouterr()
    assert "domain_power.csv" in captured.out
    assert "5 calibration" in captured.out
    assert "1 upstream" in captured.out


def test_the_command_refuses_bad_input(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A missing file is reported as input, not as a traceback."""
    assert cli.main(["--coverage", str(tmp_path / "absent.csv"), "--out-dir", str(tmp_path)]) == 2
    assert "build_calibration_domains:" in capsys.readouterr().err


def test_integer_accepts_numbers_and_refuses_text() -> None:
    """A non-numeric table value is zero, not an exception."""
    assert _integer("12") == 12
    assert _integer(12.9) == 12
    assert _integer("not a number") == 0


def test_claim_is_narrow_below_three_calibration_variants() -> None:
    """Two variants get a narrow claim; three get the full claim."""
    from fresh_fvsbc.calibration_domains import _claim

    assert "Narrow claim" in _claim("calibration", 2)
    assert "held-out" in _claim("calibration", 3)
