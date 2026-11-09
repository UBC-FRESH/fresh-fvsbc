# Boundary background candidate

Status: **frozen diagnostic layer; symmetric local calibration evaluated and recommended**
Model id: `boundary-background-v0`
Workflow: `workflows/freshforge/boundary_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 27,238 | 0.150 | 0.098 | 0.773 | 0.375 |
| PL | 15,048 | 0.232 | 0.148 | 0.804 | 0.478 |
| SE | 2,578 | 0.151 | 0.107 | 0.631 | 0.431 |
| HW | 4,366 | 0.039 | 0.134 | 0.645 | 0.214 |
| OTHER | 13,787 | 0.182 | 0.122 | 0.814 | 0.412 |
| **ALL** | **63,017** | **0.169** | **0.118** | **0.776** | **0.399** |

The base model underpredicts every supported group except HW, which overpredicts.

## Symmetric local rule

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.118 | 0.169 | 0.776 | 0.399 |
| Symmetric local | 0.149 | 0.169 | 0.778 | **0.387** |

The 20-site/40-split symmetric rule fits a group intercept when the group has at
least 500 target trees and is over- or underpredicted by more than 3 points. It
closes most of the mean gap and improves log loss. The card records the
evaluation and marks it recommended, but deployment offsets are not embedded in
the frozen card.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins,
  symmetric calibration evaluation, and limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. The symmetric rule is target-site
deployment-time calibration, not a held-out base-model improvement. Not a yield,
AAC, legal, whole-block, or certificate claim.
