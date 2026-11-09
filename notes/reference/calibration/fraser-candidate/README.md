# Fraser background candidate

Status: **frozen diagnostic layer; conditional local rule evaluated**
Model id: `fraser-background-v0`
Workflow: `workflows/freshforge/fraser_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 38,795 | 0.135 | 0.107 | 0.858 | 0.299 |
| HW | 43,614 | 0.127 | 0.176 | 0.777 | 0.334 |
| OTHER | 5,041 | 0.225 | 0.232 | 0.722 | 0.479 |
| **ALL** | **87,450** | **0.136** | **0.149** | **0.801** | **0.327** |

PL (388) and SE (93) are below the 500-tree support minimum and are omitted.

## Conditional local rule

The 20-site/40-split evaluation:

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.149 | 0.136 | 0.801 | 0.327 |
| Conditional local | 0.117 | 0.136 | 0.810 | **0.326** |

HW overpredicts by about 4.9 points, so the rule has a positive test case. The
local result is recorded in the card, but deployment offsets are not embedded in
the frozen card.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins,
  calibration evaluation, omitted groups, and limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
