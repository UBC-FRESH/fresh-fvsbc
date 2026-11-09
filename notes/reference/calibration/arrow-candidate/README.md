# Arrow background candidate

Status: **frozen diagnostic layer; weaker than the previous six**
Model id: `arrow-background-v0`
Workflow: `workflows/freshforge/arrow_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 30,485 | 0.113 | 0.094 | 0.780 | 0.301 |
| PL | 11,161 | 0.215 | 0.187 | 0.728 | 0.460 |
| SE | 3,418 | 0.155 | 0.151 | 0.707 | 0.397 |
| HW | 65,521 | 0.090 | 0.075 | 0.691 | 0.284 |
| OTHER | 20,131 | 0.203 | 0.142 | 0.672 | 0.490 |
| **ALL** | **130,716** | **0.125** | **0.101** | **0.737** | **0.338** |

No local calibration is applied. No supported group overpredicts by more than 3
points. HW discrimination (AUC 0.691) and OTHER underprediction (0.142 vs 0.203)
are the weak points.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins, and
  limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
