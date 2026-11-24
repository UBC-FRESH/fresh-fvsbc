# CWH and MH: V2 stand-level calibrations while V3 is built

Status: **CWH and MH calibrated on the legacy V2 path; V3 migration pending.** Unsigned pilots, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Bundles: `cwh-v2-bundle.json`, `mh-v2-bundle.json` (both `BAIMULT 10`).

## 1. Why this is a V2 calibration

CWH and MH have no V3 growth or mortality tables. The earlier source audit is explicit: no CWH
growth, mortality, crown, bark, volume, or regeneration tables, and six species absent from the
15-code grammar; MH lacks mountain-hemlock, amabilis-fir, and yellow-cedar tables. A V3 donor row is
not safe by construction — SBPS showed that a zero site-series intercept can overflow a coefficient
set (`SBPS/all`, `CON=0` → BA 53,188).

So both zones are calibrated where they already run: the legacy V2 path, with the `BAIMULT` lever the
D-series bundles use. This is a stand-level correction, not a V3 parameter set.

## 2. CWH

BEC-stratified CWH fold: 49 held-out, 56 train intervals, `per-bec 5`.

| Candidate | Test BA bias | Test MAE | Train BA bias | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| base | -11.81 | 11.81 | -13.75 | 14.36 |
| `BAIMULT 4` | -8.86 | 9.32 | -10.36 | 11.08 |
| `BAIMULT 8` | -2.35 | 4.63 | -3.11 | 5.87 |
| **`BAIMULT 10`** | **-0.57** | **4.12** | **-0.74** | **5.19** |
| `BAIMULT 12` | +1.08 | 4.41 | +1.28 | 5.44 |

The optimum is 10-11, inside the bundle's `0.25-15` bounds. `MORTMULT 0.5` trades a little BA for TPH
(`BAIMULT 8, MORTMULT 0.5`: BA +0.80/+0.92, TPH +37/-118) but does not improve the BA MAE; the bundle
keeps `MORTMULT 1`.

## 3. MH

MH fold: only 3 held-out and 15 train intervals across `MHmm1`, `MHmm2`, `MHwh1`.

| Candidate | Test BA bias | Test MAE | Train BA bias | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| base | -11.19 | 11.19 | -11.99 | 12.29 |
| `BAIMULT 8` | -3.53 | 3.53 | -1.19 | 3.74 |
| **`BAIMULT 10`** | **-0.53** | **1.06** | **+0.67** | **3.55** |
| `BAIMULT 12` | +1.14 | 1.14 | +2.34 | 3.82 |

The response is the same shape as CWH, but the held-out fold is three intervals: treat it as
suggestive, not a validation.

## 4. CDF and CMA

- **CDF** does not respond enough to the lever: base test -28.44, `BAIMULT 8` -22.50, `BAIMULT 10`
  -20.30, `BAIMULT 12` -18.77. The fold is also lopsided (15 test intervals from one site, 5 train),
  so a multiplier is not identified. CDF stays **D** until a V3 fit.
- **CMA** has 6 intervals on 2 sites. It cannot support a site-grouped fold and stays **D**.

## 5. Tier

- CWH **C**: solid stand-level evidence on a 49/56 fold.
- MH **C**: the same lever, but a 3-interval held-out fold.
- CDF, CMA **D**: no identified calibration.

The V3 migration for CWH and MH — entries in `regent.f`, `dgf.f`, `htgf.f`, and `morts.f`, fitted from
the 7,124 CWH and 31 MH intervals — is the next task for both.
