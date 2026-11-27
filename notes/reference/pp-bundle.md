# `pp-v3`: PP growth and mortality from leave-one-site-out

Status: **shipped in 0.41.9.** Engine unchanged at 0.4.14. Tier stays C (unsigned).

## 1. Why LOSO

PP has **27 intervals on 10 sites**; the old held-out fold was 5 intervals on 2 sites. Leave-one-
site-out uses every site as held-out exactly once, giving a 25-interval held-out estimate (two
intervals have no resolvable trees).

## 2. The candidate grid

Six candidates (growth × mortality) on the LOSO folds:

| Candidate | BA MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: |
| base | 2.58 | −0.1 | 66.05 |
| 2.5 / 0.8 | 1.85 | +1.4 | 65.57 |
| 3.0 / 0.8 | **1.76** | **−0.9** | **65.30** |
| 3.0 / 0.9 | 1.89 | −5.6 | 65.43 |
| 2.5 / 1.0 | 1.97 | −8.1 | 65.87 |
| 3.0 / 1.0 | 1.89 | −10.6 | 66.11 |

`BAIMULT 3.0` + `MORTMULT 0.8` has the best aggregate on both measures.

## 3. Evidence

`pp-v3` re-run through all 10 LOSO folds:

| Build | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | −2.58 | 2.58 | −0.1 | 66.05 |
| **pp-v3** | **−1.70** | **1.76** | **−0.9** | **65.30** |

BA improves on all 8 sites that carry intervals (−0.2 to −1.25 m²/ha). TPH improves on 5 sites
and worsens on 3; the largest worsening is +5 on a 2-interval site. The TPH gain is small
(0.75 MAE) and is not uniform by site.

## 4. What remains

PP is now the last zone with a bundle. The TPH component is marginal; BA is the clear gain. A
future PP review should weight by site size and check the 3 TPH-worsening sites individually.

## Reproduce

- LOSO candidate grid: `~/workspace/bwbs-work/loso_pp_*/`.
- Bundle LOSO: `loso3_pp_*/`.
