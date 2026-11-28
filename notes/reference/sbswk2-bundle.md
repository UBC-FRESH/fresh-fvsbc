# `sbswk2-v3`: the SBSwk2 coupled calibration

Status: **shipped in 0.41.15; verified from PyPI.** Engine unchanged at 0.4.16. Tier stays C (unsigned).

## 1. The gap

SBSwk2 has 90 repeat sites; a 20% BA-stratified site fold leaves 41 held-out and 163 train
intervals. Both folds under-predicted BA and TPH:

| Fold | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: |
| test (41) | −4.48 / 5.95 | −270 / 489 |
| train (163) | −4.33 / 6.30 | −278 / 735 |

## 2. The fit

A train-only coupled grid (all species) selected `BAIMULT 2.0` + `MORTMULT 0.85`; recruitment then
supplied the remaining TPH. The recruitment scale was selected on train:

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | 5.95 | 489.2 | 6.30 | 735.0 |
| 2.0 / 0.85, no recruitment | 5.33 | 486.5 | 5.71 | 712.1 |
| 2.0 / 0.85, rec 0.4 | 5.35 | 423.0 | 5.78 | 654.6 |
| **2.0 / 0.85, rec 0.6** | **5.35** | **406.0** | **5.78** | **647.4** |
| 2.0 / 0.85, rec 0.8 | 5.35 | 397.9 | 5.78 | 653.7 |
| 2.0 / 0.85, rec 1.0 | 5.35 | 427.5 | 5.77 | 670.5 |

The train fold prefers 0.6; the held-out fold prefers 0.8. Selecting on train keeps 0.6, which also
leaves the smaller TPH bias (−9 held out, −17 train versus +85 at 0.8). All four MAE figures improve
against base.

## 3. The bundle

`sbswk2-v3` carries `BAIMULT 2.0`, `MORTMULT 0.85` for all twelve species, and the recruitment v1
block at scale **0.6**. Domain `SBSwk2`.

## 4. Evidence

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| base | test | −4.48 | 5.95 | −270 | 489.2 |
| **sbswk2-v3** | **test** | **−1.94** | **5.35** | **−8.9** | **406.0** |
| base | train | −4.33 | 6.30 | −278 | 735.0 |
| **sbswk2-v3** | **train** | **−1.43** | **5.78** | **−17.5** | **647.4** |

## 5. What remains

SBSwk2 is now within ~2 m²/ha and ~17 TPH. SBSdw1 (43 sites) and SBSmc remain; SBSmc is already
well calibrated on the exact-BEC fold.

## Reproduce

- Fold split: `~/workspace/bwbs-work/SBSwk2_test_sites.txt` (every fifth site after sorting by mean
  BA).
- Bundle fold: `probe_sbswk2_bundle/`; scale grid: `probe_SBSwk2_rec{40,60,80,100}/`.
