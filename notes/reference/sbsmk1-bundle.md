# `sbsmk1-v3`: the SBSmk1 subzone gap

Status: **shipped in 0.41.14; verified from PyPI.** Engine unchanged at 0.4.16. Tier stays C (unsigned).

## 1. The gap

The SBS zone fold samples `per_bec`, hiding the subzone spread. A 20% BA-stratified site fold on
the province data gives SBSmk1 (118 repeat sites, 56 held-out intervals):

| Build | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: |
| base | −5.18 / 7.00 | −637 / 881 |
| growth/mortality only | −1.97 / 6.37 | −669 / 873 |
| **`sbsmk1-v3` (with recruitment)** | **−2.01 / 6.33** | **−409 / 810** |

## 2. The fit

Both folds under-predicted BA and TPH. A train-only coupled grid (all species):

| Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | 7.00 | 881 | 6.54 | 780 |
| 1.5 / 0.85 | 6.55 | 877 | 6.18 | 775 |
| **2.0 / 0.85** | **6.37** | **873** | **6.12** | **767** |
| 2.5 / 0.85 | 6.19 | 885 | 6.23 | 759 |

`BAIMULT 2.0` + `MORTMULT 0.85` improved BA but left TPH under (−669). Adding recruitment v1 at
scale 0.4 supplies the TPH: held-out TPH MAE 873 → 810, train 767 → 743, BA also improves. The
TPH bias moves from −669 to −409 (test) and −409 to −144 (train).

## 3. W22 is not the cause

Zeroing the shared BL SBS row's W22 CCFA outside SBSmc2 changed SBSmk1 and SBSmc by **zero** and
SBSmw by 0.02 MAE. The SBS-wide density term is not driving the subzone gaps.

## 4. What remains

SBSmk1 is still −409 TPH biased. SBSmw now has its own bundle (0.41.13); SBSmc remains to check.

## Reproduce

- Fold: `~/workspace/bwbs-work/probe_sbsmk1_bundle/` (274 rows).
- Grid: `probe_sbsmk1_grid/`.

## 6. Stem-shape refinement fails

The remaining TPH bias (−409) was tested with a SBSmk1-scoped stem-shape term:

| Shape | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| shipped (rec 0.4) | **6.334** | **810.4** | **6.088** | **743.0** |
| save <10 cm ×0.5 | 6.316 | 848.8 | 6.194 | 793.6 |
| save <10 ×0.5, thin ≥20 ×1.5 | 6.201 | 847.1 | 6.148 | 790.5 |

Saving small stems improves the TPH **bias** (−409 → −341) but worsens its **MAE**; the coupled
thinning-large half lowers BA a little and still leaves TPH MAE worse. The recruitment scale 0.4
is the optimum; a further stem-shape term only trades bias for variance. Reverted; no ship.
