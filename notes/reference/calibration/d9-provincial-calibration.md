# D9.43 target-TSA calibration for the provincial mortality model

Status: **Quesnel overprediction is correctable with 10–20 local sites**
Date: 2026-11-08
Code: `bcmort_provincial_calibration.py`
Evidence: `d9-provincial-calibration-summary.csv`

## 1. Design

Fit the D9.42 provincial model without Quesnel, then use k Quesnel sites to estimate species-group
intercept offsets. Test the remaining Quesnel sites; repeat 40 random site splits.

This is the local calibration layer the provincial model needs. It is not a new provincial fit and
not an FVS change.

## 2. Result

Baseline Quesnel (D9.42): mean 0.268 vs 0.161 observed, AUC 0.709, log loss 0.457, Brier 0.142.

| k calibration sites | Mean predicted | Observed | AUC | Log loss | Brier |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.214 | 0.161 | 0.704 | 0.621 | 0.171 |
| 2 | 0.189 | 0.161 | 0.705 | 0.501 | 0.147 |
| 3 | 0.183 | 0.161 | 0.707 | 0.491 | 0.143 |
| 5 | 0.137 | 0.161 | 0.713 | 0.461 | 0.129 |
| 10 | **0.135** | 0.161 | 0.722 | **0.418** | **0.121** |
| 20 | 0.142 | 0.160 | **0.727** | **0.408** | **0.119** |

One to three sites overcorrect or remain noisy. Ten sites cuts the overprediction from 0.268 to
0.135 and log loss from 0.457 to 0.418; twenty sites gives log loss 0.408 and Brier 0.119. The
calibrated mean is slightly low (0.14 vs 0.16), not high.

## 3. Interpretation

- The Quesnel residual is a real target-TSA/species level effect that local offsets can remove.
- Ten to twenty target sites are enough to make a large improvement; one site is not.
- Species-group offsets change ranking slightly, so AUC is not invariant here; the calibrated AUC is
  0.722–0.727, not a collapse.
- This is normal FVS-style local calibration, not evidence that the provincial model is invalid.
- The offset should be reported with uncertainty and a minimum sample rule.

## 4. Decision

- Pair the provincial model with a target-TSA calibration layer.
- Require at least 10 target sites for a Quesnel-like correction; report uncertainty.
- Do not integrate into FVS and do not issue a bundle yet.
- Next: repeat the calibration curve on other held-out TSAs and the post-2000 period.

## 5. Limits

- One target TSA (Quesnel); one site split design.
- Species-group offsets need enough calibration trees per group; sparse groups fall back to a global
  offset.
- The target sites are not a probability sample of the TSA.
- Growth is still observed, not FVS-predicted.
- No temporal validation of this calibration layer.

## 6. Claim boundary

This is a diagnostic calibration prototype. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
