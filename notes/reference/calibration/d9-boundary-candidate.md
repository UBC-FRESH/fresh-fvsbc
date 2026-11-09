# D9.95 Boundary candidate with symmetric local calibration

Status: **the deferred Boundary case is now frozen; symmetric local calibration closes most of the mean gap**
Date: 2026-11-09
Workflow: `workflows/freshforge/boundary_background.yaml`
Model: `boundary-background-v0`

## 1. Why Boundary

Boundary is the twelfth background candidate and the deferred hard case. It has
63,017 tree intervals across 216 sites in ICHmk/IDFdm/MSdm/IDFdh/ICHxw, with all
five species groups above the 500-tree support minimum.

The target-excluded base model underpredicts mean mortality by about 5.1 points.
The one-sided conditional rule cannot correct it because every supported group
underpredicts (except HW, which overpredicts).

## 2. Base result

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 27,238 | 0.150 | 0.098 | 0.773 | 0.375 |
| PL | 15,048 | 0.232 | 0.148 | 0.804 | 0.478 |
| SE | 2,578 | 0.151 | 0.107 | 0.631 | 0.431 |
| HW | 4,366 | 0.039 | 0.134 | 0.645 | 0.214 |
| OTHER | 13,787 | 0.182 | 0.122 | 0.814 | 0.412 |
| **ALL** | **63,017** | **0.169** | **0.118** | **0.776** | **0.399** |

## 3. Symmetric local rule

The template now supports `--calibration symmetric`:

- fit a species-group intercept when the group has at least 500 target trees;
- trigger when the group is over- **or under**predicted by more than 3 points;
- evaluate on 20 calibration sites and 40 held-out splits.

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.118 | 0.169 | 0.776 | 0.399 |
| Symmetric local | 0.149 | 0.169 | 0.778 | **0.387** |

The mean gap falls from 5.1 to 2.0 points and log loss improves. The card records
the evaluation and marks the rule recommended, but the frozen card does not embed
deployment offsets.

## 4. Checked run

```sh
freshforge run workflows/freshforge/boundary_background.yaml --workdir . \
  --evidence runtime/freshforge-boundary-evidence.json
```

Result: node `fit_and_freeze_boundary` success; metrics and model card written;
zero diagnostics.

## 5. Interpretation

- The Boundary gap is a **two-sided calibration problem**, not a global
  multiplier.
- The symmetric local rule is a deployment-time correction; it does not improve
  the target-excluded base model.
- Boundary is now documented rather than deferred.
- No global screen or provincial multiplier.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
