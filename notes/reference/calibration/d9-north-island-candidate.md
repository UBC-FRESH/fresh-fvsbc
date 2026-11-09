# D9.86 North Island background candidate

Status: **the coastal CWH background layer is frozen; PL is omitted**
Date: 2026-11-09
Workflow: `workflows/freshforge/north_island_background.yaml`
Model: `north-island-background-v0`

## 1. Why North Island

North Island is the third background candidate and the first coastal CWH test.
It has 156,358 tree intervals across 505 sites, dominated by CWHxm and CWHvm.
PL is only 0.1% of the rows, so the layer is a clean non-PL background test with
no MPB entanglement.

The regional contrast is the point: Quesnel is SBS, Okanagan is MSdm1/IDF, and
North Island is coastal CWH.

## 2. Result

Fitted without North Island:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 21,077 | 0.117 | 0.100 | 0.878 | 0.253 |
| HW | 106,803 | 0.134 | 0.121 | 0.860 | 0.288 |
| OTHER | 28,351 | 0.125 | 0.134 | 0.810 | 0.303 |
| **ALL** | **156,231** | **0.130** | **0.120** | **0.852** | **0.286** |

PL has 127 target trees, below the 500-tree support minimum. It is omitted from
the card and the aggregate; no PL claim is made.

## 3. Calibration

No local calibration is applied:

- the aggregate miss is about 1 point;
- the supported groups do not overpredict by more than 3 points;
- PL cannot trigger the rule because it is below the support minimum.

## 4. Checked run

```sh
freshforge run workflows/freshforge/north_island_background.yaml --workdir . \
  --evidence runtime/freshforge-north-island-evidence.json
```

Result: node `fit_and_freeze_north_island` success; metrics and model card
written; zero diagnostics.

## 5. Interpretation

- The growth-free background model transfers to coastal CWH better than to
  Boundary: mean within 1 point and AUC 0.852.
- The result supports a coastal HW/FD/OTHER background layer.
- It does not support a PL layer or an MPB claim.
- The pending Quesnel/Okanagan review remains independent; this candidate is not
  in the review manifest.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
