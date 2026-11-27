# SBSmc2 residual: the folds diverge at BA 40-65

Status: **negative result / data block.** The 0.41.7 bundle stays; no further shape ships.

## 1. The residual, by BA bin

Under `sbsmc2-v3` (0.41.7) on the matched stratified fold:

| BA bin | Test TPH error / MAE | Train TPH error / MAE |
| --- | ---: | ---: |
| 0–20 | +482 / 482 (n=1) | −1,803 / 1,949 |
| 20–30 | −1,224 / 1,557 | −131 / 1,053 |
| 30–40 | −924 / 1,206 | −199 / 527 |
| 40–50 | **+211 / 429** | **−192 / 521** |
| 50–65 | **+137 / 293** | **−99 / 423** |
| 65+ | — | +43 / 310 |

BA 20–40 is aligned: both folds under-predict stems. BA 40–65 is opposite: held-out
over-predicts, train under-predicts.

## 2. Why no shape works

The current bundle already doubles the 20–30 recruitment bin. Stronger boosts:

| 20–30 rate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| ×2 (shipped) | 7.84 | **794** | **8.10** | **609** |
| ×3 | 7.79 | 771 | 8.11 | 619 |
| ×4 | **7.74** | **748** | 8.12 | 648 |

More ingress keeps improving the held-out fold and keeps worsening the train fold. The train
optimum is ×2. A stand-level shape (rather than per-bin) cannot resolve a sign difference between
the folds in the same BA range; it would have to know which fold a stand belongs to.

## 3. What is needed

- **Independent held-out SBSmc2 sites**, not a re-split of the same 126, so the BA 40–65
  divergence can be tested; or
- the **CDF dense site's measurement history** (plot boundary / remeasurement change), which is
  the other unexplained discontinuity; or
- a decision to accept the current matched-fold estimate (+2.2 / −323) as the best available.

No change ships from this step.

## Reproduce

- Residual bins: `~/workspace/bwbs-work/probe_sbsmc2_v2final/`.
- Stronger boosts: `probe_strat_b2030_{3,4}/`.
