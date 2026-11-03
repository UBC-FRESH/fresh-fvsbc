"""The W2.3 subzones resolve in the built BC variant.

This is the behavioural half of the patch: the wrapper can parse the code, but
only a build with the W2.3 Fortran patch makes FVS echo that code and select the
subzone's default maximum basal area. A build without the patch silently falls
back to ``ICHmw2/01``; :func:`fresh_fvsbc.run_case` now refuses that, and this
module checks the positive path for every subzone in the defaults table.

The test needs the built extension and skips without it, because the quality
job has no Fortran toolchain. The CI extension job runs it.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from fresh_fvsbc import run_case
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.nemora import to_tree_list
from nemora_fixtures import synthetic_population

#: The defaults table is the source of truth for the expected value.
DEFAULTS: Path = (
    Path(__file__).resolve().parents[1]
    / "notes"
    / "reference"
    / "calibration"
    / "w2-subzone-defaults.csv"
)


def _subzones() -> list[tuple[str, float]]:
    """Return each subzone and its provisional default from the tracked table.

    Returns
    -------
    list of tuple
        ``(bec, expected_bamax_m2ha)`` for all 19 W2.3 subzones.
    """
    with DEFAULTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [(row["bec"], float(row["provisional_bamax_m2ha"])) for row in rows]


@pytest.mark.parametrize(("bec", "expected"), _subzones())
def test_a_w2_subzone_resolves_and_echoes_its_default(
    tmp_path: Path, bec: str, expected: float
) -> None:
    """One run per subzone echoes its code and its provisional BAMAX.

    Parameters
    ----------
    tmp_path : Path
        The run directory.
    bec : str
        The zone, subzone, and variant token, such as ``ESSFdh1``.
    expected : float
        The provisional default from ``w2-subzone-defaults.csv``.

    Raises
    ------
    pytest.skip.Exception
        If the BC extension is not built in this environment.
    """
    pytest.importorskip(
        "pyfvs", reason="the BC extension is not built in this environment; ADR 0004 is the recipe"
    )
    records = to_tree_list(synthetic_population(), species="FD", tree_age=60.0)
    keywords = (
        Keyword("STDIDENT", (f"W2 {bec}",)),
        Keyword("STDINFO", ("CAR", f"{bec}/01", "0", "200", "35", "16")),
        Keyword("SITECODE", ("FD", "100")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("TIMEINT", ("", "10")),
        Keyword("NUMCYCLE", ("1",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run_case(records, keywords, directory=tmp_path / bec)
    report = (result.directory / "run.out").read_text(encoding="latin-1")

    assert f"BEC={bec}/01" in report
    lines = [
        line
        for line in report.splitlines()
        if "MAXIMUM BASAL AREA FOR" in line and "IS SET BY DEFAULT TO:" in line
    ]
    assert lines, f"{bec} wrote no default-BAMAX line"
    assert f"{expected:.1f} SQ M/HA" in lines[0]
    assert result.database.is_file()
