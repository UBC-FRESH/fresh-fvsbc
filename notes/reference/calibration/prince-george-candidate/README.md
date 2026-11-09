# Prince George background candidate

Status: **frozen diagnostic layer; no local calibration**
Model id: `prince-george-background-v0`
Workflow: `workflows/freshforge/prince_george_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 1,715 | 0.085 | 0.063 | 0.670 | 0.430 |
| PL | 14,923 | 0.164 | 0.168 | 0.764 | 0.376 |
| SE | 34,090 | 0.096 | 0.083 | 0.766 | 0.273 |
| HW | 16,015 | 0.191 | 0.151 | 0.788 | 0.415 |
| OTHER | 26,394 | 0.153 | 0.106 | 0.739 | 0.398 |
| **ALL** | **93,137** | **0.139** | **0.115** | **0.764** | **0.352** |

No local calibration is applied. The supported groups do not overpredict by more
than 3 points. HW and OTHER are underpredicted by about 4 points; that is a
background-structure issue, not a positive local intercept.

## Files

- `metrics.csv`: aggregate base metrics.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins, and
  limitations.

The card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
