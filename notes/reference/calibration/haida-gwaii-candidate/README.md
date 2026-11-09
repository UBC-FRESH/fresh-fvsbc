# Haida Gwaii background candidate

Status: **frozen diagnostic layer; no local calibration**
Model id: `haida-gwaii-background-v0`
Workflow: `workflows/freshforge/haida_gwaii_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| HW | 71,702 | 0.134 | 0.107 | 0.772 | 0.342 |
| OTHER | 38,807 | 0.156 | 0.116 | 0.814 | 0.360 |
| **ALL** | **110,509** | **0.142** | **0.110** | **0.788** | **0.349** |

PL has 395 target trees, below the 500-tree support minimum, and is omitted.
This is a coastal HW/OTHER background layer, not a PL layer.

No local calibration is applied. Both supported groups underpredict; there is no
positive local intercept.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins,
  omitted group, and limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
