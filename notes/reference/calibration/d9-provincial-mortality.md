# D9.41 provincial mortality model on all PSP tree intervals

Status: **first all-data model; discrimination is real, calibration is still TSA-dependent**
Date: 2026-11-08
Code: `bcmort_provincial.py`
Evidence: `d9-provincial-mortality-summary.csv`

## 1. Model

This is the first mortality fit that uses the whole provincial tree-survival table, not two
BEC-specific TSAs.

- 1.78M live-tree intervals, all supported BECs.
- Five species groups: FD, PL, SE, HW, OTHER.
- Poisson interval hazard with `log(exposure)` offset.
- Covariates: log DBH, initial BA, QMD, relative DBH, height/DBH, prior growth, damage, missing flags,
  and BEC-zone effects.
- Four TSAs are held out together: Okanagan, Boundary, Quesnel, Prince George.
- Separate species-group models; no TSA identity in training for the held-out TSAs.

This is still a prototype. It is not the final FVS equation and it is not integrated.

## 2. Overall held-out result

| TSA | n | AUC | Mean predicted | Observed | Brier | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Okanagan | 134,149 | 0.730 | 0.140 | 0.147 | 0.113 | 0.374 |
| Boundary | 63,017 | 0.751 | 0.138 | 0.169 | 0.126 | 0.405 |
| Quesnel | 70,989 | 0.679 | 0.267 | 0.161 | 0.144 | 0.464 |
| Prince George | 93,137 | 0.756 | 0.115 | 0.139 | 0.107 | 0.355 |

Species-group results are in the summary CSV. The main structure is now visible: discrimination is
credible (AUC 0.68–0.76), but the target-TSA level is not calibrated. Quesnel is overpredicted by
about 10.6 percentage points; Boundary and Prince George are underpredicted by 3–4 points.

This is a large improvement over the two-TSA BCMORT prototype and it uses all available BC data. It
shows the problem is not that a provincial model is impossible; the current equation is incomplete.

## 3. What is still missing

- BEC-zone effects are too coarse. Full BEC/subzone/TSA random effects are needed.
- No continuous crown ratio; only height/DBH and prior growth.
- No site index in this fit.
- No climate or period effect.
- Prior growth is observed, not FVS-predicted, so this is still an oracle-covariate diagnostic.
- One held-out TSA split; no temporal or all-TSA validation yet.

## 4. Decision

- Use this as the new provincial baseline, not the two-TSA prototype.
- Add full BEC/TSA hierarchical effects, crown/SI, and FVS-predicted growth next.
- Do not integrate into FVS and do not issue a bundle.
- Local calibration is still required for target-TSA level; the provincial model does not remove it.

## 5. Claim boundary

This is a diagnostic provincial prototype. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
