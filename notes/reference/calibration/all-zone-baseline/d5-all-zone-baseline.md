# D5 all-zone baseline

Status: uncalibrated baseline; no parameter fitted
Date: 2026-11-03
Build: local `fresh-fvsbc-pyfvs 0.4.0` (five-zone prototype)
Sample: one interval per BEC, **139 BECs**, **139 intervals**, **0 skipped**
Data: `notes/reference/calibration/all-zone/` (all 153 BEC variants)

This is the first provincial measurement. It grows each interval from its first PSP measurement
with no cut and no calibration. It is not a certificate, and it does not support a growth-and-yield,
legal, AAC, or whole-block claim.

**D6 update (2026-11-03):** the SBPS rows in this report are superseded by
`d6-sbps-small-tree.md`. D6 found and fixed the `REGENT` model-selection defect, and the corrected
all-zone run has **139 intervals, 0 skipped, initial BA bias -0.69 / MAE 0.84, end BA bias -4.17 /
MAE 8.65**. The corrected SBPS rows are physically plausible but not calibrated; the D5
`457,348 m2/ha` row is the pre-fix overflow, not a model result to fit.

## 1. Overall

- **Initial stand:** BA bias **-0.69 m2/ha**, median **-0.49**, MAE **0.84 m2/ha**.
- **End of interval, excluding SBPS and envelope-flagged rows:** BA bias **-5.27 m2/ha**, median
  **-4.95**, MAE **8.45 m2/ha** (n=130).
- **End of interval, all rows:** the mean is **not usable**: `SBPSmc` predicts 457,348 m2/ha against
  30.6 observed. Report the median/MAE and the SBPS case, not the all-row mean.
- Envelope flags: **1 above p99**, **7 above the observed maximum**. Six of the seven are SBPS/SBS.

## 2. By zone

| Zone | Intervals | BA bias | BA MAE | TPH bias | TPH MAE | Above p99 | Above max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CWH | 21 | -9.46 | 11.75 | -151.63 | 262.57 | 0 | 0 |
| BWBS | 5 | -7.93 | 7.93 | -275.74 | 333.49 | 0 | 0 |
| CDF | 1 | -18.85 | 18.85 | -143.46 | 143.46 | 0 | 0 |
| CMA | 1 | -3.46 | 3.46 | -11.20 | 11.20 | 0 | 0 |
| MH | 3 | -11.94 | 11.94 | -334.63 | 334.63 | 0 | 0 |
| ICH | 26 | -3.03 | 6.02 | -586.28 | 841.10 | 0 | 0 |
| IDF | 18 | -3.27 | 3.90 | -1067.97 | 1149.75 | 0 | 1 |
| MS | 10 | -7.72 | 7.76 | -624.40 | 739.35 | 0 | 0 |
| ESSF | 30 | -8.09 | 10.94 | -734.31 | 1065.89 | 0 | 0 |
| SBS | 18 | 6.19 | 8.38 | 770.18 | 971.66 | 1 | 3 |
| SBPS | 4 | 116371.25 | 116383.45 | -1322.97 | 1330.42 | 0 | 3 |
| PP | 2 | 3.44 | 10.09 | 64.47 | 180.48 | 0 | 0 |

## 3. Five-zone detail

The five zones have **no envelope flags** in this sample. The zone aggregates are CWH -9.46 / 11.75,
BWBS -7.93 / 7.93, CDF -18.85 / 18.85, CMA -3.46 / 3.46, and MH -11.94 / 11.94 (BA bias / MAE). The
full per-BEC table is `baseline_five_zone.csv`; the largest single-interval deviations are
`CWHvm` +24.11 m2/ha, `CDFmm` -18.85, `MHmm2` -18.81, and `CWHws2` -20.64 with a TPH bias of -2840.79.

These are one interval per BEC. They are enough to say the donors run and do not explode; they are
not enough to decide which species needs a true table.

## 4. The SBPS failure

`SBPS` is the supported-zone emergency, not a five-zone problem:

| BEC | Observed BA1 | Predicted BA1 | Flag |
| --- | ---: | ---: | --- |
| `SBPSmc` | 30.65 | 457,348 | above max |
| `SBPSdc` | 11.23 | 4,705 | above max |
| `SBPSmk` | 32.72 | 3,531 | above max |
| `SBPSxc` | 34.39 | 10 | ok |

The initial stands are reproduced (19.35 → 19, 31.14 → 31, 34.66 → 34, 48.12 → 47), so the explosion
is in the growth/mortality path, not the tree-list construction. This is the first D6 target: the
small-tree density and mortality defaults for SBPS, not a coastal species table.

## 5. What this changes

- **SBPS is first in D6.** Three of four labels above max is a structural failure; adding coastal
  species will not fix it.
- **The five-zone donor prototype is viable.** No above-max flags and moderate BA MAE; the aliases
  work for every sampled species (0 skips).
- **The next five-zone sample is five intervals per BEC**, not one. That is enough to separate a donor
  failure from interval noise before promoting a species to a true table.
- **Species review candidates:** `CWHvm`, `CWHws2`, `CDFmm`, `MHmm2`.

## 6. Limits

- One interval per BEC; this is a stratified sample, not a provincial mean.
- The site series is `/01`; the per-plot site series is not in the extract.
- `SITECODE` uses `FD,20`; site index is not used by the variant.
- Tree age is the placeholder `--tree-age`.
- The seven missing species are donor aliases (`Ss`/`Sb`→`SE`, `Ba`→`BG`, `Hm`→`HW`, `Yc`→`CW`,
  `Dr`→`AT`, `Mb`→`AC`); the donor is not a calibrated species model.
- The five-zone `BAMAX` values are PSP p99 placeholders.
- Annual **net** change is the summary-level comparison; gross mortality is not requested.
- The envelope flag is an empirical sample property, not a biological maximum.

## 7. Artifacts

`baseline_summary.csv`, `baseline_by_zone.csv`, `baseline_five_zone.csv`, `baseline_by_tsa.csv`,
`baseline_by_species.csv`, `baseline_by_dbh.csv`, `baseline_by_ba.csv`, and `baseline_outliers.csv`
in `notes/reference/calibration/all-zone-baseline/`. The raw per-interval table stays outside the
repository because its `interval_id` carries a site identifier.
