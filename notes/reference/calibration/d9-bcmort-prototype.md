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

## 6. Height/DBH screen

Height/DBH was added to the crown model; see `d9-bcmort-hd.md` and `d9-bcmort-hd-summary.csv`. It
improves MSdm1 in both directions (AUC 0.750 -> 0.763 and 0.681 -> 0.684), but is flat on SBSmw.
It is not a calibration fix; a local target intercept still leaves the target mean biased. Add it
to the MSdm1 prototype, not as a universal term.

## 7. Growth history and calibration sample size

Prior stand growth and mortality rates were tested on top of height/DBH. They improve two directions
and worsen two, so they are not a universal term. A target-intercept curve shows that one target
site is worse than no calibration; five or more help some directions, but SBSmw Quesnel -> Prince
George remains worse than uncalibrated and the target mean stays biased. See
`d9-bcmort-growth-calibration.md`, `d9-bcmort-growth-summary.csv`, and
`d9-bcmort-calibration-curve-summary.csv`.

## 8. Individual-tree growth

The rebuilt tree-survival table carries `TREE_NO`, prior live diameter and year, and per-year growth.
Adding growth to the crown + height/DBH model improves AUC, log loss, and Brier in all four TSA
directions; it is the strongest tree-level covariate tested. Coverage is 56.4%. A local target
intercept still leaves the target mean biased. See `d9-tree-growth.md` and
`d9-tree-growth-summary.csv`.

## 9. Temporal holdout

Training on intervals ending by 2000 and testing on intervals starting in 2000 or later, growth
improves AUC/log loss/Brier in both BECs: MSdm1 AUC 0.514 -> 0.617, SBSmw 0.577 -> 0.634. The
post-2000 event rate is much higher than the model predicts (MSdm1 0.216 vs 0.162; SBSmw 0.358 vs
0.176), so temporal calibration is still required. See `d9-bcmort-temporal.md` and
`d9-bcmort-temporal-summary.csv`.

## 10. Limits

- Poisson hazard, not the final cloglog binomial; no exact interval censoring beyond exposure.
- Tree-level `dead` is a binary outcome, not a known death time.
- TSA holdout is only two TSAs per BEC.
- No climate, site index, crown ratio, or recent growth yet.
- This is a model prototype, not an FVS core change or a bundle.

## 11. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim.
