# D9.89 Cranbrook background candidate

Status: **the southeast Interior background layer is frozen**
Date: 2026-11-09
Workflow: `workflows/freshforge/cranbrook_background.yaml`
Model: `cranbrook-background-v0`

## 1. Why Cranbrook

Cranbrook is the sixth background candidate and the first southeast Interior
test. It has 52,683 tree intervals across 163 sites in MSdw/IDFdm/ESSFwm/ESSFdk/
ICHdm, with all five species groups above the 500-tree support minimum.

The regional contrast is Quesnel (SBS), Okanagan (MSdm1/IDF), North Island
(CWH), Kamloops (IDF/ICH/ESSF), and Prince George (northern SBS).

## 2. Result

Fitted without Cranbrook:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 7,723 | 0.141 | 0.135 | 0.872 | 0.291 |
| PL | 20,346 | 0.201 | 0.161 | 0.800 | 0.424 |
| SE | 1,954 | 0.114 | 0.073 | 0.756 | 0.394 |
| HW | 692 | 0.142 | 0.112 | 0.733 | 0.453 |
| OTHER | 21,968 | 0.110 | 0.123 | 0.798 | 0.293 |
| **ALL** | **52,683** | **0.150** | **0.137** | **0.812** | **0.349** |

## 3. Calibration

No local calibration is applied:

- no supported group overpredicts by more than 3 points;
- PL and SE are underpredicted by about 4 points;
- HW is just above the 500-tree support minimum, so its estimate is weak.

The underprediction is a background-structure issue, not a positive local
intercept.

## 4. Checked run

```sh
freshforge run workflows/freshforge/cranbrook_background.yaml --workdir . \
  --evidence runtime/freshforge-cranbrook-evidence.json
```

Result: node `fit_and_freeze_cranbrook` success; metrics and model card written;
zero diagnostics.

## 5. Interpretation

- The growth-free background model transfers to the southeast Interior with
  AUC 0.812 and a 1.3-point aggregate miss.
- PL and SE are the weak groups; the candidate is still a useful background
  layer.
- It does not support a PL/MPB or regional-calibration claim.
- Boundary remains the deferred hard case.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
