# D9.101 imputation sensitivity

Status: **train-only medians change the frozen metrics by less than 5×10⁻⁹**
Date: 2026-11-10
Mechanism: `bp.load(exclude_tsa=...)`, `fit_candidate --imputation train`
Cards changed: **none**

## 1. Why

The candidate review package flags full-frame median imputation: `bp.load()`
fills missing crown, SI, H-D, and growth values with medians computed before the
target split.

Before regenerating every card, quantify whether the choice matters.

## 2. Method

- Add an optional `exclude_tsa` argument to `bp.load`.
- Add `fit_candidate --imputation {full,train}`.
- Rerun eleven target-excluded fits with target-excluded medians.
- Compare aggregate mean prediction and log loss with the frozen cards.

Quesnel's non-PL card uses a separate metrics pipeline and is not in this table.

## 3. Result

Maximum absolute changes across the eleven candidates:

| Quantity | Maximum absolute delta |
| --- | ---: |
| mean prediction | **6.6×10⁻⁹** |
| log loss | **5.1×10⁻⁹** |

Largest single log-loss changes:

| Candidate | Delta log loss |
| --- | ---: |
| Haida Gwaii | −5.1×10⁻⁹ |
| Fraser | +3.7×10⁻⁹ |
| North Island | −2.1×10⁻⁹ |
| Okanagan | −1.9×10⁻⁹ |
| MacKenzie | +1.3×10⁻⁹ |

The remaining candidates are smaller. At the precision of the candidate cards
and reports, the metrics are identical.

## 4. Interpretation

- The full-frame concern is technically real; the target TSA influences the
  medians.
- Empirically, it does not move the frozen aggregate metrics.
- The reviewer can treat the concern as a disclosed minor issue, or require the
  train-only switch as a cleanliness condition.
- No candidate card is changed in this step.

## 5. Decision

- Keep the frozen cards unchanged.
- Use `--imputation train` for the next card regeneration or review-mandated
  refresh.
- Do not tune any model because of this result.
- Record the evidence in the review response.

## 6. Claim boundary

Sensitivity analysis only. Not a bundle, certificate, yield, AAC, legal, or
whole-block claim.
