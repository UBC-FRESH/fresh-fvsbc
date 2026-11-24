"""Machine-readable support tiers for FVS-BC runs.

The tiers replace prose caveats. Every BEC-by-species cell is one of four grades, and a run or a
dataset can carry the grade as data:

- ``A`` fitted and validated;
- ``B`` explicit donor species, validated at stand level;
- ``C`` provisional: it runs, and the evidence is a pilot, not a signed calibration;
- ``D`` unsupported: the parser accepts the label but there is no growth/mortality model.

No cell is ``A`` or ``B`` yet: the supported zones carry unsigned pilots. That is stated once here
rather than repeated per run.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["SupportRecord", "SupportTier", "classify"]


class SupportTier(StrEnum):
    """The four support grades."""

    FITTED = "A"
    DONOR = "B"
    PROVISIONAL = "C"
    UNSUPPORTED = "D"


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
    """

    bec: str
    species: str
    tier: SupportTier
    reason: str
    evidence: str


# Ordered so a longer or ambiguous token is tested before a shorter one (SBPS before SBS).
_ZONE_TIERS: tuple[tuple[str, SupportTier, str, str], ...] = (
    (
        "CWH",
        SupportTier.PROVISIONAL,
        "V3 fitted large-tree DG; donor small tree/height/mortality; BAIMULT 8",
        "w8-cwh-v3",
    ),
    (
        "CDF",
        SupportTier.PROVISIONAL,
        "V2 legacy path; BAIMULT 10 pilot; V3 tables pending",
        "coastal-v2-calibration",
    ),
    (
        "CMA",
        SupportTier.UNSUPPORTED,
        "parser only; no model tables or suitability evidence",
        "w2-source-audit",
    ),
    (
        "MH",
        SupportTier.PROVISIONAL,
        "V2 legacy path; BAIMULT 10 pilot on a 3-interval fold; V3 tables pending",
        "coastal-v2-calibration",
    ),
    ("BWBS", SupportTier.PROVISIONAL, "V3 pilot; W5 growth and mortality tables", "w5-bwbs-v3"),
    (
        "SBPS",
        SupportTier.PROVISIONAL,
        "V3 pilot; W7 fitted large-tree DG with the SBPS MORTMULT 2 bundle; BL/EP/OH still zero",
        "w7-sbps-large-tree",
    ),
    (
        "SBS",
        SupportTier.PROVISIONAL,
        "V3 pilot; W6 large-tree row with the D7 mortality bundle",
        "w6-sbs-large-tree",
    ),
    ("ICH", SupportTier.PROVISIONAL, "V3 pilot; unsigned", "d9-full-bc-review-bundle"),
    ("IDF", SupportTier.PROVISIONAL, "V3 pilot; unsigned", "d9-full-bc-review-bundle"),
    (
        "ESSF",
        SupportTier.PROVISIONAL,
        "V3 via defaults; subzone validation incomplete",
        "w2-subzone-patch",
    ),
    (
        "MS",
        SupportTier.PROVISIONAL,
        "V3 via defaults; subzone validation incomplete",
        "w2-subzone-patch",
    ),
    ("PP", SupportTier.PROVISIONAL, "V3 via defaults; unsigned", "d7-consolidation"),
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
        )
    for zone, tier, reason, evidence in _ZONE_TIERS:
        if zone in label.upper():
            return SupportRecord(
                bec=label, species=code, tier=tier, reason=reason, evidence=evidence
            )
    return SupportRecord(
        bec=label,
        species=code,
        tier=SupportTier.UNSUPPORTED,
        reason="BEC zone has no model entry",
        evidence="becset.f",
    )
