# Kootenay Lake background candidate

Status: **frozen diagnostic layer; HW underprediction documented**
Model id: `kootenay-lake-background-v0`
Workflow: `workflows/freshforge/kootenay_lake_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 2,669 | 0.152 | 0.146 | 0.781 | 0.363 |
| PL | 8,649 | 0.219 | 0.217 | 0.822 | 0.416 |
| SE | 976 | 0.191 | 0.181 | 0.706 | 0.449 |
| HW | 6,284 | 0.160 | 0.095 | 0.744 | 0.410 |
| OTHER | 5,798 | 0.170 | 0.152 | 0.774 | 0.392 |
| **ALL** | **24,376** | **0.184** | **0.161** | **0.775** | **0.404** |

No local calibration is applied. No supported group overpredicts by more than 3
points. HW underpredicts by about 6.5 points; that is a background-structure
issue, not a positive local intercept.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins, and
  limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
