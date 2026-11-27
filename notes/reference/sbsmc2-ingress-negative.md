# SBSmc2 ingress recalibration: tested, not shipped

Status: **negative result.** The shipped `sbsmc2-v3` bundle (0.41.5) and engine 0.4.14 (W28) stay.

## 1. Starting point

After 0.41.6 the full-subzone fold is:

| Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| test (42) | +6.9 | 11.61 | −729 | 1,081 |
| train (163) | +0.4 | 7.13 | −183 | 545 |

The remaining deficit is cross-size ingress: too few small stems.

## 2. Global recruitment scale

`sbsmc2-v3` carries the recruitment v1 block at scale 0.4. Raising the scale:

| Scale | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| **0.4 (shipped)** | 11.61 | 1,081 | **7.13** | **545** |
| 0.6 | 11.63 | 1,055 | 7.11 | 556 |
| 0.8 | 11.61 | 1,031 | 7.11 | 573 |
| 1.0 | 11.63 | 1,014 | 7.07 | 599 |
| 1.2 | 11.65 | 1,004 | 7.05 | 632 |
| 1.6 | 11.68 | 1,035 | 7.03 | 735 |

The held-out TPH improves monotonically to scale 1.2; the train TPH MAE is **minimized at the
shipped 0.4**. Train selection keeps the shipped scale.

## 3. Shape by BA bin

The errors align by QMD: both folds over-predict BA and under-predict TPH in low-QMD stands. The
rate table is binned by BA, so the shape was applied there.

- Boost all BA ≤ 50: test TPH improves (1,081 → 1,009 at ×2), train TPH worsens (545 → 559).
- Boost BA 20–30 only (the largest aligned deficit): test TPH 1,081 → 1,022 at ×2, train 545 →
  550; ×3 gives test 982, train 565.

Every shape improves the held-out TPH and worsens the train TPH MAE. The train fold is already at
or above the observed stem count in the bins where recruitment would act.

## 4. Conclusion

The SBSmc2 test and train folds differ in their stem-density distribution: the held-out stands
are systematically more under-stocked. No recruitment scale or BA-bin shape improves both. This
is a **fold-distribution problem**, not a calibratable parameter.

Further SBSmc2 gains need either:

- a reweighted or site-stratified fold that matches the population, or
- independent held-out SBSmc2 sites (the current 126 sites are split 20/80 from one dataset).

Neither is available locally. The bundle and W28 stay as shipped; the residual is +6.9/−729.

## Reproduce

- Scale grid: `~/workspace/bwbs-work/probe_sbsmc2_sc{60,80,100,120,160}/`.
- BA≤50 shape: `probe_sbsmc2_lb{2,4,8}/`.
- BA 20–30 shape: `probe_sbsmc2_ba2030_{2,3,4}/`.
