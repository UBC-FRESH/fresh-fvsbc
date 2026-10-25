"""Tests for the run orchestration.

Most of these run without the built extension, because the seam that drives the projection is one
private function and the rest of the orchestration is file handling, validation, and reading. A fake
drive writes the database the real one would write, so the error paths are exercised rather than
hoped for. The one end-to-end test needs the extension and skips without it.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

import pandas as pd
import pytest

from fresh_fvsbc import run
from fresh_fvsbc.keywords import (
    Keyword,
    KeywordSet,
    UnknownKeywordError,
    keyword_set_hash,
)
from fresh_fvsbc.nemora import MissingAssignmentError, to_tree_list
from fresh_fvsbc.outputs import MissingOutputError, RunFailedError
from fresh_fvsbc.provenance import Provenance
from fresh_fvsbc.treelist import BC_TREFMT, TreeListFields, write_tree_record
from nemora_fixtures import synthetic_population

WARNING = (
    "FVS03 WARNING:  FOREST CODE INDICATES THE GEOGRAPHIC LOCATION IS OUTSIDE THE RANGE OF THE "
    "MODEL.  DEFAULT CODE IS USED."
)
ERROR = "FVS16 ERROR:  KEYWORD ENTERED IS USED IN WRONG CONTEXT AND WAS IGNORED.  RECORDS READ= 19"


def a_tree() -> TreeListFields:
    """Build one valid tree record."""
    return {
        "plot_id": 1,
        "tree_num": 1,
        "tree_count": 1.0,
        "tree_history": 0,
        "species": "FD",
        "diam": 20.0,
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
        "tree_val": 1,
        "tree_rx": 1,
        "plot_slope": 0,
        "plot_aspect": 0,
        "plot_habitat": 0,
        "plot_topo_pos": 0,
        "plot_site_prep": 0,
        "tree_age": 60.0,
    }


def a_set(*names: str) -> tuple[Keyword, ...]:
    """Build a keyword set from names, in order, with no parameters."""
    return tuple(Keyword(name) for name in names)


def a_database(path: Path, *, cases: int = 1, messages: tuple[str, ...] = ()) -> Path:
    """Build a database shaped like a run's output, and return its path."""
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "create table FVS_Cases (CaseID text, StandID text, Variant text, RunDateTime text)"
        )
        for index in range(cases):
            connection.execute(
                "insert into FVS_Cases values (?, ?, ?, ?)",
                (f"case-{index}", "SYNTHETIC", "BC", "10/24/2026 12:00:00"),
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


def a_result(directory: Path) -> run.RunResult:
    """Build a result, for the tests that check a call is forwarded rather than a run is made."""
    frame = pd.DataFrame({"CaseID": ["case-0"]})
    return run.RunResult(
        provenance=Provenance(
            variant="bc",
            keyword_set_hash="sha256:0",
            treelist_hash="sha256:0",
            case_id="case-0",
            run_datetime="10/24/2026 12:00:00",
        ),
        cases=frame,
        warnings=frame.iloc[0:0],
        summary=frame,
        directory=directory,
        keyword_file=directory / run.KEYWORD_FILE_NAME,
        database=run.database_path(directory),
    )


def a_fake_drive(
    *, messages: tuple[str, ...] = (), cases: int = 1, database: bool = True
) -> Callable[..., run._Drive]:
    """Return a drive that writes the database a real run would write, in the run directory."""

    def drive(key_name: str, *, variant: str, directory: Path) -> run._Drive:
        assert (directory / key_name).is_file()
        assert (directory / Path(key_name).with_suffix(".tre")).is_file()
        if database:
            a_database(directory / run.DATABASE_NAME, cases=cases, messages=messages)
        return run._Drive(summary=pd.DataFrame({"Year": [0, 10]}), variants=("BC",))

    return drive


def test_the_tree_file_is_lowercase_and_shares_the_keyword_files_base() -> None:
    """PyFVS checks for ``.tre`` and refuses to start without it, so the case is not a choice."""
    assert run.tree_file_name("run.key") == Path("run.tre")
    assert run.tree_file_name("stand.KEY") == Path("stand.tre")
    assert run.tree_file_name(Path("a") / "b.key") == Path("a") / "b.tre"


def test_the_database_is_the_fixed_name_the_fortran_declares() -> None:
    """``dbsblkd.f`` has ``DATA DSNOUT/"FVSOut.db"``, so no caller can choose the name."""
    assert run.database_path("somewhere") == Path("somewhere") / "FVSOut.db"
    assert run.DATABASE_NAME == "FVSOut.db"


def test_the_format_splits_into_two_lines_that_rebuild_it() -> None:
    """``TREEFMT`` takes its format from the two lines after it, so the split must be lossless."""
    first, second = run.TREEFMT_LINES
    assert first + second == BC_TREFMT
    assert len(first) <= 80
    assert len(second) <= 80
    assert first
    assert second


def test_a_format_without_the_split_point_is_refused() -> None:
    """A format that cannot be split cannot be handed over, and guessing would misread it."""
    with pytest.raises(run.RunError, match="has no '2I3,' to split at"):
        run.treelist_format_lines("(I4,F6.0)")


def test_the_handoff_goes_before_the_first_projection_keyword() -> None:
    """FVS starts the projection at ``PROCESS``, so the trees must be read before it."""
    given = a_set("STDIDENT", "STDINFO", "NUMCYCLE", "PROCESS", "STOP")
    names = [keyword.name for keyword in run.with_tree_handoff(given)]
    assert names == ["STDIDENT", "STDINFO", "NUMCYCLE", "TREEFMT", "TREEDATA", "PROCESS", "STOP"]


def test_the_handoff_goes_before_stop_when_there_is_no_process() -> None:
    """``STOP`` ends the run, so a handoff after it would never be read."""
    names = [keyword.name for keyword in run.with_tree_handoff(a_set("STDINFO", "STOP"))]
    assert names == ["STDINFO", "TREEFMT", "TREEDATA", "STOP"]


def test_the_handoff_ends_the_set_when_it_holds_no_projection_keyword() -> None:
    """A set with no ``PROCESS`` or ``STOP`` still gets the trees, at its end."""
    names = [keyword.name for keyword in run.with_tree_handoff(a_set("STDINFO", "NUMCYCLE"))]
    assert names == ["STDINFO", "NUMCYCLE", "TREEFMT", "TREEDATA"]


def test_the_handoff_keeps_the_callers_order() -> None:
    """The set is the caller's, in the caller's order; the handoff is inserted, not sorted."""
    given = a_set("STDIDENT", "SITECODE", "INVYEAR", "PROCESS")
    result = run.with_tree_handoff(given)
    kept = [keyword for keyword in result if keyword.name not in {"TREEFMT", "TREEDATA"}]
    assert kept == list(given)


@pytest.mark.parametrize("carried", ["TREEFMT", "TREEDATA"])
def test_a_set_that_carries_a_handoff_keyword_is_refused(carried: str) -> None:
    """Overriding what the caller wrote is what the keyword contract forbids."""
    with pytest.raises(run.KeywordConflictError, match=f"carries {carried}, which the run writes"):
        run.with_tree_handoff(a_set("STDINFO", carried))


def test_the_handoff_renders_the_format_as_the_two_lines_fvs_reads() -> None:
    """The rendering is what FVS reads, so its shape is the contract, not an internal choice."""
    rendered = KeywordSet(run.with_tree_handoff(a_set("STDINFO", "PROCESS"))).render()
    first, second = run.TREEFMT_LINES
    assert f"TREEFMT\n{first}\n{second}\nTREEDATA\n" in rendered


def test_the_keyword_hash_covers_the_handoff() -> None:
    """A hash of the caller's set would identify a set no run ever saw."""
    given = a_set("STDINFO", "PROCESS")
    handoff = run.with_tree_handoff(given)
    assert KeywordSet(handoff).digest != KeywordSet(given).digest
    assert KeywordSet(handoff).digest == keyword_set_hash(handoff)


def test_an_unknown_keyword_is_refused_before_anything_is_written(tmp_path: Path) -> None:
    """Validation comes before the disk, so a bad set leaves nothing behind."""
    target = tmp_path / "run"
    with pytest.raises(UnknownKeywordError, match="is not a keyword"):
        run.run_case([a_tree()], a_set("STDINFO", "NOTAKEYWORD"), directory=target)
    assert not target.exists()


def test_the_run_writes_the_inputs_the_record_and_the_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One call writes the keyword file, the tree list, the record, and returns the tables."""
    monkeypatch.setattr(run, "_drive", a_fake_drive(messages=(WARNING,)))
    given = (
        Keyword("STDINFO"),
        Keyword("RANNSEED", ("1",)),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run.run_case([a_tree()], given, directory=tmp_path / "run")

    assert result.keyword_file.read_text().startswith("STDINFO\n")
    assert result.keyword_file.read_text().count("TREEFMT") == 1
    tree_file = run.tree_file_name(result.keyword_file)
    assert tree_file.read_text() == write_tree_record(a_tree()) + "\n-999\n"
    assert result.database == result.directory / "FVSOut.db"

    record = json.loads((result.directory / "provenance.json").read_text())
    assert record["case_id"] == "case-0"
    assert record["variant"] == "bc"
    assert record["variant_list"] == ["BC"]
    assert record["keyword_set_hash"] == KeywordSet(run.with_tree_handoff(given)).digest
    assert result.provenance.treelist_hash == result.provenance.as_record()["treelist_hash"]

    assert len(result.cases) == 1
    assert result.warnings["Message"].tolist() == [WARNING]
    assert result.summary["Year"].tolist() == [0, 10]


def test_the_callers_working_directory_is_never_changed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The run's directory belongs to the child, so the caller's is never touched (ADR 0010)."""
    monkeypatch.setattr(run, "_drive", a_fake_drive())
    before = Path.cwd()
    run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")
    assert Path.cwd() == before


def test_a_failed_drive_leaves_the_callers_directory_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A drive that raises must not leave the process anywhere but where it started."""

    def explode(key_name: str, *, variant: str, directory: Path) -> run._Drive:
        raise run.RunError("the projection ended with return code 1")

    monkeypatch.setattr(run, "_drive", explode)
    before = Path.cwd()
    with pytest.raises(run.RunError, match="return code 1"):
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")
    assert Path.cwd() == before


def test_a_run_drives_in_a_child_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """FVS keeps its state in the process, so a run is a process of its own (ADR 0010)."""
    captured: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        captured.append(command)
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="the child said no")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(run.RunError, match="child process") as raised:
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")
    assert captured[0][1:3] == ["-m", "fresh_fvsbc._child"]
    assert "the child said no" in str(raised.value)


def test_a_child_that_writes_nothing_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A child that exits cleanly without its files is a failure, not an empty result."""

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(run.RunError, match="wrote no"):
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")


def test_a_child_that_reports_no_extension_keeps_the_error_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The child's exit code maps back to the type a caller catches, not to a generic failure."""

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command, run.EXTENSION_UNAVAILABLE_CODE, stdout="", stderr="pyfvs is not importable"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(run.ExtensionUnavailableError, match="pyfvs is not importable"):
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")


def test_a_run_with_an_error_row_raises_and_writes_no_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed run is a failure, not a result that happens to hold an error."""
    monkeypatch.setattr(run, "_drive", a_fake_drive(messages=(WARNING, ERROR)))
    with pytest.raises(RunFailedError, match="the run reported 1 error"):
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")
    assert not (tmp_path / "run" / "provenance.json").exists()


def test_a_run_that_writes_no_database_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Output contract rule 1: a run that cannot produce a database is a reported failure."""
    monkeypatch.setattr(run, "_drive", a_fake_drive(database=False))
    with pytest.raises(MissingOutputError, match="wrote no database"):
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")


def test_a_run_with_no_case_cannot_record_its_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Provenance is mandatory, so a database with no case is not a run that can be recorded."""
    monkeypatch.setattr(run, "_drive", a_fake_drive(cases=0))
    with pytest.raises(run.RunError, match="no FVS_Cases row"):
        run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")


def test_the_seed_is_recorded_from_the_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A record that says no seed was used, when one was, is a false record."""
    monkeypatch.setattr(run, "_drive", a_fake_drive())
    result = run.run_case(
        [a_tree()],
        (Keyword("STDINFO"), Keyword("RANNSEED", ("7",))),
        directory=tmp_path / "run",
    )
    assert result.provenance.random_seed == 7


def test_a_set_without_a_seed_records_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A deterministic run that used no seed says so, rather than inventing one."""
    monkeypatch.setattr(run, "_drive", a_fake_drive())
    result = run.run_case([a_tree()], a_set("STDINFO"), directory=tmp_path / "run")
    assert result.provenance.random_seed is None


def test_a_seed_that_is_not_a_whole_number_is_refused() -> None:
    """FVS reads ``RANNSEED`` as an integer, so a record of anything else would be a guess."""
    with pytest.raises(run.RunError, match="RANNSEED is not a whole number"):
        run._seed_of((Keyword("RANNSEED", ("abc",)),))


def test_a_seed_with_more_than_one_parameter_is_refused() -> None:
    """Two parameters mean the set is not the one this module knows how to record."""
    with pytest.raises(run.RunError, match="RANNSEED takes one parameter"):
        run._seed_of((Keyword("RANNSEED", ("1", "2")),))


def test_the_extension_being_absent_is_reported_rather_than_crashing(tmp_path: Path) -> None:
    """The build is not in every environment, so its absence is a named failure."""
    if importlib.util.find_spec("pyfvs") is not None:
        pytest.skip("the extension is present here, so its absence cannot be shown")
    with pytest.raises(run.ExtensionUnavailableError, match="pyfvs is not importable"):
        run._drive("run.key", variant="bc", directory=tmp_path)


def test_run_population_adapts_the_population_before_running(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The convenience is the adapter then the run, and it must pass the adapted records on."""
    captured: list[Sequence[TreeListFields]] = []

    def stub(
        records: Sequence[TreeListFields],
        keywords: Sequence[Keyword],
        *,
        directory: str | Path,
        variant: str = "bc",
        key_name: str = run.KEYWORD_FILE_NAME,
    ) -> run.RunResult:
        captured.append(records)
        return a_result(Path(directory))

    monkeypatch.setattr(run, "run_case", stub)
    population = synthetic_population()
    run.run_population(population, species="FD", tree_age=60.0, directory=tmp_path / "run")
    assert list(captured[0]) == to_tree_list(population, species="FD", tree_age=60.0)


def test_run_population_refuses_a_population_without_species(tmp_path: Path) -> None:
    """The adapter's refusal is the run's refusal, because the run does not add a default."""
    with pytest.raises(MissingAssignmentError, match="needs a species"):
        run.run_population(synthetic_population(), tree_age=60.0, directory=tmp_path / "run")


def test_a_compute_block_reaches_fvs(tmp_path: Path) -> None:
    """A ``COMPUTE`` block is written as a block, and FVS's own report shows it read one.

    ``FVS_Compute`` is still not written through this route, because that needs a ``DATABASE``
    block asking for ``ComputDB`` and PyFVS occupies that block. What this checks is the keyword
    layer: the block reaches FVS, which echoes it as ``DEFINE THE FOLLOWING``.
    """
    pytest.importorskip(
        "pyfvs", reason="the BC extension is not built in this environment; ADR 0004 is the recipe"
    )
    expression = "BigVol = spmcdbh(3,0,0, 20.0, 999.0, 0,999,0)"
    keywords = (
        Keyword("STDIDENT", ("BLOCK   compute",)),
        Keyword("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "100")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("NUMCYCLE", ("2",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("COMPUTE", ("0",), (expression,)),
        Keyword("ECHOSUM"),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run.run_population(
        synthetic_population(), species="FD", tree_age=60.0, keywords=keywords, directory=tmp_path
    )
    report = (result.directory / "run.out").read_text(encoding="latin-1")
    assert "DEFINE THE FOLLOWING" in report
    assert expression in report


def test_a_synthetic_stand_runs_end_to_end(tmp_path: Path) -> None:
    """One call runs a synthetic stand and returns its tables with provenance.

    This needs the built extension. It skips without it rather than failing, because the suite must
    not depend on a Fortran compiler, and the skip names why.
    """
    pytest.importorskip(
        "pyfvs",
        reason="the BC extension is not built in this environment; ADR 0004 is the recipe",
    )
    population = synthetic_population()
    keywords = (
        Keyword("STDIDENT", ("SYNTHETIC   P3.5 end to end",)),
        Keyword("STDINFO", ("712", "CHS131", "0", "200", "35", "16")),
        Keyword("MANAGED", ("0", "1")),
        Keyword("SITECODE", ("FD", "100")),
        Keyword("INVYEAR", ("0",)),
        Keyword("DESIGN", ("0", "1", "999", "1", "0", "1", "1")),
        Keyword("NUMCYCLE", ("4",)),
        Keyword("RANNSEED", ("1",)),
        Keyword("ECHOSUM"),
        Keyword("PROCESS"),
        Keyword("STOP"),
    )
    result = run.run_population(
        population, species="FD", tree_age=60.0, keywords=keywords, directory=tmp_path / "run"
    )

    assert len(result.cases) == 1
    assert result.provenance.case_id
    assert result.provenance.random_seed == 1
    assert result.provenance.variant_list == ("BC",)
    assert not result.summary.empty
    assert result.warnings["Message"].map(lambda text: "ERROR" in str(text)).sum() == 0
    assert (result.directory / "provenance.json").is_file()
