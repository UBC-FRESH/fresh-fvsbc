# D9.56 INITMORT severity calibration: one multiplier does not transfer

Status: **the correct lever works, but a single severity multiplier is stand/TSA-dependent**
Date: 2026-11-08
Build: D9.46 BC MPB extension

## 1. Design

Training: three IDFdk3 100 Mile five-year high-PL intervals.
Holdout: SBSdw1/SBSdw2/SBPSmk Williams Lake five-year high-PL intervals.

The observed inch-class vector was fed to `INITMORT` with multipliers 0.02–0.08.

## 2. Result

| Interval | Set | Observed | 0.04× | 0.05× | 0.08× |
| --- | --- | ---: | ---: | ---: | ---: |
| `4024547` | train | 0.960 | 0.715 | 0.776 | 1.000 |
| `4024546` | train | 0.955 | 0.754 | 0.810 | 1.000 |
| `4024754` | train | 0.944 | 0.622 | 0.697 | 0.888 |
| `4032478` | holdout | 0.964 | 0.879 | 1.000 | 1.000 |
| `4024340` | holdout | 0.960 | 0.944 | 1.000 | 1.000 |
| `4024380` | holdout | 0.806 | 0.813 | 1.000 | 1.000 |

A single multiplier cannot satisfy both sets:

- **0.04×** fits the holdout well but underpredicts the training stands by 0.20–0.32.
- **0.08×** fits the training stands much better but overpredicts the holdout stands to 1.00.
- **0.05×** is a poor compromise: training 0.697–0.810, holdout 1.00 on all three.

The INITMORT response is steep and saturates. The severity is not a global constant.

## 3. Interpretation

- `INITMORT` is the correct lever; this is not a keyword or unit problem anymore.
- The remaining variation is stand/TSA/outbreak severity, not a single multiplier.
- A global INITMORT multiplier would overfit the training BEC or the holdout BEC.
- The correct model is a severity function of stand/outbreak covariates, or a local calibration
  sample per target TSA.

## 4. Next

1. Fit a severity model using PL BA/TPH, QMD, BEC/TSA, and outbreak timing.
2. Or require local target-TSA calibration for INITMORT, with ≥2 intervals per target.
3. Add non-PL BA/TPH checks.
4. Keep five-year intervals; the 10-year cap remains separate.
5. Do not adopt 0.04× or 0.08× as a provincial constant.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
