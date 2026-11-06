# D9.18 ICHmw2 Arrow-to-Cascadia spatial holdout

Status: **holdout passes**
Date: 2026-11-06
Data: ICHmw2, 4 cm PSP, sites with >=5 intervals
Evidence: `d9-ichmw2-holdout-summary.csv`

## 1. Method

- Select `BAIMULT` on Arrow only, using the well-sampled sites (66 sites / 383 intervals).
- Grid: baseline, 0.5, 0.75, 1.0, 1.25.
- Freeze the selected value.
- Test Cascadia once (33 sites / 186 intervals), no refit.

## 2. Selection on Arrow

| Candidate | BA | TPH | Sites passing |
| --- | ---: | ---: | ---: |
| baseline | +1.5% | −4.3% | 58 / 66 |
| 0.5 | −3.2% | −2.8% | 61 / 66 |
| **0.75** | **−0.8%** | **−3.6%** | **63 / 66** |
| 1.0 | +1.5% | −4.3% | 58 / 66 |
| 1.25 | +3.8% | −5.0% | 53 / 66 |

`BAIMULT 0.75` wins the Arrow selection.

## 3. Cascadia holdout

| Candidate | BA | TPH | Sites passing |
| --- | ---: | ---: | ---: |
| 0.5 | −1.1% | −2.5% | 29 / 33 |
| **0.75** | **+1.1%** | **−3.1%** | **29 / 33** |
| 1.0 | +3.3% | −3.7% | 25 / 33 |
| 1.25 | +5.5% | −4.2% | 23 / 33 |
| baseline | +3.3% | −3.7% | 25 / 33 |

The frozen Arrow choice transfers to Cascadia: 29/33 sites pass, BA +1.1%, TPH −3.1%.

## 4. Decision

The spatial holdout supports `BAIMULT 0.75` as a candidate for ICHmw2 Arrow/Cascadia. It does
not make the bundle a certificate. The remaining limits are:

- no third TSA;
- the bundle cannot enforce the >=5-interval evidence limit;
- Okanagan and Kootenay Lake remain excluded;
- only one temporal split is available;
- the bundle remains unsigned.

## 5. Claim boundary

This is a spatial holdout for an unsigned candidate. It is not a certificate and does not support a
yield, AAC, legal, or whole-block claim.
