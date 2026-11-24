# W9: MH and CDF on the V3 path

Status: **built and calibrated on site-grouped folds.** Unsigned pilots, tier C.
Supersedes the MH and CDF V2 bundles.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w9-mh-cdf-v3.patch.gz`, applied after `w8-cwh-v3.patch.gz`.
Bundles: `mh-v3-bundle.json`, `cdf-v3-bundle.json` (both `BAIMULT 8`).

## 1. Why

MH and CDF had no V3 entries. Their V2 bundles (`BAIMULT 10`) were stand-level corrections on the
legacy path, not zone calibrations. W9 puts both on V3 by reusing the fitted coastal (CWH)
large-tree rows as donors and the CWH donor wiring for the other four tables:

- `becset.f`: MH and CDF join the V3 condition.
- `regent.f`: MH and CDF join the five small-tree CCF/height branches and the generic pooled
  `ST_COEF` entry.
- `dgf.f`: `MH/all` and `CDF/all` on the ten fitted CWH `ZNKONST` rows and on the site-series row.
- `htgf.f`: `MH/all` and `CDF/all` on every `LTHG` block that carries `CWH/all`.
- `morts.f`: `MH/all` and `CDF/all` on the hardwood `LMRT(1)` row; conifers use the ICH tabular
  mortality.

This is a donor calibration: the large-tree DG coefficients come from CWH, not from an MH or CDF fit.
The folds below are the evidence that the donor is usable at stand level.

## 2. MH

MH fold: 3 held-out / 15 train intervals across `MHmm1`, `MHmm2`, `MHwh1`.

| Build | Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| V2 | `BAIMULT 10` | -0.53 | 1.06 | +0.67 | 3.55 |
| V3 | base | -3.66 | 5.89 | -3.66 | 5.89 |
| V3 | `BAIMULT 4` | +1.81 | 1.81 | -1.86 | 4.75 |
| **V3** | **`BAIMULT 8`** | **+2.47** | **2.47** | **+0.21** | **3.46** |
| V3 | `BAIMULT 10` | +3.14 | 3.14 | +1.14 | 3.53 |

The held-out fold is three intervals. Treat MH as suggestive, not validated.

## 3. CDF

CDF fold: one interval per site, 6 held-out / 13 train.

| Build | Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| V2 | `BAIMULT 10` | -0.72 | 6.58 | -0.65 | 5.03 |
| V3 | base | — | — | -3.96 | 4.10 |
| V3 | `BAIMULT 4` | -3.39 | 3.60 | -2.50 | 3.10 |
| **V3** | **`BAIMULT 8`** | **-2.05** | **2.94** | **-0.42** | **2.01** |
| V3 | `BAIMULT 10` | -1.22 | 3.07 | +0.58 | 2.23 |

CDF's V3 MAE is roughly half the V2 bundle's, with the same bias gate.

## 4. Tier and claim

MH and CDF are **C**: V3 structure, donor large-tree coefficients, stand-level evidence, unsigned.
The V3 bundles supersede the V2 ones. CMA remains **D**: 6 intervals on 2 sites cannot support a
site-grouped calibration.

## 5. Build

Apply after W8; the wheel recipe does this. The patch is verified with `patch -p1 --dry-run` against
the W8 tree.
