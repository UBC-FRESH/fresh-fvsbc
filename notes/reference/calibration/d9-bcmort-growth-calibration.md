# D9.36 BCMORT growth history and target calibration curve

Status: **growth history is mixed; local calibration needs several target sites and still does not fix every BEC**
Date: 2026-11-08
Code: `bcmort_growth.py`, `bcmort_calibration_curve.py`
Evidence: `d9-bcmort-growth-summary.csv`, `d9-bcmort-calibration-curve-summary.csv`

## 1. Growth-history screen

The previous interval's stand rates were added to the D9.35 height/DBH model: net and gross BA
rate, BA and TPH mortality, and interval length. The previous interval ends at the current start
visit, so the rates are known at prediction time. Coverage is 66.7%; missing values carry a flag.

| BEC | Train → test | AUC H/D → growth | Log loss H/D → growth | Brier H/D → growth |
| --- | --- | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.763 → **0.767** | 0.386 → **0.383** | 0.1200 → **0.1196** |
| MSdm1 | Boundary → Okanagan | 0.684 → 0.684 | 0.412 → 0.423 | 0.1256 → 0.1305 |
| SBSmw | Quesnel → Prince George | 0.758 → 0.756 | 0.382 → 0.384 | 0.1186 → 0.1190 |
| SBSmw | Prince George → Quesnel | 0.721 → 0.720 | 0.463 → **0.455** | 0.1387 → **0.1365** |

Growth history improves MSdm1 Okanagan → Boundary and SBSmw Prince George → Quesnel, but worsens
MSdm1 Boundary → Okanagan and SBSmw Quesnel → Prince George. It is not a robust transfer covariate.

## 2. Target calibration curve

The D9.35 height/DBH model was fit on the source TSA. For each k, k randomly selected target sites
estimated one intercept and the remaining target sites were tested. Repeated 40 times.

| BEC | Train → test | Base log loss | k=1 | k=5 | k=20 | Local mean at k=20 | Observed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.386 | 0.397 | 0.383 | **0.379** | 0.135 | 0.155 |
| MSdm1 | Boundary → Okanagan | 0.412 | 0.416 | 0.412 | 0.411 | 0.143 | 0.160 |
| SBSmw | Quesnel → Prince George | 0.382 | 0.401 | 0.385 | 0.387 | 0.138 | 0.164 |
| SBSmw | Prince George → Quesnel | 0.463 | 0.476 | 0.458 | 0.459 | 0.151 | 0.187 |

A single target site is worse than no calibration. Five or more sites help MSdm1 Okanagan → Boundary
and SBSmw Prince George → Quesnel, but SBSmw Quesnel → Prince George remains worse than the
uncalibrated model even at 20 sites. The local mean is still below the observed event rate in every
direction. AUC is unchanged by an intercept.

## 3. Interpretation

- Prior stand growth is a direction-dependent covariate, not a universal transfer term.
- A target intercept needs several target sites; one site is not enough.
- Even with 20 target sites, the target mean remains biased and the source ranking is unchanged.
  The missing term is not a single global covariate.
- The result is consistent with a real data limit: no available tree or stand covariate predicts
  the target-TSA level, and a local intercept alone cannot repair the ranking or the residual mean.
- A hierarchical random intercept would shrink the local intercept, but it cannot manufacture
  target information that is not in the source covariates.

## 4. Decision

- Do not add prior stand growth as a universal BCMORT term.
- Do not integrate BCMORT into FVS and do not issue a bundle.
- For deployment, require a target local calibration sample; this evidence says one site is not
  enough, and five is not uniformly enough.
- Stop global covariate/multiplier screens. The next useful model work is a hierarchical
  TSA/site model with explicit target data, or a climate/crown-ratio data source.
- No parameter or bundle change.

## 5. Limits

- Only two TSAs per BEC; the calibration curve is a site-split diagnostic, not a production
  sampling design.
- Growth history uses stand-level previous-interval rates, not individual-tree growth.
- The calibration curve uses a single intercept; it does not estimate a full hierarchical model.
- No climate, continuous crown ratio, or individual-tree growth yet.
- The target sites are not a random sample of the TSA.

## 6. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim, and
it is not a certificate.
