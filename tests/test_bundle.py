"""Tests for the calibration bundle contract.

The fixture is a small, valid bundle with one stand-level and one species-level
parameter. The tests check the pins, the domain, the bounds, the review record,
and the rendering. The pilot file is loaded too, because it is the example a
reader will copy.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path

# The fixture is intentionally JSON-shaped and mutated by each test, so its
# nested values are Any rather than a typed record.
from typing import Any

import pytest

from fresh_fvsbc import __version__
from fresh_fvsbc.bec import BecCode
from fresh_fvsbc.bundle import (
    BundleBoundsError,
    BundleDomainError,
    BundleError,
    CalibrationBundle,
    load_bundle,
)
from fresh_fvsbc.keywords import KeywordSet
from fresh_fvsbc.provenance import FVS_SOURCE_COMMIT, PYFVS_COMMIT

ROOT: Path = Path(__file__).resolve().parents[1]
PILOT: Path = ROOT / "notes" / "reference" / "calibration" / "pilot-bundle.json"
KC_PILOT: Path = ROOT / "notes" / "reference" / "calibration" / "kc-pilot-bundle.json"


def _record() -> dict[str, Any]:
    """Return a valid bundle record."""
    return {
        "bundle_id": "test-bundle",
        "version": "0.1.0",
        "pins": {
            "pyfvs_commit": PYFVS_COMMIT,
            "fvs_source_commit": FVS_SOURCE_COMMIT,
            "variant": "bc",
        },
        "domain": {
            "regions": ["CAR"],
            "becs": ["IDFdk3"],
            "species_groups": ["FD", "PL"],
            "dbh_classes": [[0, 10], [10, 25], [25, 40], [40, 999]],
            "management": ["untreated"],
        },
        "parameters": [
            {
                "keyword": "BAMAX",
                "fields": ["53"],
                "units": "m2/ha",
                "value_index": 0,
                "bounds": {"min": 25.0, "max": 89.0},
            },
            {
                "keyword": "MORTMULT",
                "fields": ["1", "FD", "1.8000", "0", "999"],
                "units": "multiplier",
                "value_index": 2,
                "bounds": {"min": 0.25, "max": 4.0},
            },
        ],
        "training": {
            "data_checksum": "sha256:" + "a" * 64,
            "split": "test",
            "objective": "test",
            "convergence": {"iterations": 1},
        },
        "review": {"reviewer": "test", "date": "2026-11-02", "signed_off": True},
        "claim": "test bundle only",
    }


def _write(tmp_path: Path, record: dict[str, Any]) -> Path:
    """Write a bundle and return its path."""
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(record))
    return path


def test_a_valid_bundle_loads_and_renders(tmp_path: Path) -> None:
    """The two parameters become two keywords, and the set validates."""
    bundle = load_bundle(_write(tmp_path, _record()))
    rendered = bundle.render()
    assert [keyword.name for keyword in rendered] == ["BAMAX", "MORTMULT"]
    assert rendered[0].parameters == ("53",)
    assert KeywordSet(rendered).render().startswith("BAMAX")
    assert bundle.record() == {"calibration_id": "test-bundle", "calibration_version": "0.1.0"}
    assert bundle.warnings == ()


def test_an_ingrowth_only_bundle_has_an_empty_parameter_list(tmp_path: Path) -> None:
    """CWH and other domain models can carry rates without a capacity override."""
    record = _record()
    record["parameters"] = []
    bundle = load_bundle(_write(tmp_path, record))
    assert bundle.parameters == ()
    assert bundle.render() == ()


def test_the_cwh_pilot_bundle_loads_and_renders_all_parameters() -> None:
    """The CWH growth pilot is a real bundle, not a screening table."""
    bundle = load_bundle("notes/reference/calibration/d7-cwh-bundle.json")
    assert bundle.ingrowth is None
    assert bundle.domain.becs == ("CWH",)
    assert len(bundle.parameters) == 16
    assert len(bundle.render()) == 16
    assert any("not signed off" in warning for warning in bundle.warnings)


def test_the_bwbs_pilot_bundle_loads_and_renders_all_parameters() -> None:
    """The BWBS growth pilot is a real bundle, not a screening table."""
    bundle = load_bundle("notes/reference/calibration/d8-bwbs-bundle.json")
    assert bundle.ingrowth is None
    assert bundle.domain.becs == ("BWBS",)
    assert len(bundle.parameters) == 18
    assert len(bundle.render()) == 18
    assert any("not signed off" in warning for warning in bundle.warnings)


def test_the_review_manifest_matches_its_bundles_and_is_unsigned() -> None:
    """The review packet cannot drift from the bundle bytes it names."""
    manifest = json.loads(
        Path("notes/reference/calibration/d8-review-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["signed_off"] is False
    assert manifest["reviewer"] is None
    assert manifest["decision"] == "pending"
    assert len(manifest["bundles"]) == 3
    for item in manifest["bundles"]:
        data = Path(item["path"]).read_bytes()
        assert item["sha256"] == "sha256:" + hashlib.sha256(data).hexdigest()
        assert item["bytes"] == len(data)


def test_the_kc_pilot_bundle_loads_and_carries_its_two_warnings() -> None:
    """The KC bundle is unsigned and its PL multiplier sits at its bound."""
    bundle = load_bundle(KC_PILOT)
    assert bundle.bundle_id == "kc-pilot-v2c-2026-11-02"
    assert len(bundle.render()) == 9
    assert any("not signed off" in warning for warning in bundle.warnings)
    assert any("sits at a bound" in warning for warning in bundle.warnings)


def test_the_pilot_bundle_loads_and_is_unsigned(tmp_path: Path) -> None:
    """The shipped pilot is a contract example, so it loads and warns."""
    bundle = load_bundle(PILOT)
    assert bundle.bundle_id == "bc-pilot-2026-11-02"
    assert bundle.warnings
    assert "not signed off" in bundle.warnings[0]


def test_domain_accepts_a_run_inside_it(tmp_path: Path) -> None:
    """A CAR IDFdk3, FD/PL, untreated run is inside the fixture's domain."""
    bundle = load_bundle(_write(tmp_path, _record()))
    bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD", "PL"), "untreated", (20.0,))


