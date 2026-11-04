# D9.10 CWH top-height correction

Status: **metric mismatch corrected; height failure retracted**
Date: 2026-11-04
Issue: #426
Evidence: `d9-cwh-4cm-validation-summary.csv`

D9.8 compared two different quantities:

- the PSP `top_height` was `max(HEIGHT)` over live trees;
- FVS `TopHt` is the top height of the largest-diameter trees, not the single tallest tree.

The comparison was therefore invalid. On one CWH interval the raw tree list gives:

- observed `max(HEIGHT)` = 38.2 m;
- observed top-100-by-DBH height = 33.9 m;
- FVS `TopHt` = 33.0 m.

The 38.2 m value is a single-tree maximum; it is not the FVS definition.

## 1. Matched comparison

Observed top height is recomputed as the expansion-weighted average height of the **100 largest-DBH
trees per hectare** at the end visit. This matches the FVS `TopHt` basis closely.

| Holdout | BA | TPH | QMD | Matched top height | Volume |
| --- | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | -2.9% | -1.3% | -1.1% | -5.3% | -6.5% |
| Fraser | -3.3% | -5.9% | +0.8% | -8.0% | -7.9% |
| Haida Gwaii | +0.6% | +7.9% | -0.5% | -3.7% | -3.1% |
| temporal >=2000 | +3.4% | +12.1% | -5.5% | -9.0% | -8.1% |
| non-PSP external | -1.3% | +1.5% | -2.2% | -7.2% | **-18.7%** |

The height failure is retracted. Matched top height is inside ±10% on every hold.

## 2. What remains

- PSP volume is within ±8%; the non-PSP external volume is -18.7% and unresolved. It may include a
  volume-standard difference, but it is not yet explained.
- The max-height multiplier screen is not evidence for or against `HTGMULT`/`REGHMULT`; it used the
  wrong target.
- The CWH 4 cm bundle remains a pilot and unsigned.

## 3. Decision

- Correct the D9.6/D9.8 record.
- Do not promote the CWH 4 cm pilot on the old height claim.
- Resolve the external volume gap before certification.
- Do not use the max-height numbers in any future validation.

## 4. Claim boundary

This is a metric correction and re-validation. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate.
