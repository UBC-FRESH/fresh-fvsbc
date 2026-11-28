# SBSmk1 BA-bin recruitment: negative, and the residual is a 1970s pulse

Status: **negative result / data block.** No change ships; `sbsmk1-v3` stays.

## 1. What was tested

The remaining SBSmk1 TPH residual (−409 test / −144 train) was attacked with recruitment scoped to
initial-BA bins instead of a larger uniform scale, on top of the shipped uniform scale 0.4:

| Variant | Test BA MAE | Test TPH bias / MAE | Train BA MAE | Train TPH bias / MAE |
| --- | ---: | ---: | ---: | ---: |
| shipped (`sbsmk1-v3`) | 6.334 | −409 / **810** | 6.088 | −144 / **743** |
| 20–30 ×2 | 6.334 | −319 / 811 | 6.084 | −61 / 751 |
| 20–30 ×3 | 6.334 | −228 / 828 | 6.084 | +23 / 785 |
| 20–30 ×4 | 6.334 | −138 / 853 | 6.084 | +106 / 832 |
| 20–40 ×2 | 6.334 | −265 / 838 | 6.084 | +14 / 780 |
| 20–40 ×3 | 6.334 | −121 / 883 | 6.084 | +173 / 856 |
| 20–30 ×3, 30–40 ×2 | 6.334 | −175 / 855 | 6.084 | +98 / 814 |

Two things are decisive:

1. **BA does not move** — the MAE is identical to four decimals in every variant. Recruitment adds
   stems below the diameter that carries BA, so no ingress variant can improve the BA half of the
   acceptance test.
2. **TPH MAE worsens monotonically** as the targeted bins are boosted, even while the bias
   improves. The shipped uniform 0.4 is already the MAE optimum; adding stems only trades bias for
   variance.

## 2. Why: the residual is an early-period regeneration pulse

Splitting the shipped fold's residual by start decade:

| Fold | Start decade | n | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| test | 1970s | 18 | 8.0 | −1,619 | 1,621 |
| test | 1980s | 20 | 5.0 | +282 | 458 |
| test | 1990s | 14 | 5.0 | +147 | 266 |
| train | 1970s | 69 | 8.0 | −1,231 | 1,267 |
| train | 1980s | 82 | 5.0 | +311 | 468 |
| train | 1990s | 55 | 4.0 | +390 | 513 |

The 1970s intervals carry the entire deficit; from 1980 onward the model slightly **over**-predicts
TPH. The 1970s are 29 of 327 intervals with `next_tph > 5,000`, including post-disturbance pulses:

| Interval | BA0 | TPH0 | BA1 | TPH1 |
| --- | ---: | ---: | ---: | ---: |
| `4045242\|1\|1976\|1986` | 28.1 | 2,646 | 74.2 | 15,233 |
| `4045247\|1\|1976\|1986` | 34.2 | 1,969 | 64.8 | 9,477 |
| `4045266\|1\|1976\|1986` | 20.1 | 1,864 | 37.3 | 8,587 |
| `4045263\|1\|1976\|1986` | 31.2 | 2,184 | 46.5 | 7,994 |

Each gains ~10,000 stems in ten years (QMD falls to ~8 cm). That is a post-disturbance regeneration
pulse, not an untreated stand response; the v1 recruitment model cannot produce it, and no
stationary BEC/species/BA-bin multiplier reproduces it without inflating every other stand by the
same factor.

## 3. Consequence

The SBSmk1 TPH number is not an ingress-scale defect. Fixing it needs one of:

- **disturbance-aware recruitment** (fire/harvest history per interval), which the current data
  does not carry; or
- a documented **data screen** that excludes design/regime breaks (`next_tph > 5,000` or a BA
  change that is not a growth response) from growth calibration, applied to every fold before
  refitting.

Neither is an ingress-bundle change, so nothing ships. The shipped `sbsmk1-v3` (uniform
recruitment 0.4) remains the MAE optimum on the current fold.

## Reproduce

- Variants: `~/workspace/bwbs-work/bundle_sbsmk1_b*.json`.
- Probes: `probe_sbsmk1_b20x{2,3,4}`, `probe_sbsmk1_b2040x{2,3}`, `probe_sbsmk1_b20x3_3040x2`.
- Residual split: `probe_sbsmk1_final/probe.csv`.
