"""Tests for the FVS-BC tree-list writer.

They cover three things: the layout the format string implies, the species resolution, and the
fields the writer refuses to write. The layout assertions are the load-bearing ones, because
``T1`` makes the writer's columns differ from the declared widths in a way that is invisible unless
something checks it.
"""

from __future__ import annotations

import re

import pytest

from fresh_fvsbc.treelist import (
    BC_TREFMT,
    FIA_CODES,
    FIELD_DESCRIPTORS,
    FIELD_NAMES,
    JSP_CODES,
    PLANTS_SYMBOLS,
    READ_COLUMNS,
    RECORD_WIDTH,
    WRITE_COLUMNS,
    AmbiguousSpeciesError,
    FieldWidthError,
    TreeListFields,
    UnknownSpeciesError,
    _to_float,
    _to_int,
    resolve_species,
    write_tree_list,
    write_tree_record,
)

# The contract page's field table, transcribed. The writer's own list must agree with it.
CONTRACT_FIELDS: tuple[str, ...] = (
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


def a_record(**overrides: object) -> TreeListFields:
    """Return a complete, valid tree record, with ``overrides`` applied."""
    record: TreeListFields = {
        "plot_id": 1,
        "tree_num": 7,
        "tree_count": 1.0,
        "tree_history": 0,
        "species": "PIMO3",
        "diam": 21.4,
        "dg_incr": 3.2,
        "live_ht": 105.0,
        "trunc_ht": 0.0,
        "htg_incr": 0.5,
        "crown_ratio": 7,
        "damage1": 0,
        "severity1": 0,
        "damage2": 0,
        "severity2": 0,
        "damage3": 0,
        "severity3": 0,
        "tree_val": 0,
        "tree_rx": 0,
        "plot_slope": 0,
        "plot_aspect": 0,
        "plot_habitat": 0,
        "plot_topo_pos": 0,
        "plot_site_prep": 0,
        "tree_age": 80.0,
    }
    record.update(overrides)  # type: ignore[typeddict-item]  # overrides are checked by each test
    return record


def test_the_field_names_match_the_contract_table() -> None:
    """The writer's fields are the contract's fields, in the contract's order."""
    assert FIELD_NAMES == CONTRACT_FIELDS


def test_the_format_expands_to_one_descriptor_per_field_plus_one_tab() -> None:
    """Every field has a descriptor, and ``T1`` is the only directive naming no field."""
    named = [field for field, _ in FIELD_DESCRIPTORS if field is not None]
    positional = [edit for field, edit in FIELD_DESCRIPTORS if field is None]
    assert named == list(FIELD_NAMES)
    assert positional == ["T1"]


def test_t1_puts_the_tree_number_back_at_column_one() -> None:
    """``T1`` is FORTRAN's absolute-column directive, so it targets column 1 and not column 6."""
    assert READ_COLUMNS["plot_id"] == (1, 4)
    assert READ_COLUMNS["tree_num"] == (1, 7)
    assert READ_COLUMNS["tree_count"] == (8, 13)
    assert READ_COLUMNS["tree_age"] == (67, 69)


def test_the_writer_places_the_tree_number_after_the_plot_id() -> None:
    """The writer cannot overwrite the plot id, so the tree number uses columns 5 to 7."""
    assert WRITE_COLUMNS["tree_num"] == (5, 7)
    assert WRITE_COLUMNS["plot_id"] == (1, 4)


def test_every_field_is_written_inside_the_span_fvs_reads() -> None:
    """A field's written span never runs past the span FVS reads it from."""
    for field in FIELD_NAMES:
        first, last = WRITE_COLUMNS[field]
        read_first, read_last = READ_COLUMNS[field]
        assert read_first <= first <= last == read_last


def test_the_written_spans_tile_the_record_with_no_gap_or_overlap() -> None:
    """The written spans cover every column exactly once, which is what makes a fixed-width line."""
    covered: list[int] = []
    for field in FIELD_NAMES:
        first, last = WRITE_COLUMNS[field]
        covered.extend(range(first, last + 1))
    assert sorted(covered) == list(range(1, RECORD_WIDTH + 1))


def test_the_record_is_sixty_nine_columns_not_seventy_three() -> None:
    """The declared widths sum to 73, but ``plot_id`` and ``tree_num`` share four columns."""
    declared = sum(
        int(match.group(1))
        for _, edit in FIELD_DESCRIPTORS
        if (match := re.fullmatch(r"[AIF](\d+)(?:\.\d+)?", edit)) is not None
    )
    assert declared == 73
    assert RECORD_WIDTH == 69
    assert declared - 4 == RECORD_WIDTH


def test_the_contract_format_string_is_the_one_that_was_read() -> None:
    """The format string is BC's, without its FORTRAN continuation wrapping."""
    assert BC_TREFMT.startswith("(I4,T1,I7,")
    assert BC_TREFMT.endswith("F3.0)")
    assert "\n" not in BC_TREFMT


def test_each_field_lands_in_the_columns_the_contract_gives_it() -> None:
    """A written record carries every value at its own column, checked one field at a time."""
    line = write_tree_record(
        a_record(
            plot_id=12,
            tree_num=7,
            tree_count=3.0,
            tree_history=1,
            species="FD",
            diam=21.4,
            dg_incr=3.2,
            live_ht=105.0,
            trunc_ht=0.0,
            htg_incr=0.5,
            crown_ratio=7,
            damage1=1,
            severity1=2,
            plot_slope=3,
            plot_aspect=180,
            plot_habitat=5,
            tree_age=80.0,
        )
    )
    assert len(line) == RECORD_WIDTH
    assert line[0:4] == "  12"
    assert line[4:7] == "  7"
    assert line[7:13] == "     3"
    assert line[13] == "1"
    assert line[14:17] == "FD "
    assert line[17:22] == " 21.4"
    assert line[22:26] == " 3.2"
    assert line[26:31] == "105.0"
    assert line[31:36] == "  0.0"
    assert line[36:41] == "  0.5"
    assert line[41] == "7"
    assert line[42:44] == " 1"
    assert line[44:46] == " 2"
    assert line[56:58] == " 3"
    assert line[58:61] == "180"
    assert line[61:64] == "  5"
    assert line[66:69] == " 80"


def test_a_record_read_back_the_way_fvs_reads_it() -> None:
    """Read with BC's format, the tree number FVS sees is the plot id followed by the tree number.

    This is the consequence of ``plot_id`` and ``tree_num`` sharing columns 1 to 4. The result stays
    unique within a plot, which is what FVS needs, and this test is what makes the composite visible
    rather than surprising.
    """
    line = write_tree_record(a_record(plot_id=12, tree_num=7))
    plot_as_fvs_reads_it = line[0:4]
    tree_as_fvs_reads_it = line[0:7]
    assert int(plot_as_fvs_reads_it) == 12
    assert int(tree_as_fvs_reads_it.replace(" ", "")) == 127


def test_every_jsp_code_resolves_to_itself() -> None:
    """A BC species code is accepted unchanged."""
    for code in JSP_CODES:
        assert resolve_species(code) == code


def test_every_plants_symbol_resolves_to_its_jsp_code() -> None:
    """A PLANTS symbol resolves to the BC species in the same position."""
    for symbol, jsp in zip(PLANTS_SYMBOLS, JSP_CODES, strict=True):
        assert resolve_species(symbol) == jsp


def test_every_fia_code_resolves_unless_it_appears_twice() -> None:
    """An FIA numeric code resolves, except the one BC gives to two species."""
    for fia, jsp in zip(FIA_CODES, JSP_CODES, strict=True):
        if fia == "202":
            continue
        assert resolve_species(fia) == jsp


def test_case_and_surrounding_whitespace_are_ignored() -> None:
    """A caller may write a code in lower case, or padded as FORTRAN stores it."""
    assert resolve_species("  pimo3 ") == "PW"
    assert resolve_species("pw") == "PW"
    assert resolve_species(" 119 ") == "PW"


def test_the_duplicate_fia_code_is_ambiguous_rather_than_defaulted() -> None:
    """``202`` means both ``FD`` and ``OC``, so it is refused instead of guessed at."""
    with pytest.raises(AmbiguousSpeciesError, match="could mean any of FD, OC"):
        resolve_species("202")


def test_an_unknown_species_code_is_refused() -> None:
    """A code in none of the three lists is an error, not a default."""
    with pytest.raises(UnknownSpeciesError, match="is not one of BC's 15 species"):
        resolve_species("ZZ")


def test_the_three_species_lists_agree_in_length() -> None:
    """BC declares 15 species in each of the three parallel lists."""
    assert len(JSP_CODES) == len(FIA_CODES) == len(PLANTS_SYMBOLS) == 15
    assert len(set(JSP_CODES)) == 15


def test_the_species_is_resolved_before_it_is_written() -> None:
    """A PLANTS symbol reaches the record as the BC species code."""
    line = write_tree_record(a_record(species="THPL"))
    assert line[14:17] == "CW "
    assert line[14:17].strip() == resolve_species("THPL")


def test_a_tree_number_too_wide_for_its_columns_is_refused() -> None:
    """The tree number has three columns, so a four-digit value cannot be written."""
    with pytest.raises(FieldWidthError, match="tree_num needs 4 columns but has 3"):
        write_tree_record(a_record(tree_num=1000))


def test_a_plot_id_too_wide_for_its_field_is_refused() -> None:
    """The plot id has four columns, so a five-digit value cannot be written."""
    with pytest.raises(FieldWidthError, match="plot_id needs 5 columns"):
        write_tree_record(a_record(plot_id=10000))


def test_a_diameter_too_wide_for_its_field_is_refused() -> None:
    """A value that overflows any field is refused, not truncated."""
    with pytest.raises(FieldWidthError, match="diam needs 7 columns but has 5"):
        write_tree_record(a_record(diam=10000.0))


def test_a_tree_list_puts_one_record_on_each_line() -> None:
    """The list writes a newline after every record, including the last."""
    text = write_tree_list([a_record(), a_record(tree_num=8)])
    lines = text.splitlines()
    assert len(lines) == 2
    assert text.endswith("\n")
    assert all(len(line) == RECORD_WIDTH for line in lines)


def test_an_empty_tree_list_writes_nothing() -> None:
    """No trees is an empty file rather than a blank line."""
    assert write_tree_list([]) == ""


def test_int_coercion_accepts_the_number_types_and_refuses_the_rest() -> None:
    """The integer boundary accepts integers and integral floats, and refuses the alternatives."""
    assert _to_int(7) == 7
    assert _to_int(7.0) == 7
    assert _to_int(" 7 ") == 7
    with pytest.raises(ValueError, match="has a fractional part"):
        _to_int(7.5)
    with pytest.raises(TypeError, match="is a boolean"):
        _to_int(True)
    with pytest.raises(TypeError, match="is not a number"):
        _to_int(None)


def test_float_coercion_accepts_the_number_types_and_refuses_the_rest() -> None:
    """The real boundary accepts integers, floats, and their text."""
    assert _to_float(7) == 7.0
    assert _to_float(7.5) == 7.5
    assert _to_float(" 7.5 ") == 7.5
    with pytest.raises(TypeError, match="is a boolean"):
        _to_float(False)
    with pytest.raises(TypeError, match="is not a number"):
        _to_float(None)
