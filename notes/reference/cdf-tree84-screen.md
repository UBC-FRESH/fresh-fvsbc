# CDF dense stand: the 2008–2024 BA jump is one keying error

Status: **diagnosed and screened; no shipped parameter changes; verified from PyPI in 0.41.19.** Tool: `--max-dbh-growth-rate`.

## 1. The record

The dense site `4002349` is one permanent 0.405 ha `PSP_R` plot; the plot header is identical at
2008 and 2024 (0.4046 ha main, 0.0900 ha subplot, blowup 2.47/11.11). The DBH tally limit is 2.0 cm
at both visits, so the DBH-limit break does not apply here.

One tree carries the jump. Tree 84 is a long-term Douglas-fir:

| Visit | Year | DBH (cm) | Height (m) |
| --- | ---: | ---: | ---: |
| 9 | 1977 | 84.1 | 46.2 |
| 10 | 1987 | 90.0 | 44.8 |
| 11 | 1997 | 94.9 | 45.7 |
| 12 | 2008 | **98.3** | 49.8 |
| 13 | 2024 | **401.7** | 58.3 |

A 98.3 cm tree growing to 401.7 cm in 16 years (19.0 cm/yr) while its height grows 8.5 m is a
keying error, not growth. The value is consistent with a typo for **101.7 cm** (98.3 + 3.4 cm,
3.4 cm over 16 years). With PHF 2.471, the 401.7 cm value contributes **31.3 m²/ha**; at 101.7 cm
it contributes 2.0 m²/ha.

## 2. The screen

`scripts/run_calibration_probe.py --max-dbh-growth-rate CM_PER_YEAR` matches live trees by
`TREE_NO` at both visits and drops any interval with a matched tree above the rate (or an end DBH
above 300 cm). `5.0` is the recommended screen for calibration: it catches this 19 cm/yr jump and
keeps the site's other fast tree (tree 253, 134.8 → 148.7 cm in 5 years, 2.78 cm/yr).

The screen writes `screened_intervals.csv`. On the CDF held-out fold it flags exactly one interval:

```
interval_id            BEC    SITE_IDENTIFIER  max_growth_cm_per_year  max_end_dbh_cm
4002349|1|2008|2024    CDFmm  4002349          18.962                  401.7
```

## 3. Held-out CDF fold

The held-out fold is the 16-interval CDF test set (six held-out sites, `--per-bec 30`) under
`cdf-v3` on engine 0.4.16:

| Treatment | Test intervals | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw fold | 16 | −1.87 | 3.01 | +11.0 | 50.6 |
| typo corrected (401.7 → 101.7) | 16 | — | **1.33** | +15.5 | 50.6 |
| interval screened | 15 | −0.12 | **1.34** | +15.5 | 50.2 |

The two treatments agree: the BA error on the interval falls from −28.1 to +1.2 m²/ha. The train
fold is unchanged (the affected interval is held out). **No shipped parameter changes**; the model's
BA prediction of 125 m²/ha is correct against the corrected observation of 123.8.

## 4. What remains

TPH is still low on the dense interval: model 462 vs observed 518 (−56), and the fold's TPH MAE is
~50. This is not a discontinuity; TPH moves 526 → 518 smoothly. Two real components:

- The fold applies **no recruitment** (`cdf-v3` has no ingrowth block). The recruitment v1 model
  predicts 13.5 TPH for this stand; the observed new trees contribute 50.6 TPH.
- The model still loses ~77 TPH to mortality over 16 years against ~59 observed.

Closing that needs a high-BA ingress/mortality calibration, not another data screen. The W30
mortality term stays as shipped; no parameter changed here.

## Reproduce

- Raw fold: `~/workspace/bwbs-work/probe_cdf_dense_current/`.
- Screened fold: `probe_cdf_dense_screened5/` (`--max-dbh-growth-rate 5.0`).
- Raw tree series: `faib_tree_detail.csv`, site 4002349, tree 84.
