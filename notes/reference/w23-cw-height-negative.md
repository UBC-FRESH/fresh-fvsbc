# A negative result: a taper-free CW height form does not ship

Status: **explored, reverted. CW keeps the donor large-tree height row.**

## 1. The hypothesis

The W11 fit for CW improved pair-level RMSE but halved tall-cedar height growth on a real
interval, so CW kept the donor. The row forms carry `EXP(C*HTM²)`, which trades the tall end
against the mid-range. A taper-free form should fit both.

## 2. The data

CWH CW/YC same-tree pairs, live both, DBH ≥ 10.16, crown D/C (`cwh_height_pairs.csv`):

| Initial height (m) | n | Mean 10-yr growth | Median | 10th | 90th |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10–20 | 3,211 | 2.56 | 2.25 | 0.60 | 4.80 |
| 20–30 | 4,303 | 1.95 | 1.60 | 0.42 | 3.90 |
| 30–40 | 1,586 | 1.63 | 1.19 | 0.26 | 3.59 |
| 40–50 | 249 | 1.19 | 0.59 | 0.10 | 3.00 |
| 50–80 | 53 | 1.24 | 1.25 | 0.24 | 2.73 |

The tall end is not a clean signal: above 40 m the growth ranges from 0.1 to 3.0 m/decade
(median 0.59, mean 1.19), and the 50+ bin turns back up on 53 trees.

## 3. The candidate form

`HTG10 = EXP(a + b*HTM + c*D + d*DGM)` fitted on 10,562 pairs (`htg10 ≤ 6`), with smearing:

```
a = 0.37250   b = -0.005410   c = -0.010080   d = 0.202320
```

Tall-end bias at 40–50 m: **−0.25 m/decade**, better than the old row's halving. But the
aggregate RMSE is **3.17** (the old W11 row: 1.20) because the mid-range is dominated by
wide scatter, and the relative-error fit pulls the mid-range.

## 4. Stand-level A/B

246 CWH intervals, 12 per BEC, the same tree lists, donor versus the new form:

| Metric | Donor | New form |
| --- | ---: | ---: |
| Top-height bias (m) | −5.55 | −5.60 |
| Volume bias (m³/ha) | −106.98 | **−108.44** |
| Volume MAE (m³/ha) | 127.11 | **128.13** |
| BA bias (m²/ha) | −4.737 | −4.761 |

Both the height and volume cells move the wrong way. The absolute top-height bias is a
definition mismatch (FVS `TopHt` vs FAIB), so the A/B delta is the usable signal: the new form
is **worse** by 0.05 m of top height and 1.46 m³/ha of volume.

## 5. Conclusion

The tall-end pair fit does not survive at stand level. The CW pair data at 40+ m are too
dispersed to identify a form that improves the tall end without costing the mid-range, and the
donor is closer at stand level. CW keeps the donor.

This closes the height-form route on the current data. A new CW equation would need either
more tall-cedar measurements or a height measurement definition that separates top damage from
growth; the current FAIB pairs cannot do it.

## Reproduce

- Fit: the local `cwh_height_pairs.csv` analysis (heights, medians, taper-free fit).
- A/B: `~/workspace/bwbs-work/cwh-height-w23base-summary.csv` (donor) and
  `cwh-height-w23-summary.csv` (new form), 246 intervals each.
- Patch was applied to `htgf.f`, built, measured, and reverted; the engine is back on 0.4.13.
