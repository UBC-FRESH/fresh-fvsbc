# W33: a donor-preserving tall-tree CW term

Status: **negative for shipping.** It improves top height and volume marginally but leaves BA and
TPH unchanged; the donor stays.

## 1. The term

Instead of replacing the CW row, the donor is kept at small and mid heights and a tall-tree factor
is applied:

```
HTG_CW = HTG_donor * (1 + 0.047657 * max(0, H_m - 25))
```

for CW in CWH only. The coefficient was fitted on the CWH pairs with the donor as the base, using
the same 20% interval holdout as the earlier CW fits.

## 2. Pair fit

| Model | RMSE (m/decade) | Bias | Tall-quintile bias (28.6–57 m) |
| --- | ---: | ---: | ---: |
| donor | 1.493 | −0.049 | −0.638 |
| W33 tall term | **1.478** | +0.047 | **−0.295** |

The tall-end error is roughly halved without moving the small/mid-size trees.

## 3. Held-out CWH fold (65 test / 142 train intervals)

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| donor | 3.3810 | 171.414 | 4.2705 | 269.067 |
| W33 | 3.3810 | 171.414 | 4.2705 | 269.067 |

The fold sample has no CW tall enough for the term to act, so held-out BA and TPH are identical.

## 4. Stand-level A/B (246 CWH intervals)

| Build | BA bias | Top-height bias | Volume bias |
| --- | ---: | ---: | ---: |
| donor | −4.737 | −5.55 | −106.98 |
| W33 | −4.737 | **−5.53** | **−106.57** |

Top height and volume improve by 0.02 m and 0.41 m³/ha; BA is unchanged. The shipping rule requires
BA, TPH and top-height all to improve, so the term does not ship.

## 5. Consequence

The CW donor stays. The pair-level tall-end gain is real but too small to move the stand metrics
under the current rule; a future CW formulation needs a stronger, structurally different term.

## Reproduce

- Fit: `~/workspace/bwbs-work/fit_cw_new.py` tall-term grid (H0=25, exp=1).
- A/B: `cwh-height-w33-summary.csv` against `cwh-height-w11revert-summary.csv`.
- Fold: `probe_CWH_w33/` against `probe_CWH_zone_stable_bundle/`.
