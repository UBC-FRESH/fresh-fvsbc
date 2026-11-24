# W6: SBS and SBPS large-tree diameter growth on V3

Status: **built; SBS validated on a BEC-stratified fold; SBPS fold pending.** Unsigned pilot.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w6-sbs-sbps-large-tree.patch.gz`, applied after `w5-bwbs-v3.patch.gz`.

## 1. Defect

`canada/bc/dgf.f` needs two matches before it computes large-tree diameter growth: a zone entry
in `ZNKONST` and a site-series entry in `SSKONST`. `SSKONST` held only ICH and IDF site series, so
SBS and SBPS matched a zone and then failed the site-series test. The fall-through sets the
coefficients to their zero initial state, and large-tree DG is then zero. The stand's basal area can
still rise through small-tree growth, which is why the defect hid inside a plausible summary.

W5 fixed this for BWBS by adding a BWBS zonal `SSKONST` entry. W6 adds `SBS/all` and `SBPS/all` to the
same entry. It is a one-hunk patch.

## 2. Evidence

The SBS fold is BEC-stratified: every SBS site group has held-out members, 38 held-out intervals in
the `per-bec 10` sample. `BAIMULT 1` unless the bundle says otherwise.

| Build | Mortality | Held-out BA bias | BA MAE | Train BA bias |
| --- | --- | ---: | ---: | ---: |
| pre-W6 | `MORTMULT 1` | +1.79 | 6.78 | -0.25 |
| W6 | `MORTMULT 1` | +3.02 | 7.09 | +2.83 |
| W6 | D7 SBS bundle (`MORTMULT 2`, FD/PL/SE/HW) | **-2.66** | **6.29** | -1.30 |

W6 makes large trees grow, which is the correct structure for tree-level output. It also adds basal
area, so the existing SBS pilot bundle (higher mortality) is what brings the stand back inside the
gate. The W6 + D7 combination has the best MAE of the three. Do not run W6 with `MORTMULT 1` and call
SBS calibrated.

SBPS uses the same `SSKONST` row. Its fold has not been rerun; treat SBPS as **C** until it is.

## 3. Tier

SBS and SBPS are **C (provisional)**: structurally correct, stand-level evidence on a BEC-stratified
fold for SBS, no signed review, SBPS pending. That is the tier `fresh_fvsbc.support` returns.

## 4. Build

Apply after `w5-bwbs-v3.patch.gz`; the wheel recipe does this. The patch is verified with
`patch -p1 --dry-run` against the W5 tree.
