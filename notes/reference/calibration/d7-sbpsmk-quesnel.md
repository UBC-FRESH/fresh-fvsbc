# D7.17 SBPSmk/Quesnel high-QMD second-domain check

Status: **pooled pass, site folds fail**; no bundle
Date: 2026-11-03
Issue: #387
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSmk` / `Quesnel TSA`, QMD >= 13
Evidence: `d7-sbpsmk-quesnel-summary.csv`

The Quesnel SBPSdc high-QMD candidate is not a general Quesnel rule. This applies the same playbook
to a second BEC/TSA: `SBPSmk` in Quesnel.

## 1. Sample

- 190 intervals / 68 sites overall.
- 163 eligible / 61 sites.
- QMD >= 13: **113 intervals / 43 sites**, years 1970–1990.
- QMD < 13 remains validation-only.

## 2. Result

| BAMAX | Pooled BA | Pooled TPH | Worst site BA | Worst site TPH | Sites passing |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 60 | -6.9% | -11.0% | 30.6% | 64.6% | 27 / 43 |
| 65 | -6.5% | -10.7% | 30.6% | 64.6% | 29 / 43 |
| 70 | -6.3% | -10.4% | 30.6% | 64.6% | 29 / 43 |
| **75** | **-6.1%** | **-10.2%** | **30.6%** | **64.6%** | **29 / 43** |
| 80 | -6.0% | -10.1% | 30.6% | 64.6% | 30 / 43 |

The pooled result looks acceptable, but **29–30 of 43 sites fail**; the worst site is BA +30.6% and
TPH +64.6%. A QMD boundary alone does not make SBPSmk a single domain.

## 3. Decision

**No SBPSmk bundle.** The Quesnel SBPSdc candidate is specific to its BEC/TSA and QMD domain; it
does not transfer to SBPSmk/Quesnel.

This is the same pattern as D7.6/7.11: pooled improvement hides site-level failures. The next model
must be site-level or use a covariate that explains the failing subset; another pooled BAMAX is not
enough.

## 4. Next

1. Fit a site-level/hierarchical model with SI, QMD, BA, and TPH for SBPSmk; validate by site.
2. If no stable site effect is identifiable, narrow the SBPSmk claim to the passing sites or keep it
   validation-only.
3. Do not pool SBPSdc and SBPSmk.
4. The 100 Mile and Quesnel SBPSdc candidates remain separate; neither is a certificate.

## 5. Claim boundary

This is a second-domain screen. It does not calibrate SBPSmk, change a default, or support a yield,
AAC, legal, or whole-block claim.
