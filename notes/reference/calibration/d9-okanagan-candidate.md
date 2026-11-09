# D9.78 Okanagan background candidate

Status: **the Quesnel template replicates on Okanagan; no local correction needed**
Date: 2026-11-08
Model: D9.42 provincial mortality, growth-free

## 1. Design

Fit the provincial growth-free model without Okanagan. Test Okanagan all species and the conditional
local calibration rule with 20 sites.

## 2. Result

| Set | n | Observed | Predicted | AUC | Brier | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | 128,048 | 0.147 | 0.144 | **0.792** | 0.104 | **0.345** |
| Conditional local | 128,048 | 0.147 | 0.134 | 0.790 | 0.105 | 0.346 |

Species:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 39,225 | 0.146 | 0.121 | 0.839 | 0.316 |
| PL | 25,079 | 0.190 | 0.168 | 0.784 | 0.411 |
| HW | 33,122 | 0.114 | 0.110 | 0.780 | 0.307 |
| SE | 9,875 | 0.122 | 0.142 | 0.744 | 0.330 |
| OTHER | 20,747 | 0.165 | 0.153 | 0.735 | 0.394 |

## 3. Interpretation

- Okanagan is calibrated out of the box: mean within 0.3 points and AUC 0.792.
- The conditional local rule makes mean/log loss slightly worse; do not apply it.
- PL AUC is 0.784, mean 0.168 vs 0.190; no global PL adjustment is justified.
- This replicates the Quesnel candidate template on a second TSA.
- The result is a background candidate, not a certificate.

## 4. Decision

- Freeze Okanagan as a second background candidate layer.
- No local Okanagan multiplier.
- Keep MPB/PL local layers separate where high-PL events exist.
- No integration or bundle.
- Next: SBSdw2 local severity or the next TSA.

## 5. Claim boundary

This is a diagnostic candidate layer. It does not support a yield, AAC, legal, or whole-block claim,
and it is not a certificate.
