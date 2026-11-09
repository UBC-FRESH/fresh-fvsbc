# D9.91 Fraser background candidate

Status: **the mainland coastal-transition layer is frozen; local rule evaluated**
Date: 2026-11-09
Workflow: `workflows/freshforge/fraser_background.yaml`
Model: `fraser-background-v0`

## 1. Why Fraser

Fraser is the eighth background candidate and the first mainland
coastal-transition test. It has 87,450 tree intervals across 219 sites in
CWHms/CWHdm/CWHds/IDFww, with FD, HW, and OTHER above the 500-tree support
minimum.

The regional contrast is Quesnel (SBS), Okanagan (MSdm1/IDF), North Island
(outer CWH), Kamloops (IDF/ICH/ESSF), Prince George (northern SBS), Cranbrook
(southeast Interior), and Arrow (ICH wet belt).

## 2. Result

Fitted without Fraser:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 38,795 | 0.135 | 0.107 | 0.858 | 0.299 |
| HW | 43,614 | 0.127 | 0.176 | 0.777 | 0.334 |
| OTHER | 5,041 | 0.225 | 0.232 | 0.722 | 0.479 |
| **ALL** | **87,450** | **0.136** | **0.149** | **0.801** | **0.327** |

PL (388) and SE (93) are below the support minimum and are omitted.

## 3. Conditional local rule

The 20-site/40-split evaluation:

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.149 | 0.136 | 0.801 | 0.327 |
| Conditional local | 0.117 | 0.136 | 0.810 | **0.326** |

HW overpredicts by about 4.9 points; the rule reduces the aggregate
overprediction and gives a small log-loss improvement. The card records the
evaluation, but the frozen card does not embed deployment offsets.

## 4. Checked run

```sh
freshforge run workflows/freshforge/fraser_background.yaml --workdir . \
  --evidence runtime/freshforge-fraser-evidence.json
```

Result: node `fit_and_freeze_fraser` success; metrics and model card written;
zero diagnostics.

## 5. Interpretation

- Fraser is a clean mainland coastal-transition candidate with AUC 0.801.
- HW is the group that needs the conditional intercept; FD is underpredicted
  but not by enough to trigger the rule.
- The local improvement is small, so it is a deployment option, not a new model
  structure.
- Boundary remains the deferred hard case.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
