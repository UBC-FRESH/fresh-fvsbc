# W16: ESSF on the V3 path

Status: **built and calibrated on the ESSF fold.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w16-essf-v3.patch.gz`, applied after `w15-ms-v3.patch.gz`.
Bundles: none.

## 1. Why

ESSF was the largest zone left on V2 after W15 (620 intervals, 278 sites). On the fold, V2 ESSF
scored **−7.86 m²/ha** BA bias (MAE 8.78, TPH −242).

It also carried the `MSdk/01` substitution: every ESSF site series outside the mapped handful was
rewritten before the model ran. On V3 the run returns before that table, so the substitution
disappears with the wiring.

## 2. What changed

The same five-file package as W15, anchored on the W15 state:

- **`becset.f`**: `ESSF` joins the `LV2ATV` list.
- **`regent.f`**: `ESSF` joins the five small-tree/height zone lists; `ESSF/all` on the pooled
  `ST_COEF` row.
- **`dgf.f`**: five `ZNKONST` rows (55–59) for BL, FD, HW, PL, and SE; `ESSF/all` on the zonal
  site-series row; `P_ZN` 54 → 59.
- **`htgf.f`**: three `LTHG` blocks (69–71) for BL, PL, and SE; `P_MD` 68 → 71.
- **`morts.f`**: `ESSF/all` on the hardwood row; conifers keep the tabular mortality.

Rows are appended, so nothing renumbers. CW, LW, AT, PA, and PW keep their donors.

## 3. Fits

Diameter growth, live pairs 10.16–80 cm:

| Species | n | r² | Observed | Fitted |
| --- | ---: | ---: | ---: | ---: |
| BL | 7,369 | 0.072 | 0.235 | 0.197 |
| SE | 3,049 | 0.085 | 0.267 | 0.217 |
| PL | 1,139 | 0.059 | 0.135 | 0.109 |
| FD | 357 | 0.344 | 0.261 | 0.228 |
| HW | 323 | 0.552 | 0.205 | 0.189 |

Height growth, dominant and codominant pairs, ten-year increments:

| Species | n | r² | Observed | Fitted |
| --- | ---: | ---: | ---: | ---: |
| BL | 8,457 | 0.506 | 1.592 | 1.578 |
| SE | 4,386 | 0.544 | 1.692 | 1.626 |
| PL | 2,330 | 0.360 | 0.901 | 0.863 |

PL's free height fit landed on its bounds with a power term that predicted 7.5 m per decade for a
2 m tree, so that species uses a **scale-only** fit: the donor shape with a fitted level. The
recorded coefficients are the donor's `DG/DG2/DBH1/DBH2/HT2` with `CNSI = 0.30548`.

## 4. Evidence
> **In-sample.** The table below uses the intervals the rows were fitted from. The
> held-out check (`heldout-ms-essf-pp.md`) splits 20% of the sites and reproduces the
> direction and most of the size; quote that note for the defensible number.


ESSF fold, 302 intervals, one cycle each, no bundle:

| Build | Path | BA bias (m²/ha) | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.31.0 | V2 | −7.86 | 8.78 | −242 | 540 |
| **W16** | **V3** | **−1.91** | **6.20** | **−151** | **550** |

BA bias and MAE improve by 5.9 and 2.6 m²/ha; the TPH MAE is flat. No bundle: the fold has no
held-out split and the residual is small enough that a multiplier would be fitting noise.

The substitution is gone for ESSF: `ESSFdk2`, `ESSFmv1`, and `ESSFwc4` all run with
`bec_substitution = None`.

## 5. Tier and claim

ESSF is **C**: V3 structure, fitted rows for five species with their pairs, tabular mortality, and one
fold. It is not validated: no held-out split, no bundle, the minor species keep donors, and the
−1.9 m²/ha bias is open.

## 6. Build

Apply after W15. Verified against the full W2–W15 chain from the pinned tree.
