# D9.61 Quesnel background without observed growth

Status: **the Quesnel closure does not need the observed-growth oracle**
Date: 2026-11-08
Model: D9.42 provincial mortality
Code: `bcmort_provincial_calibration.py` (growth-free variant)

## 1. Design

Repeat the D9.57 Quesnel closure with the prior-growth and growth-missing columns removed from the
design. Everything else is unchanged: all PSP intervals, species groups, crown class, site index,
height/DBH, BEC-zone effects, 20-site conditional local calibration.

## 2. Result

| Set | Growth | Mean | AUC | Brier | Log loss |
| --- | --- | ---: | ---: | ---: | ---: |
| Base | with | 0.267 | 0.713 | 0.141 | 0.454 |
| Base | without | 0.248 | 0.705 | 0.133 | 0.439 |
| Local | with | 0.140 | 0.734 | 0.119 | 0.404 |
| Local | without | **0.139** | 0.725 | 0.120 | **0.408** |

The growth-free local model is effectively equivalent on Quesnel:

- mean 0.139 vs 0.140;
- log loss 0.408 vs 0.404;
- Brier 0.120 vs 0.119;
- AUC 0.725 vs 0.734.

PL without growth: mean 0.140, log loss 0.402.

## 3. Interpretation

- The observed-growth covariate is useful provincially but **not required** for the Quesnel
  background closure.
- Removing it avoids the oracle-covariate problem and the need for FVS growth coupling in this
  path.
- The local calibration layer supplies most of the target-level correction.
- Growth coupling remains optional; it is no longer a blocker for Quesnel background.

## 4. Decision

- Use the growth-free provincial model for the Quesnel background prototype.
- Do not claim growth is unimportant provincially; it improved base Brier/log loss before local
  calibration.
- Proceed to assemble the Quesnel background candidate without an observed-growth dependency.
- MPB local severity remains separate.
- No integration or bundle.

## 5. Limits

- One target TSA; species-specific behavior still varies.
- Growth may matter more in other BECs or for long intervals.
- The model still uses observed crown class and site index; those are inventory inputs, not future
  outcomes.
- No temporal validation of the growth-free variant yet.

## 6. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim, and it
is not a certificate.
