"""Tests for the mutation harness.

The harness is a checker, so these tests check the checker. The load-bearing one is that a
mutation which does not apply is an error: a mutation that silently no-ops reports a passing test,
which is the defect `P2` produced twice.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import mutation_check
from mutation_check import MUTATIONS, Mutation, MutationError, check, control, main

PROTOTYPE_MODULES: tuple[str, ...] = (
    "src/fresh_fvsbc/treelist.py",
    "src/fresh_fvsbc/keywords.py",
    "src/fresh_fvsbc/nemora.py",
    "src/fresh_fvsbc/outputs.py",
    "src/fresh_fvsbc/provenance.py",
)


def a_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, find: str, replace: str
) -> Mutation:
    """Return a mutation over a temporary file, with the harness pointed at it."""
    source = tmp_path / "module.py"
    source.write_text("value = 1\nother = 2\n")
    monkeypatch.setattr(mutation_check, "ROOT", tmp_path)
    return Mutation(
        "test-mutation",
        "module.py",
        find,
        replace,
        "tests/test_provenance.py::test_the_json_round_trips",
    )


def test_the_registry_covers_every_prototype_module() -> None:
    """A module with no mutation has no evidence that its tests can fail."""
    covered = {mutation.module for mutation in MUTATIONS}
    assert set(PROTOTYPE_MODULES) <= covered


def test_every_registered_mutation_names_a_test_that_exists() -> None:
    """A mutation pointing at a missing node would fail for the wrong reason and look caught."""
    for mutation in MUTATIONS:
        file_part, _, node = mutation.test.partition("::")
        assert (mutation_check.ROOT / file_part).exists(), mutation.identifier
        assert node, mutation.identifier


def test_an_anchor_that_does_not_apply_is_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A mutation that does not apply proves nothing, so it must fail loudly."""
    mutation = a_mutation(tmp_path, monkeypatch, find="value = 999", replace="value = 3")
    with pytest.raises(MutationError, match="occurs 0 times"):
        mutation_check.apply(mutation)


def test_an_anchor_that_applies_twice_is_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A doubled anchor would mutate a place the test does not cover, or the wrong one."""
    (tmp_path / "module.py").write_text("value = 1\nvalue = 1\n")
    monkeypatch.setattr(mutation_check, "ROOT", tmp_path)
    mutation = Mutation("twice", "module.py", "value = 1", "value = 3", "x")
    with pytest.raises(MutationError, match="occurs 2 times"):
        mutation_check.apply(mutation)


def test_apply_then_restore_returns_the_file_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The restore is the harness's safety property: a mutation must never outlive its run."""
    mutation = a_mutation(tmp_path, monkeypatch, find="value = 1", replace="value = 3")
    original = mutation_check.apply(mutation)
    assert (tmp_path / "module.py").read_text() == "value = 3\nother = 2\n"
    mutation_check.restore(mutation, original)
    assert (tmp_path / "module.py").read_text() == original


def test_check_returns_true_when_the_test_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The harness's contract: a failing test under the mutation is a caught mutation."""
    mutation = a_mutation(tmp_path, monkeypatch, find="value = 1", replace="value = 3")
    monkeypatch.setattr(mutation_check, "_pytest", lambda node: False)
    assert check(mutation) is True


def test_check_returns_false_when_the_test_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A test that passes under the mutation caught nothing, and the harness must say so."""
    mutation = a_mutation(tmp_path, monkeypatch, find="value = 1", replace="value = 3")
    monkeypatch.setattr(mutation_check, "_pytest", lambda node: True)
    assert check(mutation) is False


def test_check_restores_the_file_even_when_the_test_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A harness that leaves a source mutated after a crash is worse than no harness."""
    mutation = a_mutation(tmp_path, monkeypatch, find="value = 1", replace="value = 3")

    def explode(node: str) -> bool:
        raise RuntimeError("the runner failed")

    monkeypatch.setattr(mutation_check, "_pytest", explode)
    with pytest.raises(RuntimeError):
        check(mutation)
    assert (tmp_path / "module.py").read_text() == "value = 1\nother = 2\n"


def test_control_reports_the_suites_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """The control is the baseline a mutation run is compared against."""
    monkeypatch.setattr(mutation_check, "_pytest", lambda node: True)
    assert control() is True
    monkeypatch.setattr(mutation_check, "_pytest", lambda node: False)
    assert control() is False


def test_list_prints_every_registered_mutation(capsys: pytest.CaptureFixture[str]) -> None:
    """The list is how a reader finds an identifier to run alone."""
    assert main(["--list"]) == 0
    printed = capsys.readouterr().out.splitlines()
    assert len(printed) == len(MUTATIONS)
    assert printed[0].split("\t")[0] == MUTATIONS[0].identifier


def test_control_exits_zero_when_the_suite_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    """A red control means the baseline is broken and every result is meaningless."""
    monkeypatch.setattr(mutation_check, "control", lambda: True)
    assert main(["--control"]) == 0
    monkeypatch.setattr(mutation_check, "control", lambda: False)
    assert main(["--control"]) == 1


def test_an_identifier_that_matches_nothing_exits_one(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A filter that selects nothing must not report success."""
    assert main(["--only", "no-such-mutation"]) == 1
    assert "no mutation matches" in capsys.readouterr().err


def test_a_missed_mutation_exits_one(monkeypatch: pytest.MonkeyPatch) -> None:
    """A mutation whose test passed is the finding, so the exit code must say so."""
    monkeypatch.setattr(mutation_check, "check", lambda mutation: False)
    assert main(["--only", "treelist"]) == 1


def test_an_unapplied_mutation_exits_one_and_is_reported(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The harness's own failure mode, surfaced rather than counted as a pass."""

    def broken(mutation: Mutation) -> bool:
        raise MutationError("the anchor occurs 0 times")

    monkeypatch.setattr(mutation_check, "check", broken)
    assert main(["--only", "treelist"]) == 1
    assert "ERROR" in capsys.readouterr().err


def test_every_mutation_is_caught_end_to_end() -> None:
    """One real run, so the registry is not merely well-formed.

    It runs the whole registry, which is a few seconds, and asserts every mutation was applied,
    caught, and restored. The per-mutation runs are what CI does; this is the proof that the
    registry works.
    """
    result = subprocess.run(
        [sys.executable, "scripts/mutation_check.py"],
        cwd=mutation_check.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"{len(MUTATIONS)} of {len(MUTATIONS)} mutations caught" in result.stdout
