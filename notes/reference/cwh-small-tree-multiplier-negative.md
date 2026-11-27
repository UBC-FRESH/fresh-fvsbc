# CWH small-tree donor and CW height donor: multipliers tested, not shipped

Status: **negative result.** No change shipped; `cwh-v3` and engine 0.4.11 stay as they are.

## 1. What was tried

The W18 row fit for CWH small-tree **height** was already reverted (see
`cwh-small-tree-negative.md`). This step took the other route the note named: correct the donor
with the engine's multipliers rather than replace the rows.

- `REGDMULT` — small-tree diameter growth, all 12 CWH species, 0.70–1.30.
- `REGHMULT` — small-tree height growth, all species, 0.70–1.30.
- `HTGMULT` — large-tree height, CW only, 1.10–1.20 (the CW donor is known to be ~4% low on
  dominants; W11).
- Combinations with `BAIMULT` 7.0–7.8 to offset the BA cost of faster small-tree growth.

Everything ran through the CWH fold: 398 intervals, 108 held out, recruitment, five-year
cycles.

## 2. Single multipliers

| Candidate | Test BA bias / MAE | Test TPH bias / MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| **shipped (BAIMULT 8)** | **+0.158 / 4.000** | **+199.8 / 273.0** | **5.030** | **357.3** |
| REGDMULT 1.10 | +0.270 / 4.049 | +195.5 / 269.3 | 5.009 | 356.1 |
| REGDMULT 1.15 | +0.334 / 4.040 | +193.5 / 267.6 | 5.012 | 355.5 |
| REGDMULT 1.20 | +0.390 / 4.095 | +191.5 / 266.0 | 5.020 | 354.9 |
| REGHMULT 1.15 | +0.18 / 3.62* | +156.6 / 199.7* | 5.10* | 431.5* |
| HTGMULT CW 1.10 | +0.000 / 3.63* | +159.6 / 202.5* | 5.13* | 434.2* |
| HTGMULT CW 1.20 | +0.02 / 3.64* | +159.5 / 202.3* | 5.12* | 434.2* |

\* per-BEC-10 screen; the full fold was run for `REGDMULT`.

Faster small trees consistently **reduce TPH error but raise BA error**. The held-out BA optimum is
the shipped build. `HTGMULT` for CW moves BA and TPH by less than 0.1, as expected for a
height-only change.

## 3. Combination with BAIMULT

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| shipped | **3.632** | 202.52 | 5.131 | 434.25 |
| REGD 1.15 / BAI 7.8 | 3.687 | 200.57 | 5.063 | 432.71 |
| REGD 1.30 / BAI 7.8 | 3.687 | 197.63 | 5.086 | 429.84 |

Lowering `BAIMULT` restores the BA level but cannot beat the shipped BA MAE on the held-out fold.

## 4. The one cell that improves

At `REGDMULT 1.15`, the **CWHvm1** test cell improves both BA and TPH MAE (−0.20 and −0.46),
and its train cells improve too. But the test cell is **5 intervals**, the effect is ~0.2 m²/ha,
and other test subzones move the other way. That is too thin to scope a bundle on.

## 5. Why nothing ships

- No global small-tree multiplier improves held-out BA and TPH together; they trade.
- `HTGMULT` for CW is neutral for BA/TPH, so it cannot satisfy the BA-and-TPH gate even though it
  would correct the known ~4% CW donor bias.
- The only cell-level win is 5 held-out intervals.

The donor cells stay. The data needed to do better: CWH small-tree **diameter** remeasurement
pairs with measured crown ratio and the engine's own CCF, or a small-tree height form that fits
the tall end without the quadratic taper (the W11/W18 limitation).

## 6. Decision for the user

A CW `HTGMULT` around 1.04 would correct a known donor bias and improve the height cell while
leaving BA/TPH essentially unchanged. The current shipping rule requires BA and TPH to improve,
so it cannot ship as written. If height-only corrections should be allowed when BA and TPH are
neutral, that is a rule change, not a calibration result.

## Reproduce

- `~/workspace/bwbs-work/probe_cwh_small/` (multiplier screen, 2,277 rows).
- `~/workspace/bwbs-work/probe_cwh_regd_full/` (full-fold REGDMULT, 1,592 rows).
- `~/workspace/bwbs-work/probe_cwh_combo/` (REGDMULT × BAIMULT, 1,449 rows).
- Shipped fold reproduced: test +0.158 / 4.000, TPH +199.8 / 273.0; train −0.108 / 5.030.
