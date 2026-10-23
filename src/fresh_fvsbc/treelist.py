"""The FVS-BC tree-list writer.

``docs/reference/tree-list.rst`` is the contract. BC's record format is ``TREFMT``, read from
``canada/bc/blkdat.f``, and the field names are the corresponding PyFVS template names. This module
parses that format string rather than restating it, so the layout cannot drift from the contract.

``T1``, and why the layout is not the declared one
-------------------------------------------------

BC's format opens ``I4,T1,I7``. ``T1`` is FORTRAN's *absolute column* directive, so it targets
column 1, and ``tree_num`` is consequently read from columns 1 to 7 — its first four columns are
shared with ``plot_id``. Every later field begins four columns earlier than the declared widths
suggest, and the line occupies 69 columns rather than the 73 that the widths sum to.

Two pieces of evidence, both reproducible. ``gfortran`` reads ``(I4,T1,I7)`` from the character
string ``' 123  456  789  012 345'`` as ``123`` and ``1234``, where ``(I4,1X,I7)`` reads ``4567``;
FVS's own reader is an internal read of a whole line (``base/intree.f``), so ``T1`` positions within
it. And ``FVSso/sot03.tre``, the one tree list in the official corpus that relies on the default
format instead of declaring one, decodes into ``species`` ``WF``, ``diam`` 21.4, and ``live_ht`` 105
under this reading, and into the non-species text ``10WF`` under the other.

A consequence to state plainly: because ``plot_id`` and ``tree_num`` share columns 1 to 4, the
number FVS reads as the tree number is the digits of the plot id followed by the digits of the tree
number. It stays unique within a plot, which is what FVS requires, but it is a composite. Only a run
confirms this against BC's own reader, which is `P2.2`'s run.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from typing import TypedDict

__all__ = [
    "BC_TREFMT",
    "FIA_CODES",
    "FIELD_DESCRIPTORS",
    "FIELD_NAMES",
    "JSP_CODES",
    "PLANTS_SYMBOLS",
    "READ_COLUMNS",
    "RECORD_WIDTH",
    "WRITE_COLUMNS",
    "AmbiguousSpeciesError",
    "FieldWidthError",
    "SpeciesError",
    "TreeListFields",
    "UnknownSpeciesError",
    "resolve_species",
    "write_tree_list",
    "write_tree_record",
]

#: BC's tree-record format, from ``canada/bc/blkdat.f``, in ``BLOCK DATA BLKDAT``.
BC_TREFMT: str = "(I4,T1,I7,F6.0,I1,A3,F5.1,F4.1,2F5.1,F5.1,I1,3(I2,I2),2I1,I2,2I3,2I1,F3.0)"

#: The fields, in the order the format declares them. The names come from the corresponding PyFVS
#: template, and the contract page carries the same list beside the edit descriptors.
FIELD_NAMES: tuple[str, ...] = (
    "plot_id",
    "tree_num",
    "tree_count",
    "tree_history",
    "species",
    "diam",
    "dg_incr",
    "live_ht",
    "trunc_ht",
    "htg_incr",
    "crown_ratio",
    "damage1",
    "severity1",
    "damage2",
    "severity2",
    "damage3",
    "severity3",
    "tree_val",
    "tree_rx",
    "plot_slope",
    "plot_aspect",
    "plot_habitat",
    "plot_topo_pos",
    "plot_site_prep",
    "tree_age",
)

_TOKEN = re.compile(r"\d+\s*\([^)]*\)|\d*[AIF]\d+(?:\.\d+)?|T\d+")
_GROUPED_EDIT = re.compile(r"(\d+)\s*\(([^)]*)\)")
_REPEATED_EDIT = re.compile(r"(\d+)([AIF]\d+(?:\.\d+)?)")
_FIELD_EDIT = re.compile(r"([AIF])(\d+)(?:\.(\d+))?")


def _edits(fmt: str) -> list[str]:
    """Expand a FORTRAN format string into one entry per edit descriptor.

    The repetition forms are expanded: ``2I1`` becomes two ``I1`` entries, ``2F5.1`` two ``F5.1``
    entries, and ``3(I2,I2)`` six ``I2`` entries. Positioning directives such as ``T1`` are kept,
    because the layout depends on them.

    Parameters
    ----------
    fmt : str
        A FORTRAN format string, with or without its enclosing parentheses.

    Returns
    -------
    list of str
        One descriptor per field, in order.
    """
    entries: list[str] = []
    for token in _TOKEN.findall(fmt):
        grouped = _GROUPED_EDIT.fullmatch(token)
        if grouped is not None:
            inner = [part.strip() for part in grouped.group(2).split(",")]
            entries.extend(inner * int(grouped.group(1)))
            continue
        repeated = _REPEATED_EDIT.fullmatch(token)
        if repeated is not None:
            entries.extend([repeated.group(2)] * int(repeated.group(1)))
            continue
        entries.append(token)
    return entries


def _field_edit(edit: str) -> re.Match[str]:
    """Return the parsed edit descriptor, or raise if it is not one this writer supports.

    Parameters
    ----------
    edit : str
        One edit descriptor, such as ``I4`` or ``F5.1``.

    Returns
    -------
    re.Match
        The match, whose groups are the letter, the width, and the decimals.

    Raises
    ------
    ValueError
        If the descriptor is not an ``A``, ``I``, or ``F`` field.
    """
    match = _FIELD_EDIT.fullmatch(edit)
    if match is None:
        raise ValueError(f"unsupported edit descriptor {edit!r}")
    return match


def _descriptors() -> tuple[tuple[str | None, str], ...]:
    """Pair each field name with its edit descriptor, keeping positioning directives.

    Returns
    -------
    tuple of tuple
        ``(field, edit)`` pairs in order, where ``field`` is ``None`` for a positioning directive
        that names no field.
    """
    names: Iterator[str] = iter(FIELD_NAMES)
    return tuple(
        (None, edit) if edit.startswith("T") else (next(names), edit) for edit in _edits(BC_TREFMT)
    )


#: ``(field, edit)`` pairs in order. A field of ``None`` is a positioning directive.
FIELD_DESCRIPTORS: tuple[tuple[str | None, str], ...] = _descriptors()

#: Each field's edit descriptor.
_EDIT_OF: dict[str, str] = {field: edit for field, edit in FIELD_DESCRIPTORS if field is not None}


def _read_columns() -> dict[str, tuple[int, int]]:
    """Return the columns FVS reads each field from, honouring the positioning directives.

    Returns
    -------
    dict of str to tuple
        One ``(first, last)`` pair per field, 1-based and inclusive. ``T1`` resets the cursor, so
        ``tree_num`` starts at column 1 rather than after ``plot_id``.
    """
    columns: dict[str, tuple[int, int]] = {}
    cursor = 1
    for field, edit in FIELD_DESCRIPTORS:
        if field is None:
            cursor = int(edit[1:])
            continue
        width = int(_field_edit(edit).group(2))
        columns[field] = (cursor, cursor + width - 1)
        cursor += width
    return columns


#: The columns FVS reads each field from. ``tree_num`` overlaps ``plot_id``.
READ_COLUMNS: dict[str, tuple[int, int]] = _read_columns()


def _write_columns() -> dict[str, tuple[int, int]]:
    """Return the columns this writer places each field in.

    A field never overwrites what an earlier field has already written, so where a field's read span
    begins before the write cursor, the field is placed in the remainder of its span. That is what
    moves ``tree_num`` from its read span of columns 1 to 7 into columns 5 to 7.

    Returns
    -------
    dict of str to tuple
        One ``(first, last)`` pair per field, 1-based and inclusive.
    """
    placed: dict[str, tuple[int, int]] = {}
    cursor = 1
    for field, _ in FIELD_DESCRIPTORS:
        if field is None:
            continue
        first, last = READ_COLUMNS[field]
        placed[field] = (max(first, cursor), last)
        cursor = last + 1
    return placed


#: The columns this writer places each field in. ``tree_num`` is three columns wide here.
WRITE_COLUMNS: dict[str, tuple[int, int]] = _write_columns()

#: The width of a record, in columns. It is 69, not the 73 that the declared widths sum to, because
#: ``plot_id`` and ``tree_num`` share their first four columns.
RECORD_WIDTH: int = max(last for _, last in WRITE_COLUMNS.values())


class SpeciesError(ValueError):
    """A species code that this writer cannot resolve to one BC species."""


class UnknownSpeciesError(SpeciesError):
    """A species code that appears in none of BC's three lists."""


