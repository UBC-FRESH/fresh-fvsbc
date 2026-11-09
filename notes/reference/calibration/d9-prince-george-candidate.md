# D9.88 Prince George background candidate

Status: **the northern SBS background layer is frozen**
Date: 2026-11-09
Workflow: `workflows/freshforge/prince_george_background.yaml`
Model: `prince-george-background-v0`

## 1. Why Prince George

Prince George is the fifth background candidate and the first northern SBS test.
It has 93,137 tree intervals across 257 sites in SBSwk/SBSmk/SBSmw/SBSmc/SBSdw,
with all five species groups above the 500-tree support minimum.

The regional contrast is Quesnel (SBSmw), Okanagan (MSdm1/IDF), North Island
(CWH), and Kamloops (IDF/ICH/ESSF).

## 2. Result

Fitted without Prince George:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 1,715 | 0.085 | 0.063 | 0.670 | 0.430 |
| PL | 14,923 | 0.164 | 0.168 | 0.764 | 0.376 |
| SE | 34,090 | 0.096 | 0.083 | 0.766 | 0.273 |
| HW | 16,015 | 0.191 | 0.151 | 0.788 | 0.415 |
| OTHER | 26,394 | 0.153 | 0.106 | 0.739 | 0.398 |
| **ALL** | **93,137** | **0.139** | **0.115** | **0.764** | **0.352** |

## 3. Calibration

No local calibration is applied:

- PL is within 1 point;
- no supported group overpredicts by more than 3 points;
- HW and OTHER are underpredicted by about 4 points.

The underprediction is a background-structure issue, not something a positive
local intercept should hide.

## 4. Checked run

```sh
freshforge run workflows/freshforge/prince_george_background.yaml --workdir . \
  --evidence runtime/freshforge-prince-george-evidence.json
```

Result: node `fit_and_freeze_prince_george` success; metrics and model card
written; zero diagnostics.

## 5. Interpretation

- The growth-free background model transfers to northern SBS, but with a
  2.4-point aggregate underprediction and larger HW/OTHER gaps.
- The candidate is usable as a diagnostic background layer.
- It does not support a PL/MPB or regional-calibration claim.
- Boundary remains the deferred hard case.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
