# D9.15 MSdm1 screen: high multipliers alone do not calibrate it

Status: **no bundle; validation-only**
Date: 2026-11-06
Data: MSdm1, 4 cm PSP, 591 intervals / 133 sites
Evidence: `d9-msdm1-screen-summary.csv`

## 1. Baseline

- BA **−15.5%**
- TPH **−14.9%**
- 15 of 125 compared sites pass BA ±10% / TPH ±15%
- worst site BA 47.1%, TPH 53.6%

MSdm1 is severely underpredicted, much worse than ICHmw2 or CWH.

## 2. Grid

| Candidate | BA | TPH | Sites passing | Worst BA | Worst TPH |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | −15.5% | −14.9% | 15 / 125 | 47.1% | 53.6% |
| BAIMULT 2 | −13.5% | −15.0% | 20 / 125 | 44.6% | 53.6% |
| BAIMULT 4 | −7.0% | −12.3% | 54 / 125 | 33.3% | 47.3% |
| **BAIMULT 6** | **+2.8%** | **−9.1%** | **63 / 125** | 33.2% | 44.3% |
| BAIMULT 8 | +7.0% | −9.5% | 52 / 125 | 40.6% | 43.6% |
| BAIMULT 10 | +10.4% | −10.4% | 42 / 125 | 48.0% | 43.3% |
| BAIMULT 12 | +13.5% | −11.4% | 33 / 125 | 62.8% | 43.3% |

`BAIMULT 6` is the best, but **62 of 125 sites still fail**, and a 6× growth multiplier is a
structural correction, not a calibration. `REGDMULT` adds nothing.

## 3. Decision

- No MSdm1 bundle.
- Do not promote a 6× multiplier.
- MSdm1 needs a BEC/subzone-specific growth model or a data-quality explanation, not another
  global multiplier.
- Okanagan and Boundary both fail; Boundary is worse (BA −27.8% at BAIMULT 1).

## 4. Next

Apply the same screen to SBSmw only if it has a different data/model signature. Otherwise the
remaining work is structural: submodel refitting or internal increment calibration.

## 5. Claim boundary

This is a negative calibration screen. It does not support a yield, AAC, legal, or whole-block claim.
