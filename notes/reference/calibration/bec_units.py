"""Assign rows to pooled BEC ecological units.

The thresholds match D9.107: variant if large enough, otherwise parent subzone,
otherwise parent zone; remaining small units fall back to zone.
"""

from __future__ import annotations

import re

import pandas as pd

MIN_VARIANT = 5000
MIN_VARIANT_SITES = 20
MIN_SUBZONE = 10000
MIN_SUBZONE_SITES = 40
MIN_UNIT = 5000


def parse_bec(value: object) -> tuple[str, str, str]:
    """Return zone, subzone, and variant from a BEC code."""
    text = str(value).strip()
    match = re.match(r"^([A-Z]+)([a-z]*)([0-9]*)$", text)
    if match:
        return match.group(1), match.group(2), match.group(3)
    fallback = re.match(r"^([A-Za-z]+)", text)
    zone = fallback.group(1).upper() if fallback else "UNKNOWN"
    return zone, "", ""


def assign_units(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with BEC zone, subzone, variant, and pooled unit columns."""
    result = frame.copy()
    result["site"] = result["interval_id"].str.split("|").str[0]
    parsed = result["BEC"].map(parse_bec)
    result["bec_zone"] = [item[0] for item in parsed]
    result["bec_subzone"] = [f"{item[0]}{item[1]}" for item in parsed]
    result["bec_variant"] = result["BEC"].astype(str).str.upper()
    counts = result.groupby("bec_variant").agg(n=("dead", "size"), sites=("site", "nunique"))
    subzone_counts = result.groupby("bec_subzone").agg(
        n=("dead", "size"), sites=("site", "nunique")
    )
    choices = []
    for row in result.itertuples(index=False):
        variant = str(row.bec_variant)
        subzone = str(row.bec_subzone)
        zone = str(row.bec_zone)
        if (
            variant in counts.index
            and counts.loc[variant, "n"] >= MIN_VARIANT
            and counts.loc[variant, "sites"] >= MIN_VARIANT_SITES
        ):
            choices.append(("variant", variant))
        elif (
            subzone in subzone_counts.index
            and subzone_counts.loc[subzone, "n"] >= MIN_SUBZONE
            and subzone_counts.loc[subzone, "sites"] >= MIN_SUBZONE_SITES
        ):
            choices.append(("subzone", subzone))
        else:
            choices.append(("zone", zone))
    result["unit_level"] = [item[0] for item in choices]
    result["unit"] = [item[1] for item in choices]
    unit_counts = result["unit"].value_counts()
    small = result["unit"].map(unit_counts) < MIN_UNIT
    result.loc[small & (result["unit_level"] != "zone"), "unit_level"] = "zone"
    result.loc[small & (result["unit_level"] == "zone"), "unit"] = result.loc[
        small & (result["unit_level"] == "zone"), "bec_zone"
    ]
    return result
