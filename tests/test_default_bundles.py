"""The calibration bundles ship inside the package and load without the repository."""

from __future__ import annotations

from pathlib import Path

import pytest

from fresh_fvsbc.bundle import (
    DEFAULT_BUNDLES,
    BundleError,
    default_bundle_path,
    load_default_bundle,
)


def test_every_shipped_bundle_has_a_file() -> None:
    """Each registry name resolves to a file that exists in the installed package."""
    for name in DEFAULT_BUNDLES:
        path = default_bundle_path(name)
        assert path.is_file(), path
        assert path.parent.name == "data"


def test_every_shipped_bundle_loads() -> None:
    """Each shipped bundle validates against this build's pins."""
    ids = set()
    for name in DEFAULT_BUNDLES:
        bundle = load_default_bundle(name)
        assert bundle.bundle_id
        assert bundle.bundle_id not in ids, "two shipped bundles share an id"
        ids.add(bundle.bundle_id)
        assert bundle.domain.becs, f"{name} declares no BEC domain"


def test_the_zone_bundles_carry_parameters_and_recruitment_carries_rates() -> None:
    """A zone bundle renders keywords; recruitment carries an ingrowth model."""
    for name in DEFAULT_BUNDLES:
        bundle = load_default_bundle(name)
        assert bundle.claim, name
        if name == "recruitment-bc-v1":
            assert bundle.ingrowth is not None
            assert bundle.ingrowth.scale == pytest.approx(0.4)
            assert bundle.ingrowth.rates
        elif bundle.parameters:
            assert bundle.render(), name


def test_the_cdf_bundle_carries_the_dense_stand_mortality() -> None:
    """FD and AC keep MORTMULT 0.5; no other species does."""
    bundle = load_default_bundle("cdf-v3")
    morts = {
        parameter.fields[1]: parameter.fields[2]
        for parameter in bundle.parameters
        if parameter.keyword == "MORTMULT"
    }
    assert morts == {"FD": "0.5000", "AC": "0.5000"}


def test_the_sbs_bundle_carries_only_the_mortality_rows() -> None:
    """BL's growth is the W18 row; the bundle carries no BAIMULT for it."""
    bundle = load_default_bundle("sbs-v3")
    assert not any(p.keyword == "BAIMULT" for p in bundle.parameters)
    mort = {p.fields[1]: p.fields[2] for p in bundle.parameters if p.keyword == "MORTMULT"}
    assert mort == {"FD": "1.8500", "PL": "1.8500", "SE": "1.8500", "HW": "1.8500"}


def test_an_unknown_name_is_refused() -> None:
    """A caller cannot ask for a bundle that is not shipped."""
    with pytest.raises(BundleError, match="not a shipped bundle"):
        default_bundle_path("no-such-zone")


def test_the_data_files_match_the_calibration_record() -> None:
    """The shipped copies are the banked artifacts, not a divergent fork."""
    repo = Path(__file__).resolve().parents[1] / "notes/reference/calibration"
    for name in DEFAULT_BUNDLES:
        shipped = default_bundle_path(name).read_bytes()
        recorded = (repo / f"{name}-bundle.json").read_bytes()
        assert shipped == recorded, f"{name}-bundle.json differs from the calibration record"
