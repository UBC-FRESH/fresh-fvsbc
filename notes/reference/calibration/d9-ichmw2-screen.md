# D9.11 ICHmw2 screen: average improves, site distribution does not

Status: **no bundle; validation-only**
Date: 2026-11-05
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Data: ICHmw2, 4 cm PSP reference, 978 intervals / 225 sites
Evidence: `d9-ichmw2-screen-summary.csv`

ICHmw2 is the largest uncalibrated BEC (978 intervals / 225 sites) and spans four TSAs:
Arrow (133 sites), Cascadia (51), Okanagan (27), Kootenay Lake (14).

## 1. Baseline

No calibration:

- BA **+2.2%**
- TPH **−6.8%**
- 126 of 225 sites inside BA ±10% and TPH ±15%
- worst site BA 70.4%, TPH 75.3%

The pooled result is already acceptable; the site distribution is not.

## 2. Grid

| Candidate | BA | TPH | Sites passing | Worst BA | Worst TPH |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | +2.2% | −6.8% | 126 / 225 | 70.4% | 75.3% |
| `BAIMULT 0.75` | −0.5% | −5.9% | **148 / 225** | 62.7% | 75.0% |
| `BAMAX 60` | −2.7% | −11.2% | 133 / 225 | 62.7% | 76.6% |
| `MORTMULT 0.5` | +5.0% | −4.1% | 116 / 225 | 70.4% | 74.6% |
| `REGDMULT 1.5` | +2.4% | −6.9% | 128 / 225 | 70.4% | 75.3% |
| `REGDMULT 2.0` | +2.6% | −7.0% | 123 / 225 | 70.4% | 75.3% |
| `REGHMULT 1.5` | +2.3% | −6.8% | 128 / 225 | 70.4% | 75.3% |
| `BAIMULT 0.75 + REGDMULT 2` | −0.0% | −6.2% | 146 / 225 | 62.7% | 75.1% |

`BAIMULT 0.75` is the best candidate, but it still leaves **77 of 225 sites failing**. The worst
site remains BA 62.7% / TPH 75.0%. The CWH small-tree growth lever does not rescue ICHmw2.

Per TSA, `BAIMULT 0.75` improves the pass count but does not solve the domain:

| TSA | Sites | Baseline pass | BAIMULT 0.75 pass |
| --- | ---: | ---: | ---: |
| Arrow | 133 | 78 | 93 |
| Cascadia | 51 | 33 | 39 |
| Okanagan | 27 | 8 | 9 |
| Kootenay Lake | 14 | 7 | 7 |

## 3. Decision

- No ICHmw2 bundle.
- Do not run a larger global multiplier grid.
- The remaining problem is site-level variation, not a missing global multiplier.
- ICHmw2 is validation-only until a per-TSA/species or covariate model is available.

## 4. Next

A hierarchical or covariate model is the next real step:

- per-TSA / per-species parameters;
- site index, climate, or stand-history covariates;
- validate by TSA and time;
- report the site-error distribution, not just pooled bias.

Another BAIMULT/BAMAX/REGDMULT sweep will not close a 77-site gap.

## 5. Claim boundary

This is a negative calibration screen. It does not support a yield, AAC, legal, or whole-block claim.
