# MacKenzie background candidate

Status: **frozen diagnostic layer; boreal PL gap remains**
Model id: `mackenzie-background-v0`
Workflow: `workflows/freshforge/mackenzie_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| PL | 38,249 | 0.179 | 0.107 | 0.812 | 0.411 |
| SE | 13,996 | 0.128 | 0.107 | 0.738 | 0.346 |
| HW | 25,444 | 0.182 | 0.180 | 0.813 | 0.377 |
| OTHER | 11,121 | 0.161 | 0.250 | 0.673 | 0.440 |
| **ALL** | **88,810** | **0.170** | **0.146** | **0.761** | **0.395** |

FD has 271 target trees, below the 500-tree support minimum, and is omitted.

## Conditional local rule

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.146 | 0.170 | 0.761 | 0.395 |
| Conditional local | 0.134 | 0.170 | 0.770 | **0.394** |

OTHER overpredicts by about 9 points; the rule helps it slightly. PL remains
underpredicted by about 7 points, so the boreal PL gap is not solved by a group
intercept.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins,
  calibration evaluation, omitted group, and limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
