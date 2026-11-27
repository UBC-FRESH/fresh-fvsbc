# MS / ESSF / PP: a train-only row refit does not close the shape gap

Status: **diagnosis, no shipped change.** The V3 rows are stable; the gap is a period-basis /
mortality structure, not overfitting.

## 1. What was checked

The held-out note said the W15–W17 rows were fitted in-sample and named a train-only refit as
the honest next step. For ESSF (the best-powered fold: 42 held-out / 260 train intervals), the
dominant species' large-tree diameter rows were refitted on **train-only** pairs with the same
annual response the rows were built with (`ln(growth_cm_per_year)`), and compared with the
shipped rows.

| Species | Train pairs | Train-only CON | Shipped CON | Train-only LD | Shipped LD | Train-only BAL | Shipped BAL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BL | 6,677 | −1.6815 | −1.8281 | 0.0427 | 0.0415 | −0.01736 | −0.01813 |
| SE | 2,647 | −1.2189 | −1.4641 | 0.0222 | 0.0234 | −0.02525 | −0.02526 |
| PL | 758 | −2.5761 | −3.2054 | 0.0615 | 0.0940 | −0.01526 | −0.01721 |

BL and SE are essentially the shipped rows. PL moves more but has 758 train pairs. The rows are
**not overfit**; excluding the held-out sites does not change the shape.

## 2. The period basis

Refitting the same pairs with a **ten-year** response (`ln(10*growth)`) gives a BL constant of
about **+0.75** instead of −1.83 — a factor of ~6 in diameter growth. The engine applies the V3
row as a ten-year increment, so the shipped rows are on an annual basis.

Yet the fold's BA growth is only ~2× low, not 6–10×: ESSF test intervals show observed BA growth
3.54 m²/ha against predicted 1.63. The missing growth is partly absorbed by the tree-count and
mortality behaviour, which is why the BA bias is −3 rather than −30.

Applying the ten-year fit directly would multiply diameter growth ~6× and overshoot the fold.
The defect is a **joint growth/mortality basis mismatch**, not a row-level fitting error.

## 3. Why no ship

- A train-only annual refit reproduces the shipped rows: no change, no gain.
- A train-only ten-year refit would multiply growth ~6×; the fold needs ~2× and would then lose
  TPH to self-thinning, so it cannot improve both.
- The earlier multiplier sweeps showed the same frontier: more BA costs TPH, and the
  held-out/train folds move in opposite directions.

Closing MS/ESSF/PP needs a coupled growth + mortality recalibration on the ten-year basis, and
the held-out split must be used only for validation. That is a larger model-form change than a
row refit, and it is the realistic next target for these zones.

## Reproduce

- Train-only annual fits: the local ESSF pair extraction (`tree_survival.csv`, train sites from
  `essf_test_sites.txt`).
- Fold: `~/workspace/bwbs-work/probe_essf_held_post/` (42 test / 260 train).
