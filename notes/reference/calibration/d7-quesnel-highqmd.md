# D7.13 Quesnel high-QMD capacity candidate

Status: **candidate passes every site fold and the temporal holdout**; unsigned candidate bundle, not a certificate
Date: 2026-11-03
Issue: #376
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSdc` / `Quesnel TSA`; 20 intervals / 6 sites with initial QMD >= 13
Evidence: `d7-quesnel-highqmd-summary.csv`

D7.11/D7.12 showed no Quesnel-wide or site-index model. This is the **domain narrowing** that works:
an established, high-QMD Quesnel stratum.

## 1. Domain

- Quesnel SBPSdc.
- `QMD >= 13` (20 intervals / 6 sites).
- Excluded: the mid/dense `QMD < 13` sites, including the D7.10 dense site; they remain
  validation-only.
- `BAMAX 75`; no `BAIMULT`, `MORTMULT`, or `HTGMULT`.

This is a claim boundary, not a post-hoc rescue: the high-QMD stratum is the part of Quesnel the
current model can represent.

## 2. Result

| BAMAX | Pooled BA | Pooled TPH | Worst site BA | Worst site TPH |
| ---: | ---: | ---: | ---: | ---: |
| 70 | -2.4% | -6.5% | 8.7% | 10.6% |
| **75** | **-2.1%** | **-6.3%** | **8.7%** | **10.1%** |
| 80 | -1.8% | -6.1% | 8.7% | 9.8% |

All six site folds are inside the pre-registered bands (BA 10%, TPH 15%). `BAMAX 75` is the
candidate; 70 and 80 are effectively equivalent on this sample.

## 3. What this is

- The **first Quesnel candidate with every site fold passing**.
- A **high-QMD domain** candidate: it does not cover the mid/dense Quesnel sites.
- A **site-grouped** result; the temporal holdout is still required.

`QMD < 13` Quesnel remains a separate problem: D7.10's dense site failed BA by 151% at BAMAX55, and
D7.11's mid-QMD sites failed at BAMAX75. Do not fold them into this claim.

## 4. Next

1. Temporal holdout: passed (D7.14).
2. `BAMAX 75` is in the unsigned `d7-quesnel-highqmd-bundle.json`.
3. Add a QMD domain field before treating the bundle as self-contained.
4. Keep `QMD < 13` validation-only until it has its own capacity/recruitment model.

## 5. Claim boundary

This is a candidate for Quesnel SBPSdc stands with initial QMD at least 13 m2/ha. It is not a
Quesnel-wide calibration, not a provincial model, and not a yield, AAC, legal, or whole-block claim.
