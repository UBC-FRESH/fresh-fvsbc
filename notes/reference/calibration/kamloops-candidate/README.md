# Kamloops background candidate

Status: **frozen diagnostic layer; conditional local rule evaluated but not applied**
Model id: `kamloops-background-v0`
Workflow: `workflows/freshforge/kamloops_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 34,135 | 0.133 | 0.104 | 0.803 | 0.320 |
| PL | 10,784 | 0.242 | 0.302 | 0.751 | 0.515 |
| SE | 5,875 | 0.154 | 0.133 | 0.714 | 0.430 |
| HW | 9,834 | 0.144 | 0.096 | 0.753 | 0.376 |
| OTHER | 8,111 | 0.194 | 0.186 | 0.680 | 0.480 |
| **ALL** | **68,739** | **0.161** | **0.146** | **0.773** | **0.387** |

PL overpredicts by about 6 points, so the conditional rule has a real test case.
The 20-site/40-split evaluation gives mean 0.142 vs 0.161, AUC 0.771, and log
loss **0.389**, slightly worse than the base 0.387. The rule is not applied.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins,
  calibration evaluation, and limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
