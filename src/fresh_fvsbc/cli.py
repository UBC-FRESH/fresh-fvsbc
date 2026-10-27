"""The command-line entry point.

This is the orchestration with a shell in front of it. It parses a population file and a keyword
set, calls :func:`fresh_fvsbc.run.run_population`, and turns the result into an exit code. It adds
no modelling, no defaults for the stand, and no keyword the caller did not write.

The exit codes separate the two ways a caller can be unhappy, because they call for different
actions:

- ``0`` the run completed and wrote its outputs;
- ``1`` the run was attempted and failed, which is worth reporting;
- ``2`` the input was wrong before any run, which is worth fixing.

``argparse`` already exits 2 for a usage error, so the third code is the convention rather than an
invention.

The command's one limit is that a parameter cannot contain a comma, because the comma separates the
fields of a keyword. The API has no such limit, and a caller who needs one uses the API.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from functools import partial
from pathlib import Path

from fresh_fvsbc.keywords import (
    KEYWORD_BLOCK_KEYWORDS,
    LINES_KEYWORDS,
    Keyword,
    KeywordWidthError,
    UnknownKeywordError,
    UnsupportedKeywordError,
)
from fresh_fvsbc.nemora import MissingAssignmentError, PopulationError
from fresh_fvsbc.outputs import MissingOutputError, OutputError, RunFailedError
from fresh_fvsbc.provenance import ProvenanceError
from fresh_fvsbc.run import (
    KEYWORD_FILE_NAME,
    PROVENANCE_FILE_NAME,
    ExtensionUnavailableError,
    KeywordConflictError,
    RunError,
    RunResult,
    run_population,
)
from fresh_fvsbc.treelist import SpeciesError

__all__ = ["EXIT_BAD_INPUT", "EXIT_FAILED_RUN", "EXIT_OK", "CommandInputError", "main"]

#: The run completed and wrote its outputs.
EXIT_OK: int = 0

#: The run was attempted and failed.
EXIT_FAILED_RUN: int = 1

#: The input was wrong before any run.
EXIT_BAD_INPUT: int = 2


class CommandInputError(ValueError):
    """Input the command cannot use, which is refused before a run is attempted.

    It is raised while the entries are parsed, inside the command's own ``try``, so the message
    reaches the caller rather than being replaced by ``argparse``'s generic one for a failed
    ``type=``.
    """


#: What the run raises when the input is wrong: a keyword FVS does not hold, one it cannot
#: carry, a species that does not resolve, a population record the adapter cannot read.
_INPUT_ERRORS: tuple[type[Exception], ...] = (
    CommandInputError,
    KeywordConflictError,
    KeywordWidthError,
    MissingAssignmentError,
    OSError,
    PopulationError,
    SpeciesError,
    UnknownKeywordError,
    UnsupportedKeywordError,
)

#: What the run raises when it was attempted and failed: an error row, no database, a bad
#: projection, no extension, or a run whose provenance cannot be recorded.
_RUN_ERRORS: tuple[type[Exception], ...] = (
    ExtensionUnavailableError,
    MissingOutputError,
    OutputError,
    ProvenanceError,
    RunError,
    RunFailedError,
)


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns
    -------
    argparse.ArgumentParser
        The parser for the command.
    """
    parser = argparse.ArgumentParser(
        prog="fresh-fvsbc",
        description="Run one FVS-BC case from a synthetic stem population.",
    )
    parser.add_argument(
        "population",
        type=Path,
        metavar="POPULATION",
        help="a JSON list of stem records: stand_id, dbh_cm, height_m, crown_ratio",
    )
    parser.add_argument(
        "--directory",
        type=Path,
        required=True,
        metavar="DIR",
        help="where the run writes; it is created if absent, and the run owns it",
    )
    parser.add_argument(
        "--species",
        required=True,
        metavar="CODE",
        help="the BC species code, which nemora does not supply",
    )
    parser.add_argument(
        "--tree-age",
        type=float,
        required=True,
        dest="tree_age",
        metavar="YEARS",
        help="the age at breast height, which nemora does not supply",
    )
    parser.add_argument(
        "--keyword",
        action="append",
        dest="entries",
        type=partial(_tagged, "keyword"),
        metavar="NAME[=FIELD,...][;RECORD]",
        help=(
            "one keyword, in the order given; the fields are FVS's own parameter fields, and "
            "a blank one is written as a gap, as in --keyword TIMEINT=,5. A keyword that reads a "
            "supplemental record takes it after a semicolon, as in "
            "--keyword THINQFA=1,0,24,0,1.4,2,100;1"
        ),
    )
    parser.add_argument(
        "--block",
        action="append",
        dest="entries",
        type=partial(_tagged, "block"),
        metavar="NAME[=FIELD,...][;RECORD]|LINE|LINE",
        help=(
            "one keyword that takes a block, in the order given; the fields come before the first "
            "|, and each | starts an entry, as in "
            '--block "DATABASE|DSNOut|FVSOut.db|ComputDB". FMIN takes keywords rather than lines, '
            'as in --block "FMIN|SNAGOUT=1|SNAGSUM=2|CARBREPT=2"'
        ),
    )
    parser.add_argument(
        "--key-name",
        default=KEYWORD_FILE_NAME,
        dest="key_name",
        metavar="NAME",
        help=f"the keyword file's name inside DIR (default: {KEYWORD_FILE_NAME})",
    )
    return parser