class AmbiguousSpeciesError(SpeciesError):
    """A species code that appears at more than one species position."""


class FieldWidthError(ValueError):
    """A value that does not fit the width its field has on the record."""


#: BC's species list, ``JSP`` in ``canada/bc/blkdat.f``, in order.
JSP_CODES: tuple[str, ...] = (
    "PW",
    "LW",
    "FD",
    "BG",
    "HW",
    "CW",
    "PL",
    "SE",
    "BL",
    "PY",
    "EP",
    "AT",
    "AC",
    "OC",
    "OH",
)

#: The parallel FIA numeric codes, ``FIAJSP``. ``202`` appears twice, for ``FD`` and for ``OC``.
FIA_CODES: tuple[str, ...] = (
    "119",
    "073",
    "202",
    "017",
    "263",
    "242",
    "108",
    "093",
    "019",
    "122",
    "375",
    "746",
    "747",
    "202",
    "376",
)

#: The parallel PLANTS symbols, ``PLNJSP``. ``SOFT`` and ``HARD`` are BC aggregates, not symbols.
PLANTS_SYMBOLS: tuple[str, ...] = (
    "PIMO3",
    "LAOC",
    "PSME",
    "ABGR",
    "TSHE",
    "THPL",
    "PICO",
    "PIEN",
    "ABLA",
    "PIPO",
    "BEPA",
    "POTR5",
    "POBAT",
    "SOFT",
    "HARD",
)


