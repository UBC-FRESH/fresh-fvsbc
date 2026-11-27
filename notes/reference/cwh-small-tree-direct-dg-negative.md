# CWH small-tree diameter: the density response is real, but fixing it costs TPH

Status: **negative result.** No change shipped; `cwh-v3` and engine 0.4.11 stay as they are.

## 1. The data

Direct same-tree diameter pairs below 10.16 cm in CWH: **120,865** pairs on 4,879 intervals
(`cwh_height_pairs.csv`, live both visits).

Small-tree diameter growth falls steeply with stand CCF:

| Stand CCF | Pairs | Mean DBH (cm) | DG (cm/yr) |
| --- | ---: | ---: | ---: |
| < 100 | 22,687 | 5.7 | **0.484** |
| 100–150 | 20,350 | 6.5 | 0.296 |
| 150–200 | 25,406 | 6.9 | 0.199 |
| 200–250 | 26,519 | 7.1 | 0.146 |
| 250–300 | 17,321 | 7.3 | 0.102 |
| 300–400 | 8,137 | 7.3 | 0.081 |

A pooled log fit gives `ln(DG) = −1.386 + 0.200*D − 0.0102*D² − 0.790*(CCF/100)`
(residual SD 0.89; species-specific fits in the local script).

## 2. The engine is flat

Two synthetic CWHvm1 HW stands, 5-year cycles, CWH bundle:

| Stand CCF | TPH | BA | Small-tree DG (cm/yr) |
| ---: | ---: | ---: | ---: |
| 14 | 180 | 3 | 0.161 |
| 69 | 279 | 16 | 0.179 |
| 166 | 459 | 40 | 0.186 |
| 329 | 761 | 81 | 0.176 |
| 655 | 1,359 | 162 | 0.155 |

The height-derived small-tree model is essentially density-neutral (0.155–0.186 across CCF
166–655), while the data fall to ~0.08–0.10 above CCF 250. The structural gap is real.

## 3. W20: fit and patch

A density multiplier on the small-tree diameter increment, fitted from the observed/engine ratio
(~−0.45 per 100 CCF around the CCF-166 match point):

```
DGK = DGK * EXP(-0.45 * (CCF/100 - 1.66))     ! CWH only
```

Inserted in `regent.f` after the height-to-diameter increment is formed (`w20-cwh-small-density`).

## 4. Fold A/B (shipped `BAIMULT 8`)

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| **shipped** | test | +0.158 | **4.000** | +199.8 | **273.0** |
| W20 | test | −0.304 | **3.804** | +227.5 | 297.8 |
| **shipped** | train | −0.108 | **5.030** | +139.3 | **357.3** |
| W20 | train | −0.301 | **4.976** | +147.8 | 364.1 |

W20 improves BA MAE on **both** folds — the structural correction is doing what it should — but it
adds stems (less competition) and worsens TPH, which was already over-predicted.

Pairing W20 with heavier mortality moves back along the same frontier:

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| shipped | **4.000** | **273.0** | **5.030** | **357.3** |
| W20 | 3.804 | 297.8 | 4.976 | 364.1 |
| W20 + MORTMULT 1.1 | 3.857 | 285.7 | 5.037 | 357.2 |
| W20 + MORTMULT 1.2 | 3.911 | 274.7 | 5.167 | 350.3 |
| W20 + MORTMULT 1.35 | 4.095 | 258.7 | 5.380 | 341.0 |

No setting improves both BA and TPH, and every mortality increase also worsens train BA.

## 5. Conclusion

The direct diameter response confirms the W18 read: the small-tree model needs a real density
term, not a row edit. But adding it to the current bundle trades BA for TPH, and the CWH fold
already over-predicts TPH. Shipping would require a mortality/growth interaction that the current
one-parameter form cannot express.

W20 was reverted; the shipped fold is verified at test +0.158 / 4.000, TPH +199.8 / 273.0 and
train −0.108 / 5.030. The next form should carry density in both diameter and mortality jointly
(for example a small-tree mortality that responds to the same CCF), not a diameter-only term.

## Reproduce

- Fit/analysis: `~/workspace/bwbs-work/fit_cwh_small_dg.py` (local) and
  `cwh_height_pairs.csv`.
- Synthetic density A/B: the two-stand script recorded in the shell log.
- Fold: `~/workspace/bwbs-work/probe_cwh_verify3/` (shipped) and
  `~/workspace/bwbs-work/probe_cwh_w20_mort/` (W20 × mortality).
