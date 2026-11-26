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
    assert record.evidence == "w7-sbps-large-tree"
    assert "MORTMULT 2" in record.reason


def test_sbs_cites_the_w6_large_tree_row() -> None:
    """SBS is provisional on W6 plus the D7 mortality bundle."""
    record = classify("SBSdw2/01", "PL")
    assert record.tier is SupportTier.PROVISIONAL
    assert "D7 mortality bundle" in record.reason


def test_cma_is_out_of_scope_not_a_gap() -> None:
    """CMA is a deliberate exclusion, not an unsupported cell to chase."""
    record = classify("CMAunp", "HW")
    assert record.tier is SupportTier.OUT_OF_SCOPE
    assert record.evidence == "cma-out-of-scope"


def test_cwh_is_provisional_on_the_v2_bundle() -> None:
    """CWH runs on the legacy path with a stand-level calibration."""
    record = classify("CWHvm1", "HW")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.evidence == "w11-cwh-height"
    assert "CW donor height" in record.reason


def test_mh_is_provisional_with_its_own_large_tree_rows() -> None:
    """MH fits HW and BG from its own pairs and keeps the donor for the rest."""
    record = classify("MHmm1", "HW")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.evidence == "w10-mh-cdf-own-dg"
    assert "own HW/BG" in record.reason


def test_cdf_is_provisional_with_its_own_large_tree_rows() -> None:
    """CDF fits FD and AT from its own pairs and keeps the donor for the rest."""
    record = classify("CDFmm", "FD")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.evidence == "w10-mh-cdf-own-dg"
    assert "own FD/AT" in record.reason


def test_essf_names_the_site_series_restriction() -> None:
    """A zone that falls back to MSdk for an unmapped series says so."""
    record = classify("ESSFdk2", "BL")
    assert record.tier is SupportTier.PROVISIONAL
    assert "MSdk/01" in record.reason
    assert record.evidence == "bec-substitution"


def test_pp_names_the_v2_path() -> None:
    """PP resolves to its own habitat but still runs the V2 growth path."""
    record = classify("PPxh2", "PL")
    assert record.tier is SupportTier.PROVISIONAL
    assert "V2 path" in record.reason
    assert "p99 caps" in record.reason


def test_unknown_bec_is_unsupported() -> None:
    """An unknown zone is refused rather than guessed."""
    assert classify("XYZmk", "PL").tier is SupportTier.UNSUPPORTED


def test_unknown_species_is_unsupported() -> None:
    """Only the BC variant's fifteen codes can be graded."""
    assert classify("BWBSmw", "ZZ").tier is SupportTier.UNSUPPORTED


def test_region_prefix_does_not_hide_the_zone() -> None:
    """Provenance carries ``CAR BWBSmw/01``; the classifier still finds BWBS."""
    assert classify("CAR BWBSmw/01", "AT").tier is SupportTier.PROVISIONAL
