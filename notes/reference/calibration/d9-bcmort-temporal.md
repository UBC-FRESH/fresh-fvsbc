# D9.38 BCMORT temporal holdout with growth

Status: **growth carries temporal signal; calibration shift is severe**
Date: 2026-11-08
Code: `bcmort_temporal.py`
Evidence: `d9-bcmort-temporal-summary.csv`

## 1. Design

Train on intervals that end by 2000; test on intervals that start in 2000 or later. The split has
no overlap and keeps the growth covariate prior to each interval.

The model is the D9.37 crown + height/DBH model, with and without individual-tree prior growth.

## 2. Result

| BEC | Train trees | Test trees | AUC H/D → +growth | Log loss H/D → +growth | Brier H/D → +growth | Mean +growth | Observed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | 26,747 | 1,845 | 0.514 → **0.617** | 0.588 → **0.562** | 0.187 → **0.174** | 0.162 | 0.216 |
| SBSmw | 27,702 | 3,285 | 0.577 → **0.634** | 0.878 → **0.853** | 0.275 → **0.255** | 0.176 | 0.358 |

Growth improves discrimination, log loss, and Brier in both temporal tests. It is not a temporal
calibration fix: the post-2000 event rate is much higher than the pre-2000 model predicts. SBSmw is
especially far off (mean 0.176 vs 0.358 observed).

The pre-2000 height/DBH model is close to random in MSdm1 (AUC 0.514); growth restores a real
signal. This is strong evidence that individual-tree growth is not a TSA-specific artifact.

## 3. Interpretation

- Growth is the first covariate that improves both the TSA holdout and a temporal holdout.
- The temporal level shift is large and not removed by growth. A period/TSA intercept or a climate
  term is still required.
- The post-2000 event rate is high enough that a calibration claim from the pre-2000 model would be
  wrong. Do not use the pooled model without local/temporal calibration.
- The result does not establish a provincial model; it establishes a robust tree-level covariate.

## 4. Decision

- Keep individual-tree prior growth in the BCMORT prototype.
- Do not integrate into FVS and do not issue a bundle.
- The next model must include hierarchical TSA/site or period effects and target calibration.
- No parameter or bundle change.

## 5. Limits

- One temporal split; the post-2000 period mixes several disturbances and climates.
- Only MSdm1 and SBSmw; two BECs, two TSAs each.
- Growth is missing for 43.6% of rows; the missing flag is crude.
- No climate, continuous crown ratio, or period covariate.
- The event rate shift is not explained by the current covariates.

## 6. Claim boundary

This is a diagnostic prototype and a temporal validation. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate.