def _tagged(kind: str, text: str) -> tuple[str, str]:
    """Tag an entry with the option that produced it, so the two options keep their order.

    Parameters
    ----------
    kind : str
        ``"keyword"`` or ``"block"``.
    text : str
        The raw argument.

    Returns
    -------
    tuple of str
        The kind and the text, parsed later, because ``argparse`` replaces a ``type=`` callable's
        message with a generic one and the message is the useful part.
    """
    return kind, text


def _parse_keyword(text: str) -> Keyword:
    """Parse one ``--keyword`` argument.

    A keyword that reads a supplemental record takes it after a semicolon, so
    ``THINQFA=1,0,24,0,1.4,2,100;1`` gives the keyword its seven fields and the units record ``1``.

    Parameters
    ----------
    text : str
        The argument, as ``NAME``, ``NAME=FIELD,...`` or ``NAME=FIELD,...;RECORD``.

    Returns
    -------
    Keyword
        The keyword, its fields and its supplemental record, in order.

    Raises
    ------
    CommandInputError
        If the argument names no keyword.
    """
    body, _, record = text.partition(";")
    name, separator, fields = body.partition("=")
    name = name.strip()
    if not name:
        raise CommandInputError(f"--keyword needs a name, and got {text!r}")
    supplemental = (record.strip(),) if record else ()
    if not separator:
        return Keyword(name, supplemental=supplemental)
    return Keyword(name, tuple(fields.split(",")), supplemental=supplemental)


def _parse_block(text: str) -> Keyword:
    """Parse one ``--block`` argument.

    Parameters
    ----------
    text : str
        The argument, as ``NAME|LINE|LINE`` or ``NAME=FIELD,...|LINE|LINE``.

    Returns
    -------
    Keyword
        The keyword, its fields, and its lines.

    Raises
    ------
    CommandInputError
        If the argument names no keyword, or names one that takes no block of lines.
    """
    head, *entries = text.split("|")
    keyword = _parse_keyword(head)
    if keyword.name in KEYWORD_BLOCK_KEYWORDS:
        # The fire-model block holds keywords, so each entry is parsed as one and rendered by the
        # same writer as any other keyword. A raw line here would be spaced by hand, and a
        # mis-spaced field is read as a different number rather than refused.
        return Keyword(
            keyword.name, keyword.parameters, nested=tuple(_parse_keyword(e) for e in entries)
        )
    if keyword.name not in LINES_KEYWORDS:
        raise CommandInputError(
            f"--block names {keyword.name!r}, which does not take a block; use --keyword for it, "
            f"and --block for {', '.join(sorted(LINES_KEYWORDS | KEYWORD_BLOCK_KEYWORDS))}"
        )
    return Keyword(keyword.name, keyword.parameters, tuple(entries))


