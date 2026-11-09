# D9.70 Quesnel small PL survives both base and MPB

Status: **the residual small PL is absent from both the base and MPB projections**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Cases: `4031355|1|2000|2013`, `4031394|1|2001|2014`

## 1. Base-vs-MPB final PL

| Case | Initial PL/ac | Base final PL/ac | MPB final PL/ac | Observed final |
| --- | ---: | ---: | ---: | ---: |
| `4031355` | 165.12 | 148.42 | 24.78 | 0 |
| `4031394` | 185.75 | 166.40 | 16.40 | 0 |

The base FVS projection removes only about 10% of PL. MPB removes 85–91%. The observed interval
removes 100%.

## 2. Size of the survivors

MPB final live PL:

- `4031355`: 20.48 in 5–10 cm, 1.92 in 10–12.5, 2.38 in 12.5–15; none >15.
- `4031394`: 12.28 in 5–10, 4.05 in 10–12.5, 0.07 in 12.5–15; none >15.

Base final live PL also leaves small trees (41.2 and 12.3 in 5–10 cm; 98.5 and 86.3 in
10–12.5 cm).

## 3. Interpretation

- The small PL residual is not an MPB severity issue.
- The base model does not remove those trees either; the observed interval does.
- This is a **small-tree mortality** gap, separate from both background and MPB.
- Do not force it with INITMORT or a global mortality multiplier.

## 4. Decision

- Keep Quesnel PL as:
  - large-tree MPB segment 85–91%;
  - small-tree residual 7–15%.
- Fit a small-tree mortality term from PSP, or report the residual explicitly.
- No integration or bundle.
- Next: small-tree PL mortality diagnostic and joint Quesnel report.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