def _species_index() -> tuple[dict[str, str], dict[str, list[str]]]:
    """Index every accepted species spelling, keeping the ambiguous ones apart.

    Returns
    -------
    tuple of dict
        The spellings that resolve to one ``JSP`` code; and the spellings that do not, each mapped
        to the codes it could mean.
    """
    seen: dict[str, list[str]] = {}
    for codes in zip(JSP_CODES, FIA_CODES, PLANTS_SYMBOLS, strict=True):
        for spelling in codes:
            seen.setdefault(spelling.strip().upper(), []).append(codes[0])
    unique = {spelling: found[0] for spelling, found in seen.items() if len(found) == 1}
    ambiguous = {spelling: found for spelling, found in seen.items() if len(found) > 1}
    return unique, ambiguous


_SPECIES, _AMBIGUOUS_SPECIES = _species_index()


def resolve_species(code: str) -> str:
    """Resolve a species code from any of BC's three lists to a ``JSP`` code.

    Parameters
    ----------
    code : str
        A ``JSP`` code such as ``PW``, an FIA numeric code such as ``119``, or a PLANTS symbol such
        as ``PIMO3``. Case and surrounding whitespace are ignored.

    Returns
    -------
    str
        The ``JSP`` code for the species.

    Raises
    ------
    UnknownSpeciesError
        If the code appears in none of the three lists.
    AmbiguousSpeciesError
        If the code appears at more than one position, which ``202`` does because BC gives it to
        both ``FD`` and ``OC``. An ambiguous code is not resolved to a default.
    """
    key = code.strip().upper()
    if key in _AMBIGUOUS_SPECIES:
        candidates = ", ".join(_AMBIGUOUS_SPECIES[key])
        raise AmbiguousSpeciesError(f"species code {code!r} could mean any of {candidates}")
    if key not in _SPECIES:
        raise UnknownSpeciesError(f"species code {code!r} is not one of BC's 15 species")
    return _SPECIES[key]


