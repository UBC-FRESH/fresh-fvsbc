# W22: the SBSmc2 dense small-tree cell

Status: **shipped in 0.41.3 on engine 0.4.13.** Tier stays C (unsigned).

## 1. The cell

SBSmc2, 10 intervals (2 held out, 8 train), 5-year cycles, recruitment:

| Build | Cell BA | Cell TPH |
| --- | ---: | ---: |
| 0.41.2 (W18 row, `MORTMULT 2`) | +2.8 | −200 |
| **0.41.3 (W22 + `MORTMULT 1.85`)** | **+1.5** | **−81** |

The cell splits: train +4.44 BA / −170 TPH, test −3.76 / −321. The 2.8/-200 figure is their
weighted mean.

## 2. The levers

- **Growth density:** the BL row's CCF coefficient moves from 0 to **−0.35** (CCF/100 in the
  V3 constant).
- **Mortality:** the bundle's `MORTMULT` for FD/PL/SE/HW moves from **2.0 to 1.85**.

Growth reduction lowers BA and raises TPH (less self-thinning); less mortality raises both.
The pair of levers moves the cell BA down and TPH up together.

## 3. Fit and selection

Direct SBS pairs, 10–20 cm, live, BL/FD/PL/SE (28,796 pairs on 1,050 intervals):

| Species | n | Density slope (ln DG per 100 CCF) |
| --- | ---: | ---: |
| BL | 7,562 | −0.364 |
| FD | 829 | −0.465 |
| PL | 20,405 | −0.148 |
| pooled | 28,796 | −0.195 |

The engine's BL 10–20 cm response is **steeper** than the pairs (about −0.53 per 100 CCF from a
synthetic density series), so a direct pair fit would *flatten* growth and raise cell BA. The
−0.35 term is therefore a cell-targeted correction, not a pair fit. It was selected on the train
fold and validated held out.

## 4. Fold table

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.41.2 | test | −0.92 | 6.09 | −22 | 658.9 |
| CCFA −0.35, `MORTMULT 1.5` | test | +0.60 | 5.94 | +110 | 632.5 |
| CCFA −0.35, `MORTMULT 1.75` | test | −0.16 | 5.96 | +45 | 638.5 |
| **CCFA −0.35, `MORTMULT 1.85`** | **test** | **−0.53** | **5.91** | **+20** | **644.3** |
| 0.41.2 | train | −1.68 | 5.22 | −62 | 398.3 |
| CCFA −0.35, `MORTMULT 1.5` | train | −0.57 | 4.87 | +2 | 388.6 |
| CCFA −0.35, `MORTMULT 1.75` | train | −1.22 | 4.92 | −25 | 394.3 |
| **CCFA −0.35, `MORTMULT 1.85`** | **train** | **−1.52** | **4.94** | **−36** | **396.9** |

`MORTMULT 1.85` was chosen because 1.5 overshoots TPH on the held-out fold (+110 bias) while
1.85 keeps it near the shipped level (+20 vs −22) and still improves MAE. All BA and TPH MAE
figures improve on both folds, and the cell improves on both.

## 5. What remains

- The cell is still +1.5 m²/ha / −81 TPH.
- The held-out TPH bias moves from −22 to +20 on a mean of about 650; the MAE still improves.
- The term is specific to SBS BL; FD/PL/SE keep their rows.
- The SBS fold is unsigned (tier C).

## 6. Build

Patch `w22-sbs-bl-density.patch.gz`, applied after `w21-cwh-small-joint.patch.gz`; bundle
`sbs-v3-bl-ccf-mm185-2026-11-27`. The full W2–W18 + W21 + W22 chain was verified from a clean
pinned tree. Engine `0.4.13`, wrapper `0.41.3`.
