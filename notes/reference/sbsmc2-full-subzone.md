# The SBSmc2 sample was not representative: the full subzone is far worse

Status: **finding + non-shipped grid.** The shipped SBS bundle stays; its SBSmc2 validation is
sample-specific and should be restated.

## 1. The sample

The SBS fold samples `per_bec 10` across all subzones, which gave only **10 SBSmc2 intervals**
(2 held out, 8 train). The calibration data actually contains **249 SBSmc2 intervals on 126
sites**. A dedicated 20% site split gives 42 held-out and 163 train intervals.

## 2. The full-subzone result

Base (no SBS bundle parameters, recruitment, 5-year cycles):

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 10-interval sample | test | −3.76 | — | −321 | — |
| **full subzone** | **test** | **+11.6** | **14.0** | **−1,064** | **1,298** |
| full subzone | train | +5.0 | 8.4 | −297 | 574 |

The full subzone **over-predicts BA by 11.6 m²/ha** and **under-predicts TPH by 1,064**, an
order of magnitude larger than the sampled cell. The 10-interval cell happened to sit near the
crossing point; it is not representative.

The shipped bundle adds `MORTMULT 1.85`, which improves the full-subzone BA (test 6.5 / 10.5)
but pushes TPH further down (test −1,295 / 1,393). The shipped `MORTMULT` was selected on the
unrepresentative sample and does not generalize.

## 3. Size-specific grid on the full subzone

`FIXDG BL g 10 20` × `MORTMULT m` (FD/PL/SE/HW), 249-interval subzone:

| g / m | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| 1.0 / 1.0 | 14.0 | 1,298 | 8.4 | 574 |
| 0.5 / 1.0 | 13.7 | 1,278 | 8.3 | 571 |
| 0.5 / 1.85 | 10.2 | 1,374 | 6.0 | 629 |
| 0.5 / 0.7 | 16.0 | 1,243 | 9.7 | 563 |
| 1.0 / 0.7 | 16.3 | 1,260 | 9.8 | 566 |

Growth reduction buys BA and costs TPH; lower mortality buys TPH and costs BA. The best
both-MAE point (0.5 / 1.0) improves only 0.3/21 and leaves the defect essentially intact. A
size-specific 10–20 cm term cannot fix a full-subzone TPH deficit of this size.

## 4. What this means

- The SBSmc2 claim of +1.5/−81 (0.41.3) is **sample-specific**; the full subzone is +11.6/−1,064.
- The shipped `MORTMULT 1.85` is tuned to the sample and worsens full-subzone TPH.
- The real defect is in small-stem mortality/ingrowth across the whole subzone, not BL 10–20 cm
  growth.
- A proper SBS recalibration needs a full-subzone fold (which now exists) and a mortality /
  ingrowth shape change, and it should replace the sample-selected bundle.

No change ships from this step. The finding is recorded so the next SBS release starts from the
representative fold.

## Reproduce

- Split: `~/workspace/bwbs-work/sbsmc2_test_sites.txt` (27 test sites).
- Base: `~/workspace/bwbs-work/probe_sbsmc2_full/` (205 rows).
- Grid: `~/workspace/bwbs-work/probe_sbsmc2_grid/` (1,845 rows).