class TreeListFields(TypedDict):
    """The tree-list fields of one record, as a caller supplies them.

    The values are the FVS side of the record. ``species`` is a code from any of BC's three lists,
    and the writer resolves it. ``crown_ratio`` is the single digit the field holds; which scale it
    is in is `nemora-ingest.rst`'s open question rather than this writer's.
    """

    plot_id: int
    tree_num: int
    tree_count: float
    tree_history: int
    species: str
    diam: float
    dg_incr: float
    live_ht: float
    trunc_ht: float
    htg_incr: float
    crown_ratio: int
    damage1: int
    severity1: int
    damage2: int
    severity2: int
    damage3: int
    severity3: int
    tree_val: int
    tree_rx: int
    plot_slope: int
    plot_aspect: int
    plot_habitat: int
    plot_topo_pos: int
    plot_site_prep: int
    tree_age: float


def _to_int(value: object) -> int:
    """Return ``value`` as an integer, rejecting anything that is not one.

    Parameters
    ----------
    value : object
        The value to convert.

    Returns
    -------
    int
        The value as an integer.

    Raises
    ------
    TypeError
        If the value is a boolean, or is not a number.
    ValueError
        If a float has a fractional part, so that converting it would truncate silently.
    """
    if isinstance(value, bool):
        raise TypeError(f"{value!r} is a boolean, not a number")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(f"{value!r} has a fractional part")
        return int(value)
    if isinstance(value, str):
        return int(value.strip())
    raise TypeError(f"{value!r} is not a number")


def _to_float(value: object) -> float:
    """Return ``value`` as a float, rejecting anything that is not a number.

    Parameters
    ----------
    value : object
        The value to convert.

    Returns
    -------
    float
        The value as a float.

    Raises
    ------
    TypeError
        If the value is a boolean, or is not a number.
    """
    if isinstance(value, bool):
        raise TypeError(f"{value!r} is a boolean, not a number")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value.strip())
    raise TypeError(f"{value!r} is not a number")


def _render(field: str, value: object) -> str:
    """Render one value as exactly the text that occupies its field.

    The width used is the field's width on the record, which for ``tree_num`` is narrower than its
    edit descriptor declares, because ``plot_id`` shares the field's opening columns.

    Parameters
    ----------
    field : str
        The field name.
    value : object
        The value to render.

    Returns
    -------
    str
        The rendered text, justified and padded to the field's width.

    Raises
    ------
    FieldWidthError
        If the value does not fit the width its field has on the record.
    """
    match = _field_edit(_EDIT_OF[field])
    first, last = WRITE_COLUMNS[field]
    width = last - first + 1
    letter, decimals = match.group(1), match.group(3)
    if letter == "A":
        text = f"{value!s}"[:width].ljust(width)
    elif letter == "I":
        text = f"{_to_int(value):>{width}d}"
    else:
        text = f"{_to_float(value):>{width}.{int(decimals or 0)}f}"
    if len(text) != width:
        raise FieldWidthError(
            f"{field} needs {len(text)} columns but has {width} on the record: {value!r}"
        )
    return text


def write_tree_record(fields: TreeListFields) -> str:
    """Write one tree record in BC's format.

    Parameters
    ----------
    fields : TreeListFields
        The tree-list fields of one tree.

    Returns
    -------
    str
        One fixed-width record, ``RECORD_WIDTH`` columns wide.

    Raises
    ------
    FieldWidthError
        If any value does not fit its field.
    SpeciesError
        If ``species`` is not one of BC's codes, or resolves to more than one.
    """
    line = [" "] * RECORD_WIDTH
    resolved: dict[str, object] = dict(fields)
    resolved["species"] = resolve_species(fields["species"])
    for field, _ in FIELD_DESCRIPTORS:
        if field is None:
            continue
        first, last = WRITE_COLUMNS[field]
        line[first - 1 : last] = _render(field, resolved[field])
    return "".join(line)


def write_tree_list(records: Sequence[TreeListFields]) -> str:
    """Write a tree list in BC's format, one record per line.

    Parameters
    ----------
    records : Sequence[TreeListFields]
        The trees, in the order to write them.

    Returns
    -------
    str
        The records, each on its own line and each ending with a newline.
    """
    return "".join(f"{write_tree_record(record)}\n" for record in records)
