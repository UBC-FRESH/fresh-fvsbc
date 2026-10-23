"""The provenance record.

``docs/reference/provenance.rst`` is the contract. A record names the two pinned inputs, the variant
and the build's variant list, a hash of the keyword set and one of the tree list, and the case id
and run datetime from ``FVS_Cases``.

The build's variant list is exposed at run time
-----------------------------------------------

The contract listed as unverified whether PyFVS exposes the built variant list. It does:
``pyfvs.list_variants()`` returns a mapping of variant name to the module it would import and a
status, and in this project's build it returns ``{'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}``.

The status is the useful part, because the contract records the list so that a mistaken build is
visible, and a variant whose status is not ``OK`` is exactly that. :func:`built_variants` turns the
report into the record's list and refuses a build that reported anything but ``OK``, rather than
recording a failure as a fact.

Why the hashes are not file hashes
----------------------------------

The contract is explicit that the two hashes are of a canonical serialization rather than of a file,
because a file hash moves with a trailing newline or a column width and would then report a
difference that is not one. The tree-list hash is therefore taken over the records' *values*, so
rewriting the same trees in a different width gives the same hash. The keyword hash is
:func:`fresh_fvsbc.keywords.keyword_set_hash`, which is taken over the text a set renders to; that
text is fully determined by the set, with no incidental whitespace, so it is canonical in the same
sense.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from fresh_fvsbc import __version__

__all__ = [
    "FVS_SOURCE_COMMIT",
    "PYFVS_COMMIT",
    "BuildError",
    "Provenance",
    "ProvenanceError",
    "built_variants",
    "from_cases",
    "treelist_hash",
]

#: The pinned PyFVS fork commit, from ADR 0004, read back from the clone rather than quoted.
PYFVS_COMMIT: str = "e95172b"

#: The pinned FVS source submodule commit, from ADR 0004, read back from the submodule.
FVS_SOURCE_COMMIT: str = "ef5fa847"

#: The two ``FVS_Cases`` columns the record carries.
_CASE_FIELDS: tuple[str, ...] = ("CaseID", "RunDateTime")


class ProvenanceError(Exception):
    """A run whose provenance cannot be recorded, which the contract calls a failure."""


class BuildError(ProvenanceError):
    """A build whose reported variant list holds a variant that did not import."""


def built_variants(report: Mapping[str, Mapping[str, str]]) -> tuple[str, ...]:
    """Turn PyFVS's variant report into the record's variant list.

    Parameters
    ----------
    report : Mapping
        What ``pyfvs.list_variants()`` returns: each variant name mapped to its module and its
        status.

    Returns
    -------
    tuple of str
        The variant names, sorted, so two records of the same build read alike.

    Raises
    ------
    BuildError
        If any variant's status is not ``OK``. The contract records this list so that a mistaken
        build is visible, and a variant that did not import is the case it is there to catch.
    """
    failed = sorted(name for name, info in report.items() if info.get("status") != "OK")
    if failed:
        raise BuildError(f"the build reported {', '.join(failed)} as not OK")
    return tuple(sorted(report))


def from_cases(row: Mapping[str, object]) -> tuple[str, str]:
    """Return the case id and run datetime that a ``FVS_Cases`` row carries.

    Parameters
    ----------
    row : Mapping
        One row from ``FVS_Cases``, as :func:`fresh_fvsbc.outputs.read_cases` returns it.

    Returns
    -------
    tuple of str
        The ``CaseID`` and the ``RunDateTime``.

    Raises
    ------
    ProvenanceError
        If the row carries neither. The contract makes provenance mandatory rather than optional, so
        a run that cannot supply these has not recorded its provenance.
    """
    missing = [field for field in _CASE_FIELDS if field not in row]
    if missing:
        raise ProvenanceError(f"FVS_Cases did not carry {', '.join(missing)}")
    return str(row["CaseID"]), str(row["RunDateTime"])


def treelist_hash(records: Sequence[Mapping[str, object]]) -> str:
    """Return the hash of a tree list's values.

    The hash is taken over the values rather than over the written text, so the same trees hash the
    same way at a different column width. That is what the contract asks for, and it is what keeps a
    change of record format from reading as a change of input.

    Parameters
    ----------
    records : Sequence of Mapping
        The tree list, in order, because order is part of what a run was given. A sequence of
        :class:`fresh_fvsbc.treelist.TreeListFields` is what a caller usually has.

    Returns
    -------
    str
        ``"sha256:"`` followed by the hexadecimal digest.
    """
    payload = json.dumps(
        [dict(record) for record in records], sort_keys=True, separators=(",", ":")
    )
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


@dataclass(frozen=True, slots=True)
class Provenance:
    """What a run records about itself, per the contract.

    Parameters
    ----------
    variant : str
        The variant that ran, which for this project is ``bc``.
    keyword_set_hash : str
        The hash of the keyword set, from :mod:`fresh_fvsbc.keywords`.
    treelist_hash : str
        The hash of the tree list, from :func:`treelist_hash`.
    case_id : str
        The ``CaseID`` from ``FVS_Cases``.
    run_datetime : str
        The ``RunDateTime`` from ``FVS_Cases``.
    fresh_fvsbc_version : str, optional
        The version of this package that ran. Defaults to the installed one.
    pyfvs_commit : str, optional
        The pinned PyFVS fork commit.
    fvs_source_commit : str, optional
        The pinned FVS source submodule commit.
    variant_list : tuple of str, optional
        The build's variant list, from :func:`built_variants`.
    random_seed : int, optional
        The seed, when the run used one.
    """

    variant: str
    keyword_set_hash: str
    treelist_hash: str
    case_id: str
    run_datetime: str
    fresh_fvsbc_version: str = __version__
    pyfvs_commit: str = PYFVS_COMMIT
    fvs_source_commit: str = FVS_SOURCE_COMMIT
    variant_list: tuple[str, ...] = ()
    random_seed: int | None = None

    def as_record(self) -> dict[str, object]:
        """Return the record as a JSON-ready mapping, in the contract's field order.

        Returns
        -------
        dict
            One key per field the contract lists. It carries no credential and no path, which
            contract rule 4 requires of a record that may be cited in a tracked file.
        """
        return {
            "fresh_fvsbc_version": self.fresh_fvsbc_version,
            "pyfvs_commit": self.pyfvs_commit,
            "fvs_source_commit": self.fvs_source_commit,
            "variant": self.variant,
            "variant_list": list(self.variant_list),
            "keyword_set_hash": self.keyword_set_hash,
            "treelist_hash": self.treelist_hash,
            "case_id": self.case_id,
            "run_datetime": self.run_datetime,
            "random_seed": self.random_seed,
        }

    def to_json(self) -> str:
        """Return the record as JSON, with a trailing newline.

        Returns
        -------
        str
            The record, formatted for a reader rather than for a machine.
        """
        return json.dumps(self.as_record(), indent=2) + "\n"

    def write(self, path: str | Path) -> Path:
        """Write the record beside a run's outputs, as JSON.

        Parameters
        ----------
        path : str or Path
            Where to write it. The contract puts it beside the outputs.

        Returns
        -------
        Path
            The path written.
        """
        destination = Path(path)
        destination.write_text(self.to_json())
        return destination
