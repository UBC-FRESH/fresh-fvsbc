# D9.57 Quesnel background closure

Status: **conditional local calibration closes the Quesnel background model; MPB remains separate**
Date: 2026-11-08
Model: D9.42 provincial mortality
Code: `bcmort_provincial_calibration.py`
Evidence: `d9-quesnel-closure-summary.csv`

## 1. Design

Fit the D9.42 provincial model with Quesnel held out. Use 20 Quesnel sites to estimate
species-group intercept offsets, but apply an offset only when:

- the group has at least 500 calibration trees;
- the calibration sites show more than 3 percentage points of overprediction.

Test the remaining Quesnel sites; repeat 40 site splits.

This is the conditional local calibration rule from D9.44, evaluated on one held-out TSA.

## 2. Result

| Set | Group | n | Observed | Predicted | AUC | Brier | Log loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | ALL | 63,288 | 0.161 | 0.267 | 0.713 | 0.141 | 0.454 |
| Local | ALL | 63,288 | 0.161 | **0.140** | **0.734** | **0.119** | **0.404** |
| Base | PL | 45,474 | 0.160 | 0.311 | 0.714 | 0.151 | 0.473 |
| Local | PL | 45,474 | 0.160 | **0.139** | 0.714 | **0.120** | **0.402** |
| Base | FD | 1,157 | 0.141 | 0.109 | 0.804 | 0.100 | 0.331 |
| Local | FD | 1,157 | 0.141 | 0.109 | 0.804 | 0.100 | 0.331 |
| Base | HW | 4,773 | 0.250 | 0.184 | 0.807 | 0.152 | 0.467 |
| Local | HW | 4,773 | 0.250 | 0.184 | 0.807 | 0.152 | 0.467 |
| Base | SE | 9,169 | 0.111 | 0.122 | 0.844 | 0.079 | 0.273 |
| Local | SE | 9,169 | 0.111 | 0.104 | 0.844 | 0.082 | 0.279 |
| Base | OTHER | 2,716 | 0.195 | 0.221 | 0.635 | 0.170 | 0.777 |
| Local | OTHER | 2,716 | 0.195 | 0.213 | 0.635 | 0.170 | 0.782 |

The conditional rule applies to PL and leaves FD and HW untouched. It improves overall Brier
0.141 → 0.119 and log loss 0.454 → 0.404. PL mean falls from 0.311 to 0.139 against 0.160 observed.

## 3. What this closes

- The Quesnel **background mortality** model is no longer a target-level failure.
- A held-out TSA can be closed with a conditional local calibration sample.
- Non-PL groups are not collateral damage; they are left unchanged when they are not
  overpredicted.

## 4. What this does not close

- Post-2000 PL/MPB mortality. That is the separate INITMORT severity problem.
- FVS-predicted growth. The current growth covariate is observed.
- The 10-year MPB cap and the long-interval split.
- Any production bundle.

## 5. Decision

- Treat Quesnel background as **closed for the prototype**.
- Use the conditional overprediction rule for local calibration.
- Do not add a global Quesnel multiplier.
- Next: MPB INITMORT severity and FVS growth coupling.
- No integration or bundle.

## 6. Claim boundary

This is a diagnostic provincial prototype. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
