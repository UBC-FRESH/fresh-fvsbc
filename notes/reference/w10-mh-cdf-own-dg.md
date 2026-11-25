# W10: MH and CDF large-tree rows fitted from their own pairs

Status: **built and calibrated on the same site folds W9 used.** Unsigned pilots, tier C.
Supersedes the W9 donor wiring for the four species with enough pairs.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w10-mh-cdf-own-dg.patch.gz`, applied after `w9-mh-cdf-v3.patch.gz`.
Bundles: `mh-v3-bundle.json`, `cdf-v3-bundle.json` (both still `BAIMULT 8`).

## 1. Why

W9 put MH and CDF on V3 by copying the fitted coastal (CWH) large-tree rows onto `MH/all` and
`CDF/all`. That is a donor, and the donor is visibly wrong where the zones differ:

| Zone | Species | n | Observed DG (cm/yr) | CWH donor prediction | Own fit |
| --- | --- | ---: | ---: | ---: | ---: |
| MH | HW (mountain hemlock) | 536 | 0.133 | 0.212 | 0.118 |
| MH | BG (amabilis fir) | 358 | 0.221 | 0.301 | 0.201 |
| CDF | FD (Douglas-fir) | 3,642 | 0.352 | 0.240 | 0.299 |
| CDF | AT (red alder) | 593 | 0.176 | 0.237 | 0.155 |

Mountain hemlock grows about 40% slower than the coastal hemlock donor predicts, and coastal
Douglas-fir about 45% faster than the coastal-row donor. W10 fits those four rows from the MH and
CDF pairs themselves.

## 2. What changed

`dgf.f` only. Four `ZNKONST` rows are inserted **ahead** of the CWH donor rows, so the search finds
them first:

| Row | Zone | Species | n | r² |
| --- | --- | --- | ---: | ---: |
| `ZNKONST(34)` | `MH/all` | HW | 536 | 0.328 |
| `ZNKONST(35)` | `MH/all` | BG | 358 | 0.487 |
| `ZNKONST(36)` | `CDF/all` | FD (OC still coastal) | 3,642 | 0.212 |
| `ZNKONST(37)` | `CDF/all` | AT | 593 | 0.258 |

`P_ZN` moves from 43 to 47 and the ten CWH rows renumber to 38–47. Every other MH and CDF species
keeps the coastal donor through the existing CWH rows, and the site-series (`SSKONST`) row with
`CON=0` is unchanged. The form is the same log-link quadratic in DBH with an additive BAL term the
CWH rows use, fitted on live pairs with DBH 10.16–80 cm and 0 < DG < 3 cm/yr.

## 3. Evidence

The folds are W9's held-out sites and candidate set, rerun against the identical eligible sample so
the only difference is the four rows. Held-out bias and MAE are BA in m²/ha; train is the intervals
outside the held-out sites.

### MH (3 held-out / 15 train)

| Build | Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| W9 donor | `BAIMULT 8` | +2.47 | 2.47 | +0.21 | 3.46 |
| **W10 own** | **`BAIMULT 8`** | **+1.81** | **1.81** | **−0.53** | **3.82** |
| W9 donor | `BAIMULT 10` | +3.14 | 3.14 | +1.14 | 3.53 |
| W10 own | `BAIMULT 10` | +2.14 | 2.14 | +0.21 | 3.59 |

### CDF (16 held-out / 14 train)

| Build | Candidate | Test BA | Test MAE | Train BA | Train MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| W9 donor | `BAIMULT 8` | −16.12 | 17.07 | +2.84 | 4.23 |
| **W10 own** | **`BAIMULT 8`** | **−15.87** | **16.07** | **+2.34** | **4.36** |
| W9 donor | `BAIMULT 10` | −15.43 | 17.00 | +3.70 | 4.55 |
| W10 own | `BAIMULT 10` | −14.87 | 15.20 | +3.20 | 4.34 |

The own rows move held-out bias toward zero and cut held-out MAE at every candidate in both zones.
`BAIMULT 8` stays: it still has the smallest held-out MAE in MH, and the CDF difference between 8
and 10 is inside the fold's noise.

The CDF fold is hard and should be read as such. Its held-out sites are high-density CDFmm stands
(BA0 40–112 m²/ha) while the train intervals are young and open (mean BA0 39); both builds
under-predict the dense stands by 15–20 m²/ha, and the 16-interval fold is not the six-interval fold
the W9 note published. The W10 comparison is valid because donor and own rows ran on the same
sample; the absolute CDF error is a mortality/height gap, not a DG-row gap, and it stays on the
backlog.

## 4. Tier and claim

MH, CDF, and CWH remain **C**. W10 replaces a conspicuous donor with zone fits for four species but
does not make either zone validated: the small-tree, height, and mortality models are still donors,
the folds are unsigned, and MH's held-out fold is three intervals. The CDF dense-stand bias above is
open.

## 5. Build

Apply after W9; the wheel recipe does this. Verified by applying W8, W9, then W10 to the pinned tree
and compiling.
