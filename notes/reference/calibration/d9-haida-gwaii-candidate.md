# D9.93 Haida Gwaii background candidate

Status: **the hypermaritime CWH layer is frozen; coastal underprediction documented**
Date: 2026-11-09
Workflow: `workflows/freshforge/haida_gwaii_background.yaml`
Model: `haida-gwaii-background-v0`

## 1. Why Haida Gwaii

Haida Gwaii is the tenth background candidate and the first hypermaritime CWH
test. It has 110,509 tree intervals across 532 sites in CWHwh/CWHvh, distinct
from North Island's CWHxm/vm/mm/vh and Fraser's mainland transition.

HW and OTHER are the only supported groups; PL has 395 target trees and is
omitted.

## 2. Result

Fitted without Haida Gwaii:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| HW | 71,702 | 0.134 | 0.107 | 0.772 | 0.342 |
| OTHER | 38,807 | 0.156 | 0.116 | 0.814 | 0.360 |
| **ALL** | **110,509** | **0.142** | **0.110** | **0.788** | **0.349** |

## 3. Calibration

No local calibration is applied:

- both supported groups underpredict;
- the aggregate underpredicts by about 3.2 points;
- there is no positive local intercept.

The underprediction is a hypermaritime background-structure issue.

## 4. Checked run

```sh
freshforge run workflows/freshforge/haida_gwaii_background.yaml --workdir . \
  --evidence runtime/freshforge-haida-gwaii-evidence.json
```

Result: node `fit_and_freeze_haida_gwaii` success; metrics and model card
written; zero diagnostics.

## 5. Interpretation

- Haida Gwaii extends coverage to the hypermaritime CWH with AUC 0.788.
- HW discrimination is 0.772; OTHER is 0.814.
- The aggregate underprediction is documented, not corrected.
- It does not support a PL/MPB claim.
- Boundary remains the deferred hard case.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
