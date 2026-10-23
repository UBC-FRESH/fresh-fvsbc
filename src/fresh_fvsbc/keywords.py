"""The FVS-BC keyword-set validator.

``docs/reference/keywords.rst`` is the contract. This module holds FVS's keyword table as it is
declared in ``base/keywds.f``, validates a keyword set against it, and gives the set a hash.

What the table is
-----------------

``TABLE`` is a ``CHARACTER*8`` array of 150 slots, declared in ``base/keywds.f`` for the base model;
BC adds nothing to it. Six of the slots are blank, and a blank slot is not a keyword, so the table
holds 144 named keywords.

Matching is FVS's own. ``base/fndkey.f`` compares the caller's word to the table with FORTRAN's
``.EQ.`` on character strings, which is an exact, case-sensitive, blank-padded comparison. A
validator that accepted ``database`` would therefore accept something FVS does not, so this one does
not either; it rejects the name and points at the table's spelling when there is one close.

The misspelling
---------------

Slot 30 holds ``xSALVAGE``, with a leading ``x``, which is a spelling defect in FVS itself. FVS
matches what the table holds, so ``xSALVAGE`` is the *correct* spelling and ``SALVAGE`` is not a
keyword at all. The validator warns when a set contains ``xSALVAGE``, because a caller who reached
for that name is working around a defect they should know about, and it names ``xSALVAGE`` when a
caller writes ``SALVAGE`` instead.

What this module does not do
----------------------------

Contract rule 4, that a set never silently gains a keyword the caller did not write, is not enforced
here. The one exception the contract allows is the tree-record format, which is a property of how a
run is set up rather than of validation, and it is handled where the run is.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field

__all__ = [
    "BLANK_SLOTS",
    "KEYWORDS",
    "KEYWORD_TABLE",
    "MISSPELLED_KEYWORD",
    "Keyword",
    "KeywordSet",
    "UnknownKeywordError",
    "keyword_set_hash",
    "render_keyword",
    "render_keywords",
    "validate_keyword",
    "validate_keywords",
]

#: FVS's keyword table, ``TABLE`` in ``base/keywds.f``, in slot order. ``None`` is a blank slot, and
#: a blank slot is not a keyword. Names are stored as ``CHARACTER*8`` compares them, without the
#: trailing blanks that pads them.
KEYWORD_TABLE: tuple[str | None, ...] = (
    # slots 1 to 20
    "PROCESS",
    "TIMEINT",
    "FIXCW",
    "TREEDATA",
    "TREEFMT",
    "MPB",
    "DFTM",
    "WSBW",
    "CWEQN",
    "DESIGN",
    "NUMCYCLE",
    "TFIXAREA",
    "GROWTH",
    "STDINFO",
    "STDIDENT",
    "INVYEAR",
    "TREELIST",
    "REWIND",
    "NOSUM",
    "DEBUG",
    # slots 21 to 40
    "ECHOSUM",
    "ADDFILE",
    "THINAUTO",
    "THINBTA",
    "THINATA",
    "THINBBA",
    "THINABA",
    "THINPRSC",
    "THINDBH",
    "xSALVAGE",
    "SPLABEL",
    "AGPLABEL",
    "COMPUTE",
    "FERTILIZ",
    "THINHT",
    "STATS",
    "TOPKILL",
    "HTGSTOP",
    "MCFDLN",
    "BFFDLN",
    # slots 41 to 60
    "MCDEFECT",
    "BFDEFECT",
    "VOLUME",
    "BFVOLUME",
    "REGDMULT",
    "COVER",
    "ESTAB",
    "MINHARV",
    "SPECPREF",
    "SPCODES",
    "NODEBUG",
    "CUTEFF",
    "NOTRIPLE",
    "READCORD",
    "REUSCORD",
    "NOCALIB",
    "DGSTDEV",
    "BAIMULT",
    "MORTMULT",
    "NOHTDREG",
    # slots 61 to 80
    "RANNSEED",
    "HTGMULT",
    "CHEAPO",
    "NUMTRIP",
    "ENDFILE",
    "BAMAX",
    "READCORH",
    "REUSCORH",
    "MGMTID",
    "REGHMULT",
    "TCONDMLT",
    "NOAUTOES",
    "READCORR",
    "REUSCORR",
    "BRUST",
    "IF",
    "SCREEN",
    "COMPRESS",
    "THEN",
    "ALSOTRY",
    # slots 81 to 100
    "ENDIF",
    "NOTREES",
    "CALBSTAT",
    "OPEN",
    "CLOSE",
    "NOSCREEN",
    "RRIN",
    "FIXMORT",
    "SDIMAX",
    "DELOTAB",
    "SERLCORR",
    "CUTLIST",
    "RESETAGE",
    "SITECODE",
    "MISTOE",
    "CRNMULT",
    "CFVOLEQU",
    "BFVOLEQU",
    "ANIN",
    "DFB",
    # slots 101 to 120, which hold three blank slots
    "RDIN",
    "MANAGED",
    "YARDLOSS",
    "FMIN",
    "STRCLASS",
    "MODTYPE",
    "FVSSTAND",
    "PRUNE",
    "SVS",
    "FIXDG",
    "FIXHTG",
    "THINSDI",
    "LOCATE",
    None,
    "THINCC",
    "ECON",
    "DATABASE",
    None,
    "DEFECT",
    None,
    # slots 121 to 135
    "STANDCN",
    "THINMIST",
    "TREESZCP",
    "THINRDEN",
    "SPGROUP",
    "BMIN",
    "DATASCRN",
    "SETPTHIN",
    "THINPT",
    "VOLEQNUM",
    "POINTREF",
    "ECHO",
    "NOECHO",
    "CYCLEAT",
    "ATRTLIST",
    # slots 136 to 150, which hold three blank slots
    "THINRDSL",
    "MORTMSB",
    "SETSITE",
    "CLIMATE",
    "SDICALC",
    "THINQFA",
    "PTGROUP",
    "ORGANON",
    "SPLEAVE",
    "CCADJ",
    "PRMFROST",
    "FIAVBC",
    None,
    None,
    None,
)

#: The named keywords, as a set for lookup.
KEYWORDS: frozenset[str] = frozenset(name for name in KEYWORD_TABLE if name is not None)

#: The 1-based slot numbers that hold no keyword.
BLANK_SLOTS: tuple[int, ...] = tuple(
    slot for slot, name in enumerate(KEYWORD_TABLE, start=1) if name is None
)

#: The keyword whose spelling is defective in FVS, at slot 30.
MISSPELLED_KEYWORD: str = "xSALVAGE"

#: The warning the validator gives for :data:`MISSPELLED_KEYWORD`.
MISSPELLING_WARNING: str = (
    f'The table spells this "{MISSPELLED_KEYWORD}", with a leading "x", because the defect is in '
    f'FVS itself. "SALVAGE" is not a keyword, so this is the spelling FVS matches.'
)


class UnknownKeywordError(ValueError):
    """A keyword that FVS's table does not hold."""


