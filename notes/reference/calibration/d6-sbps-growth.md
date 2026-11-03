# D6.1 SBPS growth diagnosis

Status: first diagnosis; fixed in D6.4 (`d6-sbps-small-tree.md`)
Date: 2026-11-03
Issue: #336
Build: local `fresh-fvsbc-pyfvs 0.4.0` (five-zone prototype)
Interval: the Quesnel TSA `SBPSmc` interval selected by the D5 baseline, 1995–2006, 11 years

## 1. Reproduction

The D5 all-zone baseline selects the first `SBPSmc` interval by BEC, TSA, site, plot, and year. The
stand has 195 live trees, 5,403.6 TPH, and 31.1 m²/ha initial BA. The run reproduces the initial
stand (31.1 → 31.0 m²/ha), then reports at the next measurement:

| Quantity | Initial | After 11 years |
| --- | ---: | ---: |
| BA (m²/ha) | 31.0 | 457,348 |
| TPH | 5,400 | 2,762 |
| QMD (cm) | 8.6 | 1,451.6 |
| Top height (m) | 16 | 304.5 |

The run does not report an FVS error and does not fall back to another BEC; `STDINFO BEC=SBPSmc/01`
and the `BAMAX` echo of 50.0 are correct.

## 2. The tree list

`FVS_TreeList_Metric` at the end of the cycle shows the explosion is in **diameter growth**:

- The largest `SE` tree has `DBH` 2,319.9, `DG` 2,215.6, `Ht` 304.5, and `HtG` 301.6 in the tree-list
  units. The initial largest `SE` tree has `DBH` 13.4.
- The largest `PL` tree has `DBH` 438.2 and `DG` 420.8. Both species explode; this is not one
  species code.
- At the initial measurement the tree list has 195 records and the correct BA. At the end it has
  585 rows: three rows for each tree, with different TPH values. The duplicate rows are a second
  finding, but the growth is already visible in the first.

A diameter change of ~2,200 tree-list units in 11 years cannot be mortality, ingrowth, or a
classification change. The failure is in the diameter-growth path or in the units the path consumes.

## 3. What this changes

The D5 report correctly ranked SBPS first but described it as “small-tree density and mortality”.
The evidence narrows it to **diameter growth**:

- The initial stand and tree list are reproduced.
- The stand loses TPH (5,400 → 2,762), so mortality is active, not absent.
- A single cycle drives QMD and BA far above any density explanation; the per-tree DBH is the
  exploded quantity.

**Correction:** the 11,214 m²/ha figure came from an incomplete tree-list read in the W3.1
supported baseline (its initial BA was 21.0, not 31.1). A clean full-stand run gives 457,348 on both
0.3.13 and 0.4.0. The five-zone patch did not cause the explosion. `d6-small-tree-growth.md` records
the corrected comparison.

## 4. Next instrument

A one-tree, one-cycle sensitivity run, at fixed species (`SE`, `PL`), DBH, and age, with `SITECODE`
fixed and `BAMAX` held constant. `d6-small-tree-growth.md` carries the result: the explosion is a
small-tree threshold (DBH below 8 for diameter, below 11 for height), not a unit conversion and not
density. The next step is to read the small-tree branches in `canada/bc/dgf.f` and the height-growth
routine.

## 5. Limits

- One interval, one stand, one 11-year cycle.
- The tree-list units are the BC tree-list units, not the metric summary units; the note keeps them
  distinct.
- Raw per-tree rows and the site identifier stay in `runtime/`; this note carries aggregates and
  diagnostic values only.
