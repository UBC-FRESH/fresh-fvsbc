"""Tests for the FVS-BC keyword-set validator.

They check the table against what ``base/keywds.f`` declares, the two direction of the ``xSALVAGE``
defect, and the hash that the run's provenance depends on.
"""

from __future__ import annotations

import pytest

from fresh_fvsbc.keywords import (
    BLANK_SLOTS,
    FIELD_WIDTH,
    FIRE_MODEL_ORDER_WARNING,
    FMIN_KEYWORDS,
    KEYWORD_TABLE,
    KEYWORDS,
    LINES_KEYWORDS,
    MISSPELLED_KEYWORD,
    MISSPELLING_WARNING,
    RECORD_KEYWORDS,
    SPECIAL_KEYWORDS,
    Keyword,
    KeywordOrderError,
    KeywordSet,
    KeywordWidthError,
    UnknownKeywordError,
    UnsupportedKeywordError,
    keyword_set_hash,
    render_keyword,
    render_keywords,
    validate_keyword,
    validate_keywords,
)

# Slots 1 to 20, transcribed from base/keywds.f.
FIRST_BLOCK: tuple[str, ...] = (
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
)

# Slots 136 to 150, which hold the last three blank slots.
LAST_BLOCK: tuple[str | None, ...] = (
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


def test_the_table_has_one_hundred_and_fifty_slots() -> None:
    """``TABLE`` is declared over 150 slots in blocks of twenty."""
    assert len(KEYWORD_TABLE) == 150


def test_the_table_names_one_hundred_and_forty_four_keywords() -> None:
    """Six slots are blank, and a blank slot is not a keyword."""
    assert len(KEYWORDS) == 144
    assert len(BLANK_SLOTS) == 6
    assert len(KEYWORDS) + len(BLANK_SLOTS) == len(KEYWORD_TABLE)


def test_the_blank_slots_are_the_six_that_are_blank() -> None:
    """The blanks are known by slot, so a shift cannot pass unnoticed."""
    assert BLANK_SLOTS == (114, 118, 120, 148, 149, 150)


def test_the_first_block_is_the_one_the_source_declares() -> None:
    """Slots 1 to 20, in order."""
    assert KEYWORD_TABLE[:20] == FIRST_BLOCK


def test_the_last_block_is_the_one_the_source_declares() -> None:
    """Slots 136 to 150, in order, blanks included."""
    assert KEYWORD_TABLE[135:] == LAST_BLOCK


def test_every_keyword_fits_a_character_eight_field() -> None:
    """``TABLE`` is ``CHARACTER*8``, so no name is longer, and none carries padding."""
    for name in KEYWORDS:
        assert 1 <= len(name) <= 8
        assert name == name.strip()


def test_the_misspelled_keyword_is_the_only_one_not_in_capitals() -> None:
    """``xSALVAGE`` is the table's only defect, and ``SALVAGE`` is not a keyword."""
    odd = sorted(name for name in KEYWORDS if name != name.upper())
    assert odd == [MISSPELLED_KEYWORD]
    assert MISSPELLED_KEYWORD in KEYWORDS
    assert MISSPELLED_KEYWORD[1:] == "SALVAGE"
    assert MISSPELLED_KEYWORD[1:] not in KEYWORDS


def test_a_table_keyword_validates_with_no_warning() -> None:
    """An ordinary keyword passes silently."""
    assert validate_keyword(Keyword("STDIDENT", ("101",))) == []


def test_an_unknown_keyword_is_rejected_and_named() -> None:
    """Rule 2: an unknown keyword is refused by name rather than passed through."""
    with pytest.raises(UnknownKeywordError, match='"ZZZZZZZZ" is not a keyword'):
        validate_keyword(Keyword("ZZZZZZZZ"))


def test_an_unknown_keyword_with_no_near_miss_carries_no_hint() -> None:
    """The refusal does not offer a spelling when the table holds nothing close."""
    with pytest.raises(UnknownKeywordError, match=r"^\"ZZZZZZZZ\" is not a keyword\.$"):
        validate_keyword(Keyword("ZZZZZZZZ"))


def test_the_misspelled_keyword_warns_rather_than_failing() -> None:
    """Rule 3: ``xSALVAGE`` is valid, because FVS matches it, and it warns."""
    assert validate_keyword(Keyword(MISSPELLED_KEYWORD)) == [MISSPELLING_WARNING]


def test_the_warning_says_the_defect_is_fvs_own() -> None:
    """The warning has to say which spelling FVS matches, since neither is obvious."""
    assert "leading" in MISSPELLING_WARNING
    assert "SALVAGE" in MISSPELLING_WARNING
    assert MISSPELLED_KEYWORD in MISSPELLING_WARNING


def test_the_intended_spelling_is_a_fire_model_keyword_not_a_top_level_one() -> None:
    """``SALVAGE`` is real, but only inside ``FMIN``; the top-level table spells it ``xSALVAGE``.

    The refusal names the context rather than the table's defect, because the defect is not the
    reason here: FVS holds both spellings, in two different tables, and the caller needs to know
    which one they are in.
    """
    with pytest.raises(KeywordOrderError, match="only between FMIN"):
        validate_keyword(Keyword("SALVAGE"))
    assert validate_keyword(Keyword("FMIN", nested=(Keyword("SALVAGE", ("1",)),))) == []


def test_a_case_difference_is_refused_and_points_at_the_table() -> None:
    """FVS compares with FORTRAN ``.EQ.``, which is case sensitive, so the lower-case name fails."""
    with pytest.raises(UnknownKeywordError, match='The table spells it "DATABASE"'):
        validate_keyword(Keyword("database"))


def test_a_set_collects_the_warnings_of_its_keywords() -> None:
    """Every warning is kept, in the order the keywords were checked."""
    warnings = validate_keywords(
        [Keyword("xSALVAGE"), Keyword("STDIDENT", ("101",)), Keyword(MISSPELLED_KEYWORD)]
    )
    assert warnings == [MISSPELLING_WARNING, MISSPELLING_WARNING]


def test_a_set_stops_at_the_first_unknown_keyword() -> None:
    """A set with an unknown keyword cannot run, so validation does not report past it."""
    with pytest.raises(UnknownKeywordError, match='"NOPE" is not a keyword'):
        validate_keywords([Keyword("STDIDENT"), Keyword("NOPE"), Keyword("ALSONOPE")])


def test_a_field_keyword_renders_ten_column_fields_on_its_own_record() -> None:
    """``keyrdr.f`` reads ``KARD(I)=RECORD(J:J+9)``, so a parameter is a field, not a line."""
    assert render_keyword(Keyword("VOLUME", ("FD", "17.5"))) == "VOLUME    FD        17.5\n"
    assert render_keyword(Keyword("TIMEINT", ("", "5"))) == "TIMEINT             5\n"


def test_each_field_starts_ten_columns_after_the_last() -> None:
    """The columns are the contract: a field one column out is a different parameter."""
    record = render_keyword(Keyword("VOLUME", ("FD", "17.5")))
    assert record.index("FD") == FIELD_WIDTH
    assert record.index("17.5") == 2 * FIELD_WIDTH


def test_a_keyword_without_parameters_renders_as_one_line() -> None:
    """A valueless keyword is one record, which is how FVS's own files carry them."""
    assert render_keyword(Keyword("ECHOSUM")) == "ECHOSUM\n"


def test_a_field_parameter_may_contain_spaces() -> None:
    """A field is read as text, so a space inside one does not end it."""
    assert render_keyword(Keyword("MGMTID", ("A B",))) == "MGMTID    A B\n"


def test_a_parameter_wider_than_the_field_is_refused() -> None:
    """A field is ten columns, so a longer parameter would be split into the next one."""
    statement = "SELECT * FROM FVS_StandInit WHERE Stand_ID = 'Fir.15'"
    with pytest.raises(KeywordWidthError, match="FVS reads 10"):
        render_keyword(Keyword("StandSQL", (statement,)))


def test_a_wide_parameter_is_refused_when_the_set_is_built() -> None:
    """The refusal comes at construction, before anything is written."""
    with pytest.raises(KeywordWidthError, match="11 characters"):
        KeywordSet((Keyword("MGMTID", ("elevenchars",)),))


def test_stdident_carries_its_title_on_the_following_record() -> None:
    """``initre.f`` reads the record after ``STDIDENT``, not a field of its own record."""
    assert render_keyword(Keyword("STDIDENT", ("101  the title",))) == "STDIDENT\n101  the title\n"


def test_the_tree_format_carries_its_lines_on_the_following_records() -> None:
    """``intree.f`` reads the two records after ``TREEFMT``, so its parameters are lines."""
    assert render_keyword(Keyword("TREEFMT", ("(I4,", "F3.0)"))) == "TREEFMT\n(I4,\nF3.0)\n"


def test_the_two_record_keywords_are_the_ones_the_reader_reads() -> None:
    """The set is what makes the renderer's two shapes possible, so it is asserted."""
    assert frozenset({"STDIDENT", "TREEFMT"}) == RECORD_KEYWORDS


def test_a_block_of_lines_renders_its_lines_and_its_terminator() -> None:
    """``COMPUTE`` takes a block ended by ``END``, and a block without one swallows the rest."""
    keyword = Keyword("COMPUTE", ("0",), ("SmVol = spmcdbh(3,0,0, 10.0, 16.7, 0,999,0)",))
    assert render_keyword(keyword) == (
        "COMPUTE   0\nSmVol = spmcdbh(3,0,0, 10.0, 16.7, 0,999,0)\nEND\n"
    )


def test_a_block_line_is_written_whole_rather_than_as_a_field() -> None:
    """A line is a record, not a ten-column field, so a long expression survives intact."""
    expression = "SmVol = spmcdbh(3,0,0, 10.0, 16.7, 0,999,0)"
    assert expression in render_keyword(Keyword("COMPUTE", (), (expression,)))


def test_every_line_block_is_accepted() -> None:
    """Each name in ``LINES_KEYWORDS`` takes lines, and each is a keyword FVS reads.

    The set has grown by discovery rather than by design: ``MISTOE`` in ``P26``, because the
    dwarf-mistletoe options live inside it, and ``RDIN`` in ``P33``. ``FMIN`` left the set in
    ``P50``: its body is keywords, and raw lines let a mis-spaced field be read as another number.
    """
    for name in sorted(LINES_KEYWORDS):
        assert validate_keyword(Keyword(name, lines=("x",))) == []


def test_a_mistoe_block_renders_its_lines_and_its_terminator() -> None:
    """``MISTOE`` is a block whose sub-keywords are not keywords, so a caller supplies the lines."""
    keyword = Keyword("MISTOE", (), ("MISTPINF        0        1       0.5",))
    assert render_keyword(keyword) == "MISTOE\nMISTPINF        0        1       0.5\nEND\n"


def test_a_database_block_must_precede_the_stand() -> None:
    """FVS refuses a ``DATABASE`` block after the stand, so the set is refused before it runs."""
    with pytest.raises(KeywordOrderError, match="must precede the stand setup"):
        KeywordSet((Keyword("STDIDENT", ("x",)), Keyword("DATABASE", (), ("Summary",))))


def test_a_database_block_first_is_accepted() -> None:
    """The official case puts the block first, and so must a caller."""
    rendered = KeywordSet(
        (Keyword("DATABASE", (), ("DSNOut", "FVSOut.db", "Summary")), Keyword("STDIDENT", ("x",)))
    ).render()
    assert rendered.startswith("DATABASE\nDSNOut\nFVSOut.db\nSummary\nEND\nSTDIDENT")


def test_a_conditional_renders_its_condition_then_body_then_endif() -> None:
    """``IF`` takes a condition, ``THEN``, the keywords and ``ENDIF``, as the official case does."""
    rendered = render_keyword(
        Keyword("IF", (), ("MOD(AGE,60) EQ 0",), (Keyword("THINBBA", ("0", "0.0")),))
    )
    assert rendered == "IF\nMOD(AGE,60) EQ 0\nTHEN\nTHINBBA   0         0.0\nENDIF\n"


def test_a_conditional_renders_its_else_branch() -> None:
    """An ``ELSE`` branch follows the body. No fixture in this repository uses one."""
    rendered = render_keyword(
        Keyword("IF", (), ("AGE GT 50",), (Keyword("ECHOSUM"),), (Keyword("NODEBUG"),))
    )
    assert rendered == "IF\nAGE GT 50\nTHEN\nECHOSUM\nELSE\nNODEBUG\nENDIF\n"


def test_a_conditional_validates_its_body() -> None:
    """An unknown keyword inside a conditional is refused like one outside it."""
    with pytest.raises(UnknownKeywordError, match="is not a keyword"):
        KeywordSet((Keyword("IF", (), ("AGE GT 50",), (Keyword("NOTAKEYWORD"),)),))


def test_nested_keywords_on_a_keyword_that_takes_none_are_refused() -> None:
    """A conditional body under a keyword that takes none would swallow the rest of the file."""
    with pytest.raises(UnsupportedKeywordError, match="does not take nested keywords"):
        validate_keyword(Keyword("ECHOSUM", nested=(Keyword("ECHOSUM"),)))


def test_lines_on_a_keyword_that_takes_none_are_refused() -> None:
    """A block written under a keyword that does not take one would swallow the rest of the file."""
    with pytest.raises(UnsupportedKeywordError, match="does not take lines"):
        validate_keyword(Keyword("ECHOSUM", lines=("x",)))


def test_a_set_with_a_compute_block_renders_the_block() -> None:
    """The set's text is what FVS reads, so the block has to survive the set."""
    rendered = KeywordSet((Keyword("COMPUTE", ("0",), ("MdVol = 1",)), Keyword("STOP"))).render()
    assert rendered == "COMPUTE   0\nMdVol = 1\nEND\nSTOP\n"


def test_stop_is_a_keyword_although_the_table_does_not_hold_it() -> None:
    """``keyrdr.f`` matches ``STOP`` before it consults the table, so a key file may end with it."""
    assert KEYWORDS.isdisjoint({"STOP"})
    assert "STOP" in SPECIAL_KEYWORDS
    assert KeywordSet((Keyword("STOP"),)).render() == "STOP\n"


def test_a_set_renders_as_the_concatenation_of_its_keywords() -> None:
    """The rendering is what a caller would hand to FVS."""
    keywords = [Keyword("STDIDENT", ("101",)), Keyword("ECHOSUM")]
    assert render_keywords(keywords) == "STDIDENT\n101\nECHOSUM\n"


def test_the_hash_is_stable_for_the_same_set() -> None:
    """The same set hashes the same way, which is what makes it provenance."""
    keywords = [Keyword("STDIDENT", ("101",)), Keyword("ECHOSUM")]
    assert keyword_set_hash(keywords) == keyword_set_hash(keywords)


def test_the_hash_changes_when_the_order_changes() -> None:
    """Order is part of the identity, because FVS processes a keyword set in order."""
    forward = [Keyword("STDIDENT", ("101",)), Keyword("ECHOSUM")]
    backward = [Keyword("ECHOSUM"), Keyword("STDIDENT", ("101",))]
    assert keyword_set_hash(forward) != keyword_set_hash(backward)


def test_the_hash_changes_when_a_parameter_changes() -> None:
    """A different value is a different set."""
    one = [Keyword("STDIDENT", ("101",))]
    two = [Keyword("STDIDENT", ("102",))]
    assert keyword_set_hash(one) != keyword_set_hash(two)


def test_the_hash_names_its_algorithm() -> None:
    """A reader of the provenance record should not have to know the algorithm already."""
    digest = keyword_set_hash([Keyword("ECHOSUM")])
    assert digest.startswith("sha256:")
    assert len(digest) == len("sha256:") + 64


def test_the_hash_is_over_the_rendered_text() -> None:
    """Two sets that render the same text hash the same, whatever built them."""
    keywords = [Keyword("STDIDENT", ("101",))]
    rebuilt = [Keyword("STDIDENT", ("101",))]
    assert render_keywords(keywords) == render_keywords(rebuilt)
    assert keyword_set_hash(keywords) == keyword_set_hash(rebuilt)


def test_a_keyword_set_validates_at_construction() -> None:
    """Rule 2 applies to the set, not only to a keyword: an unknown name cannot build one."""
    with pytest.raises(UnknownKeywordError, match='"NOPE" is not a keyword'):
        KeywordSet(keywords=(Keyword("NOPE"),))


def test_a_keyword_set_carries_its_warnings_rendering_and_digest() -> None:
    """The set is the object the contract describes: ordered, validated, and carrying a hash."""
    keywords = (Keyword(MISSPELLED_KEYWORD), Keyword("STDIDENT", ("101",)))
    keyword_set = KeywordSet(keywords=keywords)
    assert keyword_set.warnings == (MISSPELLING_WARNING,)
    assert keyword_set.render() == f"{MISSPELLED_KEYWORD}\nSTDIDENT\n101\n"
    assert keyword_set.digest == keyword_set_hash(keywords)
    assert keyword_set.keywords == keywords


def test_two_keyword_sets_with_the_same_keywords_are_equal() -> None:
    """A set is its contents, so a rebuilt set compares equal and hashes the same."""
    first = KeywordSet(keywords=(Keyword("ECHOSUM"),))
    second = KeywordSet(keywords=(Keyword("ECHOSUM"),))
    assert first == second
    assert first.digest == second.digest


def test_thinqfa_renders_its_supplemental_record_without_a_terminator() -> None:
    """``THINQFA`` reads one extra record, and the record stands alone: no ``END`` follows it."""
    keyword = Keyword("THINQFA", ("1", "0", "24", "0", "1.4", "2", "100"), supplemental=("1",))
    rendered = render_keyword(keyword)
    assert rendered.endswith("100       \n1\n") or rendered.endswith("100\n1\n")
    assert "END" not in rendered


def test_thinqfa_without_its_record_is_refused() -> None:
    """FVS would read the next keyword as the units record, so the set is refused instead."""
    with pytest.raises(UnsupportedKeywordError, match="exactly one supplemental record"):
        validate_keyword(Keyword("THINQFA", ("1", "0", "24", "0", "1.4", "2", "100")))


def test_thinqfa_with_two_records_is_refused() -> None:
    """One record is what FVS reads; a second would be read as a keyword and fail later."""
    with pytest.raises(UnsupportedKeywordError, match="exactly one"):
        validate_keyword(Keyword("THINQFA", (), supplemental=("1", "0")))


def test_thinqfa_takes_only_the_three_units_codes() -> None:
    """The units code is 0, 1 or 2, and the refusal names all three with their meaning."""
    for code in ("0", "1", "2"):
        assert validate_keyword(Keyword("THINQFA", (), supplemental=(code,))) == []
    with pytest.raises(UnsupportedKeywordError, match="basal area per acre"):
        validate_keyword(Keyword("THINQFA", (), supplemental=("3",)))


def test_a_supplemental_record_on_another_keyword_is_refused() -> None:
    """Only the keywords that read a second record may carry one, and the refusal names them."""
    with pytest.raises(UnsupportedKeywordError, match="does not take a supplemental record"):
        validate_keyword(Keyword("THINBA", ("1", "20"), supplemental=("1",)))


def test_the_fire_model_block_renders_its_keywords_with_fvs_fields() -> None:
    """``FMIN`` holds keywords, and each is written in FVS's ten-column fields.

    A hand-spaced line is the failure this prevents: ``SNAGCLAS  0.0   10.0  20.0`` reads as
    ``CLASS 2= 20.0`` rather than ``10.0``, and FVS reports no error for it.
    """
    block = Keyword(
        "FMIN",
        nested=(
            Keyword("SNAGCLAS", ("0.0", "10.0", "20.0", "40.0")),
            Keyword("CARBREPT", ("2",)),
        ),
    )
    assert render_keyword(block) == (
        "FMIN\nSNAGCLAS  0.0       10.0      20.0      40.0\nCARBREPT  2\nEND\n"
    )


def test_a_fire_model_keyword_outside_the_block_is_refused() -> None:
    """FVS reads these only between ``FMIN`` and its ``END``, so a loose one is a silent no-op."""
    with pytest.raises(KeywordOrderError, match="only between FMIN"):
        validate_keyword(Keyword("SNAGOUT", ("1",)))


def test_the_fire_model_block_refuses_a_name_fvs_does_not_hold() -> None:
    """The block's body is checked against ``fmin.f``'s own table, not against the top-level one."""
    with pytest.raises(UnknownKeywordError, match="not a fire-model keyword"):
        validate_keyword(Keyword("FMIN", nested=(Keyword("SNAGOUTT", ("1",)),)))


def test_the_fire_model_block_refuses_lines_and_nesting() -> None:
    """None of the fire-model keywords takes a block, so one that does is a mistake."""
    with pytest.raises(UnsupportedKeywordError, match="takes one record"):
        validate_keyword(Keyword("FMIN", nested=(Keyword("SNAGOUT", lines=("x",)),)))


def test_two_fire_model_keywords_take_a_supplemental_record() -> None:
    """``FUELMODL`` reads two more numbers and ``DEFULMOD`` seven fuel-model names."""
    block = Keyword(
        "FMIN",
        nested=(
            Keyword("DEFULMOD", ("1",), supplemental=("F1", "F2", "F3", "F4", "F5", "F6", "F7")),
        ),
    )
    assert "F7" in render_keyword(block)


def test_a_fire_model_keyword_with_a_supplemental_record_it_does_not_take_is_refused() -> None:
    """``SNAGOUT`` reads one record, so a second one would be read as the next keyword."""
    with pytest.raises(UnsupportedKeywordError, match="takes no supplemental record"):
        validate_keyword(Keyword("FMIN", nested=(Keyword("SNAGOUT", ("1",), supplemental=("2",)),)))


def test_the_block_holds_every_fire_model_keyword_fvs_declares() -> None:
    """The table is FVS's own, so a keyword it reads cannot be missing from the set."""
    assert len(FMIN_KEYWORDS) == 55
    for name in ("SNAGCLAS", "SNAGOUT", "SNAGSUM", "DWDVLOUT", "DWDCVOUT", "FUELOUT", "CARBREPT"):
        assert name in FMIN_KEYWORDS


def test_a_fire_model_block_after_invyear_warns_that_its_tables_will_be_missing() -> None:
    """``FUELOUT`` and ``POTFIRE`` capture the inventory year, and FVS reads a positive value as
    'suppress'. After ``INVYEAR`` they switch their own reports off, and nothing says so."""
    keywords = (
        Keyword("INVYEAR", ("2020",)),
        Keyword("FMIN", nested=(Keyword("FUELOUT", ("2",)),)),
    )
    assert validate_keywords(keywords) == [FIRE_MODEL_ORDER_WARNING]


def test_a_fire_model_block_before_invyear_does_not_warn() -> None:
    """Read first, the year is still zero, and the reports are written."""
    keywords = (
        Keyword("FMIN", nested=(Keyword("FUELOUT", ("2",)), Keyword("POTFIRE", ("2",)))),
        Keyword("INVYEAR", ("2020",)),
    )
    assert validate_keywords(keywords) == []


def test_a_block_that_captures_no_year_does_not_warn_after_invyear() -> None:
    """``CARBREPT`` does not capture the year, so its position does not matter."""
    keywords = (
        Keyword("INVYEAR", ("2020",)),
        Keyword("FMIN", nested=(Keyword("CARBREPT", ("2",)),)),
    )
    assert validate_keywords(keywords) == []
