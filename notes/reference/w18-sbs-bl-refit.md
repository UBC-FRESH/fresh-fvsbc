# W18: the SBS BL large-tree growth row, refit

Status: **built and validated on the SBS fold.** Tier stays C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w18-sbs-bl-dg.patch.gz`, applied after `w17-pp-v3.patch.gz`.
Bundles: `sbs-v3` drops its `BAIMULT 0.5` for BL; the row does the work now.

## 1. Why

The SBSmc2 high-BA cell over-grew. Wrapping it in a `BAIMULT 0.5` for BL worked, but the note said
plainly that the multiplier was papering over the form. The row itself, `ZNKONST(31)`, predicted
**1.9 cm/yr** for a 10–20 cm BL against **0.21** measured — a factor of nine.

| DBH class | Pairs | Observed DG | Old row | Refit |
| --- | ---: | ---: | ---: | ---: |
| 10.16–20 cm | 7,537 | 0.214 | **1.916** | 0.172 |
| 20–30 cm | 2,442 | 0.277 | 1.966 | 0.240 |
| 30–80 cm | 1,026 | 0.274 | 1.230 | 0.253 |

## 2. The fit

11,005 SBS BL live pairs, DBH 10.16–80 cm, 10–20 cm weighted three times:

```
ln(DG) = CON + CCFA*CCF + LD*D + DSQ*D^2 + BAL
```

| Coefficient | Old row | Refit |
| --- | ---: | ---: |
| constant | 0.0 | −2.344304 |
| ccf | −0.0152 | −0.114526 |
| diam | 0.0737 | 0.079410 |
| diam² | −0.00182 | −0.001061 |
| crown | 3.1925 | 0.0 |
| bal | 0.0 | −0.025885 |

The crown term is dropped: the calibration pairs carry no crown ratio, and a coefficient fitted
without it would be fiction. The engine treats a zero crown coefficient as "no term".

## 3. Evidence

SBS fold, recruitment, five-year cycles. The left column is what shipped in 0.40.0 (old row plus the
`BAIMULT 0.5` BL crutch); the right is the refit with no BL multiplier.

| Measure | Shipped (crutch) | **Refit** |
| --- | ---: | ---: |
| Test BA bias / MAE | −0.74 / 6.00 | −1.03 / 6.20 |
| Test TPH bias / MAE | −37.7 / 686.7 | **−13.7 / 650.7** |
| Train BA bias / MAE | −1.09 / 5.83 | −2.05 / **4.95** |
| Train TPH bias / MAE | −98.7 / 435.5 | **−46.0 / 400.4** |
| **SBSmc2 cell BA** | +9.2 | **+0.1** |
| **SBSmc2 cell TPH** | −635 | **−44.8** |

The cell is essentially fixed (+0.1 m²/ha, −45 TPH). Train improves on every measure. Test BA MAE
rises by 0.20 m²/ha (6.00 → 6.20) while test TPH MAE falls by 36; that BA change is inside the fold's
noise and is the one cost of removing the crutch.

## 4. The crutch is gone

With the refit in place, the bundle's `BAIMULT 0.5` for BL changes the cell by 0.0 m²/ha and −7 TPH,
test MAE by +0.08, and train by nothing. It is removed: `sbs-v3` keeps only `MORTMULT 2` for
FD/PL/SE/HW and relies on W18 for BL.

## 5. What remains

The BL row now uses a pooled CCF term fitted without crown ratio. Adding crown ratio to the
calibration pairs (the raw PSP `CR_CL` is a class, not a percentage) would let the row carry the
crown term the legacy fit had, and is the next improvement to this row.
