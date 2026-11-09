# Quesnel candidate joint report

Candidate: `quesnel-sbsmw-background-v0`  
Status: **candidate layer assembled; not a bundle or certificate**  
Date: 2026-11-08

## 1. Scope

This report assembles the Quesnel evidence as two separate layers:

| Layer | Scope | Status |
| --- | --- | --- |
| Non-PL background | FD, SE, HW, OTHER; Quesnel TSA; all periods and post-2000 | frozen candidate layer |
| PL/MPB | large-tree MPB and small-tree residual | separate diagnostic, not in candidate |

There is no single all-species Quesnel calibration claim.

## 2. Non-PL background candidate

| View | n | Observed | Predicted | AUC | Brier | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All periods | 20,047 | 0.163 | 0.153 | **0.792** | 0.114 | **0.408** |
| Post-2000 | 3,918 | 0.220 | 0.191 | **0.713** | 0.153 | 0.486 |

All-period mean is within 1 point. Post-2000 AUC is 0.713, mean under by about 3 points. FD/HW
drive the post-2000 bias; SE is close.

## 3. PL/MPB evidence

Large-tree MPB, corrected one-cycle segment at 0.08× INITMORT:

| Case | Dead PL fraction | Observed |
| --- | ---: | ---: |
| `4031355` | 85.0% | 100% |
| `4031394` | 91.2% | 100% |

The remaining live PL is entirely 5–15 cm. Base FVS also leaves those small PL. This is a
small-tree mortality gap, not MPB severity.

## 4. Candidate composition

The candidate is:

- provincial growth-free mortality model;
- Quesnel non-PL background;
- no global Quesnel multiplier;
- no PL claim;
- no MPB wrapper integration.

The PL/MPB layer is:

- local INITMORT severity;
- five-year or segmented intervals;
- large-tree MPB;
- small-tree residual reported separately.

## 5. Decisions

- Freeze `quesnel-sbsmw-background-v0` as a non-PL candidate layer.
- Do not issue a bundle.
- Do not claim an all-species post-2000 Quesnel calibration.
- Do not add a global temporal or Quesnel multiplier.
- Do not open new diagnostic seams until review feedback or the MPB wrapper integration.

## 6. Open items

1. Wire the MPB build patch into the pinned wrapper.
2. Decide whether the small-tree PL residual needs a model or is a documented limit.
3. Finish SBSdw2 local severity.
4. Build the same candidate template for other TSAs.

## 7. Claim boundary

This report does not support a yield, AAC, legal, or whole-block claim, and it is not a certificate.
