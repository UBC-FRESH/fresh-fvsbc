# D9.64 Quesnel temporal check: PL is still the gap

Status: **post-2000 Quesnel is a PL/MPB failure, not a non-PL temporal failure**
Date: 2026-11-08
Model: D9.42 provincial mortality, growth-free

## 1. Design

Train on all non-Quesnel intervals ending by 2000. Test on Quesnel intervals starting in 2000 or
later. Apply the conditional local calibration rule with a 20-site sample.

Training: 1,219,534 trees. Target: 8,377 trees at 55 Quesnel sites.

## 2. Result

| Set | Group | n | Observed | Predicted | AUC | Brier | Log loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | ALL | 5,449 | 0.416 | 0.248 | 0.586 | 0.270 | 0.844 |
| Local | ALL | 5,449 | 0.416 | 0.244 | 0.589 | 0.271 | 0.845 |
| Base | PL | 2,950 | 0.588 | 0.295 | 0.455 | 0.375 | 1.164 |
| Base | FD | 256 | 0.209 | 0.289 | 0.803 | 0.144 | 0.444 |
| Base | HW | 369 | 0.310 | 0.192 | 0.779 | 0.186 | 0.566 |
| Base | SE | 1,165 | 0.174 | 0.166 | 0.742 | 0.126 | 0.410 |
| Base | OTHER | 709 | 0.242 | 0.165 | 0.609 | 0.184 | 0.585 |

The conditional local rule does not fire because the base model underpredicts post-2000 Quesnel
overall. PL dominates the pooled failure: observed 0.588, predicted 0.295, AUC 0.455, log loss 1.164.
FD, HW, and SE retain usable discrimination and roughly plausible means.

## 3. Interpretation

- The all-period Quesnel background closure is real, but it is not a post-2000 PL validation.
- Post-2000 Quesnel is the same MPB/PL seam, not a new temporal failure of the background model.
- A global temporal intercept would smear a disturbance across species; do not add one.
- Quesnel non-PL can be treated as background; PL needs the local MPB layer.

## 4. Decision

- Split the Quesnel candidate into:
  - non-PL background mortality;
  - PL local MPB severity.
- Do not claim a post-2000 all-species Quesnel calibration yet.
- No global temporal multiplier, no integration, no bundle.
- Next: combine the non-PL background and the local MPB layer, then run the joint held-out test.

## 5. Claim boundary

This is a diagnostic validation. It does not support a yield, AAC, legal, or whole-block claim, and
it is not a certificate.
