# D9.84 Okanagan background workflow

Status: **the background template replicates on a second TSA through FreshForge**
Date: 2026-11-09
Workflow: `workflows/freshforge/okanagan_background.yaml`
Model: `okanagan-background-v0`

## 1. What the node does

`fit_candidate.py` fits the target-excluded growth-free species-group model,
scores the target, writes aggregate metrics, and freezes coefficients, scalers,
checksums, and pins in a model card. It stores no site-level rows.

The Okanagan workflow runs it with `--target-tsa "Okanagan TSA"` and
`--calibration none`.

## 2. Result

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 41,211 | 0.146 | 0.121 | 0.839 | 0.316 |
| PL | 26,189 | 0.190 | 0.172 | 0.783 | 0.409 |
| SE | 10,322 | 0.122 | 0.147 | 0.744 | 0.330 |
| HW | 34,725 | 0.113 | 0.142 | 0.780 | 0.305 |
| OTHER | 21,702 | 0.165 | 0.158 | 0.735 | 0.392 |
| ALL | 134,149 | 0.147 | 0.144 | **0.792** | **0.345** |

The conditional local rule was already tested at 20 sites; it made mean and log
loss slightly worse (0.134, 0.346). It is not applied.

## 3. Checked run

```sh
freshforge run workflows/freshforge/okanagan_background.yaml --workdir . \
  --evidence runtime/freshforge-okanagan-evidence.json
```

Result: node `fit_and_freeze_okanagan` success; metrics and model card written;
zero diagnostics.

## 4. Interpretation

- The Quesnel background template replicates on Okanagan without a local
  multiplier.
- The helper is parameterized, so the next TSA reuses the same script and
  provider.
- PL is within 0.018 of observed; no global PL adjustment is justified.

## 5. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
