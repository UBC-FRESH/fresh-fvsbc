# W7: SBPS large-tree diameter growth on V3

Status: **built and calibrated on a BEC-stratified SBPS fold.** Unsigned pilot.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w7-sbps-large-tree.patch.gz`, applied after `w6-sbs-large-tree.patch.gz`.
Bundle: `sbps-v3-bundle.json` (`MORTMULT 2`).

## 1. Defect

SBPS had no large-tree diameter growth on V3: `SSKONST` held only ICH/IDF site series. W6 tried to
add `SBPS/all` with a zero intercept and overflowed (BA 53,188). The reason is visible in the old
`ZNKONST` SBPS entries: they are unfinished. The PL `SBPSdc` row carries a constant of -4.17 and a
diam coefficient of 2.44 with no site-series intercept, so `exp(CON + 2.44*D + ...)` is enormous at
any plausible D. A donor row cannot fix an unfinished coefficient set.

## 2. Fit

Fitted from 24,360 SBPS large-tree PSP pairs (DBH >= 10.16 cm, 2-20 year intervals), log-linear in
the DGF forms with BAL = larger-tree basal area:

| Species | n | Form | Mean observed DG | Mean fitted |
| --- | ---: | --- | ---: | ---: |
| PL | 23,042 | default | 0.120 | 0.097 |
| SE (from SW) | 560 | default | 0.234 | 0.201 |
| AT | 419 | aspen | 0.124 | 0.103 |
| FD | 133 | default | 0.276 | 0.245 |

BL (n=1), EP (n=4) and SB (not in the variant) are too thin to fit; they keep the pre-W7 path and
their SBPS large-tree DG stays zero. The fitted intercept is carried by the new `ZNKONST` rows; the
`SSKONST` row is `CON=0` and now includes `SBPS/all`.

W7 adds four new `ZNKONST` rows (PL, FD/OC, SE, AT/AC) before the old SBS/ SBPS donor block and
removes the SBPS tokens from the old rows, so the first-match search reaches the fitted rows for an
SBPS label and leaves the SBS rows untouched.

## 3. Evidence

BEC-stratified SBPS fold: 6 held-out, 21 train intervals.

| Candidate | Fold | BA bias | BA MAE |
| --- | --- | ---: | ---: |
| pre-W7, `MORTMULT 1` | test | +17.34 | 17.34 |
| W7, `MORTMULT 1` | test | +14.51 | 14.51 |
| W7, `MORTMULT 2` | test | **+2.01** | **2.47** |
| W7, `MORTMULT 2` | train | -2.12 | 7.51 |

The largest predicted BA in the W7 battery is 50 m2/ha against an observed maximum of 41; the W6
overflow is gone. The train side still has interval-level outliers (up to +122% on one interval), so
this is a first calibration, not a certificate.

## 4. Tier

SBPS is **C (provisional)**: fitted large-tree growth, stand-level evidence, unsigned. BL/EP/OH have
no SBPS large-tree row yet. The bundle is `sbps-v3-bundle.json`.

## 5. Build

Apply after W6; the wheel recipe does this. The patch is verified with `patch -p1 --dry-run` against
the W6 tree.
