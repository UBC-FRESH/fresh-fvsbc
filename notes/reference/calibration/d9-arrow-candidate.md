# D9.90 Arrow background candidate

Status: **the ICH wet-belt background layer is frozen, with weaker metrics**
Date: 2026-11-09
Workflow: `workflows/freshforge/arrow_background.yaml`
Model: `arrow-background-v0`

## 1. Why Arrow

Arrow is the seventh background candidate and the first interior wet-belt test.
It has 130,716 tree intervals across 276 sites in ICHMW/ICHDW/ESSFWC/ICHWK/
ESSFWH, with all five species groups above the 500-tree support minimum.

The regional contrast is Quesnel (SBS), Okanagan (MSdm1/IDF), North Island
(CWH), Kamloops (IDF/ICH/ESSF), Prince George (northern SBS), and Cranbrook
(southeast Interior).

## 2. Result

Fitted without Arrow:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 30,485 | 0.113 | 0.094 | 0.780 | 0.301 |
| PL | 11,161 | 0.215 | 0.187 | 0.728 | 0.460 |
| SE | 3,418 | 0.155 | 0.151 | 0.707 | 0.397 |
| HW | 65,521 | 0.090 | 0.075 | 0.691 | 0.284 |
| OTHER | 20,131 | 0.203 | 0.142 | 0.672 | 0.490 |
| **ALL** | **130,716** | **0.125** | **0.101** | **0.737** | **0.338** |

## 3. Calibration

No local calibration is applied:

- no supported group overpredicts by more than 3 points;
- the aggregate underpredicts by about 2.4 points;
- OTHER is underpredicted by about 6 points;
- HW discrimination is the weakest of the candidates (AUC 0.691).

This is a background-structure issue, not a positive local intercept.

## 4. Checked run

```sh
freshforge run workflows/freshforge/arrow_background.yaml --workdir . \
  --evidence runtime/freshforge-arrow-evidence.json
```

Result: node `fit_and_freeze_arrow` success; metrics and model card written; zero
diagnostics.

## 5. Interpretation

- Arrow extends coverage but is **not** as strong as the previous candidates.
- The aggregate AUC is 0.737; HW is 0.691 and OTHER is 0.672.
- Do not compare Arrow's AUC to Quesnel/North Island without the caveat.
- It does not support a PL/MPB or regional-calibration claim.
- Boundary remains the deferred hard case.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