def test_domain_refuses_the_wrong_bec(tmp_path: Path) -> None:
    """An SBS stand is outside an IDFdk3 bundle."""
    bundle = load_bundle(_write(tmp_path, _record()))
    with pytest.raises(BundleDomainError, match="IDFdk3"):
        bundle.check_domain(BecCode.parse("CAR SBSmc2/01"), ("FD",), "untreated", (20.0,))


def test_domain_refuses_the_wrong_species(tmp_path: Path) -> None:
    """A bundle that covers FD and PL does not cover HW."""
    bundle = load_bundle(_write(tmp_path, _record()))
    with pytest.raises(BundleDomainError, match="HW"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD", "HW"), "untreated", (20.0,))


def test_domain_refuses_a_dbh_outside_the_domain(tmp_path: Path) -> None:
    """A run with a tree outside the declared DBH classes is refused."""
    record = _record()
    record["domain"]["dbh_classes"] = [[0, 10], [10, 25]]
    bundle = load_bundle(_write(tmp_path, record))
    with pytest.raises(BundleDomainError, match="DBH"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (50.0,))


def test_domain_refuses_the_wrong_management(tmp_path: Path) -> None:
    """An untreated bundle is not a managed-run bundle."""
    bundle = load_bundle(_write(tmp_path, _record()))
    with pytest.raises(BundleDomainError, match="managed"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "managed", (20.0,))


def test_domain_enforces_qmd_min(tmp_path: Path) -> None:
    """A QMD boundary is enforced when the domain declares one."""
    record = _record()
    record["domain"]["qmd_min"] = 13.0
    bundle = load_bundle(_write(tmp_path, record))
    bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), 13.0)
    with pytest.raises(BundleDomainError, match="QMD"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), 12.0)
    with pytest.raises(BundleDomainError, match="needs the initial QMD"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,))


def test_domain_enforces_ba_min(tmp_path: Path) -> None:
    """A BA boundary is enforced when the domain declares one."""
    record = _record()
    record["domain"]["ba_min"] = 20.0
    bundle = load_bundle(_write(tmp_path, record))
    bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), ba=20.0)
    with pytest.raises(BundleDomainError, match="BA"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), ba=19.9)
    with pytest.raises(BundleDomainError, match="needs the initial BA"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,))


def test_domain_enforces_tsa(tmp_path: Path) -> None:
    """A TSA boundary is enforced when the domain declares one."""
    record = _record()
    record["domain"]["tsas"] = ["Quesnel TSA"]
    bundle = load_bundle(_write(tmp_path, record))
    bundle.check_domain(
        BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), tsa="Quesnel TSA"
    )
    with pytest.raises(BundleDomainError, match="TSAs"):
        bundle.check_domain(
            BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), tsa="100 Mile House TSA"
        )
    with pytest.raises(BundleDomainError, match="needs the TSA"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,))


