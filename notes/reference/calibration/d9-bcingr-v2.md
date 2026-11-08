# D9.40 BCINGR v2 screen: year and prior growth do not transfer

Status: **100 Mile failure is not a missing zero process or a simple growth/year term**
Date: 2026-11-08
Code: `bcingr_v2.py`
Evidence: `d9-bcingr-v2-summary.csv`

## 1. Design

The D9.28 hurdle model was extended with:

- start year (`year0`);
- prior-interval net and gross BA rate, BA and TPH mortality, and prior interval length;
- missing flags for the prior rates.

Training: IDFdk outside 100 Mile House (712 intervals). Test: 100 Mile House (203 intervals). The
model is still a logistic presence part plus a log-linear positive-count part, not a fitted
zero-inflated NB.

## 2. Result

| Model | Train corr | Train RMSE | Test corr | Test RMSE | Test observed TPH/yr | Test predicted TPH/yr | Test observed zeros | Test predicted zeros |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base D9.28 | 0.353 | 135.6 | 0.088 | 177.8 | 88.53 | 76.24 | 6.4% | 0% |
| + year / prior rates | 0.365 | 137.4 | **0.066** | **198.8** | 88.53 | 81.76 | 6.4% | 0% |

The extra covariates improve the training correlation slightly and the test mean slightly, but the
test correlation gets worse and RMSE increases. The model still predicts no zero-recruitment
intervals even though 6.4% of the 100 Mile intervals have zero recruitment.

## 3. Interpretation

- The 100 Mile failure is not explained by a missing zero process: the observed zero fraction is
  small, and the hurdle still has no predicted zeros.
- Year and prior stand growth do not carry the missing 100 Mile signal. More prior-rate detail is not
  the answer.
- The residual failure is the same data limit as BCMORT: the target TSA (and likely seed-year/
  climate) is not represented.
- A local intercept could move the mean but cannot repair the test correlation of 0.07. The ranking
  failure remains.

## 4. Decision

- Do not add year or prior stand rates to BCINGR.
- Do not integrate BCINGR into FVS and do not issue a bundle.
- The next ingress model needs target-TSA/seed-year/climate data, not more global stand covariates.
- No parameter or bundle change.

## 5. Limits

- Only five IDFdk TSAs; 100 Mile is a single held-out TSA.
- The count part is log-linear with a smearing correction, not a fitted NB/ZINB likelihood.
- No species composition, seed rain, dispersal, or seed-year term.
- Prior stand rates are not individual-tree seed production.
- The test has only 203 intervals and 6.4% zeros.

## 6. Claim boundary

This is a diagnostic screen. It does not support a yield, AAC, legal, or whole-block claim, and it is
not a certificate.
