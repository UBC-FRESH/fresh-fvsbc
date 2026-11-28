# CDF high-BA ingress: the stand-level term cannot help the full fold

Status: **negative.** No engine or bundle change ships.

## 1. What the observed new stems say

The recruitment model's CDF 60+ rate is 2.11 TPH/yr at scale 1.0 (0.84 at the shipped 0.4). The
observed gross ingress in the high-BA intervals is not a single rate:

| Interval group | Observed gross TPH/yr |
| --- | ---: |
| dense stand, 1977–1987 | 18.9 |
| dense stand, 1987–1997 | 9.2 |
| dense stand, 1997–2008 | −4.8 (unaccounted removal) |
| dense stand, 2008–2024 | 0.5 |
| 60–81 m²/ha sites | 0 to 5.3 |

The model rate is already close to the recent dense interval (0.84 vs 0.5 TPH/yr). The large
deficits are two historical pulses, and several other high-BA intervals have essentially no
ingress. A single high-BA multiplier cannot represent both.

## 2. Candidates tested

All candidates keep `cdf-v3` and add CDF 60+ recruitment at the selected bins:

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| `cdf-v3` | **2.489** | **201.406** | **2.032** | **164.062** |
| 60+ ×2 | 2.489 | 208.561 | 2.032 | 171.642 |
| 60+ ×3 | 2.489 | 209.464 | 2.032 | 171.700 |
| 60+ ×4 | 2.489 | 210.206 | 2.032 | 171.527 |
| 60+ ×2, QMD 28.99–33.01 only | 2.489 | 207.748 | 2.032 | 171.546 |
| 60+ ×3, QMD 28.99–33.01 only | 2.489 | 207.587 | 2.032 | 171.508 |

BA is unchanged because ingress adds stems below the BA-carrying sizes. TPH gets worse in every
variant on the expanded clean fold (31 test / 52 train).

## 3. The LOOCV signal does not transfer

On the 20-interval high-BA leave-one-site-out subset, 60+ ingress ×2–×3 improved mean TPH MAE
(47.2 → 41.4–42.8). The full clean fold contains many intervals where TPH is already over-predicted;
adding stems there raises the MAE. The subset average was not a fold-level improvement.

## 4. Consequence

No ingress term ships. The CDF high-BA TPH residual is interval-specific: two historical ingress
pulses, several near-zero-ingress stands, and several over-predicted dense intervals. A stand-level
BA/QMD-scoped multiplier cannot separate them. The engine and `cdf-v3` stay as they are.

## Reproduce

- Expanded fold: `probe_cdf_ingress_expanded_b60x{2,3,4}/`, `probe_cdf_qmding_expanded_x{2,3}/`
  against `probe_cdf_base_expanded/`.
- LOOCV: `probe_cdf_loocv_*`.
