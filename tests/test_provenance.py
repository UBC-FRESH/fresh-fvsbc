"""Tests for the provenance record.

They check the record's shape against the contract, the two hashes against what the contract says
they are *not*, and the two ``FVS_Cases`` columns against the row a real run produced.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from fresh_fvsbc import __version__
from fresh_fvsbc.keywords import Keyword, keyword_set_hash
from fresh_fvsbc.nemora import to_tree_list
from fresh_fvsbc.provenance import (
    FVS_SOURCE_COMMIT,
    PYFVS_COMMIT,
    BuildError,
    Provenance,
    ProvenanceError,
    built_variants,
    from_cases,
    treelist_hash,
)
from fresh_fvsbc.treelist import TreeListFields, write_tree_list
from nemora_fixtures import synthetic_population

# The contract's field list, transcribed in its order.
CONTRACT_FIELDS: tuple[str, ...] = (
    "fresh_fvsbc_version",
    "pyfvs_commit",
    "fvs_source_commit",
    "variant",
    "variant_list",
    "keyword_set_hash",
    "treelist_hash",
    "case_id",
    "run_datetime",
    "random_seed",
)

# What pyfvs.list_variants() returned in this project's build.
REAL_VARIANT_REPORT: dict[str, dict[str, str]] = {"BC": {"lib": "pyfvs.fvsbc", "status": "OK"}}

# One row of FVS_Cases, from the synthetic run of 2026-10-23.
REAL_CASE_ROW: dict[str, object] = {
    "CaseID": "95c84d73-a88b-486a-9930-7af04f29f003",
    "StandID": "SYNTHETIC",
    "Variant": "BC",
    "RunDateTime": "2026-10-23-07:47:38",
}

A_RECORD: TreeListFields = {
    "plot_id": 1,
    "tree_num": 1,
    "tree_count": 1.0,
    "tree_history": 0,
    "species": "PW",
    "diam": 21.4,
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
    "tree_age": 60.0,
}


def a_provenance() -> Provenance:
    """Return a complete record, built from a real run's case row."""
    case_id, run_datetime = from_cases(REAL_CASE_ROW)
    return Provenance(
        variant="bc",
        keyword_set_hash=keyword_set_hash([Keyword("TREEDATA"), Keyword("PROCESS")]),
        treelist_hash=treelist_hash([A_RECORD]),
        case_id=case_id,
        run_datetime=run_datetime,
        variant_list=built_variants(REAL_VARIANT_REPORT),
        random_seed=1,
    )


def test_the_record_carries_the_contracts_fields_in_order() -> None:
    """Every field the contract lists, in the order it lists them, and nothing else."""
    assert tuple(a_provenance().as_record()) == CONTRACT_FIELDS


def test_the_record_names_commits_and_not_versions_for_the_pinned_inputs() -> None:
    """Rule 2: a version can be republished, and a commit cannot."""
    for commit in (PYFVS_COMMIT, FVS_SOURCE_COMMIT):
        assert re.fullmatch(r"[0-9a-f]{7,40}", commit)
    assert a_provenance().pyfvs_commit == PYFVS_COMMIT
    assert a_provenance().fvs_source_commit == FVS_SOURCE_COMMIT
    assert __version__ != PYFVS_COMMIT


def test_the_version_defaults_to_this_packages_own() -> None:
    """The record says which wrapper ran, not only which FVS did."""
    assert a_provenance().fresh_fvsbc_version == __version__


def test_the_source_commit_is_the_one_the_notes_abbreviate() -> None:
    """The notes write ``ef5fa84``; the clone's commit is longer, and both name the same commit."""
    assert FVS_SOURCE_COMMIT.startswith("ef5fa84")


def test_the_record_carries_no_path_and_no_credential() -> None:
    """Rule 4: a record may be cited in a tracked file, so it holds neither."""
    text = a_provenance().to_json()
    assert "/" not in text
    assert "password" not in text.lower()
    assert "token" not in text.lower()


def test_the_hashes_are_named_with_their_algorithm() -> None:
    """A reader should not have to know which hash was used."""
    record = a_provenance().as_record()
    assert str(record["keyword_set_hash"]).startswith("sha256:")
    assert str(record["treelist_hash"]).startswith("sha256:")


def test_built_variants_takes_the_report_pyfvs_gives() -> None:
    """The contract's first unverified item is answered: PyFVS does expose the built list."""
    assert built_variants(REAL_VARIANT_REPORT) == ("BC",)


