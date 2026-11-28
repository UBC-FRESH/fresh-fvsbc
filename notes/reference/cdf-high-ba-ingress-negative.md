# CDF high-BA ingress/mortality: negative on the held-out fold

Status: **negative result / identifiability block.** `cdf-v3` stays; no shipped parameter changes.

## 1. The task

The dense CDF stand still under-predicts TPH (model 462 vs observed 518, −56). The next test was a
high-BA ingress or mortality term, fitted on the train fold and validated on the held-out fold.

The train fold cannot identify it: in the 16-interval CDF fold the train BA range is **29.4–55.9
m²/ha**. The only BA > 90 intervals in the whole calibration set are the held-out dense site's own
history (four intervals at 93.6, 102.8, 109.6 and 112.5). Expanding the train with the high-BA
sites that are not held out adds only eight intervals at **63–81 m²/ha**. A > 90 response is
therefore fitted on one site and validated on the same site.

## 2. What was tested

The clean fold applies both data screens: tree 84's typo (`--max-dbh-growth-rate 5`) and
unaccounted removals (`--max-unaccounted-removal 0.1`). That drops the 2008–2024 typo interval and
three harvest/removal intervals (`4002933|1|2008|2022`, `4002809|1|2002|2022`,
`4002975|1|1944|1947`). The fold is then 14 test / 12 train intervals; the baseline TPH MAE falls
from 50.6 to **36.1** once the harvest intervals are removed.

Candidates were built on top of `cdf-v3` (BAIMULT 8; MORTMULT 0.5 FD/AC; W30 ×0.1 above BA 90):

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| **cdf-v3 (shipped)** | **1.318** | **36.10** | **1.827** | **125.15** |
| recruitment v1, scale 0.4 | 1.318 | 38.64 | 1.827 | 124.23 |
| recruitment v1, scale 1.0 | 1.318 | 48.94 | 1.827 | 131.57 |
| 60+ bin ×2 | 1.318 | 40.44 | 1.827 | 124.23 |
| 60+ bin ×3 | 1.318 | 42.80 | 1.827 | 124.23 |
| 60+ bin ×4 | 1.318 | 44.80 | 1.827 | 124.23 |
| all-species MORTMULT 0.5 | 1.247 | 43.59 | 1.827 | 117.65 |
| all-species MORTMULT 0.25 | 1.196 | 50.30 | 1.827 | 117.23 |
| 60+ ×2 + all-species mort 0.5 | 1.247 | 51.23 | 1.827 | 119.32 |
| 40–60 bin ×2 | 1.318 | 42.28 | 1.827 | 123.82 |
| 30–40 bin ×2 | 1.318 | 40.07 | 1.827 | 129.90 |

No candidate improves both BA and TPH. The shipped `cdf-v3` is already the TPH optimum; every
ingress or mortality change trades one set of intervals for another.

## 3. Why

The clean-fold TPH errors change sign within the same stand:

| Interval | BA0 | TPH error |
| --- | ---: | ---: |
| `4002349|1|1977|1987` | 93.6 | −169 |
| `4002349|1|1987|1997` | 102.8 | −58 |
| `4002349|1|1997|2008` | 109.6 | +29 |
| `4002349|1|1927|1932` | 58.3 | +37 |
| `4002349|1|1936|1942` | 64.9 | +48 |
| `4002932|1|1998|2008` | 44.4 | −200 |

The model under-predicts the 1977–1997 dense intervals and over-predicts the 1997–2008 and early
intervals; it also under-predicts the low-BA `4002932` intervals. A stand-level multiplier cannot
separate these without a stand-specific switch.

## 4. What would unlock it

An **independent CDF stand with BA > 90 and two or more remeasurements**. The current data has one
such site, and it is the validation point. With a second high-BA site, a > 90 ingress/mortality
term could be fitted on one and tested on the other.

The `--max-unaccounted-removal` screen is added to the probe for future folds; it is a data screen,
not a parameter change. It removed three harvest/removal intervals that were inflating the CDF TPH
error.

## Reproduce

- Raw and clean folds: `probe_cdf_dense_current/`, `probe_cdf_clean_cdf/`.
- Candidate runs: `probe_cdf_clean_{rec04,rec10,rec15,b60x2,b60x3,b60x4}`, `probe_cdf_mort_*`,
  `probe_cdf_ing2_*`.
- Tool: `--max-unaccounted-removal 0.1`.