def _near_miss(name: str) -> str | None:
    """Return the table's spelling of a name that looks like a near miss, if there is one.

    Parameters
    ----------
    name : str
        The name a caller wrote, which is not in the table.

    Returns
    -------
    str or None
        The table's spelling, when the name differs from it only in case or by the leading ``x``
        that FVS's own misspelling carries. ``None`` when nothing in the table is close.
    """
    for candidate in (name.upper(), f"x{name}", f"x{name.upper()}"):
        if candidate in KEYWORDS:
            return candidate
    return None


@dataclass(frozen=True, slots=True)
class Keyword:
    """One keyword and its parameters, in the order FVS reads them.

    Parameters
    ----------
    name : str
        The keyword, spelled as FVS's table spells it.
    parameters : tuple of str, optional
        The values that follow the keyword. FVS reads them as separate tokens, so a parameter may
        contain spaces.
    """

    name: str
    parameters: tuple[str, ...] = ()


def validate_keyword(keyword: Keyword) -> list[str]:
    """Validate one keyword against FVS's table.

    Parameters
    ----------
    keyword : Keyword
        The keyword and its parameters.

    Returns
    -------
    list of str
        The warnings this keyword raises. An empty list means there are none.

    Raises
    ------
    UnknownKeywordError
        If the name is not in the table. The message names the keyword, and names the table's
        spelling when the name is a near miss.
    """
    if keyword.name not in KEYWORDS:
        near = _near_miss(keyword.name)
        hint = f' The table spells it "{near}".' if near is not None else ""
        raise UnknownKeywordError(f'"{keyword.name}" is not a keyword.{hint}')
    if keyword.name == MISSPELLED_KEYWORD:
        return [MISSPELLING_WARNING]
    return []


