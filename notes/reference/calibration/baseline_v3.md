# W3.1 full-domain baseline

Status: first pass complete with the released 0.3.13 build
Date: 2026-11-03
Issue: #325
Build: `fresh-fvsbc-pyfvs 0.3.13` + `fresh-fvsbc 0.21.2`
Inputs: public FAIB PSP extract, four CSV files; raw tree rows stay outside the tracked tree

This is the uncalibrated reference, not a calibration. Each interval is grown from
its first PSP measurement with no cut and no calibration.

## 1. Dataset

The rebuild from the public extract produced:

| Table | Rows |
| --- | ---: |
| Sites | 7,341 |
| Visits | 23,956 |
| Plot visits | 13,966 |
| Intervals | 9,186 |
| Tree-survival rows | 1,031,828 |
| BEC coverage units | 153 |
| BEC envelope units | 121 |

The tree-level tables stay in `runtime/calibration`; only aggregates are tracked
here. The input SHA-256 values are in the runtime manifest.

## 2. Result

The baseline compares **108 intervals across 108 BEC units and skips none**.
W1.4 compared 89 and skipped 19. The 19 new units are exactly the W2.3 subzones:

`ESSFdh1`, `ESSFdv1`, `ESSFmv`, `ESSFmv1`–`ESSFmv4`, `ESSFvc`, `ESSFwh1`,
`ESSFwv`, `ESSFxv2`, `ICHvc`, `ICHxw`, `IDFdh`, `IDFxw`, `IDFxx2`, `MSxv`,
`SBSdh1`, `SBSun`.

The 89 W1.4 rows are unchanged to floating-point precision; the new units add
the only new rows.

### Initial stand

| Statistic | Value |
| --- | ---: |
| Mean initial BA bias | -0.87 m2/ha |
| Median initial BA bias | -0.60 m2/ha |
| Initial BA MAE | 0.95 m2/ha |

The tree-list reconstruction still reproduces the first measurement closely. The
end of the interval does not:

| Statistic | Value |
| --- | ---: |
| Median final BA bias | -2.77 m2/ha |
| Median final BA MAE | 5.69 m2/ha |
| Mean final BA bias excluding SBPS | -3.35 m2/ha |

The mean is dominated by three SBPS outliers and is not a useful central
tendency; the median is reported beside it.

### Envelope flags

- **1 interval above p99**: `SBSwk1`.
- **7 intervals above the observed maximum**: `IDFxx2`, `SBPSdc`, `SBPSmc`,
  `SBPSmk`, `SBSmc3`, `SBSun`, `SBSwk3`.
- W1.4 had 1 above p99 and 5 above max; the two new max flags are `IDFxx2` and
  `SBSun`.

`SBPSmc` reaches 11,214 m2/ha against 30.6 observed, and `SBPSdc` 4,705 against
11.2. Those are model failures, not capacity signals. The default mortality does
not remove enough small-tree density on those intervals. W4 owns the response.

## 3. Residual tables

The tracked aggregates are:

| File | Grouping |
| --- | --- |
| `baseline_summary_v3.csv` | BEC |
| `baseline_by_tsa_v3.csv` | BEC × TSA |
| `baseline_by_species_v3.csv` | BEC × species group |
| `baseline_by_dbh_v3.csv` | BEC × DBH class |
| `baseline_by_ba_v3.csv` | BEC × BA class |
| `baseline_skipped_becs_v3.csv` | BEC units with no interval |
| `baseline_skip_reasons_v3.csv` | Skip reasons |

The per-interval table stays in `runtime/baseline_w3_fixed` because `interval_id`
carries a site identifier. Each grouping has one row per BEC in this pass because
the sample is one interval per BEC; W3.2 deepens the sample before the atlas is
used for a domain ranking.

## 4. The resolver fix

The first run stopped on `KAM MSxk1/01`: FVS echoed `MSmm/01`. `HABTYP` matched
`MM` across the `KAM`+`MS` boundary before the real `XK` token. The fourth patch,
`w3-habtyp-boundary.patch.gz`, anchors the subzone token after the zone. The
108-interval run above uses that fixed build; `w3-bec-boundary.md` records the
finding and the tests.

## 5. Claim boundary

- This is a **baseline**, not a calibration.
- The sample is **one interval per BEC**. It is a coverage and failure-mode
  reference, not a representative estimate for a BEC.
- The envelope is empirical and not independent of the training plots.
- The five unsupported zones are absent; W2.2 recorded them as no-go without a
  parameter source.
- The fixed binary is released as `fresh-fvsbc-pyfvs 0.3.13`; the result is
  reproducible from PyPI with `fresh-fvsbc 0.21.2`.
