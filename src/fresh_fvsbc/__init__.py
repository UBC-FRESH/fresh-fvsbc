"""A Python wrapper for the BC variant of the Forest Vegetation Simulator.

This package is the public surface that ``fresh-fvsbc`` offers a caller. Its contracts are the
reference pages under ``docs/reference/``: the tree-list input, the keyword set, the outputs, the
provenance record, and the ``nemora`` ingestion.

The names re-exported here are the ones those pages name. Each module remains importable on its own,
so ``fresh_fvsbc.treelist.write_tree_record`` and ``fresh_fvsbc.write_tree_record`` are the same
function. The package is under construction, one bounded move at a time: every module lands with its
tests in the same change set, and the gates configured in ``pyproject.toml`` cover it.
"""

from __future__ import annotations

__version__ = "0.19.0"

from fresh_fvsbc.keywords import (
    Keyword,
    KeywordSet,
    UnknownKeywordError,
    keyword_set_hash,
    validate_keywords,
)
from fresh_fvsbc.nemora import (
    CrownRatioError,
    MissingAssignmentError,
    to_tree_list,
)
from fresh_fvsbc.outputs import (
    MissingOutputError,
    RunFailedError,
    UnknownTableError,
    check_run,
    read_cases,
    read_errors,
    read_table,
)
from fresh_fvsbc.provenance import (
    BuildError,
    Provenance,
    built_variants,
    from_cases,
    treelist_hash,
)
from fresh_fvsbc.run import (
    ExtensionUnavailableError,
    KeywordConflictError,
    RunError,
    RunResult,
    run_case,
    run_population,
)
from fresh_fvsbc.treelist import (
    AmbiguousSpeciesError,
    FieldWidthError,
    SpeciesError,
    UnknownSpeciesError,
    resolve_species,
    write_tree_list,
    write_tree_record,
)

__all__ = [
    "AmbiguousSpeciesError",
    "BuildError",
    "CrownRatioError",
    "ExtensionUnavailableError",
    "FieldWidthError",
    "Keyword",
    "KeywordConflictError",
    "KeywordSet",
    "MissingAssignmentError",
    "MissingOutputError",
    "Provenance",
    "RunError",
    "RunFailedError",
    "RunResult",
    "SpeciesError",
    "UnknownKeywordError",
    "UnknownSpeciesError",
    "UnknownTableError",
    "__version__",
    "built_variants",
    "check_run",
    "from_cases",
    "keyword_set_hash",
    "read_cases",
    "read_errors",
    "read_table",
    "resolve_species",
    "run_case",
    "run_population",
    "to_tree_list",
    "treelist_hash",
    "validate_keywords",
    "write_tree_list",
    "write_tree_record",
]