def _read_population(path: Path) -> list[Mapping[str, object]]:
    """Read a population file.

    Parameters
    ----------
    path : Path
        The JSON file, holding a list of stem records.

    Returns
    -------
    list of Mapping
        The records, ready for :func:`fresh_fvsbc.nemora.to_tree_list`.

    Raises
    ------
    CommandInputError
        If the file is not JSON, or does not hold a non-empty list of objects.
    """
    try:
        parsed: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CommandInputError(f"{path} is not JSON: {error}") from error
    if not isinstance(parsed, list):
        raise CommandInputError(f"{path} must hold a list of stem records")
    if not parsed:
        raise CommandInputError(f"{path} holds no stem records")
    records: list[Mapping[str, object]] = []
    for index, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise CommandInputError(f"{path}: record {index} is not an object")
        records.append({str(key): value for key, value in item.items()})
    return records


def _report(result: RunResult) -> str:
    """Render what a completed run wrote.

    Parameters
    ----------
    result : RunResult
        The run's result.

    Returns
    -------
    str
        One line per fact a caller needs to find the outputs again.
    """
    lines = [
        f"case {result.provenance.case_id}",
        f"ran {result.provenance.variant} in {result.directory}",
        f"summary: {len(result.summary)} rows, {len(result.summary.columns)} columns",
        f"warnings: {len(result.warnings)}",
        f"provenance: {result.directory / PROVENANCE_FILE_NAME}",
    ]
    return "\n".join(lines)


def _web_main(argv: Sequence[str]) -> int:
    """Hand a ``web`` invocation to the optional service.

    The import is lazy so the core install never needs FastAPI, and a missing extra is reported as
    input
    the command cannot use rather than a traceback.

    Parameters
    ----------
    argv : sequence of str
        The arguments after ``web``.

    Returns
    -------
    int
        The service's exit code, or ``2`` when the web extra is not installed.
    """
    try:
        from fresh_fvsbc.web.app import main as web_main
    except ImportError:
        print(
            "fresh-fvsbc: the web extra is not installed; run `pip install 'fresh-fvsbc[web]'`",
            file=sys.stderr,
        )
        return EXIT_BAD_INPUT
    return web_main(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run one case from the command line.

    Parameters
    ----------
    argv : sequence of str or None, optional
        Arguments to parse. ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        ``0`` for a completed run, ``1`` for a run that failed, and ``2`` for input the command
        cannot use.

    Notes
    -----
    ``fresh-fvsbc web ...`` is dispatched to :func:`fresh_fvsbc.web.app.main` before the run parser
    sees the arguments, so the optional service never changes how a run is invoked.
    """
    arguments = list(argv) if argv is not None else sys.argv[1:]
    if arguments[:1] == ["web"]:
        return _web_main(arguments[1:])
    args = _parser().parse_args(arguments)
    try:
        keywords = tuple(
            _parse_block(text) if kind == "block" else _parse_keyword(text)
            for kind, text in (args.entries or ())
        )
        population = _read_population(args.population)
        result = run_population(
            population,
            directory=args.directory,
            species=args.species,
            tree_age=args.tree_age,
            keywords=keywords,
            key_name=args.key_name,
        )
    except _INPUT_ERRORS as error:
        print(f"fresh-fvsbc: {error}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except _RUN_ERRORS as error:
        print(f"fresh-fvsbc: the run failed: {error}", file=sys.stderr)
        return EXIT_FAILED_RUN
    print(_report(result))
    return EXIT_OK
