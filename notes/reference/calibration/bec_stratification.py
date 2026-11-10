"""Audit BEC zone/subzone/variant strata as the ecological model hierarchy.

The audit tabulates intervals, sites, events, and species groups at three BEC
levels, then assigns each row to a pooled unit. It does not fit a model.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

DATA = Path("/srv/shared-data/gep/ws4/.opencode/tmp/opencode/psp4-growth/tree_survival.csv")
MIN_VARIANT = 5000
MIN_VARIANT_SITES = 20
MIN_SUBZONE = 10000
MIN_SUBZONE_SITES = 40
MIN_UNIT = 5000


def _parse_bec(value: object) -> tuple[str, str, str]:
    """Return zone, subzone, and variant from a BEC code."""
    text = str(value).strip()
    match = re.match(r"^([A-Z]+)([a-z]*)([0-9]*)$", text)
    if match:
        return match.group(1), match.group(2), match.group(3)
    fallback = re.match(r"^([A-Za-z]+)", text)
    zone = fallback.group(1).upper() if fallback else "UNKNOWN"
    return zone, "", ""


def _aggregate(frame: pd.DataFrame, level: str, key: list[str]) -> pd.DataFrame:
    """Return one aggregate row per stratum at a BEC level."""
    grouped = (
        frame.groupby(key, dropna=False)
        .agg(
            n=("dead", "size"),
            events=("dead", "sum"),
            sites=("site", "nunique"),
            intervals=("interval_id", "nunique"),
            groups=("group", "nunique"),
            min_group_n=("group", lambda values: int(values.value_counts().min())),
        )
        .reset_index()
    )
    grouped["level"] = level
    grouped["stratum"] = grouped[key].astype(str).agg("|".join, axis=1)
    grouped["event_rate"] = grouped["events"] / grouped["n"]
    return grouped


def main() -> None:
    """Write the stratification audit and pooled-unit table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("notes/reference/calibration/d9-bec-stratification.csv"),
    )
    parser.add_argument(
        "--units",
        type=Path,
        default=Path("notes/reference/calibration/d9-bec-strata.csv"),
    )
    args = parser.parse_args()

    frame = pd.read_csv(
        DATA,
        usecols=["interval_id", "BEC", "TSA_DESC", "group", "dead", "known", "exposure"],
    )
    frame = frame[(frame["known"] == 1) & (frame["exposure"] > 0)].copy()
    frame["group"] = frame["group"].astype(str).str.upper()
    frame.loc[~frame["group"].isin(["FD", "PL", "SE", "HW"]), "group"] = "OTHER"
    frame["site"] = frame["interval_id"].str.split("|").str[0]
    parsed = frame["BEC"].map(_parse_bec)
    frame["zone"] = [item[0] for item in parsed]
    frame["subzone"] = [f"{item[0]}{item[1]}" for item in parsed]
    frame["variant"] = frame["BEC"].astype(str).str.upper()

    levels = [
        _aggregate(frame, "zone", ["zone"]),
        _aggregate(frame, "subzone", ["subzone"]),
        _aggregate(frame, "variant", ["variant"]),
    ]
    audit = pd.concat(levels, ignore_index=True)
    audit = audit[
        [
            "level",
            "stratum",
            "n",
            "events",
            "event_rate",
            "sites",
            "intervals",
            "groups",
            "min_group_n",
        ]
    ].sort_values(["level", "n"], ascending=[True, False])
    args.output.write_text(audit.to_csv(index=False))

    zone_counts = audit[audit["level"] == "zone"].set_index("stratum")
    subzone_counts = audit[audit["level"] == "subzone"].set_index("stratum")
    variant_counts = audit[audit["level"] == "variant"].set_index("stratum")
    choices = []
    for row in frame.itertuples(index=False):
        variant = str(row.variant)
        subzone = str(row.subzone)
        zone = str(row.zone)
        if (
            variant in variant_counts.index
            and variant_counts.loc[variant, "n"] >= MIN_VARIANT
            and variant_counts.loc[variant, "sites"] >= MIN_VARIANT_SITES
        ):
            choices.append(("variant", variant))
        elif (
            subzone in subzone_counts.index
            and subzone_counts.loc[subzone, "n"] >= MIN_SUBZONE
            and subzone_counts.loc[subzone, "sites"] >= MIN_SUBZONE_SITES
        ):
            choices.append(("subzone", subzone))
        else:
            choices.append(("zone", zone if zone in zone_counts.index else "UNKNOWN"))
    frame["unit_level"] = [item[0] for item in choices]
    frame["unit"] = [item[1] for item in choices]
    unit_counts = frame["unit"].value_counts()
    small = frame["unit"].map(unit_counts) < MIN_UNIT
    frame.loc[small & (frame["unit_level"] != "zone"), "unit_level"] = "zone"
    frame.loc[small & (frame["unit_level"] == "zone"), "unit"] = frame.loc[
        small & (frame["unit_level"] == "zone"), "zone"
    ]
    units = (
        frame.groupby(["unit_level", "unit"], dropna=False)
        .agg(
            n=("dead", "size"),
            events=("dead", "sum"),
            sites=("site", "nunique"),
            intervals=("interval_id", "nunique"),
            groups=("group", "nunique"),
            min_group_n=("group", lambda values: int(values.value_counts().min())),
        )
        .reset_index()
    )
    units["event_rate"] = units["events"] / units["n"]
    units = units.sort_values("n", ascending=False)
    args.units.write_text(units.to_csv(index=False))
    print(f"wrote {args.output} and {args.units}")
    counts = units["unit_level"].value_counts()
    print(
        f"units: {len(units)}; variants: {counts.get('variant', 0)}; "
        f"subzones: {counts.get('subzone', 0)}; zones: {counts.get('zone', 0)}"
    )


if __name__ == "__main__":
    main()
