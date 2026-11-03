"""The calibration bundle contract.

A calibration bundle is a versioned JSON document that names the build it is
valid for, the domain it covers, the parameters it applies, the evidence behind
them, and the reviewer who signed it. It is **data, not code**: the package
loads it, checks it, renders it into FVS keywords, and records its id in
provenance. It does not fit the parameters.

Why the pins are part of the bundle
-----------------------------------

A parameter set is reproducible only against the build that produced it. The
bundle names the PyFVS fork commit, the FVS source submodule commit, and the
variant; the loader refuses a bundle whose pins do not match the package. A
future pin is a new bundle, not an edit to an old one.

The domain
----------

``domain`` can name a region, a BEC, a species group, and a management regime.
An empty list means "no restriction" for that field. A run asks
:meth:`CalibrationBundle.check_domain` with the actual BEC, species groups, and
management, and the bundle refuses a run outside its domain.

The fields
----------

``parameters`` is a list of keyword records. Each has the FVS keyword, its raw
fields, the unit, the index of the field a bound applies to, and an optional
minimum and maximum. A value at a bound is a warning, not a pass: a parameter
that sits at its bound is a sign the model structure or the data do not
identify it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from fresh_fvsbc.bec import REGIONS, BecCode
from fresh_fvsbc.calibration import SPECIES_GROUPS
from fresh_fvsbc.ingrowth import IngrowthError, IngrowthModel
from fresh_fvsbc.keywords import (
    Keyword,
    KeywordSet,
    KeywordWidthError,
    UnknownKeywordError,
)
from fresh_fvsbc.provenance import FVS_SOURCE_COMMIT, PYFVS_COMMIT

__all__ = [
    "CALIBRATION_KEYWORDS",
    "MANAGEMENT_REGIMES",
    "BundleBoundsError",
    "BundleDomain",
    "BundleDomainError",
    "BundleError",
    "BundleParameter",
    "CalibrationBundle",
    "load_bundle",
]

#: The keywords a bundle may render. They are the calibration levers the pinned
#: variant supports; a bundle cannot invent a keyword the package does not know.
CALIBRATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "BAMAX",
        "SDIMAX",
        "SDICALC",
        "BAIMULT",
        "MORTMULT",
        "HTGMULT",
        "DGSTDEV",
        "CRNMULT",
        "FIXMORT",
        "MORTMSB",
    }
)

#: The management regimes a domain may name. ``managed`` means a treatment
#: keyword is present; the bundle does not infer a specific treatment.
MANAGEMENT_REGIMES: frozenset[str] = frozenset({"untreated", "managed"})

_BUNDLE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
_CHECKSUM = re.compile(r"^sha256:[0-9a-f]{64}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class BundleError(ValueError):
    """A bundle that cannot be loaded or applied."""


@dataclass(frozen=True, slots=True)
class BundleDomain:
    """The domain a bundle covers.

    An empty tuple means the field is unrestricted.

    Attributes
    ----------
    regions : tuple of str
        The accepted BC regions.
    becs : tuple of str
        The accepted BEC labels, such as ``IDFdk3`` or a zone such as ``IDF``.
    species_groups : tuple of str
        The accepted calibration groups.
    dbh_classes : tuple of tuple of float
        Inclusive DBH ranges in centimetres.
    management : tuple of str
        ``untreated``, ``managed``, or both.
    """

    regions: tuple[str, ...] = ()
    becs: tuple[str, ...] = ()
    species_groups: tuple[str, ...] = ()
    dbh_classes: tuple[tuple[float, float], ...] = ()
    management: tuple[str, ...] = ()


class BundleDomainError(BundleError):
    """A run outside the domain the bundle declares."""


class BundleBoundsError(BundleError):
    """A parameter outside the bounds the bundle declares."""


@dataclass(frozen=True, slots=True)
class BundleParameter:
    """One FVS keyword and the bounds on its numeric value.

    Parameters
    ----------
    keyword : str
        The FVS keyword, in the table's spelling.
    fields : tuple of str
        The raw parameter fields, in FVS's order.
    units : str
        The unit of the bounded value.
    value_index : int
        The zero-based index of the field the bounds apply to.
    bounds : tuple of float, optional
        The minimum and maximum, inclusive. ``None`` means no bound.
    """

    keyword: str
    fields: tuple[str, ...]
    units: str
    value_index: int
    bounds: tuple[float, float] | None

    def keyword_object(self) -> Keyword:
        """Return the :class:`~fresh_fvsbc.keywords.Keyword` this parameter renders.

        Returns
        -------
        Keyword
            The keyword and its fields.
        """
        return Keyword(self.keyword, self.fields)


@dataclass(frozen=True, slots=True)
class CalibrationBundle:
    """A validated calibration bundle.

    Parameters
    ----------
    bundle_id : str
        The stable identifier, such as ``kc-pilot-2026-11-02``.
    version : str
        The bundle's semantic version.
    pins : Mapping
        The build the bundle is valid for: ``pyfvs_commit``,
        ``fvs_source_commit``, and ``variant``.
    domain : BundleDomain
        The accepted regions, BECs, species groups, DBH classes, and management.
    parameters : tuple of BundleParameter
        The keywords the bundle renders.
    training : Mapping
        The data checksum, split, objective, and convergence record.
    review : Mapping
        The reviewer, date, and sign-off flag.
    claim : str
        The claim boundary, in one sentence.
    warnings : tuple of str
        Non-fatal findings, such as a parameter at a bound or an unsigned bundle.
    ingrowth : IngrowthModel, optional
        The natural-regeneration model the bundle carries, if any.
    """

    bundle_id: str
    version: str
    pins: Mapping[str, str]
    domain: BundleDomain
    parameters: tuple[BundleParameter, ...]
    training: Mapping[str, object]
    review: Mapping[str, object]
    claim: str
    warnings: tuple[str, ...] = ()
    ingrowth: IngrowthModel | None = None

    def ingrowth_keyword(
        self,
        *,
        bec: str,
        years: float,
        ba: float | None = None,
        qmd: float | None = None,
        cycles: int = 1,
        cycle_years: float | None = None,
        cycle: int = 1,
    ) -> Keyword | None:
        """Return the bundle's ``ESTAB`` block for a stand, if it has one.

        Parameters
        ----------
        bec : str
            The stand's BEC label.
        years : float
            The total interval length, in years.
        ba : float or None, optional
            The stand's initial BA, in m2/ha.
        qmd : float or None, optional
            The stand's initial QMD, in cm.
        cycles : int, optional
            The number of establishment cycles.
        cycle_years : float or None, optional
            The length of each cycle.
        cycle : int, optional
            The first cycle number.

        Returns
        -------
        Keyword or None
            The block, or ``None`` when the bundle carries no ingrowth model.
        """
        if self.ingrowth is None:
            return None
        return self.ingrowth.estab_keyword(
            bec=bec,
            years=years,
            ba=ba,
            qmd=qmd,
            cycles=cycles,
            cycle_years=cycle_years,
            cycle=cycle,
        )

    def render(self) -> tuple[Keyword, ...]:
        """Return the keywords the bundle applies, in contract order.

        Returns
        -------
        tuple of Keyword
            One keyword per parameter. The caller inserts them before the first
            ``PROCESS`` or ``STOP``; the run does not add them itself.
        """
        return tuple(parameter.keyword_object() for parameter in self.parameters)

    def record(self) -> dict[str, str]:
        """Return the two fields the provenance record carries.

        Returns
        -------
        dict
            ``calibration_id`` and ``calibration_version``.
        """
        return {
            "calibration_id": self.bundle_id,
            "calibration_version": self.version,
        }

    def check_domain(
        self,
        bec: BecCode,
        species_groups: Sequence[str],
        management: str = "untreated",
        dbh_values: Sequence[float] | None = None,
    ) -> None:
        """Refuse a run outside the bundle's declared domain.

        Parameters
        ----------
        bec : BecCode
            The run's validated BEC.
        species_groups : Sequence of str
            The calibration groups present in the run's tree list.
        management : str, optional
            ``untreated`` or ``managed``. Defaults to ``untreated``.
        dbh_values : Sequence of float, optional
            The DBHs present in the run. Required when the domain names DBH
            classes.

        Raises
        ------
        BundleDomainError
            If the BEC, region, species, management, or DBH is outside the domain.
        """
        regions = self.domain.regions
        if regions and bec.region not in regions:
            raise BundleDomainError(
                f"{self.bundle_id} covers regions {', '.join(regions)}, not {bec.region}"
            )
        becs = self.domain.becs
        label = f"{bec.zone}{bec.subzone}"
        if becs and label not in becs and bec.zone not in becs:
            raise BundleDomainError(f"{self.bundle_id} covers BECs {', '.join(becs)}, not {label}")
        accepted = self.domain.species_groups
        if accepted:
            outside = sorted(group for group in species_groups if group not in accepted)
            if outside:
                raise BundleDomainError(
                    f"{self.bundle_id} covers species groups {', '.join(accepted)}, "
                    f"not {', '.join(outside)}"
                )
        regimes = self.domain.management
        if regimes and management not in regimes:
            raise BundleDomainError(
                f"{self.bundle_id} covers management {', '.join(regimes)}, not {management}"
            )
        if self.domain.dbh_classes:
            if dbh_values is None:
                raise BundleDomainError(
                    f"{self.bundle_id} names DBH classes and the run did not provide DBHs"
                )
            outside_dbh = [
                value
                for value in dbh_values
                if not any(low <= value <= high for low, high in self.domain.dbh_classes)
            ]
            if outside_dbh:
                raise BundleDomainError(
                    f"{self.bundle_id} covers DBH classes {self.domain.dbh_classes}, "
                    f"not {sorted(set(outside_dbh))[:3]}"
                )

    @classmethod
    def from_record(cls, record: Mapping[str, object]) -> CalibrationBundle:
        """Validate a decoded JSON record and return the bundle.

        Parameters
        ----------
        record : Mapping
            The decoded bundle.

        Returns
        -------
        CalibrationBundle
            The validated bundle.

        Raises
        ------
        BundleError
            If a required field is missing or a value is outside its contract.
        BundleBoundsError
            If a parameter is outside its declared bounds.
        """
        required = {
            "bundle_id",
            "version",
            "pins",
            "domain",
            "parameters",
            "training",
            "review",
            "claim",
        }
        missing = sorted(required - set(record))
        if missing:
            raise BundleError(f"the bundle is missing {', '.join(missing)}")
        bundle_id = _string(record, "bundle_id")
        if _BUNDLE_ID.fullmatch(bundle_id) is None:
            raise BundleError(
                f"bundle_id {bundle_id!r} must be lower-case letters, digits, "
                "underscores, or hyphens"
            )
        version = _string(record, "version")
        if _VERSION.fullmatch(version) is None:
            raise BundleError(f"version {version!r} is not a semantic version")
        pins_raw = _mapping(record, "pins")
        pins = {
            "pyfvs_commit": _string(pins_raw, "pyfvs_commit"),
            "fvs_source_commit": _string(pins_raw, "fvs_source_commit"),
            "variant": _string(pins_raw, "variant"),
        }
        for key, expected in (
            ("pyfvs_commit", PYFVS_COMMIT),
            ("fvs_source_commit", FVS_SOURCE_COMMIT),
        ):
            actual = pins[key]
            if actual != expected:
                raise BundleError(
                    f"{key} {actual!r} is not the package's pin {expected!r}; "
                    "a bundle is valid only for the build it names"
                )
        if pins["variant"] != "bc":
            raise BundleError('the variant must be "bc"')

        domain = _domain(_mapping(record, "domain"))
        parameters = _parameters(record.get("parameters"))
        training = _training(_mapping(record, "training"))
        review = _review(_mapping(record, "review"))
        claim = _string(record, "claim")
        ingrowth_raw = record.get("ingrowth")
        ingrowth = None
        if ingrowth_raw is not None:
            if not isinstance(ingrowth_raw, Mapping):
                raise BundleError("ingrowth must be an object")
            try:
                ingrowth = IngrowthModel.from_record(ingrowth_raw)
            except IngrowthError as error:
                raise BundleError(str(error)) from error
        warnings: list[str] = []
        if not cast(bool, review["signed_off"]):
            warnings.append(f"{bundle_id} is not signed off; use it as a pilot, not a certificate")
        for parameter in parameters:
            if parameter.bounds is None:
                continue
            value = _value(parameter)
            if value in parameter.bounds:
                warnings.append(
                    f"{parameter.keyword} value {value} sits at a bound "
                    f"({parameter.bounds[0]} to {parameter.bounds[1]}); "
                    "a parameter at a bound is not identified"
                )
        return cls(
            bundle_id=bundle_id,
            version=version,
            pins=pins,
            domain=domain,
            parameters=parameters,
            training=dict(training),
            review=dict(review),
            claim=claim,
            warnings=tuple(warnings),
            ingrowth=ingrowth,
        )


def load_bundle(path: str | Path) -> CalibrationBundle:
    """Load and validate a bundle from a JSON file.

    Parameters
    ----------
    path : str or Path
        The bundle file.

    Returns
    -------
    CalibrationBundle
        The validated bundle.

    Raises
    ------
    BundleError
        If the file is missing, is not JSON, or is not a valid bundle.
    """
    source = Path(path)
    try:
        record = json.loads(source.read_text(encoding="utf-8"))
    except OSError as error:
        raise BundleError(f"cannot read {source}: {error}") from error
    except json.JSONDecodeError as error:
        raise BundleError(f"{source} is not JSON: {error}") from error
    if not isinstance(record, Mapping):
        raise BundleError(f"{source} must hold a JSON object")
    return CalibrationBundle.from_record(record)


def _string(record: Mapping[str, object], key: str) -> str:
    """Return a required string field, refusing a missing or non-string value."""
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BundleError(f"{key} must be a non-empty string")
    return value


def _mapping(record: Mapping[str, object], key: str) -> Mapping[str, object]:
    """Return a required mapping field, refusing a missing or non-mapping value."""
    value = record.get(key)
    if not isinstance(value, Mapping):
        raise BundleError(f"{key} must be an object")
    return value


def _strings(record: Mapping[str, object], key: str) -> tuple[str, ...]:
    """Return a list of strings, or an empty tuple when the key is absent."""
    value = record.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BundleError(f"domain.{key} must be a list of strings")
    return tuple(cast(list[str], value))


def _domain(record: Mapping[str, object]) -> BundleDomain:
    """Validate the domain block."""
    regions = _strings(record, "regions")
    becs = _strings(record, "becs")
    species_groups = _strings(record, "species_groups")
    management = _strings(record, "management")
    unknown_regions = sorted(set(regions) - set(REGIONS))
    if unknown_regions:
        raise BundleError(f"domain.regions has unknown values: {', '.join(unknown_regions)}")
    unknown_groups = sorted(set(species_groups) - set(SPECIES_GROUPS.values()))
    if unknown_groups:
        raise BundleError(f"domain.species_groups has unknown values: {', '.join(unknown_groups)}")
    unknown_management = sorted(set(management) - MANAGEMENT_REGIMES)
    if unknown_management:
        raise BundleError(f"domain.management has unknown values: {', '.join(unknown_management)}")
    dbh_raw = record.get("dbh_classes", [])
    if not isinstance(dbh_raw, list):
        raise BundleError("domain.dbh_classes must be a list of [min, max] pairs")
    dbh_classes: list[tuple[float, float]] = []
    for index, pair in enumerate(dbh_raw):
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or not all(isinstance(value, (int, float)) for value in pair)
        ):
            raise BundleError(f"domain.dbh_classes[{index}] must be a [min, max] pair of numbers")
        low, high = float(pair[0]), float(pair[1])
        if low >= high:
            raise BundleError(f"domain.dbh_classes[{index}] min must be below max")
        dbh_classes.append((low, high))
    return BundleDomain(
        regions=regions,
        becs=becs,
        species_groups=species_groups,
        dbh_classes=tuple(dbh_classes),
        management=management,
    )


def _parameters(value: object) -> tuple[BundleParameter, ...]:
    """Validate the parameter list."""
    if not isinstance(value, list):
        raise BundleError("parameters must be a list")
    parameters: list[BundleParameter] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise BundleError(f"parameters[{index}] must be an object")
        keyword = _string(item, "keyword")
        if keyword not in CALIBRATION_KEYWORDS:
            raise BundleError(
                f"parameters[{index}] keyword {keyword!r} is not one of "
                f"{', '.join(sorted(CALIBRATION_KEYWORDS))}"
            )
        fields_raw = item.get("fields")
        if not isinstance(fields_raw, list) or not all(
            isinstance(field, str) for field in fields_raw
        ):
            raise BundleError(f"parameters[{index}].fields must be a list of strings")
        fields = tuple(cast(list[str], fields_raw))
        units = _string(item, "units")
        value_index = item.get("value_index")
        if not isinstance(value_index, int) or value_index < 0:
            raise BundleError(f"parameters[{index}].value_index must be a non-negative integer")
        if value_index >= len(fields):
            raise BundleError(
                f"parameters[{index}].value_index {value_index} is past its {len(fields)} fields"
            )
        bounds_raw = item.get("bounds")
        bounds: tuple[float, float] | None = None
        if bounds_raw is not None:
            if not isinstance(bounds_raw, Mapping):
                raise BundleError(f"parameters[{index}].bounds must be an object")
            minimum = bounds_raw.get("min")
            maximum = bounds_raw.get("max")
            if not isinstance(minimum, (int, float)) or not isinstance(maximum, (int, float)):
                raise BundleError(f"parameters[{index}].bounds needs numeric min and max")
            if float(minimum) >= float(maximum):
                raise BundleError(f"parameters[{index}].bounds min must be below max")
            bounds = (float(minimum), float(maximum))
        parameter = BundleParameter(
            keyword=keyword,
            fields=fields,
            units=units,
            value_index=value_index,
            bounds=bounds,
        )
        try:
            KeywordSet((parameter.keyword_object(),))
        except (KeywordWidthError, UnknownKeywordError) as error:
            raise BundleError(f"parameters[{index}] is not a valid keyword: {error}") from error
        if bounds is not None:
            number = _value(parameter)
            if not (bounds[0] <= number <= bounds[1]):
                raise BundleBoundsError(
                    f"{keyword} value {number} is outside {bounds[0]} to {bounds[1]}"
                )
        parameters.append(parameter)
    return tuple(parameters)


def _value(parameter: BundleParameter) -> float:
    """Return the bounded field as a float, refusing a non-numeric value."""
    try:
        return float(parameter.fields[parameter.value_index])
    except ValueError as error:
        raise BundleError(
            f"{parameter.keyword} field {parameter.value_index} is not numeric: "
            f"{parameter.fields[parameter.value_index]!r}"
        ) from error


def _training(record: Mapping[str, object]) -> dict[str, object]:
    """Validate the training block."""
    checksum = _string(record, "data_checksum")
    if _CHECKSUM.fullmatch(checksum) is None:
        raise BundleError("training.data_checksum must be 'sha256:' followed by 64 hex digits")
    split = _string(record, "split")
    objective = _string(record, "objective")
    convergence = _mapping(record, "convergence")
    return {
        "data_checksum": checksum,
        "split": split,
        "objective": objective,
        "convergence": dict(convergence),
    }


def _review(record: Mapping[str, object]) -> dict[str, object]:
    """Validate the review block."""
    reviewer = _string(record, "reviewer")
    date = _string(record, "date")
    if _DATE.fullmatch(date) is None:
        raise BundleError("review.date must be YYYY-MM-DD")
    signed_off = record.get("signed_off")
    if not isinstance(signed_off, bool):
        raise BundleError("review.signed_off must be true or false")
    return {"reviewer": reviewer, "date": date, "signed_off": signed_off}