def test_built_variants_refuses_a_variant_that_did_not_import() -> None:
    """Rule 3: the list exists so that a mistaken build is visible, and this is that case."""
    report = dict(REAL_VARIANT_REPORT)
    report["PN"] = {"lib": "pyfvs.fvspn", "status": "Failed"}
    with pytest.raises(BuildError, match="reported PN as not OK"):
        built_variants(report)


def test_built_variants_sorts_so_two_records_of_a_build_read_alike() -> None:
    """A report built in another order describes the same build."""
    forward = {"BC": {"status": "OK"}, "PN": {"status": "OK"}}
    backward = {"PN": {"status": "OK"}, "BC": {"status": "OK"}}
    assert built_variants(forward) == built_variants(backward) == ("BC", "PN")


def test_from_cases_returns_the_two_columns_the_contract_names() -> None:
    """The run's identity comes from FVS_Cases rather than from the caller's bookkeeping."""
    assert from_cases(REAL_CASE_ROW) == (REAL_CASE_ROW["CaseID"], REAL_CASE_ROW["RunDateTime"])


def test_from_cases_refuses_a_row_without_them() -> None:
    """Rule 1: a run that cannot record its provenance is a failure."""
    with pytest.raises(ProvenanceError, match="did not carry CaseID, RunDateTime"):
        from_cases({"StandID": "SYNTHETIC"})


def test_the_treelist_hash_is_stable() -> None:
    """The same trees hash the same way, which is what makes the value comparable."""
    assert treelist_hash([A_RECORD]) == treelist_hash([A_RECORD])


def test_the_treelist_hash_moves_with_a_value() -> None:
    """A different tree is a different input."""
    other: TreeListFields = {**A_RECORD, "diam": 99.9}
    assert treelist_hash([A_RECORD]) != treelist_hash([other])


def test_the_treelist_hash_moves_with_the_order() -> None:
    """Order is part of what a run was given, so it is part of the identity."""
    second: TreeListFields = {**A_RECORD, "tree_num": 2}
    assert treelist_hash([A_RECORD, second]) != treelist_hash([second, A_RECORD])


def test_the_treelist_hash_does_not_depend_on_how_a_record_was_built() -> None:
    """The same values hash alike however the mapping was assembled, which a file hash would not."""
    as_plain: dict[str, object] = dict(A_RECORD)
    shuffled: dict[str, object] = {key: as_plain[key] for key in reversed(list(as_plain))}
    assert list(shuffled) != list(A_RECORD)
    assert treelist_hash([shuffled]) == treelist_hash([A_RECORD])


def test_the_treelist_hash_is_not_a_hash_of_the_written_text() -> None:
    """The contract asks for a canonical serialization rather than a file hash.

    This is that difference stated as a check: the written text is a different string, at a width
    the record does not fix, so hashing it gives a different value.
    """
    written = write_tree_list([A_RECORD])
    as_file = "sha256:" + hashlib.sha256(written.encode()).hexdigest()
    assert treelist_hash([A_RECORD]) != as_file


def test_the_json_round_trips() -> None:
    """What is written can be read back into the same record."""
    record = a_provenance()
    assert json.loads(record.to_json()) == record.as_record()


def test_the_record_is_written_beside_the_outputs(tmp_path: Path) -> None:
    """The contract puts it on disk beside a run's outputs, as JSON."""
    record = a_provenance()
    written = record.write(tmp_path / "provenance.json")
    assert written == tmp_path / "provenance.json"
    assert written.read_text() == record.to_json()


def test_a_record_for_the_whole_chain_from_the_fixture_to_the_database() -> None:
    """The modules compose: a population, a tree list, a hash of it, and a record carrying it."""
    records = to_tree_list(synthetic_population(), species="FD", tree_age=60.0)
    case_id, run_datetime = from_cases(REAL_CASE_ROW)
    record = Provenance(
        variant="bc",
        keyword_set_hash=keyword_set_hash([Keyword("TREEDATA"), Keyword("PROCESS")]),
        treelist_hash=treelist_hash(records),
        case_id=case_id,
        run_datetime=run_datetime,
        variant_list=built_variants(REAL_VARIANT_REPORT),
        random_seed=1,
    )
    as_record = record.as_record()
    assert as_record["variant_list"] == ["BC"]
    assert str(as_record["treelist_hash"]).startswith("sha256:")
    assert as_record["case_id"] == REAL_CASE_ROW["CaseID"]
    assert as_record["random_seed"] == 1
