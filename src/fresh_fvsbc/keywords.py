"""The FVS-BC keyword-set validator.

``docs/reference/keywords.rst`` is the contract. This module holds FVS's keyword table as it is
declared in ``base/keywds.f``, validates a keyword set against it, and gives the set a hash.

What the table is
-----------------

``TABLE`` is a ``CHARACTER*8`` array of 150 slots, declared in ``base/keywds.f`` for the base model;
BC adds nothing to it. Six of the slots are blank, and a blank slot is not a keyword, so the table
holds 144 named keywords.

``STOP`` is not in the table, and is still a keyword
----------------------------------------------------

``base/keyrdr.f`` reads each record, upcases its first eight characters, and compares them with
``STOP`` *before* it consults the table; a match ends the file with code 3. So ``STOP`` is a keyword
that ``keywds.f`` does not hold, and it is in :data:`SPECIAL_KEYWORDS` rather than in the table.
The run orchestration found this the first time it wrote a whole key file: every real key file ends
with ``STOP``, and a validator that refused it refused all of them.

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
    "BLOCK_KEYWORDS",
    "FIELD_WIDTH",
    "FIRE_MODEL_ORDER_WARNING",
    "FMIN_KEYWORDS",
    "KEYWORDS",
    "KEYWORD_BLOCK_KEYWORDS",
    "KEYWORD_TABLE",
    "LINES_KEYWORDS",
    "MISSPELLED_KEYWORD",
    "NESTED_KEYWORDS",
    "RECORD_KEYWORDS",
    "SPECIAL_KEYWORDS",
    "STAND_KEYWORDS",
    "SUPPLEMENTAL_KEYWORDS",
    "Keyword",
    "KeywordOrderError",
    "KeywordSet",
    "KeywordWidthError",
    "UnknownKeywordError",
    "UnsupportedKeywordError",
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

#: The keywords FVS matches before it consults the table. ``base/keyrdr.f`` compares the record's
#: first eight characters with ``STOP`` and returns code 3, which ends the keyword file, so ``STOP``
#: is a keyword that ``base/keywds.f`` does not hold. A validator that refused it would refuse every
#: real key file, which is what the run orchestration found the first time it wrote one.
SPECIAL_KEYWORDS: frozenset[str] = frozenset({"STOP", "COMMENT"})

#: The width of a parameter field. ``base/keyrdr.f`` reads ``KARD(I)=RECORD(J:J+9)`` with ``J``
#: stepping by ten from eleven, so every parameter is a ten-column field of the keyword's own record
#: and a longer one cannot be carried.
FIELD_WIDTH: int = 10

#: The keywords whose content is a record of its own rather than a field of the keyword's record.
#: ``canada/bc/initre.f`` reads the record after ``STDIDENT`` as the stand id and title, and
#: ``intree.f`` reads the two after ``TREEFMT`` as the format.
RECORD_KEYWORDS: frozenset[str] = frozenset({"STDIDENT", "TREEFMT"})

#: The keywords whose content is a block of **text lines** ended by ``END``. A caller supplies the
#: lines, and the writer supplies the terminator, because a block without one swallows the rest of
#: the file.
LINES_KEYWORDS: frozenset[str] = frozenset(
    {"COMMENT", "COMPUTE", "DATABASE", "ESTAB", "MISTOE", "RDIN"}
)

#: The keywords whose block holds **other keywords** rather than lines: ``IF`` opens a conditional
#: whose body is a sequence of keywords and whose terminator is ``ENDIF``. That is a nested
#: structure this model does not have, so it is refused by name rather than written wrongly.
#: Keywords that read **one extra record** after their own. ``THINQFA`` is the one in this
#: variant: its own record carries the year and six parameters, and the record that follows names
#: the units of its residual-density target. ``cuts.f`` reads ``PRMS(1..6)`` from the six post-year
#: fields, which leaves ``QFATAR = INT(PRMS(7))`` for the supplemental record's value; the keyword
#: guide says the same.
SUPPLEMENTAL_KEYWORDS: frozenset[str] = frozenset({"THINQFA", "FUELMODL", "DEFULMOD"})

NESTED_KEYWORDS: frozenset[str] = frozenset({"IF"})

#: The fire-model keywords ``FMIN`` reads, from ``metric/fire/base/fmin.f``'s own table. They are
#: **not** top-level keywords: FVS accepts them only between ``FMIN`` and its ``END``, so the
#: validator refuses one that stands alone rather than writing a record FVS would ignore.
FMIN_KEYWORDS: frozenset[str] = frozenset(
    {
        "BURNREPT",
        "CANCALC",
        "CANFPROF",
        "CARBCALC",
        "CARBCUT",
        "CARBREPT",
        "CFIMCALC",
        "DEFULMOD",
        "DROUGHT",
        "DUFFPROD",
        "DWDCVOUT",
        "DWDVLOUT",
        "FIRECALC",
        "FLAMEADJ",
        "FMODLIST",
        "FMORTMLT",
        "FUELDCAY",
        "FUELFOTO",
        "FUELINIT",
        "FUELMODL",
        "FUELMOVE",
        "FUELMULT",
        "FUELOUT",
        "FUELPOOL",
        "FUELREPT",
        "FUELSOFT",
        "FUELTRET",
        "LANDOUT",
        "MOISTURE",
        "MOREOUT",
        "MORTCLAS",
        "MORTREPT",
        "PILEBURN",
        "POTFIRE",
        "POTFMOIS",
        "POTFPAB",
        "POTFSEAS",
        "POTFTEMP",
        "POTFWIND",
        "SALVAGE",
        "SALVSP",
        "SIMFIRE",
        "SNAGBRK",
        "SNAGCLAS",
        "SNAGDCAY",
        "SNAGFALL",
        "SNAGINIT",
        "SNAGOUT",
        "SNAGPBN",
        "SNAGPSFT",
        "SNAGSUM",
        "SOILHEAT",
        "STATFUEL",
        "SVIMAGES",
        "USECFIM",
    }
)

#: The block keywords whose body holds **other keywords** and is closed by ``END``. ``FMIN`` is the
#: one in this variant; its body is rendered with the same writer as any other keyword, so a
#: parameter is padded to FVS's ten-column field rather than hand-spaced.
KEYWORD_BLOCK_KEYWORDS: frozenset[str] = frozenset({"FMIN"})

#: Every keyword that takes a block of some kind.
BLOCK_KEYWORDS: frozenset[str] = LINES_KEYWORDS | NESTED_KEYWORDS | KEYWORD_BLOCK_KEYWORDS

#: The keywords that start a stand's setup. A ``DATABASE`` block must precede the first of them:
#: FVS refuses it later with ``FVS16 ERROR: KEYWORD ENTERED IS USED IN WRONG CONTEXT``, which is
#: what the official case avoids by putting the block first.
STAND_KEYWORDS: frozenset[str] = frozenset({"STDIDENT", "STDINFO", "STANDSQL"})

#: The keyword whose spelling is defective in FVS, at slot 30.
MISSPELLED_KEYWORD: str = "xSALVAGE"

#: The fire-model keywords whose report gate captures the inventory year. ``FUELOUT`` and
#: ``POTFIRE`` set ``IFLALB`` and ``IPFLMB`` to ``IY(1)`` when they are read, and ``fmdout.f`` and
#: ``fmpofl.f`` treat any positive value as "suppress this report". Read after ``INVYEAR``, they
#: therefore switch their own reports off, and the tables are never written.
YEAR_CAPTURING_KEYWORDS: frozenset[str] = frozenset({"FUELOUT", "POTFIRE"})

#: The warning the validator gives for a fire-model block that follows ``INVYEAR``.
FIRE_MODEL_ORDER_WARNING: str = (
    "an FMIN block that asks for FUELOUT or POTFIRE must precede INVYEAR: both capture the "
    "inventory year when they are read, and FVS treats a positive value as 'suppress this report', "
    "so the fuels and potfire tables would be silently not written"
)

#: The warning the validator gives for :data:`MISSPELLED_KEYWORD`.
MISSPELLING_WARNING: str = (
    f'The table spells this "{MISSPELLED_KEYWORD}", with a leading "x", because the defect is in '
    f'FVS itself. "SALVAGE" is not a keyword, so this is the spelling FVS matches.'
)


class UnknownKeywordError(ValueError):
    """A keyword that FVS's table does not hold."""


