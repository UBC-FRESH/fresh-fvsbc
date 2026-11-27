# SBS high basal area: too much growth, then too much self-thinning

Status: **shipped as a bundle change (`BAIMULT 0.5` for BL). Tier stays C.**

## 1. The cell

The SBS fold's `SBSmc2` intervals, with the bundle as it shipped (`MORTMULT 2` on FD/PL/SE/HW):

| Interval | Fold | BA0 | Observed BA1 | Predicted BA1 | Error | Observed TPH | Predicted TPH |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4044716\|1\|1991\|2001 | test | 45.6 | 52.3 | 66.0 | +13.7 | 2,477 | 1,591 |
| 4044716\|1\|2001\|2021 | test | 52.3 | 62.3 | 66.0 | +3.7 | 2,402 | 1,107 |
| 4044717\|1\|1991\|2001 | train | 36.6 | 44.7 | 70.0 | +25.3 | 2,902 | 1,961 |
| 4044720\|1\|1996\|2014 | train | 63.9 | 70.2 | 61.0 | −9.2 | 2,252 | 1,571 |
| 4044744\|1\|1990\|2014 | train | 39.8 | 42.6 | 62.0 | +19.4 | 1,751 | 1,240 |
| 4044949\|1\|1996\|2014 | train | 43.5 | 49.3 | 55.0 | +5.7 | 1,762 | 1,312 |
| 4044950\|1\|1989\|1999 | train | 54.4 | 53.6 | 73.0 | +19.4 | 4,686 | 2,317 |
| 4044950\|1\|1999\|2014 | train | 53.6 | 52.2 | 71.0 | +18.8 | 3,477 | 1,460 |
| 4044951\|1\|1991\|2001 | train | 35.3 | 41.7 | 71.0 | +29.3 | 3,435 | 2,394 |

Ten intervals average **+13.1 m²/ha** of BA and **−1,067 TPH**: the model grows fewer, much bigger trees.
The stands are `BL`-dominated (5,736 BL TPH at `4044950`, 2,702 at `4044717`, 1,801 at `4044716`),
so the four-species mortality bundle never touched them.

## 2. Separating the causes

`4044950|1|1989|1999` (measured BA 54.4 → 53.6, TPH 5,786 → 4,686, QMD 11 cm):

| Setting | TPH | BA |
| --- | ---: | ---: |
| bundle as shipped | 3,528 | 109.0 |
| mortality 0 | 5,787 | **182.0** |
| growth 0 (`BAIMULT 0`) | 4,993 | 63.0 |
| both 0 | 5,787 | 74.0 |

With mortality off, BA reaches 182 from 54 — growth is far too high. With growth off, BA still rises to
63, so the mortality the stand actually suffered is roughly right. The over-growth pushes the stand
toward `BAMAX`, and the `BA/BAMAX` blend then books the excess as self-thinning: that is why turning
growth down also raises TPH.

`4044717|1|1991|2001` shows the same shape (mortality 0: 105 BA from 36.6; growth 0: 41).

## 3. The change

`sbs-v3` gains **`BAIMULT 0.5` for BL** on top of its `MORTMULT 2` for FD/PL/SE/HW. Applying the
half growth to the four species instead did nothing to the cell (BA +13.1 unchanged), because the
cell is BL; applying it to all twelve was no better than BL alone and moved other subzones more.

## 4. Held-out evidence

SBS fold with recruitment and five-year cycles (the configuration the bundle is validated in):

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| Previous bundle | test | −0.24 | 6.38 | −62.6 | 699.6 |
| **New bundle** | **test** | −0.74 | **6.00** | **−37.7** | **686.7** |
| Previous bundle | train | −0.39 | 6.32 | −151.7 | 471.0 |
| **New bundle** | **train** | −1.09 | **5.83** | **−98.7** | **435.5** |

BA MAE and TPH MAE improve in both folds, and the TPH bias improves in both. The test BA bias moves
from −0.24 to −0.74 (−1% of the fold's mean BA). The `SBSmc2` cell moves from **+13.1 to +9.2 m²/ha**
and from **−1,067 to −635 TPH**.

## 5. What remains

The cell is still +9 m²/ha on BA and −635 TPH. Halving BL growth is a stand-level correction, not a
fix of the BL growth form: the W6 large-tree row, fitted across SBS, over-predicts for dense stems
just above the 10 cm boundary. Re-fitting that row with a small-DBH weight is the real repair and is
listed in `notes/reference/w6-sbs-large-tree.md` as the next SBS step.
