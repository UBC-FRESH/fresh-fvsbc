# D9.30 BCMORT survival prototype

Status: **tree-level signal exists; calibration transfer is mixed**
Date: 2026-11-07
Code: `bcmort_prototype.py`
Data: `psp4/tree_survival.csv`

## 1. Model

A Poisson piecewise-exponential survival prototype:

- response: `dead` with offset `log(exposure)`;
- covariates: log DBH, log BAL (basal area of larger trees), log initial BA, log QMD,
  relative DBH, damage, and species-group dummies;
- no BEC/TSA covariates in the transfer test; train on one TSA, test on the other.

This is not the final hierarchical `BCMORT`; it is a test of whether tree-level covariates carry
survival signal beyond a constant hazard.

## 2. Result

| BEC | Train → test | Train AUC | Test AUC | Test log loss | Base log loss | Test Brier | Base Brier |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.705 | 0.721 | 0.411 | 0.417 | 0.1295 | 0.1268 |
| MSdm1 | Boundary → Okanagan | 0.776 | 0.694 | 0.411 | 0.442 | 0.1256 | 0.1346 |
| SBSmw | Quesnel → Prince George | 0.774 | 0.745 | 0.390 | 0.444 | 0.1216 | 0.1360 |
| SBSmw | Prince George → Quesnel | 0.830 | 0.710 | 0.472 | 0.468 | 0.1405 | 0.1476 |

Discrimination is consistently better than a constant hazard (AUC 0.69–0.75 on held-out TSAs).
Brier score improves in three of four directions. Log loss improves in three of four; Quesnel
→ Prince George is the clearest gain, Prince George → Quesnel is slightly worse.

Calibration is not solved:

- MSdm1 overpredicts mortality in both directions (mean predicted 0.18–0.21 vs observed 0.155–0.160).
- SBSmw underpredicts mortality when trained on Prince George and tested on Quesnel (0.142 vs 0.187).

## 3. Decision

- The DBH/BAL/BA/QMD/damage/species signal is real; the current FVS table throws it away.
- Do not integrate this prototype. The TSA-level calibration shift is still too large.
- The next step is hierarchical `BCMORT` with TSA/site intercepts, crown ratio, site index, and a
  growth term, then a joint fit against the PSP transitions.
- Calibrate the intercept/site effects on the target TSA or use a hierarchical prior; a pooled fixed
  intercept is not enough.

## 4. Site-index screen

A site-index covariate was tested with the same TSA holdouts. It did not improve transfer:

| BEC | Train → test | Test AUC (no SI → SI) | Log loss (no SI → SI) | Brier (no SI → SI) |
| --- | --- | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.721 → 0.700 | 0.411 → 0.438 | 0.1295 → 0.1392 |
| MSdm1 | Boundary → Okanagan | 0.694 → 0.677 | 0.411 → 0.419 | 0.1256 → 0.1289 |
| SBSmw | Quesnel → Prince George | 0.745 → 0.747 | 0.390 → 0.389 | 0.1216 → 0.1214 |
| SBSmw | Prince George → Quesnel | 0.710 → 0.711 | 0.472 → 0.471 | 0.1405 → 0.1402 |

Site index is not the missing transfer covariate. It does not justify a hierarchical SI-only model.

## 5. Crown-class screen

Crown class (D/C/I/S) was added to the base design; see `d9-bcmort-crown.md` and
`d9-bcmort-crown-summary.csv`. It improves held-out AUC, log loss, and Brier in three of four TSA
directions, but worsens MSdm1 Boundary -> Okanagan. A local target intercept reduces the crown
model's log loss in three directions but still leaves the target mean biased. Crown class is a
useful next covariate; it is not a calibration fix and is not integrated.

## 6. Limits

- Poisson hazard, not the final cloglog binomial; no exact interval censoring beyond exposure.
- Tree-level `dead` is a binary outcome, not a known death time.
- TSA holdout is only two TSAs per BEC.
- No climate, site index, crown ratio, or recent growth yet.
- This is a model prototype, not an FVS core change or a bundle.

## 7. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim.
