# W8: CWH on the V3 path

Status: **built and calibrated on a BEC-stratified CWH fold.** Unsigned pilot, tier C.
Supersedes the CWH V2 bundle (`cwh-v2-bundle.json`).

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w8-cwh-v3.patch.gz`, applied after `w7-sbps-large-tree.patch.gz`.
Bundle: `cwh-v3-bundle.json` (`BAIMULT 8`).

## 1. Why

CWH had no V3 entries in any of the five tables. The V2 bundle (`BAIMULT 10`) brought the fold from
-11.81 to -0.57, but it was a stand-level correction on the legacy path: the species donor layer
(SS->SE, BA->BG, DR->AT, YC->CW, MB->AC) and the V2 growth model were doing the work, not a CWH
calibration. W8 moves CWH onto V3:

- `becset.f`: CWH joins the V3 condition.
- `regent.f`: CWH joins the five small-tree CCF/height branches and the generic pooled `ST_COEF`
  entry (all species). This is a **donor** small-tree model, not a CWH fit.
- `dgf.f`: ten fitted CWH `ZNKONST` rows for HW, FD/OC, CW, SE, BG, AT, AC, PL, EP, PW, plus
  `CWH/all` in the site-series (`SSKONST`) row with `CON=0`.
- `htgf.f`: `CWH/all` on every `LTHG` block that carries `ICH/all`. This is a **donor** height model.
- `morts.f`: `CWH/all` on the hardwood `LMRT(1)` row; conifers use the ICH tabular mortality that
  `BECCLS` already selects for a non-ICH/IDF zone.

## 2. Large-tree fit

Fitted from the calibration tree-survival table, annual DG, DBH >= 10.16 cm:

| Species | n | r2 | Observed DG | Fitted |
| --- | ---: | ---: | ---: | ---: |
| HW | 137,517 | 0.284 | 0.256 | 0.212 |
| FD | 66,209 | 0.271 | 0.292 | 0.240 |
| CW | 23,677 | 0.275 | 0.261 | 0.206 |
| SE (SS/SW/SX) | 17,864 | 0.234 | 0.396 | 0.315 |
| BG (BA) | 10,430 | 0.345 | 0.351 | 0.301 |
| AT (DR) | 8,199 | 0.390 | 0.332 | 0.237 |
| AC (MB) | 1,062 | 0.575 | 0.461 | 0.380 |
| PL | 1,450 | 0.105 | 0.139 | 0.115 |
| EP | 525 | 0.265 | 0.178 | 0.140 |
| PW | 305 | 0.201 | 0.336 | 0.279 |

## 3. Evidence

BEC-stratified CWH fold: 49 held-out, 56 train intervals.

| Build | Candidate | Test BA bias | Test MAE | Train BA bias | Train MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| V2 | base | -11.81 | 11.81 | -13.75 | 14.36 |
| V2 | `BAIMULT 10` | -0.57 | 4.12 | -0.74 | 5.19 |
| V3 | base | -3.79 | 5.34 | -4.08 | 6.60 |
| V3 | `BAIMULT 6` | -0.77 | 3.62 | -0.81 | 5.16 |
| **V3** | **`BAIMULT 8`** | **+0.31** | **3.37** | **+0.39** | **5.15** |
| V3 | `BAIMULT 10` | +1.37 | 3.45 | +1.46 | 5.18 |

The V3 base already beats the V2 base by 8 m2/ha; `BAIMULT 8` is the bundle. The largest predicted BA
in the battery is 187 against an observed maximum of 191; no overflow.

## 4. Claim boundary

CWH is **C**: fitted large-tree DG, but the small-tree growth, large-tree height, and part of the
mortality are still donors. Fitting those three from the CWH pairs is the next refinement. The
bundle is `cwh-v3-bundle.json`.

## 5. Build

Apply after W7; the wheel recipe does this. The patch is verified with `patch -p1 --dry-run` against
the W7 tree.
