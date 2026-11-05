# D9.12 ICHmw2 site-index strata

Status: **partial signal; no bundle**
Date: 2026-11-05
Data: ICHmw2, 4 cm PSP, 978 intervals / 225 sites
Evidence: `d9-ichmw2-si-summary.csv`

Site index is the strongest available site covariate: it correlates −0.38 with the baseline BA
error, and low-SI sites overpredict BA.

## 1. Strata

- Low: SI < 18; 284 intervals / 72 sites.
- Mid: 18 ≤ SI < 21; 285 / 71.
- High: SI ≥ 21; 382 / 82.

## 2. In-sample screen

| Class | Candidate | BA | TPH | Sites passing | Worst BA | Worst TPH |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Low | baseline | +8.6% | −1.3% | 29 / 72 | 30.7% | 41.4% |
| Low | **BAIMULT 0.5** | +1.0% | +0.7% | **51 / 72** | 20.8% | 41.2% |
| Mid | baseline | +1.6% | −6.3% | 41 / 71 | 70.4% | 61.9% |
| Mid | **BAIMULT 0.5** | −4.1% | −4.7% | **46 / 71** | 54.9% | 64.6% |
| High | baseline | −1.3% | −12.5% | 56 / 82 | 40.6% | 75.3% |
| High | **BAIMULT 0.75** | −3.2% | −11.7% | **57 / 82** | 42.5% | 75.0% |

Low-SI sites improve substantially. Mid and high strata barely move.

## 3. TSA holdout

Selecting within Arrow and testing the other TSAs:

| Class | Candidate | Arrow | Cascadia | Okanagan | Kootenay |
| --- | --- | ---: | ---: | ---: | ---: |
| Low | BAIMULT 0.5 | 35/48 | 14/15 | 1/4 | 1/5 |
| Mid | BAIMULT 0.75 | 35/44 | 5/9 | 4/14 | 1/4 |
| High | BAIMULT 1.25 | 28/41 | 21/27 | 2/9 | 1/5 |

Cascadia transfers for the low and high strata; Okanagan and Kootenay do not. The external samples
are small, but the pattern is not a clean second-TSA pass.

## 4. Decision

- No ICHmw2 bundle.
- Site index is useful but not sufficient as a one-dimensional stratum.
- Do not run a larger SI-class grid; the remaining failures are within-class site variation.
- The next real lever is internal FVS calibration with observed tree increments, or refitting the
  BC submodels — not another keyword multiplier.

## 5. Claim boundary

This is a negative/partial calibration screen. It does not support a yield, AAC, legal, or
whole-block claim.
