# W15: MS on the V3 path

Status: **built and calibrated on the MS fold.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w15-ms-v3.patch.gz`, applied after `w14-pp-site-series.patch.gz`.
Bundles: none. MS has no calibration bundle.

## 1. Why

MS was the largest zone left on the V2 path (1,037 intervals, 307 sites). Measured on the fold, V2
MS scored **−9.01 m²/ha** BA bias (MAE 9.32, TPH −389) — worse than any V3 zone. It was left out of
W5–W9 and the support matrix wrongly described it as "V3 via defaults"; the zone-path registry added
in 0.30.0 made that visible.

## 2. What changed

Five coordinated edits, the same set W5–W9 used, all in `canada/bc`:

- **`becset.f`**: `MS` joins the `LV2ATV` list.
- **`regent.f`**: `MS` joins the five small-tree/height zone lists, and `MS/all` joins the pooled
  `ST_COEF` row.
- **`dgf.f`**: seven `ZNKONST` rows (48–54) for AT, BL, FD, LW, PL, PY, and SE, plus `MS/all` on the
  zonal site-series row; `P_ZN` 47 → 54. The rows are appended, so nothing renumbers.
- **`htgf.f`**: five `LTHG` blocks (64–68) for BL, FD, LW, PL, and SE; `P_MD` 63 → 68. Appended.
- **`morts.f`**: `MS/all` on the hardwood row; conifers keep the tabular mortality the species
  classes already select.

Species with fewer than 300 (DG) or 400 (height) pairs keep the donor: CW, EP, AC, and the minor
codes.

## 3. Fits

Large-tree diameter growth, live pairs 10.16–80 cm, log DG on a quadratic in DBH with BAL:

| Species | n | r² | Observed | Fitted |
| --- | ---: | ---: | ---: | ---: |
| PL | 18,262 | 0.228 | 0.142 | 0.124 |
| SE (SW) | 4,539 | 0.191 | 0.183 | 0.152 |
| FD | 4,043 | 0.157 | 0.299 | 0.264 |
| BL | 3,249 | 0.227 | 0.190 | 0.161 |
| LW | 2,758 | 0.331 | 0.138 | 0.122 |
| PY | 426 | 0.127 | 0.148 | 0.128 |
| AT | 391 | 0.130 | 0.186 | 0.158 |

Height growth, dominant and codominant pairs, ten-year increments:

| Species | n | r² | Observed | Fitted |
| --- | ---: | ---: | ---: | ---: |
| PL | 21,281 | 0.489 | 0.907 | 0.858 |
| SE | 3,299 | 0.519 | 1.436 | 1.384 |
| FD | 3,278 | 0.454 | 2.080 | 2.071 |
| LW | 2,683 | 0.355 | 1.339 | 1.315 |
| BL | 1,782 | 0.404 | 1.708 | 1.666 |

## 4. Evidence
> **In-sample.** The table below uses the intervals the rows were fitted from. The
> held-out check (`heldout-ms-essf-pp.md`) splits 20% of the sites and reproduces the
> direction and most of the size; quote that note for the defensible number.


MS fold, 134 intervals, one cycle each, no bundle:

| Build | Path | BA bias (m²/ha) | MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.30.0 | V2 | −9.01 | 9.32 | −389 | 739 |
| **W15** | **V3** | **−2.81** | **5.62** | **−178** | **682** |

A candidate sweep on the same fold: `BAIMULT 2` gives −2.48/5.48 and `BAIMULT 4` gives −1.82/5.30.
No bundle was written: there is no held-out split for MS yet, and a stand multiplier is not the tool
to reach for without one. The sweep is recorded here for the next pass.

## 5. Tier and claim

MS is **C**: V3 structure, fitted rows for the seven (DG) and five (height) species with the pairs,
tabular mortality, and one fold. It is not validated: no held-out split, no bundle, the minor species
keep their donors, and the −2.8 m²/ha bias is open.

## 6. Build

Apply after W14. The patch is verified against the full W2–W14 chain from the pinned tree.
