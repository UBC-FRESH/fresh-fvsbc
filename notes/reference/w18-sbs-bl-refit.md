# W18: the SBS BL large-tree growth row, refit

Status: **shipped in 0.41.1 on engine 0.4.11.** Tier stays C.
Supersedes the `BAIMULT 0.5` for BL that shipped in 0.40.0.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w18-sbs-bl-dg.patch.gz`, applied after `w17-pp-v3.patch.gz`.
Bundle: `sbs-v3` keeps only `MORTMULT 2` for FD/PL/SE/HW.

> **0.41.0 / engine 0.4.10 are superseded.** The first cut of this row was parameterised
> on annual growth while the engine applies a **10-year** increment, so it grew SBS BL about
> ten times too slowly. 0.41.1 / engine 0.4.11 carry the fit described here.

## 1. Why

The SBSmc2 high-BA cell over-grew (+13.1 m²/ha, −1,067 TPH). 0.40.0 wrapped it in
`BAIMULT 0.5` for BL, which worked but masked the row. The row is `ZNKONST(31)`, and its
legacy coefficients carried a `3.1925 * crown` term. On the cell, crown ratio runs at 0.45,
so that term adds **1.44 to ln(growth)** — a factor of 4.2. That is the over-growth.

## 2. The units

`GRADD` scales diameter growth to the cycle with `FINT/YR`, where `YR = 10`. The row
therefore predicts a **10-year** increment, in cm. The calibration pairs are annual, so the
fit response is `10 * growth_cm`. For V3 the engine passes `D` in cm and `BAL` in m²/ha,
and it multiplies the CCF coefficient by `RELDEN * 0.01` (effectively inert), so the fit
uses the terms the engine actually applies.

Observed 10-year growth for SBS BL: **2.14** (10–20 cm), **2.77** (20–30), **2.74** (30–80).

## 3. The fit

11,005 SBS BL live pairs, DBH 10.16–80 cm, 10–20 cm weighted three times:

```
ln(10*DG) = CON + LD*D + DSQ*D^2 + BAL*BAL + DBAL1*BAL/D + DBAL2*BAL/log(D+1)
```

| Coefficient | Legacy row | Refit |
| --- | ---: | ---: |
| constant | 0.0 | 0.378733 |
| ccf | −0.0152 | 0.0 (inert in V3) |
| diam | 0.0737 | 0.053222 |
| diam² | −0.00182 | −0.000853 |
| bal/dbh | 0.0 | −1.030391 |
| bal/log(dbh+1) | 0.0 | 0.427045 |
| crown | 3.1925 | 0.0 (pairs carry no crown ratio) |
| bal | 0.0 | −0.109179 |

The constant includes a **smearing correction** of ×1.2176 (`mean(exp(residual))`) so the
log fit matches the arithmetic mean; without it small trees are under-predicted.

| DBH class | Pairs | Observed 10-yr | Refit |
| --- | ---: | ---: | ---: |
| 10.16–20 | 7,537 | 2.136 | 2.102 |
| 20–30 | 2,442 | 2.766 | 2.854 |
| 30–80 | 1,026 | 2.742 | 2.961 |

## 4. Evidence

SBS fold, recruitment, five-year cycles. The shipped column is 0.40.0 (legacy row plus the
`BAIMULT 0.5` crutch); the right column is W18 with no BL multiplier.

| Measure | Shipped 0.40 | **W18 refit** |
| --- | ---: | ---: |
| Test BA bias / MAE | −0.74 / 6.00 | −0.92 / 6.09 |
| Test TPH bias / MAE | −37.7 / 686.7 | **−22.0 / 658.9** |
| Train BA bias / MAE | −1.09 / 5.83 | **−1.68 / 5.22** |
| Train TPH bias / MAE | −98.7 / 435.5 | **−62.2 / 398.3** |
| **SBSmc2 cell BA** | +9.2 | **+2.8** |
| **SBSmc2 cell TPH** | −635 | **−200** |

Test BA MAE is 0.09 m²/ha above the crutch build, which was itself selected on this fold.
Against the same row with **no** crutch (the honest row-level baseline) the refit improves
both: BA MAE 6.38 → 6.09 (paired difference −0.29, 95% CI −1.01 to +0.16) and TPH MAE
699.6 → 658.9 (−40.6, CI −103.6 to 0.0). Train improves on every measure, and the cell
improves by 6.4 m²/ha and 435 stems.

## 5. The crutch is gone

With the refit, `BAIMULT 0.5` for BL moves the cell +2.8 → +1.5 and test BA MAE 6.09 → 6.07,
at a TPH cost (658.9 → 660.5) and a train cost. It is removed: `sbs-v3` carries `MORTMULT 2`
for FD/PL/SE/HW and relies on W18 for BL.

## 6. The dense stand

`4004950`-style dense BL at 79 TPH and QMD 15.5 cm: measured growth is about 0.21 cm/yr.
The legacy row grew it at **0.50**; W18 grows it at **0.28**, with the remaining excess from
the stand's 45% crown ratio, which the row no longer reads.

## 7. What remains

The row has no crown term because the calibration pairs carry only `CR_CL` (a class, not a
percentage). Mapping those classes to midpoints and refitting would let the row respond to
crown ratio again, and is the next improvement. The BAL terms are stand-level and were
fitted across all SBS subzones.
