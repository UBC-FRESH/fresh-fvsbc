# CDF high-BA tree-level survival: no usable signal

Status: **negative.** The survival model does not validate; no engine or bundle change ships.

## 1. The trees

The four target intervals (BA ≥60, QMD 29–33) contain **157 tree records and 2 dead trees**. A
wider band (BA ≥50, QMD 27–35) gives **830 trees and 31 dead trees at four sites**; that is the
largest defensible sample.

Mortality is concentrated in small stems:

| DBH class | Trees | Dead | Dead rate |
| --- | ---: | ---: | ---: |
| ≤10 cm | 39 | 3 | 7.7% |
| 10–20 cm | 138 | 17 | 12.3% |
| 20–30 cm | 317 | 11 | 3.5% |
| 30–50 cm | 301 | 0 | 0.0% |
| ≥50 cm | 35 | 0 | 0.0% |

## 2. The model

Logistic survival with DBH, DBH², stand QMD and stand BA, PHF weights and a small ridge penalty.
Leave-one-site-out across the four band sites:

| Held-out site | Trees | Dead | AUC | Brier |
| --- | ---: | ---: | ---: | ---: |
| dense >100 m²/ha site | 547 | 25 | **0.375** | 0.0446 |
| site B | 106 | 2 | 0.579 | 0.0196 |
| site C | 81 | 3 | 0.449 | 0.0358 |
| site D | 96 | 1 | 0.758 | 0.0104 |
| **pooled** | 830 | 31 | **0.356** | **0.0366** |

The intercept-only dead rate is 3.73% with Brier 0.0373. The model has no skill; on the dense site
it ranks mortality worse than random.

## 3. Expanded clean fold

Fit on the band, predict every tree in the 31-test / 52-train expanded fold (7,879 trees, 844 dead):

| Population | Trees | Dead | AUC | Brier |
| --- | ---: | ---: | ---: | ---: |
| full fold | 7,879 | 844 | 0.606 | 0.0996 |
| high-BA/QMD subset | 830 | 31 | **0.356** | 0.0333 |
| intercept baseline | 7,879 | 844 | — | 0.1005 |

The full-fold AUC is weak and the high-BA subset is worse than random. The apparent full-fold skill
comes from low-BA stands, not the target band.

## 4. Consequence

No tree-level survival term ships. The CDF high-BA TPH residual is not a survival-model problem:
the observed small-tree mortality is high but is offset by ingress, and 31 events at four sites
cannot support a tree-level model. The gate for revisiting CW height (a validated CDF survival
model) is not met, so no CW work is done in this step.

The next fair line is **ingress/recruitment** in the high-BA band, or accepting the residual as a
documented limit. No release; the shipped package remains 0.41.22 / engine 0.4.16.

## Reproduce

- Fit/validation: `~/workspace/bwbs-work/fit_cdf_survival.py`.
- Data: `calib/tree_survival.csv`, `calib/intervals.csv`.
- Expanded fold: `probe_cdf_base_expanded/probe.csv`.
