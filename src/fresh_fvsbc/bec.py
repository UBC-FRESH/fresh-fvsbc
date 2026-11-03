"""The BC Biogeoclimatic Ecosystem Classification (BEC) code, validated.

``canada/bc/initre.f`` reads a BC stand's BEC from the **first two fields of
``STDINFO``**, concatenates them, and passes the result to ``canada/bc/habtyp.f``.
``HABTYP`` looks for a region token, a zone token, a two-letter subzone token, an
optional subzone variant, a slash, and a site-series code. If any part is
missing it calls its error path and leaves the BEC at the documented default,
``ICHmw2/01``.

That default is the hazard this module closes. A caller who writes
``STDINFO=712,CHS131,...`` is not running an IDF or SBS stand; FVS is running
``ICHmw2/01`` with a maximum basal area of 89 m2/ha. Nothing in the run says so.
This module parses the two ``STDINFO`` fields before a run starts, refuses a code
that would not resolve, and names the accepted grammar and the supported zones.

The source is the authority
----------------------------

The accepted regions are ``CAR``, ``KAM``, and ``NEL``; the zones are ``ESSF``,
``ICH``, ``IDF``, ``MS``, ``PP``, ``SBS``, and ``SBPS``; and the subzones are the
two-letter list in ``HABTYP``. The zone list is also the list ``sitset.f``
assigns default maximum basal area for. ``CWH``, ``CDF``, ``BWBS``, ``CMA``, and
``MH`` are **not** represented by the BC variant, so a code in one of those zones
is refused rather than silently defaulted.

The grammar is the working form the FVS source accepts, made explicit::

    REGION ZONE SUBZONE[VARIANT]/SERIES

``IDFdk3/01`` is a zone ``IDF``, subzone ``dk``, variant ``3``, series ``01``.
``IDFxm/01`` has no variant. The series is mandatory: ``CAR IDFdk3`` alone does
not resolve, because ``HABTYP`` requires the slash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "REGIONS",
    "SUBZONES",
    "SUPPORTED_ZONES",
    "UNSUPPORTED_ZONES",
    "BecCode",
    "BecCodeError",
]

#: The region tokens ``HABTYP`` accepts, in its order.
REGIONS: tuple[str, ...] = ("CAR", "KAM", "NEL")

#: The BEC zones the BC variant resolves, in ``HABTYP``'s order.
SUPPORTED_ZONES: tuple[str, ...] = ("ESSF", "ICH", "IDF", "MS", "PP", "SBS", "SBPS")

#: The BC zones the variant does **not** resolve. They are named so the refusal can
#: say why the code did not work, rather than only that it did not parse.
UNSUPPORTED_ZONES: tuple[str, ...] = ("CWH", "CDF", "BWBS", "CMA", "MH")

#: The two-letter subzone tokens ``HABTYP`` accepts, without duplicates. The source
#: lists ``WM`` twice; a set does not need the duplicate.
SUBZONES: tuple[str, ...] = (
    "DC",
    "DK",
    "DM",
    "DW",
    "MC",
    "MH",
    "MK",
    "MM",
    "MW",
    "VK",
    "WC",
    "WK",
    "WM",
    "WW",
    "XC",
    "XH",
    "XK",
    "XM",
    "DH",
    "DV",
    "MV",
    "VC",
    "WH",
    "WV",
    "XV",
    "XW",
    "XX",
    "UN",
)

_ZONE_PATTERN: str = "|".join(SUPPORTED_ZONES)
_SUBZONE_PATTERN: str = "|".join(SUBZONES)
_SERIES_PATTERN: str = r"[A-Z0-9-]{1,5}"
_PATTERN: re.Pattern[str] = re.compile(
    rf"^(?P<region>{'|'.join(REGIONS)})(?P<zone>{_ZONE_PATTERN})"
    rf"(?P<subzone>{_SUBZONE_PATTERN})(?P<variant>[A-Z0-9])?/(?P<series>{_SERIES_PATTERN})$",
    re.IGNORECASE,
)

_SUBZONE_RE: re.Pattern[str] = re.compile(rf"^(?:{_SUBZONE_PATTERN})[A-Z0-9]?$")
_SERIES_RE: re.Pattern[str] = re.compile(rf"^{_SERIES_PATTERN}$")


class BecCodeError(ValueError):
    """A BEC code that FVS-BC would not resolve, or a set that does not carry one."""


@dataclass(frozen=True, slots=True)
class BecCode:
    """A validated BC BEC code.

    Parameters
    ----------
    region : str
        The region token: ``CAR``, ``KAM``, or ``NEL``.
    zone : str
        The BEC zone: ``ESSF``, ``ICH``, ``IDF``, ``MS``, ``PP``, ``SBS``, or
        ``SBPS``.
    subzone : str
        The lowercase subzone and optional variant, such as ``dk3`` or ``xm``.
    series : str
        The lowercase site-series code, such as ``01`` or ``01-yc``.

    Raises
    ------
    BecCodeError
        If a field is outside the source's lists. :meth:`parse` is the normal way
        to build one, because it reads a caller's code and reports what is wrong.
    """

    region: str
    zone: str
    subzone: str
    series: str

    def __post_init__(self) -> None:
        """Check that every field is one the source can carry.

        Raises
        ------
        BecCodeError
            If the region, zone, subzone, or series is outside the accepted set.
        """
        if self.region not in REGIONS:
            raise BecCodeError(f"BEC region {self.region!r} is not one of {', '.join(REGIONS)}")
        if self.zone not in SUPPORTED_ZONES:
            raise BecCodeError(f"BEC zone {self.zone!r} is not one of {', '.join(SUPPORTED_ZONES)}")
        if _SUBZONE_RE.fullmatch(self.subzone.upper()) is None:
            raise BecCodeError(
                f"BEC subzone {self.subzone!r} is not one of {', '.join(SUBZONES)} "
                "with an optional one-character variant"
            )
        if _SERIES_RE.fullmatch(self.series.upper()) is None:
            raise BecCodeError(
                f"BEC series {self.series!r} is not one to five letters, digits, or hyphens"
            )

    @property
    def pretty(self) -> str:
        """Return the zone, subzone, slash, and series, such as ``IDFdk3/01``.

        Returns
        -------
        str
            The second ``STDINFO`` field's canonical form.
        """
        return f"{self.zone}{self.subzone}/{self.series}"

    @property
    def fields(self) -> tuple[str, str]:
        """Return the two ``STDINFO`` fields that carry this BEC.

        Returns
        -------
        tuple of str
            The region and the ``zone+subzone/series`` string, in that order.
        """
        return self.region, self.pretty

    def __str__(self) -> str:
        """Return the code in the working ``REGION ZONE/SUBSERIES`` form."""
        return f"{self.region} {self.pretty}"

    @classmethod
    def from_fields(cls, first: str, second: str) -> BecCode:
        """Parse the first two ``STDINFO`` fields.

        ``HABTYP`` concatenates the fields before it parses them, so this method
        does the same. The working form puts the region in the first field and
        the rest in the second: ``STDINFO CAR IDFdk3/01``.

        Parameters
        ----------
        first : str
            The first ``STDINFO`` field, normally the region.
        second : str
            The second ``STDINFO`` field, normally ``ZONE+SUBZONE/SERIES``.

        Returns
        -------
        BecCode
            The validated code.

        Raises
        ------
        BecCodeError
            If the concatenated fields do not parse, or if the zone is one the
            variant does not represent.
        """
        return cls.parse(f"{first}{second}")

    @classmethod
    def parse(cls, text: str) -> BecCode:
        """Parse a BEC code and report why it would not resolve.

        The parser mirrors ``HABTYP``'s accepted grammar, but it is anchored:
        the region, zone, subzone, slash, and series must be the whole code.
        Whitespace is removed first, so ``CAR IDFdk3/01`` and ``CARIDFdk3/01``
        are the same code.

        Parameters
        ----------
        text : str
            A code such as ``CAR IDFdk3/01``, ``CARIDFdk3/01``, or the legacy
            ``712CHS131`` that the package refuses.

        Returns
        -------
        BecCode
            The validated code, with the region and zone upper-case and the
            subzone and series lower-case.

        Raises
        ------
        BecCodeError
            If the code is malformed, if its zone is not represented by the BC
            variant, or if its series is missing.
        """
        compact = "".join(text.split())
        match = _PATTERN.fullmatch(compact)
        if match is not None:
            variant = match.group("variant") or ""
            return cls(
                region=match.group("region").upper(),
                zone=match.group("zone").upper(),
                subzone=f"{match.group('subzone')}{variant}".lower(),
                series=match.group("series").lower(),
            )
        upper = compact.upper()
        for zone in UNSUPPORTED_ZONES:
            if zone in upper:
                raise BecCodeError(
                    f"the BC variant does not represent the {zone} BEC zone, and FVS "
                    "would silently fall back to ICHmw2/01; the supported zones are "
                    f"{', '.join(SUPPORTED_ZONES)}"
                )
        raise BecCodeError(
            f"{text!r} is not a BC BEC code. Write the region in the first STDINFO field "
            f"and the zone, subzone, and site series in the second, as in "
            f"'CAR IDFdk3/01'. The regions are {', '.join(REGIONS)} and the zones are "
            f"{', '.join(SUPPORTED_ZONES)}. Without a valid code FVS silently uses "
            "ICHmw2/01"
        )
