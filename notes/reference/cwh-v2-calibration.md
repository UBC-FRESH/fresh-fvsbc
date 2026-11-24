# CWH: a V2 stand-level calibration while V3 is built

Status: **calibrated on the legacy V2 path; V3 migration pending.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Bundle: `cwh-v2-bundle.json` (`BAIMULT 10`).

## 1. Why this is a V2 bundle

CWH has no V3 growth or mortality tables. The earlier source audit is explicit: no CWH growth,
mortality, crown, bark, volume, or regeneration tables, and six species absent from the 15-code
grammar. A V3 donor row is not safe by construction — SBPS showed that a zero site-series intercept
can overflow a coefficient set. So CWH is calibrated where it already runs: the legacy V2 path, with
the `BAIMULT` lever the D-series bundles use.

## 2. Baseline and grid

BEC-stratified CWH fold: 49 held-out, 56 train intervals, `per-bec 5`.

| Candidate | Test BA bias | Test MAE | Train BA bias | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| base | -11.81 | 11.81 | -13.75 | 14.36 |
| `BAIMULT 4` | -8.86 | 9.32 | -10.36 | 11.08 |
| `BAIMULT 8` | -2.35 | 4.63 | -3.11 | 5.87 |
| **`BAIMULT 10`** | **-0.57** | **4.12** | **-0.74** | **5.19** |
| `BAIMULT 12` | +1.08 | 4.41 | +1.28 | 5.44 |

The optimum is around 10-11, inside the bundle's `0.25-15` bounds rather than at a bound.
`MORTMULT 0.5` trades a little BA for TPH (`BAIMULT 8, MORTMULT 0.5`: BA +0.80/+0.92, TPH +37/-118)
but does not improve the BA MAE; the bundle keeps `MORTMULT 1`.

## 3. Claim boundary

This is a **stand-level** correction on the legacy path, not a V3 parameter set, and not a
certificate. It brings CWH from a systematic -13 m2/ha to within the gate. The V3 migration — CWH
entries in `regent.f`, `dgf.f`, `htgf.f`, and `morts.f`, fitted from the 7,124 CWH intervals — is the
next CWH task.

## 4. The other three zones

- **CDF**: 94 intervals, 21 sites. Enough for a fold; not yet run.
- **MH**: 31 intervals, 12 sites. Enough for a small fold; not yet run.
- **CMA**: 6 intervals, 2 sites. Too thin for a site-grouped fold; stays unsupported until there is
  external evidence.

CDF and MH can use the same V2 lever if their folds respond; CMA cannot be validated here.
