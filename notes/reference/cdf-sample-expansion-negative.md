# CDF high-BA sample expansion: the inventory is already exhausted

Status: **data block.** No engine or bundle change ships.

## 1. Where the CDF intervals come from

- FAIB header: **26 CDF sites**.
- Sites with at least two visits: **21**.
- The calibration dataset contains **all 21** repeat sites and **94 intervals**.
- The 30-per-BEC cap is only the probe's `select_intervals`; `--per-bec 200` reads all 94.

So expanding beyond 30 per BEC does not add CDF sites or intervals. It only changes the sample
from 30 to 94.

## 2. How many intervals are in the target structure

| Band | Intervals | Sites |
| --- | ---: | ---: |
| BA ≥60, QMD 29–33 | **4** | 3 |
| BA ≥60, QMD 28–36 | 6 | 4 |
| BA ≥50, QMD 27–35 | 9 | 4 |
| BA ≥50, QMD 29–33 | 5 | 4 |

The W35 term was fitted on four intervals. Widening to the largest plausible band still yields only
nine intervals at four sites.

## 3. The CWH sample cannot stand in

CWH has **609 intervals** at BA ≥60, QMD 29–33 (449 sites), so the same structure-scoped term was
tested there. It gets worse:

| Build | CWH test BA MAE | CWH test TPH MAE | CWH train BA MAE | CWH train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| `cwh-v3` | **3.381** | **171.414** | **4.270** | **269.067** |
| W35-CWH, ×0.25 | 3.467 | 173.356 | 4.415 | 271.837 |

The CDF signal is not a general coastal high-BA/QMD response, so CWH observations cannot
substitute for missing CDF ones.

## 4. Consequence

The CDF high-BA, small-QMD band is exhausted in the existing repeat inventory. No sampling change
or borrowed zone can add held-out evidence; a term fitted to four intervals is not shippable. The
engine and `cdf-v3` stay as they are.

A fair next attempt would use **tree-level survival** inside the four intervals (many trees per
interval) to fit the mortality response, but that is still the same three sites and cannot provide
an independent site test. The alternative is to accept the CDF dense-stand TPH residual as a
documented limit.

## Reproduce

- Site/interval counts: `faib_header.csv`, `faib_sample_byvisit.csv`, `calib/intervals.csv`.
- W35 expanded fold: `probe_cdf_w35_expanded/` vs `probe_cdf_base_expanded/`.
- CWH transfer: `probe_CWH_w35/` vs `probe_CWH_zone_stable_bundle/`.

## 5. Tree-level survival was tried and has no signal

The four target intervals have two dead trees; widening to BA ≥50, QMD 27–35 gives 31 dead trees at
four sites. A logistic survival model has pooled leave-one-site-out AUC **0.356** (worse than
random) and Brier 0.0366 against an intercept baseline of 0.0373. On the expanded fold the
high-BA/QMD subset is again AUC 0.356. No survival term ships; see
`cdf-tree-survival-negative.md`.
