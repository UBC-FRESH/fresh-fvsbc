# Okanagan background candidate

Status: **frozen diagnostic layer; no local calibration**
Model id: `okanagan-background-v0`
Workflow: `workflows/freshforge/okanagan_background.yaml`

## Metrics

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 41,211 | 0.146 | 0.121 | 0.839 | 0.316 |
| PL | 26,189 | 0.190 | 0.172 | 0.783 | 0.409 |
| SE | 10,322 | 0.122 | 0.147 | 0.744 | 0.330 |
| HW | 34,725 | 0.113 | 0.142 | 0.780 | 0.305 |
| OTHER | 21,702 | 0.165 | 0.158 | 0.735 | 0.392 |
| ALL | 134,149 | 0.147 | 0.144 | **0.792** | **0.345** |

The local intercept rule does not help (mean 0.134, log loss 0.346), so it is
not applied.

## Files

- `metrics.csv`: aggregate base metrics, one row per group plus `ALL`.
- `model-card.json`: coefficients, scalers, feature names, checksums, pins, and
  limitations.

The model card contains no site-level rows.

## Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
