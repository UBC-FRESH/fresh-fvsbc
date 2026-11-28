# W37: CW height fitted against the engine's DGM

Status: **best stand-level CW result so far, but BA/TPH do not improve; no ship.**

## 1. The fit

The earlier CW forms were fitted against the observed ten-year diameter increment. W37 fits the
engine's own predicted DGM. FVS was run on 16 CWH intervals with tree output
(`FVS_TreeList_Metric`); 1,107 input trees were matched to observed height pairs by tree number and
period. The engine's periodic DG was converted to a ten-year increment.

Fitted form (CWH only):

```
HTG10 = 2.1859 + 0.0866*DGM_engine + 0.0014*D - 0.0442*max(0, H - 30)
```

with height-decile weights. The engine-DGM coefficient is much smaller than the observed-DGM
coefficient (0.087 vs 0.439); the intercept carries most of the level.

## 2. Fit quality (1,107 trees)

| Metric | Value |
| --- | ---: |
| Bias | −0.004 m/decade |
| RMSE | 1.512 m/decade |
| Tall-quintile bias | −0.047 m/decade |

The sample is dominated by small trees (75% below 12 m), so the tall term is weakly constrained.

## 3. CWH fold (65 test / 142 train)

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| donor | 3.3810 | **171.414** | 4.2705 | **269.067** |
| W37 | 3.3810 | 171.491 | 4.2634 | 269.124 |

BA is flat; TPH is marginally worse in both folds.

## 4. Stand-level A/B (246 CWH intervals)

| Build | BA bias | Top-height bias | Volume bias |
| --- | ---: | ---: | ---: |
| donor | −4.737 | −5.55 | −106.98 |
| W37 | −4.741 | **−5.376** | **−104.183** |

Top height improves by 0.17 m and volume by 2.8 m³/ha; BA is flat (−0.004) and TPH is not improved.
This is the first CW form to move top height and volume in the right direction.

## 5. Decision

The shipping rule requires BA, TPH and top-height all to improve. W37 improves only top height and
volume, so it does not ship; the engine is reverted. It is the closest CW result so far and the
natural candidate if a future rule accepts BA/TPH-neutral height improvements.

A stronger fit would need a height-balanced interval sample (the current 16 intervals are mostly
small trees), which is a sampling change on the existing CWH pairs, not new data.

## Reproduce

- Collection: `~/workspace/bwbs-work/collect_engine_dgm.py`, `engine_dgm_pairs.csv`.
- Fold: `probe_CWH_w37/` against `probe_CWH_zone_stable_bundle/`.
- A/B: `cwh-height-w37-summary.csv` against `cwh-height-w11revert-summary.csv`.
