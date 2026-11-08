# D9.44 multi-TSA calibration backtest

Status: **local calibration generalizes when the base model overpredicts; it is skipped otherwise**
Date: 2026-11-08
Code: `bcmort_multi_tsa.py`
Evidence: `d9-multi-tsa-calibration-summary.csv`

## 1. Design

Fit the D9.42 provincial model with seven target TSAs excluded:

- Okanagan, Quesnel, Arrowsmith, MacKenzie, Merritt, Haida Gwaii, Morice.

For each target, use k=20 target sites to estimate species-group intercept offsets, but apply them
only when the target calibration sites show **overprediction greater than 3 percentage points**. Test
the remaining target sites; repeat 30 site splits.

This is the local calibration layer, not a new provincial fit.

## 2. Result

| TSA | Base mean | Adaptive mean | Observed | Base AUC | Adaptive AUC | Base log loss | Adaptive log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Okanagan | 0.148 | 0.148 | 0.147 | 0.805 | 0.805 | 0.337 | 0.337 |
| Quesnel | 0.281 | **0.135** | 0.161 | 0.712 | **0.735** | 0.464 | **0.408** |
| Arrowsmith | 0.094 | 0.094 | 0.112 | 0.845 | 0.846 | 0.271 | 0.271 |
| MacKenzie | 0.150 | 0.151 | 0.169 | 0.768 | 0.768 | 0.389 | 0.390 |
| Merritt | 0.167 | 0.167 | 0.188 | 0.824 | 0.822 | 0.388 | 0.391 |
| Haida Gwaii | 0.100 | 0.100 | 0.142 | 0.809 | 0.809 | 0.341 | 0.342 |
| Morice | 0.224 | **0.127** | 0.138 | 0.661 | **0.691** | 0.411 | **0.376** |

The rule applies to Quesnel and Morice, where the base model overpredicts. Okanagan, Arrowsmith,
MacKenzie, Merritt, and Haida Gwaii are left alone or essentially unchanged. Quesnel and Morice both
improve materially in mean, AUC, and log loss.

## 3. Interpretation

- Local calibration is not a universal multiplier. It is a decision: use target sites to test for
  overprediction, then apply a species-group offset only when the bias is large.
- The rule generalizes across seven TSAs and four BECs.
- Underpredicted targets (Haida Gwaii, Merritt) are not fixed by this one-sided rule. They need a
  different correction or more target data.
- The threshold is a design choice; it should be pre-registered and reported, not tuned on test.

## 4. Decision

- Use the one-sided overprediction rule as the first local calibration layer.
- Require at least 20 target sites for this backtest; do not apply with one to three sites.
- Do not apply to underpredicted targets automatically.
- No integration or bundle yet.
- Next: underprediction calibration, post-2000 validation, and FVS-predicted growth.

## 5. Limits

- Seven target TSAs; not a probability sample of BC.
- The 3-point threshold is a design choice.
- Species-group offsets need enough calibration trees; sparse groups fall back to a global offset.
- Growth remains observed.
- No temporal validation yet.

## 6. Claim boundary

This is a diagnostic calibration prototype. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
