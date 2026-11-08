# D9.65 Quesnel non-PL background candidate

Status: **non-PL background is a credible candidate layer; PL/MPB remains separate**
Date: 2026-11-08
Model: D9.42 provincial mortality, growth-free

## 1. Scope

Fit the provincial model without Quesnel. Evaluate Quesnel non-PL trees only:

- FD, SE, HW, OTHER;
- no PL;
- no MPB;
- no global local multiplier.

Two views:

- all periods;
- post-2000 target, trained on non-Quesnel intervals ending by 2000.

## 2. Result

| View | n | Observed | Predicted | AUC | Brier | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All periods | 20,047 | 0.163 | 0.153 | **0.792** | 0.114 | **0.408** |
| Post-2000 | 3,918 | 0.220 | 0.191 | **0.713** | 0.153 | 0.486 |

Species detail:

- All-period FD AUC 0.805, SE 0.845, HW 0.809, OTHER 0.634.
- Post-2000 FD AUC 0.808, SE 0.747, HW 0.776, OTHER 0.609.
- Post-2000 mean is low across FD/HW; SE is close.

## 3. Interpretation

- Quesnel non-PL background is usable as a **candidate layer**: all-period AUC 0.792, mean within
  1 point; post-2000 AUC 0.713, mean under by about 3 points.
- The post-2000 underprediction is a level bias, not a discrimination collapse.
- A global local intercept would not fire under the overprediction rule; the candidate remains
  background-only.
- PL is excluded because it is the MPB seam, not because the model is complete.

## 4. Decision

- Assemble Quesnel non-PL background as the first candidate layer.
- Keep PL/MPB as a separate local layer.
- Do not add a global Quesnel multiplier.
- Do not integrate or issue a bundle.
- Next: combine non-PL background with local PL MPB for the joint held-out report.

## 5. Claim boundary

This is a diagnostic candidate layer. It does not support a yield, AAC, legal, or whole-block claim,
and it is not a certificate.