def test_domain_rejects_non_finite_stand_values(tmp_path: Path) -> None:
    """A NaN or infinite stand value cannot satisfy a boundary."""
    record = _record()
    record["domain"]["qmd_min"] = 13.0
    record["domain"]["ba_min"] = 20.0
    bundle = load_bundle(_write(tmp_path, record))
    with pytest.raises(BundleDomainError, match="finite initial QMD"):
        bundle.check_domain(
            BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), qmd=float("nan"), ba=25.0
        )
    with pytest.raises(BundleDomainError, match="finite initial BA"):
        bundle.check_domain(
            BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,), qmd=20.0, ba=float("inf")
        )


def test_a_wrapper_pin_must_match(tmp_path: Path) -> None:
    """A bundle that names a wrapper version is valid only for that version."""
    record = _record()
    record["pins"]["wrapper_version"] = __version__
    bundle = load_bundle(_write(tmp_path, record))
    assert bundle.pins["wrapper_version"] == __version__
    record["pins"]["wrapper_version"] = "0.0.0"
    with pytest.raises(BundleError, match="wrapper's version"):
        load_bundle(_write(tmp_path, record))


def test_a_wrong_pin_is_refused(tmp_path: Path) -> None:
    """A bundle is valid only for the build it names."""
    record = _record()
    record["pins"]["pyfvs_commit"] = "0000000"
    with pytest.raises(BundleError, match="not the package's pin"):
        load_bundle(_write(tmp_path, record))


def test_a_missing_field_is_refused(tmp_path: Path) -> None:
    """The required fields are named, not guessed."""
    record = _record()
    del record["claim"]
    with pytest.raises(BundleError, match="claim"):
        load_bundle(_write(tmp_path, record))


def test_a_bad_checksum_is_refused(tmp_path: Path) -> None:
    """A checksum that is not a SHA-256 cannot identify the training data."""
    record = _record()
    record["training"]["data_checksum"] = "not-a-checksum"
    with pytest.raises(BundleError, match="data_checksum"):
        load_bundle(_write(tmp_path, record))


def test_an_out_of_bounds_parameter_is_refused(tmp_path: Path) -> None:
    """A value outside the declared bounds is a refusal, not a warning."""
    record = _record()
    record["parameters"][0]["fields"] = ["10"]
    with pytest.raises(BundleBoundsError, match="outside"):
        load_bundle(_write(tmp_path, record))


def test_a_parameter_at_a_bound_warns(tmp_path: Path) -> None:
    """A bound is a warning because the parameter is not identified."""
    record = _record()
    record["parameters"][0]["fields"] = ["25"]
    bundle = load_bundle(_write(tmp_path, record))
    assert any("sits at a bound" in warning for warning in bundle.warnings)


def test_an_unknown_keyword_is_refused(tmp_path: Path) -> None:
    """A bundle cannot invent a calibration lever."""
    record = _record()
    record["parameters"][0]["keyword"] = "NOPE"
    with pytest.raises(BundleError, match="NOPE"):
        load_bundle(_write(tmp_path, record))


def test_a_value_index_past_the_fields_is_refused(tmp_path: Path) -> None:
    """The bounded field has to exist."""
    record = _record()
    record["parameters"][0]["value_index"] = 2
    with pytest.raises(BundleError, match="past its"):
        load_bundle(_write(tmp_path, record))


def test_a_bad_review_date_is_refused(tmp_path: Path) -> None:
    """The sign-off date is a date, not free text."""
    record = _record()
    record["review"]["date"] = "2 November 2026"
    with pytest.raises(BundleError, match="YYYY-MM-DD"):
        load_bundle(_write(tmp_path, record))


def test_a_bundle_can_be_built_directly_for_a_test() -> None:
    """The dataclass is usable without JSON, which keeps a unit test small."""
    from fresh_fvsbc.bundle import BundleDomain, BundleParameter

    parameter = BundleParameter("BAMAX", ("53",), "m2/ha", 0, (25.0, 89.0))
    bundle = CalibrationBundle(
        bundle_id="direct",
        version="0.1.0",
        pins={},
        domain=BundleDomain(),
        parameters=(parameter,),
        training={},
        review={},
        claim="test",
    )
    assert bundle.render()[0].name == "BAMAX"