class KeywordWidthError(ValueError):
    """A parameter that FVS's ten-column field cannot carry."""


class UnsupportedKeywordError(ValueError):
    """A keyword whose content is a block, which this module does not write."""


class KeywordOrderError(ValueError):
    """A keyword FVS refuses in the position the set gives it."""


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
    lines : tuple of str, optional
        The body of a block keyword, one record per entry. Only :data:`LINES_KEYWORDS` take lines,
        and the writer adds the ``END`` that closes them.
    nested : tuple of Keyword, optional
        The body of a **conditional**, which holds keywords rather than lines. Only ``IF`` takes
        one, and the writer adds the ``ENDIF`` that closes it.
    otherwise : tuple of Keyword, optional
        The ``ELSE`` branch of a conditional.
    supplemental : tuple of str, optional
        The record FVS reads **after** this keyword's own. Only :data:`SUPPLEMENTAL_KEYWORDS` take
        one, and the writer does not close it: the record stands alone on its line.
    """

    name: str
    parameters: tuple[str, ...] = ()
    lines: tuple[str, ...] = ()
    nested: tuple[Keyword, ...] = ()
    otherwise: tuple[Keyword, ...] = ()
    supplemental: tuple[str, ...] = ()


#: The residual-density units a ``THINQFA`` supplemental record may name, and what each means.
THINQFA_UNITS: dict[str, str] = {
    "0": "basal area per acre",
    "1": "trees per acre",
    "2": "stand density index",
}


def _validate_supplemental(keyword: Keyword) -> None:
    """Check the one extra record a supplemental keyword reads.

    Parameters
    ----------
    keyword : Keyword
        The keyword, which is in :data:`SUPPLEMENTAL_KEYWORDS`.

    Raises
    ------
    UnsupportedKeywordError
        If the record is missing, if there is more than one, or if it does not name a unit. A
        missing record is refused rather than written, because FVS would read the **next
        keyword** as the units record and the set would be silently wrong.
    """
    if len(keyword.supplemental) != 1:
        raise UnsupportedKeywordError(
            f'"{keyword.name}" reads exactly one supplemental record, and this set gives '
            f"{len(keyword.supplemental)}: without it FVS reads the next keyword as that record"
        )
    if keyword.name in FMIN_KEYWORDS:
        # ``FUELMODL`` reads two more numbers and ``DEFULMOD`` seven fuel-model names, and FVS
        # parses both itself; only ``THINQFA``'s record has to be one of a fixed set of codes.
        return
    record = keyword.supplemental[0]
    if record not in THINQFA_UNITS:
        allowed = ", ".join(f"{code} ({meaning})" for code, meaning in THINQFA_UNITS.items())
        raise UnsupportedKeywordError(
            f'"{keyword.name}" takes a units code as its supplemental record, one of {allowed}; '
            f"this set gives {record!r}"
        )


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
    if (keyword.nested or keyword.otherwise) and (
        keyword.name not in NESTED_KEYWORDS | KEYWORD_BLOCK_KEYWORDS
    ):
        raise UnsupportedKeywordError(
            f'"{keyword.name}" does not take nested keywords; only '
            f"{', '.join(sorted(NESTED_KEYWORDS | KEYWORD_BLOCK_KEYWORDS))} does"
        )
    if keyword.lines and keyword.name not in LINES_KEYWORDS | NESTED_KEYWORDS:
        raise UnsupportedKeywordError(
            f'"{keyword.name}" does not take lines; only '
            f"{', '.join(sorted(LINES_KEYWORDS | NESTED_KEYWORDS))} do"
        )
    if keyword.supplemental and keyword.name not in SUPPLEMENTAL_KEYWORDS:
        raise UnsupportedKeywordError(
            f'"{keyword.name}" does not take a supplemental record; only '
            f"{', '.join(sorted(SUPPLEMENTAL_KEYWORDS))} does"
        )
    if keyword.name in SUPPLEMENTAL_KEYWORDS:
        _validate_supplemental(keyword)
    if keyword.name in FMIN_KEYWORDS:
        raise KeywordOrderError(
            f'"{keyword.name}" is a fire-model keyword, and FVS reads it only between FMIN and '
            "its END; put it in the block's nested keywords"
        )
    if keyword.name not in KEYWORDS and keyword.name not in SPECIAL_KEYWORDS:
        near = _near_miss(keyword.name)
        hint = f' The table spells it "{near}".' if near is not None else ""
        raise UnknownKeywordError(f'"{keyword.name}" is not a keyword.{hint}')
    if keyword.name not in RECORD_KEYWORDS:
        for parameter in keyword.parameters:
            _check_width(keyword.name, parameter)
    warnings: list[str] = []
    if keyword.name in NESTED_KEYWORDS:
        warnings.extend(validate_keywords(keyword.nested))
        warnings.extend(validate_keywords(keyword.otherwise))
    if keyword.name in KEYWORD_BLOCK_KEYWORDS:
        warnings.extend(_validate_fire_model_body(keyword.nested))
    if keyword.name == MISSPELLED_KEYWORD:
        warnings.append(MISSPELLING_WARNING)
    return warnings


def _validate_fire_model_body(entries: Sequence[Keyword]) -> list[str]:
    """Validate the keywords inside an ``FMIN`` block.

    Parameters
    ----------
    entries : Sequence of Keyword
        The block's body, in the order FVS reads it.

    Returns
    -------
    list of str
        Every warning the body raises. The fire-model keywords carry none of their own.

    Raises
    ------
    UnknownKeywordError
        On a name that is not in ``fmin.f``'s table. The message names the table's spelling when
        the name is a near miss.
    UnsupportedKeywordError
        On a fire-model keyword given lines or a nested block, which none of them take.
    KeywordWidthError
        On a parameter wider than FVS's ten-column field.
    """
    for entry in entries:
        if entry.name not in FMIN_KEYWORDS:
            near = _near_miss(entry.name)
            hint = f' The table spells it "{near}".' if near is not None else ""
            raise UnknownKeywordError(
                f'"{entry.name}" is not a fire-model keyword.{hint} An FMIN block holds only the '
                f"keywords fmin.f reads, and {len(FMIN_KEYWORDS)} are known"
            )
        if entry.lines or entry.nested or entry.otherwise:
            raise UnsupportedKeywordError(
                f'"{entry.name}" takes one record inside FMIN, and none of them takes lines or a '
                "nested block"
            )
        if entry.supplemental and entry.name not in SUPPLEMENTAL_KEYWORDS:
            raise UnsupportedKeywordError(
                f'"{entry.name}" takes no supplemental record; only '
                f"{', '.join(sorted(SUPPLEMENTAL_KEYWORDS & FMIN_KEYWORDS))} do"
            )
        if entry.supplemental:
            _validate_supplemental(entry)
        for parameter in entry.parameters:
            _check_width(entry.name, parameter)
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
    seen_stand = False
    seen_inventory = False
    for keyword in keywords:
        if keyword.name == "INVYEAR":
            seen_inventory = True
        if keyword.name == "FMIN" and seen_inventory:
            captures = any(entry.name in YEAR_CAPTURING_KEYWORDS for entry in keyword.nested)
            if captures:
                warnings.append(FIRE_MODEL_ORDER_WARNING)
        if keyword.name == "DATABASE" and seen_stand:
            raise KeywordOrderError(
                "a DATABASE block must precede the stand setup; FVS refuses it later with "
                "'KEYWORD ENTERED IS USED IN WRONG CONTEXT'. The official case puts it first"
            )
        if keyword.name in STAND_KEYWORDS:
            seen_stand = True
    for keyword in keywords:
        warnings.extend(validate_keyword(keyword))
    return warnings


def _check_width(name: str, parameter: str) -> None:
    """Refuse a parameter that FVS's ten-column field cannot carry.

    Parameters
    ----------
    name : str
        The keyword, for the message.
    parameter : str
        The parameter.

    Raises
    ------
    KeywordWidthError
        If the parameter is wider than :data:`FIELD_WIDTH`.
    """
    if len(parameter) > FIELD_WIDTH:
        raise KeywordWidthError(
            f'"{name}" has a parameter of {len(parameter)} characters, and FVS reads '
            f"{FIELD_WIDTH}: {parameter!r}"
        )


def render_keyword(keyword: Keyword) -> str:
    """Render one keyword as the record FVS reads for it.

    FVS reads a keyword from the first eight columns of a record and its parameters from ten-column
    fields of the same record, ``KARD(I)=RECORD(J:J+9)`` with ``J`` stepping by ten from eleven.
    So a parameter is a field, and the field is padded rather than separated by a delimiter. Two
    keywords are the exception and carry their content on the records that follow them:
    ``STDIDENT`` and ``TREEFMT``.

    Parameters
    ----------
    keyword : Keyword
        The keyword and its parameters.

    Returns
    -------
    str
        The keyword's record, ending with a newline, or the keyword and the records that follow it.

    Raises
    ------
    KeywordWidthError
        If a parameter is wider than the field FVS reads it from.
    """
    if keyword.name in RECORD_KEYWORDS:
        return "".join(f"{line}\n" for line in (keyword.name, *keyword.parameters))
    fields = []
    for parameter in keyword.parameters:
        _check_width(keyword.name, parameter)
        fields.append(f"{parameter:<{FIELD_WIDTH}}")
    head = f"{keyword.name:<{FIELD_WIDTH}}{''.join(fields)}".rstrip() + "\n"
    if keyword.name in NESTED_KEYWORDS:
        body = "".join(render_keyword(entry) for entry in keyword.nested)
        otherwise = ""
        if keyword.otherwise:
            otherwise = "ELSE\n" + "".join(render_keyword(entry) for entry in keyword.otherwise)
        lines = "".join(f"{line}\n" for line in keyword.lines)
        return head + lines + "THEN\n" + body + otherwise + "ENDIF\n"
    if keyword.name in LINES_KEYWORDS:
        return head + "".join(f"{line}\n" for line in keyword.lines) + "END\n"
    if keyword.name in KEYWORD_BLOCK_KEYWORDS:
        return head + "".join(render_keyword(entry) for entry in keyword.nested) + "END\n"
    if keyword.supplemental:
        return head + "".join(f"{record}\n" for record in keyword.supplemental)
    return head


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
        """Return the text that FVS would read for this set.

        Returns
        -------
        str
            The rendered set, with one token per line.
        """
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
