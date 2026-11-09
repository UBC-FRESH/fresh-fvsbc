# D9.76 small-tree PL residual across the high-PL panel

Status: **the residual is general: MPB survivors are small PL across all 16 cases**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Panel: 16 high-PL five/six-year intervals

## 1. Result

At 0.08× INITMORT, final live PL after MPB:

| Interval | Final live PL/ac | Max DBH | Live PL >15 cm |
| --- | ---: | ---: | ---: |
| `4024547` | 0 | 16.66 | 0 |
| `4024546` | 0 | 11.83 | 0 |
| `4024754` | 58.91 | 13.03 | 0 |
| `4024449` | 36.58 | 13.66 | 0 |
| `4032478` | 0 | 13.24 | 0 |
| `4032542` | 19.16 | 14.26 | 0 |
| `4024340` | 0 | 12.75 | 0 |
| `4024339` | 41.36 | 13.69 | 0 |
| `4024338` | 0 | 12.90 | 0 |
| `4032722` | 26.78 | 15.99 | 0 |
| `4024380` | 0 | 11.08 | 0 |
| `4024382` | 0 | 11.50 | 0 |
| `4024448` | 11.65 | 15.98 | 0.04 |
| `4032464` | 0 | 11.98 | 0 |
| `4032465` | 0 | 12.14 | 0 |
| `4032466` | 0 | 13.41 | 0 |

Only **0.04 PL/ac above 15 cm** survives, in one case. The MPB survivors are essentially all
5–15 cm PL.

## 2. Interpretation

- The small-tree residual is **general across the high-PL panel**, not Quesnel-specific.
- MPB removes the host-size classes and leaves small PL everywhere.
- This is a structural small-tree mortality gap, not an INITMORT tuning problem.
- A single Quesnel residual would hide the general pattern.

## 3. Decision

- Do not tune MPB to kill the small PL.
- Add a small-tree PL mortality term or document the residual as a model boundary.
- Keep the Quesnel candidate as non-PL background plus large-tree MPB.
- No global multiplier, no integration, no bundle.

## 4. Next

1. Fit a small-tree PL mortality term from PSP or compare to base FVS small-tree mortality.
2. If not identifiable, report the residual explicitly in the Quesnel joint report.
3. Continue SBSdw2 local severity separately.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block claim,
and it is not a certificate.
