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
