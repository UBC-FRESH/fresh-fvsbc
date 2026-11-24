"""The support tiers classify BEC-by-species cells without prose caveats."""

from __future__ import annotations

from fresh_fvsbc.support import SupportTier, classify


def test_bwbs_is_provisional_and_cites_w5() -> None:
    """BWBS runs on the W5 tables and is a pilot, not a certificate."""
    record = classify("BWBSmw/01", "AT")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.evidence == "w5-bwbs-v3"


def test_sbps_is_not_matched_as_sbs() -> None:
    """The longer token wins; SBPS has its own pending fold."""
    record = classify("SBPSmc/01", "PL")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.evidence == "w6-sbs-sbps-large-tree"
    assert "SBPS fold pending" in record.reason


def test_sbs_cites_the_w6_large_tree_row() -> None:
    """SBS is provisional on W6 plus the D7 mortality bundle."""
    record = classify("SBSdw2/01", "PL")
    assert record.tier is SupportTier.PROVISIONAL
    assert "D7 mortality bundle" in record.reason


def test_parser_only_zone_is_unsupported() -> None:
    """A label that resolves is not a model."""
    record = classify("CWHvm1", "HW")
    assert record.tier is SupportTier.UNSUPPORTED
    assert record.evidence == "w2-source-audit"


def test_unknown_bec_is_unsupported() -> None:
    """An unknown zone is refused rather than guessed."""
    assert classify("XYZmk", "PL").tier is SupportTier.UNSUPPORTED


def test_unknown_species_is_unsupported() -> None:
    """Only the BC variant's fifteen codes can be graded."""
    assert classify("BWBSmw", "ZZ").tier is SupportTier.UNSUPPORTED
