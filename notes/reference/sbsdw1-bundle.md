# `sbsdw1-v3`: the SBSdw1 coupled calibration

Status: **shipped in 0.41.16; verified from PyPI.** Engine unchanged at 0.4.16. Tier stays C (unsigned).

## 1. The gap

SBSdw1 has 43 repeat sites; a 20% BA-stratified site fold leaves 11 held-out and 61 train
intervals. Both folds over-predicted BA, but the TPH error changes sign:

| Fold | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: |
| test (11) | +5.84 / 6.38 | +28 / 269 |
| train (61) | +5.38 / 7.29 | −66 / 246 |

A growth-only cut improves BA but pushes TPH further up (test already over). The coupled fix is
lower growth, higher mortality, and recruitment, so BA comes down while TPH MAE stays in range.

## 2. The fit

Train-selected coupled grid with recruitment v1:

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | 6.38 | 268.6 | 7.29 | 245.8 |
| 0.6 / 1.3, rec 0.4 | 4.25 | 264.1 | 6.26 | 243.8 |
| 0.6 / 1.4, rec 0.4 | 4.16 | 257.2 | 6.14 | 243.9 |
| **0.7 / 1.3, rec 0.4** | **4.00** | **263.7** | **6.32** | **237.6** |

The 0.6–0.7 / 1.3–1.4 neighbourhood improves all four measures; selecting on train takes
`BAIMULT 0.7`, `MORTMULT 1.3`. A weaker point (`0.5 / 1.3`) does not improve TPH, so the plateau
is real but narrow.

## 3. The bundle

`sbsdw1-v3` carries `BAIMULT 0.7`, `MORTMULT 1.3` for all twelve species, and recruitment v1 at
scale **0.4**. Domain `SBSdw1`.

## 4. Evidence

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| base | test | +5.84 | 6.38 | +28 | 268.6 |
| **sbsdw1-v3** | **test** | **+1.84** | **4.00** | **+67** | **263.7** |
| base | train | +5.38 | 7.29 | −66 | 245.8 |
| **sbsdw1-v3** | **train** | **+2.58** | **6.32** | **−43** | **237.6** |

The held-out TPH bias moves away from zero while its MAE improves slightly; BA improves strongly
in both folds. Because the fold has only 11 held-out intervals, treat the TPH gain as provisional.

## 5. What remains

The SBS subzone set is now covered for SBSmk1, SBSmw, SBSwk2 and SBSdw1; SBSmc needs none;
SBSmc2 stays at its documented +2.2 / −323 block.

## Reproduce

- Fold split: `~/workspace/bwbs-work/SBSdw1_test_sites.txt`.
- Bundle fold: `probe_sbsdw1_bundle/`; neighbourhood: `probe_SBSdw1_neighborhood/`.
