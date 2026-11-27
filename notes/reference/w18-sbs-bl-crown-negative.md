# SBS BL crown term: tested, not shipped

Status: **negative result.** The shipped W18 row stays crown-free (0.41.1 / engine 0.4.11).

## What was tried

The W18 refit left SBS BL with no crown term because the calibration pairs carry only
`CR_CL` (D/C/I/S). The next step was to map those classes to the same midpoints the tree-list
builder gives the engine and refit.

The builder maps `D=8, C=6, I=4, S=2`, and `INTREE` converts a single digit `d` to percent
`10*d - 5`. So the engine sees **0.75 / 0.55 / 0.35 / 0.15** (0.45 when the class is missing).
Crown class was joined at the **prior visit**, the one that starts the growth period, not at
the interval's end visit.

Fit: 11,005 SBS BL pairs, `ln(10 * growth_cm)`, 10–20 cm weighted ×3, the V3 terms plus CR,
×1.2038 smearing. The fitted crown coefficient was **0.888009**.

## Fit quality

| Crown class | Pairs | Observed 10-yr | No crown | With crown |
| --- | ---: | ---: | ---: | ---: |
| D | 2,174 | 3.269 | 2.659 | **3.119** |
| C | 3,945 | 2.362 | 2.383 | 2.495 |
| I | 2,978 | 1.829 | 2.188 | **1.997** |
| S | 1,906 | 1.988 | 2.174 | 1.714 |

By DBH class the fit is unchanged (10–20: 2.105 vs 2.102).

## Held-out result

| Measure | No crown | With crown |
| --- | ---: | ---: |
| Test BA bias / MAE | −0.923 / 6.095 | −0.923 / **6.095** |
| Test TPH bias / MAE | −21.58 / 658.92 | **−21.58 / 658.52** |
| Train BA bias / MAE | −1.720 / 5.218 | **−1.720 / 5.180** |
| Train TPH bias / MAE | −61.91 / 398.34 | **−61.91 / 397.35** |
| SBSmc2 BA | +2.8 | **+2.5** |
| SBSmc2 TPH | −200 | **−193** |

The held-out BA error is **identical to three decimals** on all 38 intervals (the paired
difference is exactly 0.0). TPH improves by 0.4 stems out of 659 (0.06%). Train improves by
0.7%. The cell moves by 0.3 m²/ha.

## Why it is not shipped

1. **The shipping rule is not met.** Held-out BA does not improve; it is unchanged. The TPH
   gain is 0.06%.
2. **The crown mapping is not supported by the data.** Measured crown ratios
   (`(HEIGHT - HT_BRCH) / HEIGHT`) for SBS BL are nearly flat across the classes —
   C 0.545, D 0.571, I 0.572, S 0.636 — while the engine's digit mapping spans 0.15 to 0.75.
   The fitted coefficient would bake a ~1.7× growth spread between D and S into the engine
   on a mapping the measurements do not support.
3. **The pairs cannot identify crown ratio directly.** Only **3** of the 11,005 SBS BL growth
   pairs have both `HEIGHT` and `HT_BRCH` at the prior visit, so an empirical crown-ratio
   coefficient cannot be estimated from the growth data.

The honest conclusion is that W18's crown-free row is the better-supported choice. The
correct fix, if crown response is wanted, is to improve the crown-ratio input first — derive
it from `HT_BRCH` where available and stop conflating a coarse class with a ratio — and then
refit. Until then the row stays as shipped.

## Reproduce

- Fit: `~/workspace/bwbs-work/fit_sbs_bl_crown.py` (local).
- Fold: `~/workspace/bwbs-work/probe_sbs_crown/` (local, 288 compared rows).
- The engine was rebuilt with the crown coefficient, measured, and then restored to the
  shipped patch; `tests/test_w18_sbs_bl_dg.py` passes and the dense stand returns 0.284 cm/yr.
