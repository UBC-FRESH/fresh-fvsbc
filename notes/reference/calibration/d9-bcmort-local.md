# D9.32 BCMORT target-TSA intercept calibration

Status: **local intercept helps biased source models; not a full solution**
Date: 2026-11-08
Code: `bcmort_local_calibration.py`

## 1. Design

Fit the BCMORT fixed effects on a source TSA. Hold out half of the target TSA's sites for
calibration and half for testing. Estimate one target intercept offset by Poisson IRLS, then predict
the held-out target sites. Repeat 40 random site splits.

This is a local calibration layer, not a hierarchical model and not an FVS integration.

## 2. Result

| BEC | Source → target | δ | Observed event rate | Base mean | Local mean | Base log loss | Local log loss | Base Brier | Local Brier |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | −0.55 | 0.155 | 0.209 | 0.132 | 0.4094 | 0.4006 | 0.1289 | 0.1247 |
| MSdm1 | Boundary → Okanagan | −0.24 | 0.160 | 0.179 | 0.144 | 0.4108 | 0.4109 | 0.1254 | 0.1257 |
| SBSmw | Quesnel → Prince George | −0.09 | 0.165 | 0.158 | 0.147 | 0.3912 | 0.3934 | 0.1220 | 0.1227 |
| SBSmw | Prince George → Quesnel | +0.08 | 0.186 | 0.141 | 0.151 | 0.4685 | 0.4667 | 0.1395 | 0.1392 |

The target intercept corrects the large MSdm1 overprediction (0.209 → 0.132 vs observed 0.155) and
slightly improves log loss/Brier. It does not fix the SBSmw underprediction to Quesnel
(0.141 → 0.151 vs 0.186), and it slightly worsens Quesnel → Prince George.

Discrimination is unchanged: one intercept cannot repair a ranking problem.

## 3. Decision

- A local target-TSA intercept is useful as a deployment calibration layer when the source model is
  systematically high or low.
- It is not a substitute for the hierarchical/climate model.
- Do not integrate yet; BCMORT needs the full model and a joint validation.

## 4. Next

- Add site/TSA random intercepts with partial pooling.
- Add climate/seed-year covariates.
- Require a minimum local calibration sample and report uncertainty on the intercept.
- Test on a target TSA with more than one calibration site group.

## 5. Claim boundary

This is a local-calibration prototype. It does not support a yield, AAC, legal, or whole-block claim.
