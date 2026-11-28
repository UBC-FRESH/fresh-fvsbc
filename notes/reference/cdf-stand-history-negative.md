# CDF dense stand: no available structural covariate separates the mixed sign

Status: **negative.** No engine or bundle change ships.

## 1. What history exists

The public fire perimeters cover only part of the high-BA CDF set:

| High-BA site group | Recorded fire | Years since fire in the intervals |
| --- | --- | ---: |
| dense >100 m²/ha site | none | — |
| two 60–81 m²/ha sites | none | — |
| two 60–81 m²/ha sites | 1938 | 33–53 |

There is no harvested-block polygon over a CDF high-BA site. Time-since-disturbance is therefore
missing for three of the five sites, including the dense stand where the mixed sign lives.

## 2. Interval-level covariates do not predict the error

TPH error under `cdf-v3` for the 19 high-BA intervals (the tree-84 typo interval excluded):

| Model | Leave-one-site-out MAE | Bias |
| --- | ---: | ---: |
| predict zero (baseline) | **51.5** | +6.8 |
| BA + QMD | 118.7 | −79.7 |
| BA + QMD + initial TPH | 131.5 | −124.8 |
| BA + QMD + initial TPH + fire age | 146.0 | −124.1 |

Every fitted model is far worse than the baseline. A simple QMD threshold predicts the **sign** of
the TPH error at 47–58% accuracy, i.e. at or below chance. BA, QMD, initial TPH and fire age do not
separate the intervals that are over-predicted from those under-predicted.

## 3. Consequence

The dense-stand mixed sign is not a function of the structural covariates available in the PSP
interval table or the public fire/harvest layers. It is a within-site history effect — the 1977–1997
ingress pulses and the later over-predictions occur at the same site, similar BA and QMD. A
stand-level structural covariate cannot fix it without that history.

No engine or bundle change ships. W38 (engine 0.4.17) remains the shipped aggregate CDF improvement;
the dense-specific residual stays documented.

## Reproduce

- Table: `~/workspace/bwbs-work/cdf_highba_errors.csv`.
- Fire history: `~/workspace/bwbs-work/disturbance-data/site_fire_pairs.csv`.
- Baseline errors: `probe_cdf_loocv_*_cdf/`.
