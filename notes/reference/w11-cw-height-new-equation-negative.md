# CW height: a new-form equation fits the pairs but not the stand

Status: **negative result.** The donor row stays; no engine or parameter change ships.

## 1. The equation

The old-form CW row could not represent both the level and the tall-end taper. A new-form model was
fitted to the CWH remeasurement pairs (same tree, live both visits, DBH ≥ 10.16 cm, crown class D/C,
10-year growth, height-decile weights):

```
HTGM = (CN + CNSI + DG*DGM + DG2*DGM^2) * HTM^(DBH1 + DBH2*D) * exp(HT2*HTM^2)
```

with `CN = 0` and, after scaling the fit to the train mean:

| CNSI | DG | DG2 | DBH1 | DBH2 | HT2 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.093311 | 0.598227 | −0.019986 | 0.217613 | −0.003324 | −0.000343 |

## 2. Pair-level fit (20% interval holdout, 367 test intervals / 2,268 pairs)

| Model | RMSE (m/decade) | Bias | Tall-quintile bias (28.6–57 m) |
| --- | ---: | ---: | ---: |
| donor | 1.493 | −0.049 | −0.638 |
| old-form refit | 1.156 | −0.194 | −0.713 |
| **new form (scaled)** | **1.060** | **−0.002** | **−0.322** |

The new form is a real pair-level improvement: lower RMSE, no mean bias, and the tall-end error is
halved against the donor.

## 3. Held-out CWH fold (65 test / 142 train intervals, `cwh-v3`)

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| donor | 3.3810 | 171.414 | 4.2705 | 269.067 |
| new CW row | 3.3810 | 171.506 | 4.2634 | 269.194 |

BA is flat; TPH is slightly worse in both folds.

## 4. Stand-level A/B (246 CWH intervals)

| Build | BA bias | Top-height bias | Volume bias |
| --- | ---: | ---: | ---: |
| donor | −4.737 | −5.55 | −106.98 |
| new CW row | −4.782 | −5.66 | −109.74 |

All three stand-level measures move the wrong way, so the row fails the shipping rule even though
the pair fit is better. This is the same trade the W11 note found with the old form: a pair-level
fit that is wrong where the stand is measured is worse than the donor that is close on dominants.

## 5. Consequence

The CW donor row stays. The negative is recorded so the next attempt starts from a different
formulation (for example a height-diameter equation with a separate tall-tree term) rather than
re-fitting these coefficients. No engine release ships from this test.

## Reproduce

- Fit and split: `~/workspace/bwbs-work/fit_cw_new.py`, `cwh_cw_new_fit.json`.
- Held-out fold: `probe_CWH_cwrow/` against `probe_CWH_zone_stable_bundle/`.
- A/B: `cwh-height-w11cw2-summary.csv` against `cwh-height-w11revert-summary.csv`.
