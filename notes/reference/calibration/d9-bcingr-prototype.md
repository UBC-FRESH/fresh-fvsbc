# D9.28 BCINGR hurdle prototype

Status: **mean plausible; event/composition transfer fails**
Date: 2026-11-07
Issue: #462
Code: `bcingr_prototype.py`

## 1. Model

A two-part stand-level recruitment model:

- **Presence:** logistic regression on initial BA, QMD, interval years, parent-tree BA
  by FD/PL/SE/HW, and BEC dummies.
- **Count:** log-linear regression on the positive annual recruitment rate, with a smearing
  correction for the back-transform.
- **Expected recruitment:** `P(present) * exp(Xb) * smearing * years`.

Training: IDFdk excluding 100 Mile House, 712 intervals. Test: 100 Mile House, 203 intervals.

## 2. Result

| Split | Observed mean TPH/yr | Predicted mean TPH/yr | Observed zero fraction | Predicted zero (<0.5) | RMSE | Correlation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 69.25 | 77.29 | 12.8% | 0% | 135.6 | 0.35 |
| Test | 88.53 | 76.24 | 6.4% | 0% | 177.8 | **0.09** |

The mean is plausible, but the model does not transfer to 100 Mile: correlation is 0.09, all test
recruitment events are effectively predicted as present, and the residual RMSE is high.

## 3. Decision

- Do not integrate `BCINGR` into FVS yet.
- Density and parent-BA covariates alone do not explain the 100 Mile recruitment.
- The missing signal is TSA/region/site (and likely climate/seed-year), not another global rate.
- The next model must include hierarchical TSA/site effects and an explicit zero process, and must be
  tested on a held-out TSA.

## 4. Limits

- The count model is a log-linear approximation, not a fitted NB/ZINB likelihood.
- Parent BA is a crude seed-source proxy; it has no fecundity, dispersal, or seed-year term.
- The 100 Mile test is one TSA; no independent site random effect is available for it.
- Species composition is not modeled; the response is total new TPH.

## 5. Claim boundary

This is a prototype screen. It does not support a yield, AAC, legal, or whole-block claim.
