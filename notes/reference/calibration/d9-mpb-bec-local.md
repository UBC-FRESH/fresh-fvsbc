# D9.60 BEC-stratified MPB severity calibration

Status: **BEC-within-TSA calibration halves the Williams Lake error; one global scalar remains wrong**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Panel: 12 five-year high-PL intervals

## 1. Design

D9.59 used one INITMORT multiplier per TSA. Williams Lake spans SBSdw1, SBSdw2, and SBPSmk, so this
test selects the multiplier within each BEC inside the TSA, using leave-one-site-out.

## 2. Result

| Stratum | Intervals | Leave-one-out MAE |
| --- | ---: | ---: |
| 100 Mile TSA | 4 | 0.043 |
| Williams Lake TSA (one scalar) | 8 | 0.134 |
| SBPSmk within Williams Lake | 2 | **0.050** |
| SBSdw1 within Williams Lake | 3 | **0.063** |
| SBSdw2 within Williams Lake | 3 | **0.104** |
| Williams Lake, BEC-stratified | 8 | **0.075** |

The BEC-stratified layer halves the Williams Lake error relative to one TSA scalar. SBPSmk and
SBSdw1 are close; SBSdw2 still has individual errors around 0.14.

## 3. Interpretation

- MPB severity is not one provincial multiplier and not one TSA scalar.
- BEC-within-TSA is a better local stratum where the sample supports it.
- SBSdw2 still needs a stand covariate or more intervals; one BEC scalar is too coarse.
- The number of high-PL intervals per stratum is small; report uncertainty and do not overfit.

## 4. Decision

- Use BEC-within-TSA local calibration when at least two high-PL intervals exist.
- Fall back to TSA only when the BEC stratum is too small.
- Keep the five-year interval rule and non-PL checks.
- No integration or bundle.
- Next: couple FVS-predicted growth and rerun the Quesnel/SBSmw closure.

## 5. Limits

- 12 intervals total; some strata have only two.
- No temporal validation.
- The 10-year cap remains separate.
- No production bundle.

## 6. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
