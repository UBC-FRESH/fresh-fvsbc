# D9.58 IDFdry direct-calibration screen: default retained

Status: **no calibration candidate; IDFdry stays `D-needs-work` but is the closest default**
Date: 2026-11-08
Protocol: `d9-idf-dry-protocol.md` (pre-registered in `80d9d01`)
Candidates: `d9-idf-dry-candidates.json`
Evidence: `d9-idf-dry-selection.json`, `d9-idf-dry-probe-summary.csv`

The training-only rule selected the **identity default**. No BAIMULT/MORTMULT candidate improved
it enough to justify a bundle. The Kamloops spatial holdout passes; the independent non-PSP BA
point is still just outside the band.

## 1. Sample

The IDFdry domain contains 1,167 raw PSP intervals and 387 sites. The standard filters leave 968
eligible intervals and 353 sites. The five-per-BEC probe sample has **49 intervals and 27 sites**;
the Kamloops holdout contributes **8 intervals from 7 sites**.

The per-BEC cap again makes the spatial test small. The result is a screen, not a precise estimate.

## 2. Training selection

The training fold has 41 intervals and 20 sites. Every candidate is inside both training bands; the
pre-registered score selects the baseline because its normalized maximum bias is the smallest.

| Candidate | BA % | TPH % | Site pass BA / TPH | Selected |
| --- | ---: | ---: | ---: | --- |
| **baseline** | **−2.00** | **−5.25** | **11/20 / 13/20** | **yes** |
| BAIMULT 1.25 / MORTMULT 1.0 | −0.36 | −6.58 | 13/20 / 13/20 | no |
| BAIMULT 1.5 / MORTMULT 1.0 | +1.09 | −7.82 | 12/20 / 13/20 | no |
| BAIMULT 2.0 / MORTMULT 1.0 | +4.25 | −10.05 | 11/20 / 13/20 | no |
| BAIMULT 3.0 / MORTMULT 1.0 | +9.88 | −13.88 | 10/20 / 13/20 | no |
| BAIMULT 1.5 / MORTMULT 0.75 | +4.46 | −4.94 | 12/20 / 13/20 | no |
| BAIMULT 2.0 / MORTMULT 0.75 | +8.30 | −6.66 | 8/20 / 13/20 | no |
| BAIMULT 3.0 / MORTMULT 0.75 | +16.00 | −9.58 | 8/20 / 13/20 | no |

The default already has the best normalized training score. A small BAIMULT 1.25 would slightly
improve BA and worsen TPH; it is not selected.

## 3. Kamloops spatial test

| Fold | n | Sites | BA bias | BA % | TPH bias | TPH % | Site pass BA / TPH |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kamloops test | 8 | 7 | +1.74 | **+7.48** | +139.19 | **+14.33** | 5/7 / 4/7 |

Both bands pass on the point estimate. The TPH margin is close (+14.3% against +15%), and only four
of seven sites pass TPH.

## 4. External check

The selected model is the identity default, so the independent non-PSP result is the D9.55 row
unchanged:

| Cohort | n | Sites | BA % (95% CI) | TPH % (95% CI) | Site pass BA / TPH |
| --- | ---: | ---: | ---: | ---: | ---: |
| non-PSP IDFdry | 15 | 13 | **−11.04 (−22.46 to −0.17)** | −6.64 (−17.56 to +5.42) | 7/13 / 5/13 |

BA is 1.0 percentage point outside the ±10% point band, and the confidence interval includes the
band. TPH passes. The honest verdict remains `fails`, not a pass; the sample is small.

## 5. Decision

- **No IDFdry bundle.**
- The default is retained and is now the closest `D-needs-work` domain to a pass: PSP training and
  Kamloops spatial test are inside both bands, and the external BA miss is narrow.
- The BAIMULT grid does not improve on the default; a larger multiplier makes BA worse on the
  spatial test.
- The next IDFdry step should be a larger spatial sample and a species/size diagnostic, not another
  global BAIMULT screen.
- IDFdry remains `D-needs-work` in the tier table because it has no independently validated
  candidate and its external BA point still fails.

## 6. Limits

- 49 sampled intervals; Kamloops has 8 test intervals.
- BA/TPH only; QMD, height, volume, and species composition were not tested.
- The species list is eleven codes; other species inherit the default.
- The external cohort is not a probability sample.
- The spatial test uses the largest TSA, not a random one.
- No bundle record exists because no candidate was promoted.

## 7. Claim boundary

This is a direct-calibration screen and a retained default. It does not support a yield, AAC, legal,
or whole-block claim, and it is not a certificate.