def validate_keywords(keywords: Sequence[Keyword]) -> list[str]:
    """Validate a whole keyword set, in order.

    Parameters
    ----------
    keywords : Sequence[Keyword]
        The keywords, in the order FVS will read them.

    Returns
    -------
    list of str
        Every warning the set raises, in the order the keywords were checked.

    Raises
    ------
    UnknownKeywordError
        On the first keyword whose name is not in the table. Validation stops there rather than
        reporting the rest, because a set with an unknown keyword cannot be run.
    """
    warnings: list[str] = []
    for keyword in keywords:
        warnings.extend(validate_keyword(keyword))
    return warnings


def render_keyword(keyword: Keyword) -> str:
    """Render one keyword as the lines FVS reads for it.

    FVS reads a keyword name and then its parameters as successive tokens, and its own keyword files
    put each on its own line. Rendering that way keeps a parameter containing spaces intact.

    Parameters
    ----------
    keyword : Keyword
        The keyword and its parameters.

    Returns
    -------
    str
        The keyword's lines, each ending with a newline.
    """
    return "".join(f"{line}\n" for line in (keyword.name, *keyword.parameters))


def render_keywords(keywords: Sequence[Keyword]) -> str:
    """Render a keyword set as the text that FVS would read.

    Parameters
    ----------
    keywords : Sequence[Keyword]
        The keywords, in order.

    Returns
    -------
    str
        The rendered set.
    """
    return "".join(render_keyword(keyword) for keyword in keywords)


@dataclass(frozen=True, slots=True)
class KeywordSet:
    """An ordered keyword set, validated, carrying the hash of the text it renders to.

    Parameters
    ----------
    keywords : Sequence[Keyword]
        The keywords, in the order FVS will read them.

    Raises
    ------
    UnknownKeywordError
        If any keyword's name is not in FVS's table.
    """

    keywords: tuple[Keyword, ...] = ()
    warnings: tuple[str, ...] = field(default=(), init=False)

    def __post_init__(self) -> None:
        """Validate the set and record its warnings."""
        keywords = tuple(self.keywords)
        warnings = tuple(validate_keywords(keywords))
        object.__setattr__(self, "keywords", keywords)
        object.__setattr__(self, "warnings", warnings)

    @property
    def digest(self) -> str:
        """Return the hash of the text this set renders to, naming the algorithm."""
        return keyword_set_hash(self.keywords)

    def render(self) -> str:
        """Return the text that FVS would read for this set."""
        return render_keywords(self.keywords)


def keyword_set_hash(keywords: Sequence[Keyword]) -> str:
    """Return the hash of the text a keyword set renders to.

    The hash is taken over the rendered text rather than over a structure, so that it identifies the
    exact bytes a run was given, which is what makes it useful as provenance. The algorithm is named
    in the result, so a reader does not have to know it.

    Parameters
    ----------
    keywords : Sequence[Keyword]
        The keywords, in order. Order is part of the identity, because FVS processes a set in order.

    Returns
    -------
    str
        ``"sha256:"`` followed by the hexadecimal digest.
    """
    text = render_keywords(keywords)
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"
