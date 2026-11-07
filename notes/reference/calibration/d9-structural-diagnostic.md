# D9.23 MSdm1/SBSmw structural diagnostic

Status: **keyword calibration exhausted; submodel work required**
Date: 2026-11-07
Evidence: `d9-structural-diagnostic.csv`

## 1. Initial conditions match

| BEC | BA0 obs | BA0 pred | TPH0 obs | TPH0 pred | QMD0 obs | QMD0 pred |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | 25.9 | 25.1 | 1138 | 1123 | 18.83 | 18.82 |
| SBSmw | 35.5 | 34.9 | 1456 | 1455 | 18.40 | 18.39 |

The tree-list input is not the problem.

## 2. The change is wrong

| BEC | Observed ΔBA | FVS ΔBA | Observed ΔTPH | FVS ΔTPH |
| --- | ---: | ---: | ---: | ---: |
| MSdm1 | +4.06 | **−3.28** | +27 | **−253** |
| SBSmw | +5.89 | +1.43 | −43 | **−132** |

MSdm1: FVS predicts a BA decline where the plots grow.
SBSmw: FVS undergrows BA and kills too many trees.

## 3. Combined multipliers improve the average, not the sites

| BEC | Candidate | BA | TPH | Sites passing | Worst BA |
| --- | --- | ---: | ---: | ---: | ---: |
| MSdm1 | BAIMULT 4 / MORTMULT 0.5 | +0.1% | −4.9% | 77 / 125 | 27.6% |
| MSdm1 | BAIMULT 6 / MORTMULT 0.5 | +7.7% | −3.2% | 50 / 125 | 33.2% |
| SBSmw | BAIMULT 2 / MORTMULT 0.3 | +3.5% | −2.4% | 66 / 109 | 237% |
| SBSmw | BAIMULT 2 / MORTMULT 0.5 | +1.2% | −4.8% | 63 / 109 | 213% |

The best MSdm1 combination still leaves 48 sites failing. SBSmw still has a 200%+ BA outlier.

## 4. Decision

- Stop keyword-multiplier calibration for MSdm1 and SBSmw.
- The failure is in the growth/mortality submodels, not the input tree list.
- The next path is submodel refitting or a site-level covariate model.
- No bundle for either BEC.

## 5. Claim boundary

This is a diagnostic and a negative calibration result. It does not support a yield, AAC, legal, or
whole-block claim.
