"""Tests for the command-line entry point.

The exit codes are the contract, so each one is tested on its own: ``0`` for a completed run, ``1``
for a run that failed, ``2`` for input the command cannot use. Most of these run without the built
extension, because the drive is faked; the two integration tests exercise the documented entry point
in a subprocess.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import pandas as pd
import pytest

from fresh_fvsbc import cli, run
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.outputs import read_table
from fresh_fvsbc.run import KEYWORD_FILE_NAME
from nemora_fixtures import synthetic_population

ROOT: Path = Path(__file__).resolve().parents[1]

WARNING = (
    "FVS03 WARNING:  FOREST CODE INDICATES THE GEOGRAPHIC LOCATION IS OUTSIDE THE RANGE OF THE "
    "MODEL.  DEFAULT CODE IS USED."
)
ERROR = "FVS16 ERROR:  KEYWORD ENTERED IS USED IN WRONG CONTEXT AND WAS IGNORED.  RECORDS READ= 19"


def a_population_file(path: Path) -> Path:
    """Write a population file shaped like ``nemora``'s output, and return its path."""
    path.write_text(json.dumps(synthetic_population()), encoding="utf-8")
    return path


def a_database(path: Path, *, messages: tuple[str, ...] = ()) -> Path:
    """Build a database shaped like a run's output, and return its path."""
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "create table FVS_Cases (CaseID text, StandID text, Variant text, RunDateTime text)"
        )
        connection.execute(
            "insert into FVS_Cases values (?, ?, ?, ?)",
            ("case-0", "SYNTHETIC", "BC", "10/24/2026 12:00:00"),
        )
        connection.execute("create table FVS_Error (CaseID text, StandID text, Message text)")
        for message in messages:
            connection.execute(
                "insert into FVS_Error values (?, ?, ?)", ("case-0", "SYNTHETIC", message)
            )
        connection.commit()
    finally:
        connection.close()
    return path


def a_fake_drive(*, messages: tuple[str, ...] = ()) -> Callable[..., run._Drive]:
    """Return a drive that writes the database a real run would write, in the run directory."""

    def drive(key_name: str, *, variant: str, directory: Path) -> run._Drive:
        a_database(directory / run.DATABASE_NAME, messages=messages)
        return run._Drive(summary=pd.DataFrame({"Year": [0, 10]}), variants=("BC",))

    return drive


def test_a_completed_run_exits_zero_and_names_its_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A run that worked says where its outputs are, which is what a script needs next."""
    monkeypatch.setattr(run, "_drive", a_fake_drive(messages=(WARNING,)))
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--keyword",
            "STDINFO",
            "--keyword",
            "PROCESS",
            "--keyword",
            "STOP",
        ]
    )
    printed = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "case case-0" in printed
    assert "summary: 2 rows, 1 columns" in printed
    assert "warnings: 1" in printed
    assert "provenance.json" in printed
    assert (tmp_path / "run" / "provenance.json").is_file()


def test_a_run_that_holds_an_error_exits_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failed run is reported as a failure, which is a different thing from bad input."""
    monkeypatch.setattr(run, "_drive", a_fake_drive(messages=(ERROR,)))
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
        ]
    )
    captured = capsys.readouterr()
    assert code == cli.EXIT_FAILED_RUN
    assert "the run failed" in captured.err
    assert "1 error" in captured.err
    assert captured.out == ""


