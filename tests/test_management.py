"""Tests for the management-regime interpretation."""

from __future__ import annotations

import pytest

from fresh_fvsbc.bundle import BundleError, CalibrationBundle
from fresh_fvsbc.keywords import Keyword
from fresh_fvsbc.run import _management


def test_management_defaults_to_untreated() -> None:
    """No MANAGED record is an untreated run."""
    assert _management(()) == "untreated"


def test_managed_zero_is_untreated() -> None:
    """The baseline writes MANAGED 0 1; that is not a treatment."""
    assert _management((Keyword("MANAGED", ("0", "1")),)) == "untreated"


def test_managed_one_is_managed() -> None:
    """A non-zero MANAGED value is a treatment."""
    assert _management((Keyword("MANAGED", ("1", "1")),)) == "managed"


def test_managed_non_numeric_is_managed() -> None:
    """A malformed MANAGED value is treated conservatively."""
    assert _management((Keyword("MANAGED", ("x",)),)) == "managed"


def test_bundle_refuses_bad_ingrowth() -> None:
    """A bundle with an invalid ingrowth object is refused."""
    record = {
        "bundle_id": "x",
        "version": "0.1.0",
        "pins": {},
        "domain": {},
        "parameters": [],
        "ingrowth": {},
        "training": {},
        "review": {},
        "claim": "x",
    }
    with pytest.raises(BundleError):
        CalibrationBundle.from_record(record)
