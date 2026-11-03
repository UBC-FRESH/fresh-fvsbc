"""Tests for the BC BEC code validator.

The validator exists because FVS silently falls back to ``ICHmw2/01`` when the
first two ``STDINFO`` fields do not parse. The tests therefore check both what
is accepted and that the legacy string the package used to document is refused.
"""

from __future__ import annotations

import pytest

from fresh_fvsbc.bec import BecCode, BecCodeError


@pytest.mark.parametrize(
    ("text", "region", "zone", "subzone", "series"),
    [
        ("CAR IDFdk3/01", "CAR", "IDF", "dk3", "01"),
        ("CARIDFdk3/01", "CAR", "IDF", "dk3", "01"),
        ("KAM ICHmw2/01", "KAM", "ICH", "mw2", "01"),
        ("NEL SBSmc2/01", "NEL", "SBS", "mc2", "01"),
        ("car idfxm/01", "CAR", "IDF", "xm", "01"),
        ("CAR ESSFwc2/01-YC", "CAR", "ESSF", "wc2", "01-yc"),
        ("KAM SBPSmk/01", "KAM", "SBPS", "mk", "01"),
        ("NEL MSdm1/01", "NEL", "MS", "dm1", "01"),
        ("CAR PPxh1/01", "CAR", "PP", "xh1", "01"),
    ],
)
def test_a_supported_code_parses_into_its_four_parts(
    text: str, region: str, zone: str, subzone: str, series: str
) -> None:
    """Every supported form resolves to the same four canonical parts."""
    code = BecCode.parse(text)
    assert (code.region, code.zone, code.subzone, code.series) == (
        region,
        zone,
        subzone,
        series,
    )


def test_fields_are_the_two_stdinfo_fields_fvs_concatenates() -> None:
    """The region goes in field 1 and the rest in field 2, as ``STDINFO`` writes them."""
    code = BecCode.parse("CAR IDFdk3/01")
    assert code.fields == ("CAR", "IDFdk3/01")
    assert code.pretty == "IDFdk3/01"


def test_str_round_trips_through_parse() -> None:
    """The rendered working form is itself a valid code."""
    code = BecCode.parse("KAM ICHmw2/01")
    assert str(code) == "KAM ICHmw2/01"
    assert BecCode.parse(str(code)) == code


@pytest.mark.parametrize(
    "text",
    [
        "712CHS131",
        "712 CHS131",
        "IDFdk3/01",
        "CAR IDFdk3",
        "CAR",
        "CAR IDFdk3/",
        "CAR IDFdk3/0123456",
        "CAR IDFdk3/01 extra",
    ],
)
def test_a_code_that_would_not_resolve_is_refused(text: str) -> None:
    """A code with a missing region, zone, slash, or series is refused, not defaulted."""
    with pytest.raises(BecCodeError):
        BecCode.parse(text)


@pytest.mark.parametrize(
    ("text", "zone"),
    [
        ("CAR CWHvm1/01", "CWH"),
        ("CAR CDFmm/01", "CDF"),
        ("CAR BWBSdk/01", "BWBS"),
        ("CAR CMAunp/01", "CMA"),
        ("CAR MHmm1/01", "MH"),
    ],
)
def test_the_five_prototype_zones_parse(text: str, zone: str) -> None:
    """The W2.5 extension carries the five zones and their subzones."""
    assert BecCode.parse(text).zone == zone


def test_the_legacy_stdinfo_string_names_the_silent_default() -> None:
    """A caller who copies the old example is told what FVS would have done."""
    with pytest.raises(BecCodeError, match="ICHmw2/01"):
        BecCode.from_fields("712", "CHS131")


def test_from_fields_concatenates_the_two_stdinfo_fields() -> None:
    """FVS concatenates fields 1 and 2, so a split code is valid."""
    assert BecCode.from_fields("CAR", "IDFdk3/01") == BecCode.parse("CAR IDFdk3/01")


def test_a_direct_constructor_refuses_an_unsupported_region() -> None:
    """The value object cannot be built with a region the source does not accept."""
    with pytest.raises(BecCodeError, match="region"):
        BecCode(region="USA", zone="IDF", subzone="dk3", series="01")


def test_a_direct_constructor_refuses_an_unknown_zone() -> None:
    """The value object cannot be built with a zone the source does not accept."""
    with pytest.raises(BecCodeError, match="zone"):
        BecCode(region="CAR", zone="XXX", subzone="vm1", series="01")


@pytest.mark.parametrize(
    "bec",
    [
        "ESSFdh1/01",
        "ESSFdv1/01",
        "ESSFmv/01",
        "ESSFmv1/01",
        "ESSFmv2/01",
        "ESSFmv3/01",
        "ESSFmv4/01",
        "ESSFvc/01",
        "ESSFwh1/01",
        "ESSFwv/01",
        "ESSFxv2/01",
        "ICHvc/01",
        "ICHxw/01",
        "IDFdh/01",
        "IDFxw/01",
        "IDFxx2/01",
        "MSxv/01",
        "SBSdh1/01",
        "SBSun/01",
    ],
)
def test_the_w2_subzones_parse(bec: str) -> None:
    """The wrapper knows the subzones the W2.3 patch adds to the variant."""
    code = BecCode.parse(f"CAR {bec}")
    assert code.pretty == bec
