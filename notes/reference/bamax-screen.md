# BAMAX screen: the cap against the measured envelope

Status: **screening only; no parameter changed.**

`BAMAX` is the variant's stand maximum basal area (m²/ha), set by BEC, subzone, and occasionally site
series in `canada/bc/sitset.f`. The mortality blend sends a `BA/BAMAX` share of the predicted
increment to mortality, so a stand at or above its cap cannot gain basal area. The table is therefore
part of the model, not a housekeeping value.

The screen parses the table and counts the PSP intervals that start above their BEC's cap in the
calibration dataset.

## Result

| Zone | Intervals | Share above cap | Mean overshoot (m²/ha) |
| --- | ---: | ---: | ---: |
| PP | 21 | 85.7% | 8.34 |
| ICH | 2,018 | 8.8% | 0.50 |
| SBS | 1,931 | 7.2% | 0.32 |
| IDF | 1,564 | 2.2% | 0.09 |
| CDF | 94 | 1.1% | 0.005 |
| CWH | 7,124 | 0.5% | 0.087 |
| MH | 31 | 1.4% | 0.008 |
| SBPS | 296 | 0.0% | 0.000 |
| BWBS | 710 | 0.5% | 0.020 |
| ESSF | 197 | 0.8% | 0.036 |
| MS | 792 | 1.2% | 0.019 |

The worst cells are `PPxh2` (cap 21, 86% of intervals above, mean +8.3 m²/ha) and `ICHwk1` (cap 67,
36% above, mean +2.1). `SBSmw` is 2.9% above a cap of 55; `CWHwh1` 14.5% above 115, mean +2.5.

## What it means

- **BAMAX does not explain the SBS bias.** Seven percent of SBS intervals sit above the cap and the
  mean overshoot is 0.3 m²/ha, too small for the −5.7 m²/ha held-out bias in the SBS fold. That bias
  is a growth/mortality problem in the zone rows, not the cap.
- **PP needs its own review.** `PPxh2` is capped at 21 m²/ha while the measured stands in the
  calibration sample average 29; almost every PP interval starts above the cap. PP is still on V3
  defaults and unsigned, so this is a margin to check when PP is calibrated, not a regression.
- **CWH's cap is not what moved its fold.** After the tree-count fix (see `tree-count-fix.md`), the
  CWH held-out bias is +0.15 m²/ha and only 0.5% of intervals start above the cap.

No parameter was changed: the caps are defensible as measured p99 values in every zone the folds
cover, and raising them would trade a small high-BA gain for worse mid-range mortality.

## Reproduce

`bamax_screen.py` (local) parses `sitset.f` and joins the intervals table; the per-BEC table is
`bamax-screen.csv`. The parser takes the last `BAMAX` assignment before the `BAMAX = 10.` fallback and
matches subzones longest-first.
