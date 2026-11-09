# D9.94 Kootenay Lake background candidate

Status: **the ICH wet-belt layer is frozen; HW underprediction documented**
Date: 2026-11-09
Workflow: `workflows/freshforge/kootenay_lake_background.yaml`
Model: `kootenay-lake-background-v0`

## 1. Why Kootenay Lake

Kootenay Lake is the eleventh background candidate and completes the ICH
wet-belt coverage. It has 24,376 tree intervals across 88 sites in
ICHdw/ICHdm/ICHmw/ICHwk, with all five species groups above the 500-tree support
minimum.

The regional contrast is Quesnel (SBS), Okanagan (MSdm1/IDF), North Island
(CWH), Kamloops (IDF/ICH/ESSF), Prince George (northern SBS), Cranbrook
(southeast Interior), Arrow (ICH wet belt), Fraser (mainland transition),
MacKenzie (northern boreal), and Haida Gwaii (hypermaritime CWH).

## 2. Result

Fitted without Kootenay Lake:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 2,669 | 0.152 | 0.146 | 0.781 | 0.363 |
| PL | 8,649 | 0.219 | 0.217 | 0.822 | 0.416 |
| SE | 976 | 0.191 | 0.181 | 0.706 | 0.449 |
| HW | 6,284 | 0.160 | 0.095 | 0.744 | 0.410 |
| OTHER | 5,798 | 0.170 | 0.152 | 0.774 | 0.392 |
| **ALL** | **24,376** | **0.184** | **0.161** | **0.775** | **0.404** |

## 3. Calibration

No local calibration is applied:

- no supported group overpredicts by more than 3 points;
- PL, FD, and OTHER are within 2.5 points;
- HW underpredicts by about 6.5 points.

The HW underprediction is a background-structure issue, not a positive local
intercept.

## 4. Checked run

```sh
freshforge run workflows/freshforge/kootenay_lake_background.yaml --workdir . \
  --evidence runtime/freshforge-kootenay-lake-evidence.json
```

Result: node `fit_and_freeze_kootenay_lake` success; metrics and model card
written; zero diagnostics.

## 5. Interpretation

- Kootenay Lake adds ICHdm/dw/wk coverage with AUC 0.775.
- PL is the strongest group (AUC 0.822) and is calibrated within 0.2 points.
- HW is the weak group (0.095 predicted vs 0.160 observed).
- It does not support a global HW multiplier.
- Boundary remains the deferred hard case.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
