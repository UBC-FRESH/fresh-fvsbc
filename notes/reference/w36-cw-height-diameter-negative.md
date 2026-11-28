# W36: a height-diameter CW form with a tall-tree term

Status: **negative.** The pair fit is the best so far, but every stand-level metric gets worse.
The engine is reverted.

## 1. The form

A direct height-growth regression replaces the LTHG row for CW in CWH:

```
HTG10 = 1.1327 + 0.4390*DGM - 0.0169*D + 0.0218*max(0, H - 30)
```

where `DGM` is the ten-year diameter increment (cm), `D` is DBH (cm) and `H` is height (m). The
last term is the separate tall-tree term. It was fitted on the CWH CW pairs with height-decile
weights and the same 20% interval holdout.

## 2. Pair fit (2,268 test pairs / 367 intervals)

| Model | RMSE (m/decade) | Bias | Tall-quintile bias (28.6–57 m) |
| --- | ---: | ---: | ---: |
| donor | 1.493 | −0.049 | −0.638 |
| W33 multiplicative tall term | 1.478 | +0.047 | −0.295 |
| new-form LTHG row | 1.060 | −0.002 | −0.386 |
| **W36 height–diameter** | **1.089** | **−0.040** | **−0.051** |

W36 nearly eliminates the tall-end bias. It is the best tall-end fit so far.

## 3. Stand-level results (CWH, 65 test / 142 train)

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| donor | 3.3810 | **171.414** | 4.2705 | **269.067** |
| W36 | 3.3810 | 171.521 | 4.2634 | 269.152 |

The fold sample has no tall CW for the term to act on, so BA is flat and TPH is marginally worse.

## 4. Stand-level A/B (246 CWH intervals)

| Build | BA bias | Top-height bias | Volume bias |
| --- | ---: | ---: | ---: |
| donor | **−4.737** | **−5.55** | **−106.98** |
| W36 | −4.761 | −5.64 | −109.50 |

All three move the wrong way. The likely reason is that the pair fit uses the **observed** ten-year
diameter increment, while the engine supplies its own predicted DGM. A model that is excellent on
observed DGM can under-grow when the engine's DGM is different; the donor's implicit DGM response
is more compatible with the engine's own diameter model.

## 5. Consequence

No CW change ships. This is the third structurally different CW form tested (old row, new-form row,
multiplicative tall term, now height–diameter); all fail the stand-level rule. A future attempt
should fit against the **engine's** DGM, not the observed DGM, or use a height–diameter dubbing
equation at the inventory year rather than a growth increment.

## Reproduce

- Fit: `~/workspace/bwbs-work/fit_cw_new.py` form f4.
- Fold: `probe_CWH_w36/` against `probe_CWH_zone_stable_bundle/`.
- A/B: `cwh-height-w36-summary.csv` against `cwh-height-w11revert-summary.csv`.

## 6. Engine-DGM follow-up

Fitting against the engine's predicted DGM (W37) gives the best stand-level CW result: top height
−5.55 → −5.376 and volume −106.98 → −104.18, with BA flat and TPH marginally worse. It still fails
the all-three-improve rule. See `w37-cw-engine-dgm.md`.
