# D9.69 Quesnel PL residual is small-tree survival

Status: **the MPB segment closes the large PL; the 7–15% residual is small PL**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Cases: `4031355|1|2000|2013`, `4031394|1|2001|2014`

## 1. Final live PL size

The corrected one-cycle projections at 0.08× INITMORT leave:

| Case | Final live PL/ac | 5–10 cm | 10–12.5 cm | 12.5–15 cm | >15 cm |
| --- | ---: | ---: | ---: | ---: | ---: |
| `4031355` | 24.78 | 20.48 | 1.92 | 2.38 | 0 |
| `4031394` | 16.40 | 12.28 | 4.05 | 0.07 | 0 |

No live PL above 15 cm remains. The residual is entirely small PL.

## 2. Interpretation

- The MPB segment removes the large PL host; the remaining live PL is below the effective MPB
  host/size range.
- Raising INITMORT does not remove those trees because the mortality is size/host-limited, not
  severity-limited.
- The observed 100% includes small PL, so the final 7–15% is a **small-tree mortality** component,
  not a failure of the MPB kill path.
- This is a structural boundary, not another global multiplier.

## 3. Decision

- Treat Quesnel PL as:
  - large-tree MPB segment: 85–91% dead at 0.08×;
  - small-tree residual: 7–15%.
- Do not force the small PL with INITMORT.
- Test a small-tree/background mortality term separately, or report the residual explicitly.
- Keep the Quesnel non-PL background candidate separate.
- No integration or bundle.

## 4. Next

1. Add a small-tree PL mortality term or compare to the base FVS background mortality.
2. Assemble the joint Quesnel report with the residual stated.
3. Keep SBSdw2 PL-TPH local; ACTSURF or more intervals.
4. No bundle.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
