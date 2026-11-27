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
    """SBS is provisional on W6 plus its mortality and BL growth multipliers."""
    record = classify("SBSdw2/01", "PL")
    assert record.tier is SupportTier.PROVISIONAL
    assert "W6" in record.reason
    assert "W18 BL refit" in record.reason


def test_cma_is_out_of_scope_not_a_gap() -> None:
    """CMA is a deliberate exclusion, not an unsupported cell to chase."""
    record = classify("CMAunp", "HW")
    assert record.tier is SupportTier.OUT_OF_SCOPE
    assert record.evidence == "cma-out-of-scope"


def test_cwh_is_provisional_on_the_v2_bundle() -> None:
    """CWH runs on the legacy path with a stand-level calibration."""
    record = classify("CWHvm1", "HW")
    assert record.tier is SupportTier.PROVISIONAL
    assert "w11-cwh-height" in record.evidence
    assert "w21-cwh-small-joint" in record.evidence
    assert "CW donor height" in record.reason
    assert "W21" in record.reason


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


def test_essf_is_v3_after_w16() -> None:
    """ESSF carries its own fitted rows and the engine runs it on V3."""
    record = classify("ESSFdk2", "BL")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.path == "V3"
    assert record.evidence == "w16-essf-v3"


def test_ms_is_v3_after_w15() -> None:
    """MS carries its own fitted rows and the engine runs it on V3."""
    record = classify("MSdm1", "PL")
    assert record.path == "V3"
    assert record.evidence == "w15-ms-v3"
    assert "V3 fitted" in record.reason


def test_pp_is_v3_after_w17() -> None:
    """PP runs its own fitted rows on V3."""
    record = classify("PPxh2", "PL")
    assert record.tier is SupportTier.PROVISIONAL
    assert record.path == "V3"
    assert record.evidence == "w17-pp-v3"


def test_unknown_bec_is_unsupported() -> None:
    """An unknown zone is refused rather than guessed."""
    assert classify("XYZmk", "PL").tier is SupportTier.UNSUPPORTED


def test_unknown_species_is_unsupported() -> None:
    """Only the BC variant's fifteen codes can be graded."""
    assert classify("BWBSmw", "ZZ").tier is SupportTier.UNSUPPORTED


def test_region_prefix_does_not_hide_the_zone() -> None:
    """Provenance carries ``CAR BWBSmw/01``; the classifier still finds BWBS."""
    assert classify("CAR BWBSmw/01", "AT").tier is SupportTier.PROVISIONAL


def test_every_zone_has_a_path() -> None:
    """A zone in the tier table must declare the growth path it runs."""
    from fresh_fvsbc.support import _ZONE_TIERS, ZONE_PATH

    zones = {zone for zone, _, _, _ in _ZONE_TIERS}
    assert zones == set(ZONE_PATH), "a zone is in the tier table without a path, or the reverse"
    assert set(ZONE_PATH.values()) <= {"V3", "V2", "X"}


def test_the_path_is_in_the_reason() -> None:
    """The reason text cannot claim V3 for a zone the engine runs as V2."""
    from fresh_fvsbc.support import _ZONE_TIERS, ZONE_PATH

    for zone, _, reason, _ in _ZONE_TIERS:
        path = ZONE_PATH[zone]
        if path == "V3":
            assert reason.startswith("V3"), f"{zone} is V3 and its reason does not say so"
        elif path == "V2":
            assert reason.startswith("V2"), f"{zone} is V2 and its reason does not say so"