def test_a_missing_population_file_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file that is not there is input to fix, not a run to report."""
    code = cli.main(
        [
            str(tmp_path / "absent.json"),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "No such file" in capsys.readouterr().err


def test_a_population_file_that_is_not_json_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A malformed file is named rather than traced."""
    path = tmp_path / "population.json"
    path.write_text("{not json", encoding="utf-8")
    code = cli.main(
        [str(path), "--directory", str(tmp_path / "run"), "--species", "FD", "--tree-age", "60"]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "is not JSON" in capsys.readouterr().err


def test_a_population_that_is_not_a_list_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The file holds records, not one object and not a scalar."""
    path = tmp_path / "population.json"
    path.write_text(json.dumps({"stand_id": "S1"}), encoding="utf-8")
    code = cli.main(
        [str(path), "--directory", str(tmp_path / "run"), "--species", "FD", "--tree-age", "60"]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "must hold a list" in capsys.readouterr().err


def test_an_empty_population_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A run with no trees is not a case, so it is refused rather than run."""
    path = tmp_path / "population.json"
    path.write_text("[]", encoding="utf-8")
    code = cli.main(
        [str(path), "--directory", str(tmp_path / "run"), "--species", "FD", "--tree-age", "60"]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "holds no stem records" in capsys.readouterr().err


def test_a_record_that_is_not_an_object_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A list of numbers is not a population."""
    path = tmp_path / "population.json"
    path.write_text(json.dumps([1, 2]), encoding="utf-8")
    code = cli.main(
        [str(path), "--directory", str(tmp_path / "run"), "--species", "FD", "--tree-age", "60"]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "record 0 is not an object" in capsys.readouterr().err


def test_an_unknown_keyword_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The table is the command's table too, so a typo is refused before a run."""
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--keyword",
            "NOTAKEYWORD",
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "is not a keyword" in capsys.readouterr().err


def test_a_keyword_that_carries_the_handoff_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The command invents no rule: the orchestration's refusal is the one that answers."""
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--keyword",
            "TREEDATA",
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "which the run writes itself" in capsys.readouterr().err


def test_a_species_that_does_not_resolve_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A species code BC does not know is input, and the adapter says so."""
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "ZZZ",
            "--tree-age",
            "60",
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "ZZZ" in capsys.readouterr().err


def test_an_empty_keyword_name_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--keyword =x`` names nothing, which is input the command cannot use."""
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--keyword",
            "=x",
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "--keyword needs a name" in capsys.readouterr().err


def test_a_missing_required_argument_is_a_usage_error(tmp_path: Path) -> None:
    """``argparse`` exits 2, which is the code this command gives bad input."""
    with pytest.raises(SystemExit) as raised:
        cli.main([str(tmp_path / "population.json")])
    assert raised.value.code == 2


def test_a_keyword_without_fields_has_none() -> None:
    """A valueless keyword is written without a separator, and parses to no fields."""
    assert cli._parse_keyword("ECHOSUM") == Keyword("ECHOSUM")


def test_a_keyword_keeps_its_blank_fields() -> None:
    """A blank field is a field, which is why FVS's own files write ``TIMEINT`` with one."""
    assert cli._parse_keyword("TIMEINT=,5") == Keyword("TIMEINT", ("", "5"))


def test_the_command_passes_the_callers_keywords_through(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The command adds no keyword and reorders none; the orchestration does the inserting."""
    captured: list[Sequence[Keyword]] = []

    def stub(
        population: Sequence[dict[str, object]],
        *,
        directory: str | Path,
        species: str | None = None,
        tree_age: float | None = None,
        keywords: Sequence[Keyword] = (),
        variant: str = "bc",
        plot_fields: object = None,
        key_name: str = KEYWORD_FILE_NAME,
    ) -> run.RunResult:
        captured.append(keywords)
        raise run.RunError("stub")

    monkeypatch.setattr(cli, "run_population", stub)
    cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--keyword",
            "STDINFO=712,CHS131",
            "--keyword",
            "PROCESS",
        ]
    )
    assert list(captured[0]) == [Keyword("STDINFO", ("712", "CHS131")), Keyword("PROCESS")]


def test_a_block_argument_parses_its_lines() -> None:
    """Each ``|`` starts a line, and the fields are empty when there is no ``=``."""
    keyword = cli._parse_block("DATABASE|DSNOut|FVSOut.db|ComputDB")
    assert keyword.name == "DATABASE"
    assert keyword.parameters == ()
    assert keyword.lines == ("DSNOut", "FVSOut.db", "ComputDB")


def test_a_block_argument_parses_fields_and_lines() -> None:
    """The fields come before the first ``|``, and the expression survives whole."""
    keyword = cli._parse_block("COMPUTE=0|BigVol = spmcdbh(3,0,0, 20.0, 999.0, 0,999,0)")
    assert keyword.parameters == ("0",)
    assert keyword.lines == ("BigVol = spmcdbh(3,0,0, 20.0, 999.0, 0,999,0)",)


def test_a_block_for_a_keyword_that_takes_no_lines_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A block under a keyword that takes none would be swallowed, so it is refused."""
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--block",
            "ECHOSUM|x",
        ]
    )
    assert code == cli.EXIT_BAD_INPUT
    assert "does not take a block of lines" in capsys.readouterr().err


def test_the_two_options_keep_their_relative_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A ``DATABASE`` block must precede the stand, so the order across both options matters."""
    captured: list[Sequence[Keyword]] = []

    def stub(
        population: Sequence[dict[str, object]],
        *,
        directory: str | Path,
        species: str | None = None,
        tree_age: float | None = None,
        keywords: Sequence[Keyword] = (),
        variant: str = "bc",
        plot_fields: object = None,
        key_name: str = KEYWORD_FILE_NAME,
    ) -> run.RunResult:
        captured.append(keywords)
        raise run.RunError("stub")

    monkeypatch.setattr(cli, "run_population", stub)
    cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--block",
            "DATABASE|DSNOut|FVSOut.db|ComputDB",
            "--keyword",
            "STDIDENT=x",
        ]
    )
    assert [keyword.name for keyword in captured[0]] == ["DATABASE", "STDIDENT"]


def test_a_run_through_the_command_writes_a_compute_table(tmp_path: Path) -> None:
    """The gap `0.3.0` shipped with: the command could not ask for a block.

    So the table was never written, and the clean-checkout verification found it.
    """
    pytest.importorskip(
        "pyfvs", reason="the BC extension is not built in this environment; ADR 0004 is the recipe"
    )
    code = cli.main(
        [
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
            "--block",
            "DATABASE|DSNOut|FVSOut.db|Summary|ComputDB",
            "--keyword",
            "STDIDENT=CLI   block",
            "--keyword",
            "STDINFO=712,CHS131,0,200,35,16",
            "--keyword",
            "MANAGED=0,1",
            "--keyword",
            "SITECODE=FD,100",
            "--keyword",
            "INVYEAR=0",
            "--keyword",
            "DESIGN=0,1,999,1,0,1,1",
            "--keyword",
            "NUMCYCLE=2",
            "--keyword",
            "RANNSEED=1",
            "--block",
            "COMPUTE=0|BigVol = spmcdbh(3,0,0, 20.0, 999.0, 0,999,0)",
            "--keyword",
            "ECHOSUM",
            "--keyword",
            "PROCESS",
            "--keyword",
            "STOP",
        ]
    )
    assert code == cli.EXIT_OK
    compute = read_table(tmp_path / "run" / "FVSOut.db", "FVS_Compute")
    assert not compute.empty
    assert "BIGVOL" in list(compute.columns)


def test_the_documented_entry_point_reports_bad_input_with_exit_two(tmp_path: Path) -> None:
    """``python -m fresh_fvsbc`` is what the README says, so it is what the test runs."""
    finished = subprocess.run(
        [
            sys.executable,
            "-m",
            "fresh_fvsbc",
            str(tmp_path / "absent.json"),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    assert finished.returncode == cli.EXIT_BAD_INPUT
    assert "No such file" in finished.stderr


def test_the_documented_entry_point_exits_one_without_the_extension(tmp_path: Path) -> None:
    """A run that cannot start is a failed run, and the command says which."""
    if importlib.util.find_spec("pyfvs") is not None:
        pytest.skip("the extension is present here, so its absence cannot be shown")
    finished = subprocess.run(
        [
            sys.executable,
            "-m",
            "fresh_fvsbc",
            str(a_population_file(tmp_path / "population.json")),
            "--directory",
            str(tmp_path / "run"),
            "--species",
            "FD",
            "--tree-age",
            "60",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    assert finished.returncode == cli.EXIT_FAILED_RUN
    assert "the run failed" in finished.stderr
    assert "pyfvs is not importable" in finished.stderr
