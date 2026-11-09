# Cranbrook background candidate

Status: **frozen diagnostic layer; no local calibration**
Model id: `cranbrook-background-v0`
Workflow: `workflows/freshforge/cranbrook_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 7,723 | 0.141 | 0.135 | 0.872 | 0.291 |
| PL | 20,346 | 0.201 | 0.161 | 0.800 | 0.424 |
| SE | 1,954 | 0.114 | 0.073 | 0.756 | 0.394 |
| HW | 692 | 0.142 | 0.112 | 0.733 | 0.453 |
| OTHER | 21,968 | 0.110 | 0.123 | 0.798 | 0.293 |
| **ALL** | **52,683** | **0.150** | **0.137** | **0.812** | **0.349** |

No local calibration is applied. No supported group overpredicts by more than 3
points. PL and SE are underpredicted by about 4 points; HW is just above the
500-tree support minimum, so its estimate is weak.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins, and
  limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
