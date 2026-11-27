# MS and PP: the ESSF recipe does not validate

Status: **negative result.** No `ms-v3` or `pp-v3` bundle; shipped state stays 0.41.4.

## 1. MS

Held-out 19 intervals / train 115. Base: test BA 3.80, TPH 258.3; train 5.92, 751.6.

Train-only grid, all species, BAIMULT 1.5–3.0 × MORTMULT 0.65–0.9:

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | 3.80 | 258.3 | 5.92 | **751.6** |
| 1.25 / 0.95 | 3.70 | 257.3 | 5.90 | 754.0 |
| 1.5 / 0.95 | 3.70 | 258.0 | 5.86 | 753.4 |
| 1.75 / 0.97 | 3.70 | 259.1 | 5.85 | 751.6 |
| 2.0 / 0.97 | 3.59 | 259.8 | 5.75 | 750.9 |
| 3.0 / 0.65 | 3.34 | 253.2 | 5.91 | 780.0 |

The held-out fold improves broadly, but **no candidate improves train TPH MAE**; the train
minimum is the base, i.e. the changes add variance. A paired bootstrap on the best held-out
point (1.5 / 0.95):

| Fold | BA Δ MAE | 95% CI | TPH Δ MAE | 95% CI |
| --- | ---: | ---: | ---: | ---: |
| test | −0.10 | −0.31 to +0.11 | −0.32 | −3.8 to +1.9 |
| train | −0.06 | −0.17 to +0.04 | +1.79 | −1.0 to +4.8 |

Every interval includes zero; the held-out gain is noise. Shipping MS on this would be
selecting noise. **No bundle.**

## 2. PP

Held-out **5 intervals on 2 sites** (train 20). Base: test BA 2.53, TPH 114.2; train 2.59, 54.0.

The grid does find a point that improves all four MAE figures:

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | 2.53 | 114.24 | 2.59 | 54.00 |
| 2.5 / 0.8 | **1.73** | **113.64** | **1.88** | **53.56** |
| 2.0 / 0.9 | 1.93 | 114.09 | 2.08 | 52.91 |

But five intervals on two sites cannot validate a 24-parameter bundle: one site changing its
BA by 5 m²/ha moves the test mean by 1 m²/ha, larger than the claimed gain. The result is
recorded as a candidate, not a validation. **No bundle.** PP needs more held-out sites before
this can be judged.

## 3. What this means

- MS: the train and held-out folds disagree; the held-out gain is not significant.
- PP: the fold is too thin to test.
- ESSF remains the only zone where the coupled recipe produced a both-fold MAE improvement
  (0.41.4).

## Reproduce

- `~/workspace/bwbs-work/probe_ms_joint/`, `probe_ms_joint2/`, `probe_ms_joint3/`.
- `~/workspace/bwbs-work/probe_pp_joint/`.
