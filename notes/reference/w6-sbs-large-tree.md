# W6: SBS large-tree diameter growth on V3

Status: **built; SBS validated on a BEC-stratified fold; SBPS deliberately excluded.** Unsigned pilot.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w6-sbs-large-tree.patch.gz`, applied after `w5-bwbs-v3.patch.gz`.

## 1. Defect

`canada/bc/dgf.f` needs two matches before it computes large-tree diameter growth: a zone entry in
`ZNKONST` and a site-series entry in `SSKONST`. `SSKONST` held only ICH and IDF site series, so SBS
matched a zone and then failed the site-series test. The coefficients then stayed at their zero
initial state and large-tree DG was zero. Basal area could still rise through small-tree growth,
which is why the summary looked plausible.

W5 fixed this for BWBS with a zonal `SSKONST` entry. W6 adds `SBS/all` to the same entry.

## 2. SBS evidence

The SBS fold is BEC-stratified: 38 held-out intervals drawn from every SBS BEC.

| Build | Mortality | Held-out BA bias | BA MAE | Train BA bias |
| --- | --- | ---: | ---: | ---: |
| pre-W6 | `MORTMULT 1` | +1.79 | 6.78 | -0.25 |
| W6 | `MORTMULT 1` | +3.02 | 7.09 | +2.83 |
| W6 | D7 SBS bundle (`MORTMULT 2`, FD/PL/SE/HW) | **-2.66** | **6.29** | -1.30 |

W6 makes large trees grow, which is the correct structure for tree-level output, and adds basal area.
The existing D7 SBS pilot bundle is what brings the stand back inside the gate; the W6 + D7
combination has the best MAE of the three. Do not run W6 with `MORTMULT 1` and call SBS calibrated.

## 3. Why SBPS is not in this patch

The same `SSKONST` row would apply `CON=0` to SBPS. That is not a valid intercept for the SBPS
`ZNKONST` coefficients:

| SBPS build | Held-out BA bias | Held-out MAE |
| --- | ---: | ---: |
| pre-W6 | +17.34 | 17.34 |
| W6 with `SBPS/all`, `CON=0` | **53,188** | 53,195 |

The second row is an overflow, not a calibration. SBPS therefore keeps the pre-W6 path: large-tree DG
stays zero, and its known BA overprediction is a Phase 1 fit, not something a donor row solves. Do
not add `SBPS/all` to this entry until an SBPS site-series intercept is fitted.

## 4. Tier

SBS is **C (provisional)**: structurally correct, stand-level evidence on a BEC-stratified fold, no
signed review. SBPS is **C** with a known large-tree defect and a BA overprediction. That is what
`fresh_fvsbc.support` returns.

## 5. Build

Apply after `w5-bwbs-v3.patch.gz`; the wheel recipe does this. The patch is verified with
`patch -p1 --dry-run` against the W5 tree.