def test_a_region_outside_the_domain_is_refused(tmp_path: Path) -> None:
    """The region is checked before the BEC."""
    record = _record()
    record["domain"]["regions"] = ["KAM"]
    bundle = load_bundle(_write(tmp_path, record))
    with pytest.raises(BundleDomainError, match="KAM"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated", (20.0,))


def test_an_empty_domain_is_unrestricted(tmp_path: Path) -> None:
    """An empty domain means the bundle does not narrow the run."""
    record = _record()
    record["domain"] = {}
    bundle = load_bundle(_write(tmp_path, record))
    bundle.check_domain(BecCode.parse("CAR SBSmc2/01"), ("HW",), "managed", (120.0,))


def test_domain_requires_dbh_values_when_it_names_classes(tmp_path: Path) -> None:
    """A DBH domain cannot be checked without the run's DBHs."""
    bundle = load_bundle(_write(tmp_path, _record()))
    with pytest.raises(BundleDomainError, match="did not provide DBHs"):
        bundle.check_domain(BecCode.parse("CAR IDFdk3/01"), ("FD",), "untreated")


def test_a_parameter_without_bounds_is_allowed(tmp_path: Path) -> None:
    """A keyword with no bound is rendered and not checked."""
    record = _record()
    del record["parameters"][0]["bounds"]
    bundle = load_bundle(_write(tmp_path, record))
    assert bundle.parameters[0].bounds is None


def test_a_missing_file_is_refused(tmp_path: Path) -> None:
    """A missing bundle is a BundleError, not a FileNotFoundError."""
    with pytest.raises(BundleError, match="cannot read"):
        load_bundle(tmp_path / "absent.json")


def test_a_file_that_is_not_json_is_refused(tmp_path: Path) -> None:
    """A malformed bundle names the JSON error."""
    path = tmp_path / "bundle.json"
    path.write_text("{not json")
    with pytest.raises(BundleError, match="is not JSON"):
        load_bundle(path)


def test_a_json_list_is_refused(tmp_path: Path) -> None:
    """The bundle is an object, not a list."""
    path = tmp_path / "bundle.json"
    path.write_text("[]")
    with pytest.raises(BundleError, match="JSON object"):
        load_bundle(path)


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda r: r.update(bundle_id="Bad ID"), "bundle_id"),
        (lambda r: r.update(version="1"), "semantic version"),
        (lambda r: r["pins"].update(variant="pn"), "variant"),
        (lambda r: r.update(claim=1), "claim"),
        (lambda r: r.update(pins=[]), "pins"),
        (lambda r: r["domain"].update(regions=["XXX"]), "unknown values"),
        (lambda r: r["domain"].update(species_groups=["ZZ"]), "unknown values"),
        (lambda r: r["domain"].update(management=["fire"]), "unknown values"),
        (lambda r: r["domain"].update(dbh_classes={}), "dbh_classes"),
        (lambda r: r["domain"].update(dbh_classes=[[0]]), "min, max"),
        (lambda r: r["domain"].update(dbh_classes=[[10, 0]]), "min must be below max"),
        (lambda r: r["domain"].update(qmd_min="13"), "qmd_min"),
        (lambda r: r["domain"].update(qmd_min=float("nan")), "finite"),
        (lambda r: r["domain"].update(qmd_min=float("inf")), "finite"),
        (lambda r: r["domain"].update(qmd_min=True), "qmd_min"),
        (lambda r: r["domain"].update(ba_min="20"), "ba_min"),
        (lambda r: r["domain"].update(ba_min=-1), "ba_min"),
        (lambda r: r["domain"].update(ba_min=float("nan")), "finite"),
        (lambda r: r["domain"].update(ba_min=float("inf")), "finite"),
        (lambda r: r["domain"].update(ba_min=True), "ba_min"),
        (lambda r: r["domain"].update(tsas="Quesnel TSA"), "tsas"),
        (lambda r: r.update(parameters={}), "must be a list"),
        (lambda r: r.update(parameters=[1]), "must be an object"),
        (lambda r: r["parameters"][0].update(fields="53"), "list of strings"),
        (lambda r: r["parameters"][0].update(value_index=-1), "non-negative"),
        (lambda r: r["parameters"][0].update(bounds=1), "bounds must be an object"),
        (lambda r: r["parameters"][0].update(bounds={"min": "a", "max": 2}), "numeric min and max"),
        (lambda r: r["parameters"][0].update(bounds={"min": 89, "max": 25}), "below max"),
        (
            lambda r: r["parameters"][0].update(fields=["12345678901"]),
            "not a valid keyword",
        ),
        (lambda r: r["parameters"][0].update(fields=["abc"]), "not numeric"),
        (lambda r: r["review"].update(signed_off="yes"), "true or false"),
        (lambda r: r.update(training=[]), "training"),
    ],
)
def test_an_invalid_bundle_is_refused(
    tmp_path: Path, mutate: Callable[[dict[str, Any]], None], match: str
) -> None:
    """Every malformed field is refused with a message that names it."""
    record = _record()
    mutate(record)
    with pytest.raises(BundleError, match=match):
        load_bundle(_write(tmp_path, record))
