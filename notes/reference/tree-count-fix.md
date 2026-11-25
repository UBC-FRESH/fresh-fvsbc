# The tree-count fix: densities and what it changed

Status: **fixed in the wrapper, folds re-run, bundles unchanged.**

## 1. The bug

The wrapper wrote `tree_count` under the variant's compiled format (`F6.0`), so the expansion
factor was rounded to a whole tree. A PSP plot with a 0.4 ha basis has about 2.47 trees/ha per stem,
which became 2: the stand started **19% below its measured basal area**. Small plots (0.04–0.1 ha,
10–25 trees/ha per stem) lost 1–2%. Every calibration and every backtest inherited the loss, and the
large `BAIMULT 8` bundles were partly compensating for it.

One dense CDFmm interval made it visible: observed BA0 112.5 m²/ha, run BA0 90. The tree list itself
carried 111.8.

## 2. The fix

The wrapper declares `TREEFMT` with `F6.2` for that one field. The width, the column positions, and
the rest of the record are unchanged; only the decimals appear. The variant reads the format from the
keyword, so no binary change is needed and the engine stays `fresh-fvsbc-pyfvs 0.4.4`.

After the fix the same interval starts at BA 111 against 112.5 measured.

## 3. Zone folds re-run

Same held-out sites and candidate sets as the banked notes, re-run on the fixed writer.

### CDF (16 held-out / 14 train)

| Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| `BAIMULT 1` | −8.18 | 8.18 | −0.02 | 4.58 |
| `BAIMULT 4` | −6.56 | 6.63 | +1.12 | 4.14 |
| **`BAIMULT 8`** | **−5.12** | **5.32** | **+2.70** | **4.12** |
| `BAIMULT 10` | −4.62 | 4.98 | +3.34 | 4.48 |

Before the fix the same fold read −16.1 test at `BAIMULT 8`. The remaining −5 m²/ha is real model
error at high BA on the dense held-out site, not a density artifact.

### CWH (108 held-out / 290 train)

| Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| `BAIMULT 1` | −4.49 | 5.99 | −4.88 | 6.60 |
| `BAIMULT 4` | −2.35 | 4.75 | −2.70 | 5.50 |
| **`BAIMULT 8`** | **+0.15** | **4.01** | **−0.13** | **5.03** |

`BAIMULT 8` remains the bundle: best held-out MAE and near-zero bias on both folds.

### MH (3 held-out / 15 train)

| Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| `BAIMULT 4` | +1.14 | 2.04 | −1.79 | 4.58 |
| `BAIMULT 6` | +1.14 | 2.04 | −0.59 | 4.11 |
| **`BAIMULT 8`** | **+1.47** | **1.71** | **+0.14** | **3.78** |

`BAIMULT 8` remains, and the held-out bias improves from +1.81 to +1.47.

### SBPS (6 held-out / 21 train, `MORTMULT 2`)

| Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| **`BAIMULT 1`** | **+2.18** | 2.64 | −1.65 | 7.03 |
| `BAIMULT 4` | +2.18 | 2.30 | −0.93 | 6.60 |
| `BAIMULT 8` | +2.18 | 2.18 | −0.31 | 6.31 |

The bundle stays `MORTMULT 2` with no BAIMULT. Adding one would improve the fit, but the test fold is
six intervals and the bias is already small; a stand-level multiplier is not the right tool.

### SBS (38 held-out / 106 train, `MORTMULT 2`)

| Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| **`BAIMULT 1`** | **−5.74** | **8.29** | **−6.85** | **8.77** |
| `BAIMULT 4` | −6.87 | 10.81 | −7.62 | 14.98 |
| `BAIMULT 8` | −6.32 | 16.23 | −4.43 | 21.30 |

Adding BAIMULT makes SBS much worse. The bundle stays `MORTMULT 2`; the remaining bias is the
open SBS growth/mortality gap.

## 4. What it means

The fix is a net gain and no bundle moved. It also re-frames some earlier conclusions: part of what
looked like a coastal growth gap was a density artifact, and the CDF dense-stand gap is smaller than
the W10 note recorded. The notes for W8/W10 should be read with this correction in mind.
