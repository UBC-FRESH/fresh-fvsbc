# SBS subzone folds: SBSmk1 is the real gap, and W22 is not the cause

Status: **finding + next target.** No change ships from this step.

## 1. Independent subzone folds from the province data

All SBS subzones use the same 126+ repeat-site inventory; the SBS fold's `per_bec` sampling
had hidden the subzone spread. Three 20% site folds (BA-stratified) on the current engine:

| Subzone | Test intervals | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: | ---: |
| SBSmk1 | 56 | −5.18 / 7.00 | −637 / 881 |
| SBSmw | 62 | +0.16 / 5.18 | −282 / 421 |
| SBSmc | 24 | −0.80 / 1.93 | −22 / 71 |

SBSmk1 is far worse than the SBS zone average (−0.53 / 5.91 on the sampled fold). It is also the
largest subzone by repeat sites (118).

## 2. W22 is not the cause

W22's BL CCFA −0.35 was selected on SBSmc2 and lives in the shared BL SBS row. Scoping it to
SBSmc2 (zeroing row 31's CCFA outside SBSmc2) changed SBSmk1 and SBSmc by zero and SBSmw by
0.02 in MAE. The term is effectively inactive or swamped outside SBSmc2, so the SBS-wide
concern is unfounded and no scoping patch ships.

## 3. Next

SBSmk1 has 118 repeat sites and is the worst-calibrated SBS subzone. The same train-only
coupled growth/mortality recipe used for MS/ESSF should be applied to an `sbsmk1-v3` bundle and
validated on its 56-interval held-out fold. The species mix is PL 34%, SE 20%, AT 18%, BL 15%,
EP 5%, so a species-specific growth/mortality calibration has room to work.

## Reproduce

- Splits: `~/workspace/bwbs-work/{SBSmk1,SBSmw,SBSmc}_test_sites.txt`.
- Current engine: `probe_{SBSmk1,SBSmw,SBSmc}_w22/`.
