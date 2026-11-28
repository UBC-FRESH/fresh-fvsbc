# W39: CW height refit against engine DGM with the tree key fixed

Status: **negative on the shipping rule.** Top height and volume improve; BA/TPH do not. No ship.

## 1. Fixing the tree key

FVS does not preserve the observed `TREE_NO` in `FVS_TreeList_Metric.TreeId`. The key was recovered
without changing FVS: for each interval, the initial output tree list (`Year = year0`) was matched
to each input record by **species and nearest DBH**, giving its `TreeIndex`; the end-of-period row
with the same `TreeIndex` supplied the predicted DG. This produced **1,491 matched trees from 29
tall CWH intervals** (mean height 29.6 m, mean engine DGM 1.98 cm/10-year).

## 2. The fit

Fitted against engine DGM with height-decile weights:

```
HTG10 = 0.90141 + 0.00277*DGM + 0.01158*D + 0.00003*D^2
        - 0.02657*max(0, D - 50)
```

| Metric | Value |
| --- | ---: |
| Bias | 0.000 m/decade |
| RMSE | 1.085 m/decade |
| Tall-quintile bias | +0.026 m/decade |

The engine-DGM coefficient is near zero; the form is effectively a DBH/tall-tree equation.

## 3. CWH fold (65 test / 142 train)

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| donor | 3.3810 | **171.414** | 4.2705 | **269.067** |
| W39 | 3.3810 | 171.506 | 4.2705 | 269.152 |

BA is unchanged; TPH is marginally worse.

## 4. Stand-level A/B (246 CWH intervals)

| Build | BA bias | Top-height bias | Volume bias |
| --- | ---: | ---: | ---: |
| donor | **−4.737** | −5.55 | −106.98 |
| W39 | −4.770 | **−5.493** | **−106.773** |

Top height improves 0.057 m and volume 0.21 m³/ha; BA is 0.033 worse.

## 5. Consequence

A height-only change cannot improve BA/TPH in this engine: the fold and A/B show flat-to-worse
stand metrics even with a reliable, tall-balanced engine-DGM fit. The shipping rule therefore
cannot be met by a CW height equation. The decision is whether to accept BA/TPH-neutral height
improvements; W39 is weaker than W37 on top/volume, so W37 remains the better candidate if that
decision is made.

The engine is reverted to the shipped 0.4.17 (W38) behavior; no release.

## Reproduce

- Keyed collection: `~/workspace/bwbs-work/collect_engine_dgm_keyed.py`,
  `engine_dgm_pairs_keyed.csv`.
- Fold: `probe_CWH_w39/` against `probe_CWH_zone_stable_bundle/`.
- A/B: `cwh-height-w39-summary.csv` against `cwh-height-w11revert-summary.csv`.
