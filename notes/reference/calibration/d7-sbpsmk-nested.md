# D7.22 nested selection for the mature SBPSmk candidate

Status: **corrected units: 31/38 sites pass; every-site criterion still fails**
Date: 2026-11-04
Issue: #413
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Data: SBPSmk / Quesnel, mortality fraction <= 0.4
Evidence: `d7-sbpsmk-nested-summary.csv`, `d7-sbpsmk-nested-folds.csv`

The D7.19 candidate was post-hoc: BAMAX, BAIMULT, and the domain were selected on all sites. This
test moves the selection inside five site-grouped training folds.

## 1. Design

- Five outer folds, assigned deterministically by sorted site identifier.
- Training-only grid:
  - BAMAX 70, 75, 80
  - BAIMULT 1.0, 1.25
  - QMD 15, 17
  - BA 20 fixed
- Ingrowth refit on the training sites for each candidate/domain.
- Selection score: normalized pooled BA/TPH bias plus a site-failure penalty.
- Held-out sites evaluated once.

## 2. Result

BAMAX 80 and BAIMULT 1.25 were selected in all five folds; QMD was 15 in two folds and 17 in three.

| Fold | Held-out sites | Test intervals | BA | TPH | Sites pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 16 | -3.41% | -13.62% | 5 / 8 |
| 1 | 8 | 14 | +0.25% | +1.80% | 6 / 8 |
| 2 | 8 | 22 | -2.14% | +4.23% | 8 / 8 |
| 3 | 6 | 18 | -3.39% | +5.34% | 6 / 6 |
| 4 | 8 | 16 | -0.73% | +5.28% | 6 / 8 |
| **Overall** | **38** | **86** | **-1.99%** | **+0.61%** | **31 / 38** |

Worst held-out site: BA 25.1%, TPH 61.6%, both in fold 0. Seven sites fail.

## 3. Decision

The corrected-unit nested selection **still fails the every-site criterion** (31/38). The pooled
result is acceptable, but the candidate cannot be upgraded. The fixed-parameter LOSO/temporal checks
pass; the selection procedure does not. The fixed-parameter 25/25 LOSO in D7.19 was selected on all sites and
does not establish that the selection procedure transfers.

The candidate remains:

- **post-hoc**;
- Quesnel-only;
- QMD/BA/TSA enforced;
- unsigned;
- not a certificate.

Do not tune the grid further on these test folds. A future attempt needs a new covariate, more sites,
or an independent cohort, not another pass over the same 28 sites.

## 4. What this tells us

The failures are concentrated in one fold with eight held-out sites. The selected parameters are
consistent across folds, so the instability is not mainly parameter choice; it is site-level
variation that the available QMD/BA domain does not capture. This is the same pattern as the
low-QMD/high-productivity sites in D7.18.

## 5. Claim boundary

This is a negative validation result for the selection procedure. It does not support a yield, AAC,
legal, or whole-block claim, and it does not certify the candidate.
