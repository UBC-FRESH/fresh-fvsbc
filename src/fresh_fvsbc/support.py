"""Machine-readable support tiers for FVS-BC runs.

The tiers replace prose caveats. Every BEC-by-species cell is one of five grades, and a run or a
dataset can carry the grade as data:

- ``A`` fitted and validated;
- ``B`` explicit donor species, validated at stand level;
- ``C`` provisional: it runs, and the evidence is a pilot, not a signed calibration;
- ``D`` unsupported: the parser accepts the label but there is no growth/mortality model;
- ``X`` out of scope: a deliberate exclusion, not a gap. ``CMA`` is the case: it is not a forested
  BEC zone and is immaterial to the modelling projects this package serves.

No cell is ``A`` or ``B`` yet: the supported zones carry unsigned pilots. That is stated once here
rather than repeated per run.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["SupportRecord", "SupportTier", "classify"]


class SupportTier(StrEnum):
    """The five support grades."""

    FITTED = "A"
    DONOR = "B"
    PROVISIONAL = "C"
    UNSUPPORTED = "D"
    OUT_OF_SCOPE = "X"


@dataclass(frozen=True)
class SupportRecord:
    """One BEC-by-species grade.

    Attributes
    ----------
    bec : str
        The requested BEC label, as given.
    species : str
        The FVS species code, uppercased.
    tier : SupportTier
        The grade.
    reason : str
        Why the cell has that grade.
    evidence : str
        The note or bundle that carries the evidence.
    path : str
        The growth path the engine runs for the zone: ``V3``, ``V2``, or ``X``.
    """

    bec: str
    species: str
    tier: SupportTier
    reason: str
    evidence: str
    path: str = "V3"


#: The growth path the variant runs for each zone, mirroring the ``LV2ATV`` list in
#: ``canada/bc/becset.f``. A zone is V3 only when that list names it *and* the zone has rows in
#: ``regent``, ``dgf``, ``htgf``, and ``morts``; the mapping is the single source of truth here,
#: and ``scripts/check_zone_paths.py`` compares it with the source.
ZONE_PATH: dict[str, str] = {
    "ICH": "V3",
    "IDF": "V3",
    "SBS": "V3",
    "SBPS": "V3",
    "BWBS": "V3",
    "CWH": "V3",
    "MH": "V3",
    "CDF": "V3",
    "MS": "V3",
    "ESSF": "V3",
    "PP": "V3",
    "CMA": "X",
}

# Ordered so a longer or ambiguous token is tested before a shorter one (SBPS before SBS).
_ZONE_TIERS: tuple[tuple[str, SupportTier, str, str], ...] = (
    (
        "CWH",
        SupportTier.PROVISIONAL,
        "V3 fitted large-tree DG; fitted height for HW/FD/BG/SE/AT/PL, CW donor height; "
        "W21 joint small-tree density term in diameter and mortality; BAIMULT 8",
        "w11-cwh-height, w21-cwh-small-joint",
    ),
    (
        "CDF",
        SupportTier.PROVISIONAL,
        "V3 own FD/AT rows; BAIMULT 8, MORTMULT 0.5 FD/AC, W30 high-BA mortality",
        "w10-mh-cdf-own-dg, w30-cdf-high-ba-mort",
    ),
    (
        "CMA",
        SupportTier.OUT_OF_SCOPE,
        "not a forested BEC zone; out of scope by project decision",
        "cma-out-of-scope",
    ),
    (
        "MH",
        SupportTier.PROVISIONAL,
        "V3 own HW/BG large-tree rows, coastal donor for the rest; BAIMULT 8; 3-interval fold",
        "w10-mh-cdf-own-dg",
    ),
    ("BWBS", SupportTier.PROVISIONAL, "V3 pilot; W5 growth and mortality tables", "w5-bwbs-v3"),
    (
        "SBPS",
        SupportTier.PROVISIONAL,
        "V3 pilot; W7 fitted large-tree DG; BL/EP/OH still zero; "
        "zone bundle withdrawn on stable folds",
        "w7-sbps-large-tree, dbh-limit-clean-fold",
    ),
    (
        "SBS",
        SupportTier.PROVISIONAL,
        "V3 W6 large-tree row with the W18 BL refit; W22 BL density term; "
        "MORTMULT 1.1 for FD/PL/SE/HW",
        "w6-sbs-large-tree, w18-sbs-bl-refit, w22-sbs-bl-density, sbs-v3, "
        "sbsmc2-v3, sbsmw-v3, sbswk2-v3, sbsdw1-v3, "
        "w28-sbsmc2-stem-shape",
    ),
    ("ICH", SupportTier.PROVISIONAL, "V3 pilot; unsigned", "d9-full-bc-review-bundle"),
    ("IDF", SupportTier.PROVISIONAL, "V3 pilot; unsigned", "d9-full-bc-review-bundle"),
    (
        "ESSF",
        SupportTier.PROVISIONAL,
        "V3 fitted rows; partial ten-year-basis growth correction; zone bundle "
        "withdrawn on stable folds; unsigned",
        "w16-essf-v3, dbh-limit-clean-fold",
    ),
    (
        "MS",
        SupportTier.PROVISIONAL,
        "V3 fitted rows; tabular mortality; zone bundle withdrawn on stable folds; unsigned",
        "w15-ms-v3, dbh-limit-clean-fold",
    ),
    (
        "PP",
        SupportTier.PROVISIONAL,
        "V3 fitted rows with the pp-v3 bundle (BAIMULT 3.0, MORTMULT 0.8); "
        "SE/BL/AT keep donors; LOSO across 10 sites",
        "w17-pp-v3, pp-v3",
    ),
)

#: The BC variant's fifteen species codes (``blkdat.f`` ``JSP``).
SPECIES: frozenset[str] = frozenset(
    {"PW", "LW", "FD", "BG", "HW", "CW", "PL", "SE", "BL", "PY", "EP", "AT", "AC", "OC", "OH"}
)


def classify(bec: str, species: str) -> SupportRecord:
    """Return the support grade for one BEC and species.

    Parameters
    ----------
    bec : str
        A BEC label such as ``BWBSmw`` or ``SBSdw2/01``.
    species : str
        An FVS species code such as ``PL``.

    Returns
    -------
    SupportRecord
        The grade, the reason, and the evidence note.
    """
    label = bec.strip()
    code = species.strip().upper()
    if code not in SPECIES:
        return SupportRecord(
            bec=label,
            species=code,
            tier=SupportTier.UNSUPPORTED,
            reason="species is not in the BC variant's fifteen-code grammar",
            evidence="blkdat.f",
            path="X",
        )
    for zone, tier, reason, evidence in _ZONE_TIERS:
        if zone in label.upper():
            return SupportRecord(
                bec=label,
                species=code,
                tier=tier,
                reason=reason,
                evidence=evidence,
                path=ZONE_PATH.get(zone, "X"),
            )
    return SupportRecord(
        bec=label,
        species=code,
        tier=SupportTier.UNSUPPORTED,
        reason="BEC zone has no model entry",
        evidence="becset.f",
        path="X",
    )
