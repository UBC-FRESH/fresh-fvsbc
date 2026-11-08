# D9.63 SBSdw2 severity covariate

Status: **PL TPH reduces the SBSdw2 error but does not close it**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Panel: 7 SBSdw2 five/six-year high-PL intervals

## 1. Design

Fit a simple linear severity model for the `INITMORT` multiplier using stand covariates, with
leave-one-site-out:

- PL BA;
- PL TPH;
- PL QMD;
- percent PL;
- years.

The predicted multiplier is rounded to the 0.02–0.08 grid before the mortality comparison.

## 2. Result

| Covariate | LOOCV MAE |
| --- | ---: |
| BEC scalar | 0.139 |
| PL BA | 0.121 |
| PL QMD | 0.118 |
| PL TPH | **0.096** |
| PL BA + PL TPH + QMD | 0.096 |
| Percent PL | 0.152 |

PL TPH is the useful covariate: denser PL stands need a lower per-tree severity multiplier, and the
sparse six-tree stand needs a high one. The model halves the gap but still has individual errors.

The remaining outliers are the very small stand and the high-density/high-mortality `4032465`.

## 3. Interpretation

- SBSdw2 is not a constant-severity stratum.
- PL TPH is a credible first covariate; it reduces LOOCV from 0.139 to 0.096.
- Seven intervals are not enough to claim a general severity equation.
- The result is a **local diagnostic**, not a provincial MPB model.
- `ACTSURF` remains the next direct-kill diagnostic if the covariate cannot close the outliers.

## 4. Decision

- Use PL TPH as the interim SBSdw2 severity covariate, clearly labelled local.
- Keep 100 Mile scalar, SBPSmk/SBSdw1 BEC strata.
- Do not use a global multiplier.
- Collect more SBSdw2 high-PL intervals or run ACTSURF before any claim.
- No integration or bundle.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
