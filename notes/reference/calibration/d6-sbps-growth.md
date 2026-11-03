# D6.1 SBPS growth diagnosis

Status: first diagnosis; root cause not yet fixed
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

The 0.4.0 five-zone build also gives a larger explosion than the 0.3.13 supported build on the same
interval: the W3.1 summary predicted 11,214 m²/ha, the 0.4.0 summary 457,348. The five-zone patch
changes only `HABTYP` and `SITSET`, so the next comparison is a clean 0.3.13 versus 0.4.0 run with the
same tree list. If the tree lists are identical, the difference is a build or BEC-state effect; if
they differ, the patch changed how the stand is read.

## 4. Next instrument

A one-tree, one-cycle sensitivity run, at fixed species (`SE`, `PL`), DBH (10, 20, 40 cm), and age
(60 and the measured age where available), with `SITECODE` fixed and `BAMAX` held constant:

- read `DG`, `HtG`, and the summary after one cycle;
- vary one input at a time;
- compare the 0.3.13 and 0.4.0 builds on the same tree list.

That separates a unit conversion from a growth-equation response. No parameter is changed until the
mechanism is named.

## 5. Limits

- One interval, one stand, one 11-year cycle.
- The tree-list units are the BC tree-list units, not the metric summary units; the note keeps them
  distinct.
- Raw per-tree rows and the site identifier stay in `runtime/`; this note carries aggregates and
  diagnostic values only.
