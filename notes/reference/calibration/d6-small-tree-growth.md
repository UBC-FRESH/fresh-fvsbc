# D6.2 small-tree growth threshold

Status: isolated to the small-tree diameter and height growth path; fixed in D6.4 (`d6-sbps-small-tree.md`)
Date: 2026-11-03
Issue: #338
Builds: `fresh-fvsbc-pyfvs 0.3.13` and `0.4.0`; both give the same result
Evidence: D6.1 #336, `d6-sbps-growth.md`

## 1. The build comparison is corrected

D6.1 compared the W3.1 supported baseline (11,214 m²/ha on the SBPSmc interval) with the D5
all-zone baseline (457,348 m²/ha) and suspected a build effect. That comparison was invalid.

The W3.1 baseline's initial BA on that interval was **21.0**, not the observed 31.1; its tree-list
read had lost part of the stand. A clean full-stand run of the same interval gives:

| Build | Initial BA | Final BA | Final QMD |
| --- | ---: | ---: | ---: |
| 0.3.13 | 31.0 | 457,348 | 1,451.6 |
| 0.4.0 | 31.0 | 457,348 | 1,451.6 |

The five-zone patch does not cause the explosion. The W3.1 baseline's `SBPSmc` row is an
incomplete-tree-list result and must not be used as a build comparison.

## 2. One-tree matrix

A single tree, one 11-year cycle, `SBPSmc/01`, `SITECODE FD,20`, `BAMAX` 50, on both builds. The
build, BEC, species (`SE` vs `PL`), and age (10 vs 60) make no difference. The DBH threshold does:

| Initial DBH (tree-list units) | Final DBH | DG | HtG |
| ---: | ---: | ---: | ---: |
| 1.0 | 435.5 | 421.0 | 299.5 |
| 5.0 | 439.5 | 421.0 | 299.5 |
| 7.5 | 442.0 | 421.0 | 299.5 |
| 7.6 | 442.1 | 421.0 | 299.5 |
| 8.0 | 8.86 | 0.83 | 299.5 |
| 10.0 | 10.86 | 0.83 | 299.5 |
| 11.0 | 11.85 | 0.83 | 2.15 |

- **DBH below 8:** both diameter and height growth explode.
- **DBH 8 to 10:** diameter is normal; height growth still explodes.
- **DBH 11 and above:** both are normal.

The same threshold appears at `SBPSmc` and `IDFdk3`, and for `SE` and `PL`. The one-tree test also
shows the explosion does not need density: one 5-unit tree is enough.

## 3. Density matrix

Repeating a 5-unit `PL` tree at target TPH 100, 500, 1,000, 2,000, 3,000, 4,000, and 5,400 gives
the same final DBH 439.5 and DG 421.0 at every density. Density changes BA through the expansion
factor, not the per-tree growth. This is not a density-dependent growth response.

## 4. Next instrument

The threshold pointed at the BC small-tree branches in `canada/bc/dgf.f` and the height-growth
routine, not at mortality. D6.4 found the branch in `canada/bc/regent.f`: the `SBS`/`SBPS` model
selector tested only `SBS`, so `SBPS` took the exponential IDF/ICH form with SBS coefficients and
overflowed. `d6-sbps-small-tree.md` has the fix; the next step is the D7 calibration of the
corrected residual, not another source branch hunt.

## 5. Limits

- One-tree and synthetic-density runs; the interaction with a full stand is not yet explained beyond
  the threshold.
- The tree-list units are the BC tree-list units, not the metric summary units.
- Raw per-tree rows and site identifiers stay in `runtime/`; this note carries aggregates.
