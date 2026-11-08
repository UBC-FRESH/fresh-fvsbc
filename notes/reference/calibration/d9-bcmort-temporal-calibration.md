# D9.39 temporal target calibration for the growth model

Status: **a single post-2000 intercept does not repair the temporal shift; hierarchy alone cannot**
Date: 2026-11-08
Code: `bcmort_temporal_calibration.py`
Evidence: `d9-bcmort-temporal-calibration-summary.csv`

## 1. Design

Fit the D9.37 growth model on intervals ending by 2000. Use k randomly selected post-2000 sites to
estimate one target intercept, then test the remaining post-2000 sites. Repeat 40 times. This is the
post-2000 analogue of the D9.36 target calibration curve; it tests whether the temporal level shift
is a simple intercept.

## 2. Result

| BEC | k | Base log loss | Local log loss | Local mean | Observed |
| --- | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | 1 | 0.562 | 0.726 | 0.175 | 0.218 |
| MSdm1 | 2 | 0.562 | 0.587 | 0.186 | 0.216 |
| MSdm1 | 5 | 0.562 | 0.579 | 0.184 | 0.219 |
| MSdm1 | 10 | 0.562 | 0.575 | 0.176 | 0.222 |
| MSdm1 | 20 | 0.562 | 0.576 | 0.183 | 0.222 |
| SBSmw | 1 | 0.853 | 0.817 | 0.287 | 0.356 |
| SBSmw | 2 | 0.853 | 0.811 | 0.233 | 0.356 |
| SBSmw | 3 | 0.853 | 0.794 | 0.243 | 0.357 |
| SBSmw | 5 | 0.853 | 0.805 | 0.232 | 0.358 |
| SBSmw | 10 | 0.853 | 0.801 | 0.225 | 0.355 |
| SBSmw | 20 | 0.853 | 0.807 | 0.229 | 0.361 |

AUC is unchanged by an intercept.

## 3. Interpretation

- For MSdm1, every target intercept makes log loss worse than the uncalibrated pre-2000 model. The
  post-2000 shift is not a constant hazard offset.
- For SBSmw, the intercept improves log loss and mean, but even 20 post-2000 sites leave the mean at
  0.229 vs 0.361 observed. The remaining gap is still large.
- A hierarchical random intercept would shrink the target intercept toward the pre-2000 model. Since
  the pre-2000 model underpredicts post-2000 mortality, that shrinkage moves the mean in the wrong
  direction. Hierarchy alone cannot fix this.
- The missing term is a period/TSA/climate effect that changes the hazard, not a random level with a
  zero prior mean.

## 4. Decision

- Do not add a post-2000 random intercept as a calibration fix.
- Do not integrate BCMORT into FVS and do not issue a bundle.
- A temporal calibration layer would need a period-specific model or a climate/TSA covariate, not
  just partial pooling.
- Keep individual-tree growth; it is the strongest tree-level covariate, but it does not explain the
  temporal level shift.
- No parameter or bundle change.

## 5. Limits

- One temporal split; the post-2000 period mixes several disturbances and climates.
- Only MSdm1 and SBSmw; two TSAs each.
- The intercept is estimated on a site split, not a probability sample of the TSA.
- No period, climate, or continuous crown-ratio covariate.
- Growth is missing for 43.6% of rows.

## 6. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim, and it
is not a certificate.
