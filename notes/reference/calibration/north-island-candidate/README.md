# North Island background candidate

Status: **frozen diagnostic layer; no local calibration**
Model id: `north-island-background-v0`
Workflow: `workflows/freshforge/north_island_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 21,077 | 0.117 | 0.100 | 0.878 | 0.253 |
| HW | 106,803 | 0.134 | 0.121 | 0.860 | 0.288 |
| OTHER | 28,351 | 0.125 | 0.134 | 0.810 | 0.303 |
| **ALL** | **156,231** | **0.130** | **0.120** | **0.852** | **0.286** |

PL has only 127 target trees, below the 500-tree support minimum, so it is
omitted from the card and the aggregate. This is a coastal HW/FD/OTHER
background layer, not a PL layer.

No local calibration is applied. The aggregate miss is about 1 point, and none
of the supported groups overpredicts by more than 3 points.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins,
  omitted group, and limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
