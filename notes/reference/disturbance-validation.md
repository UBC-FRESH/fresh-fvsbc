# Disturbance and post-disturbance on a calibrated zone

Status: **wiring and post-disturbance continuation validated on BWBS; not a disturbance calibration.**
Date: 2026-11-25. Build: W9 (W5–W9 applied), variant `bc`.

## What was run

One synthetic BWBS stand (`BWBSmw/01`, AT/PL/SE, 15 records each 120 TPH, DBH 6–28, BA 32 m2/ha),
projected 10 years three ways:

| Case | BA | Mean DBH | Tables written |
| --- | --- | --- | --- |
| control | 32 → 36 | 14.0 → 15.6 | summary, tree list |
| removal (`THINBBA 1 20`) | 32 → 24 | 14.0 → 14.1 | cut list 11 rows, ATRT list 5 rows |
| fire (`FMIN SIMFIRE`) | 32 → 15 | survivors remain | mortality 4, snag detail 3, snag summary 1, DWD volume 1, DWD cover 1, fuels 1, potfire 1, consumption 1, carbon 1 |

The control grows; the removal leaves a residual that continues to grow; the fire kills part of the
stand and the survivors continue. The disturbance writers fire on a zone with the W5–W9 tables, not
only on the synthetic default.

## Recipe notes

- The `FMIN` block must precede `INVYEAR`, or `FUELOUT` and `POTFIRE` capture the inventory year and
  suppress their own reports.
- The tables need both the `DATABASE` option and their trigger (`TREELIST`, `CUTLIST`, `ATRTLIST`).
- `SIMFIRE` was used at full severity; the resulting mortality is engine behaviour, not a BC fire
  validation.

## What this does and does not establish

It establishes that on a calibrated zone the disturbance options reach the writers, the expected
tables appear, and a post-disturbance stand remains and grows.

It does **not** establish that fire severity, consumption, or harvest response match BC observations.
That needs a validation dataset (fire perimeters/severity, harvested-block remeasurements, MPB
impacts) and is the next disturbance task. Until then, a disturbance run is **C** like the zone it
runs on, and the tables carry the engine's behaviour, not a calibrated claim.

## Reproduce

`scripts/` has no zone-specific disturbance case yet; the smoke case is the one above, and
`tests/test_disturbance_bwbs.py` encodes it behind `FVSBC_W5=1`.

## Validation input contract (prepared 0.41.21)

The observed side is a CSV with these columns:

| Column | Meaning |
| --- | --- |
| `SITE_IDENTIFIER` | PSP site id, matching `intervals.csv` |
| `DISTURBANCE_YEAR` | Year of the event |
| `DISTURBANCE_TYPE` | `fire`, `harvest`, `mpb`, or `windthrow` |
| `SEVERITY` | 0–1 fraction (0 = none, 1 = complete) |
| `EVENT_ID` | optional source identifier |

Header-only template: `notes/reference/calibration/disturbance-observations-template.csv`.
Check coverage (and later score BA/TPH) with:

```console
$ python scripts/validate_disturbance.py \
    --observations notes/reference/calibration/disturbance-observations-template.csv \
    --intervals <calibration-dir>
```

`--predictions` accepts one row per event with `DISTURBANCE_TYPE`, `SEVERITY`,
`observed_ba1`, `predicted_ba1`, `observed_tph1`, `predicted_tph1`; the harness
reports bias and MAE by type and severity. No BC fire/severity or
harvested-block observations are in the repository, so the template currently
reports zero events.

## Public observations materialized (0.41.22)

The BC Data Catalogue layers are public and resolvable through OpenMaps WFS:

| Layer | WFS typename |
| --- | --- |
| Fire Burn Severity - Historical | `pub:WHSE_FOREST_VEGETATION.VEG_BURN_SEVERITY_SP` |
| BC Wildfire Fire Perimeters - Historical | `pub:WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP` |
| Harvested Areas of BC (Consolidated Cutblocks) | `pub:WHSE_FOREST_VEGETATION.VEG_CONSOLIDATED_CUT_BLOCKS_SP` |

A South Coast AOI (CDF/CWH/MH sites) returned 150 burn-severity polygons, 692 fire perimeters and
7,840 cutblocks. Joining them to the PSP header points produced **24 events at 20 sites**: 20 fire
perimeters and 4 cutblocks. No burn-severity polygon covered a PSP point, so the fire events carry
`SEVERITY_SOURCE = perimeter-default` (1.0) until a severity-rated overlap exists. Two harvest
events fall inside calibration intervals.

`interval_coverage()` now reports events whose year lies between an interval's two visits, so the
harness reports both site coverage and usable calibration intervals. The observations CSV contains
PSP site ids and stays outside the repository; the tracked template remains header-only.

## Harness output on the public observations

```
"observations": 24, "matched_sites": 20, "by_type": {"fire": 20, "harvest": 4}
"events": 2, "intervals": 2, "sites": 2, "by_type": {"harvest": 2}
```
