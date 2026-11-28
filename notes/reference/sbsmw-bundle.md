# `sbsmw-v3`: recruitment-only correction

**Refit in 0.41.17 on stable-DBH-limit intervals.** The 0.41.13 numbers in this note came from a fold that mixed 9.1 cm and 2 cm visits; see `dbh-limit-break.md` for the clean fold and the current bundle.

Status: **refit and shipped in 0.41.17** (`BAIMULT 0.95`, no recruitment). Engine unchanged at 0.4.16. Tier stays C (unsigned).

## 1. The gap

SBSmw's BA is already calibrated; TPH is under.

| Fold | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: |
| test (62) | +0.16 / 5.18 | −282 / 421 |
| train (238) | −0.25 / 4.63 | −201 / 296 |

A growth or mortality multiplier would move BA off its calibration. Recruitment adds small stems,
which raise TPH with little BA.

## 2. The scale grid

Recruitment v1 scale on the 20% BA-stratified site fold:

| Scale | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| base | 5.180 | 421.0 | 4.626 | 295.6 |
| 0.4 | 5.183 | 404.0 | 4.647 | 283.8 |
| 0.8 | 5.167 | 400.7 | 4.635 | 284.0 |
| **1.2** | **5.151** | **403.0** | **4.622** | **293.7** |
| 1.6 | 5.151 | 409.1 | 4.614 | 311.1 |

`1.2` is the only scale that improves all four MAE figures and both TPH biases (−282 → −128 test,
−201 → −47 train). `1.6` overshoots train TPH.

## 3. The bundle

`sbsmw-v3` carries the recruitment v1 block at scale **1.2** and no growth or mortality
parameters. Domain `SBSmw`.

## 4. Evidence

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| base | test | +0.16 | 5.18 | −282 | 421.0 |
| **sbsmw-v3** | **test** | **+0.19** | **5.15** | **−128** | **403.0** |
| base | train | −0.25 | 4.63 | −201 | 295.6 |
| **sbsmw-v3** | **train** | **−0.21** | **4.62** | **−47** | **293.7** |

## 5. What remains

SBSmw is still −128 TPH biased. SBSmk1 remains the largest subzone defect; SBSmc2 is +2.2/−323 on
its matched fold.

## Reproduce

- Fold: `~/workspace/bwbs-work/probe_sbsmw_bundle/` (300 rows).
- Scale grid: `probe_sbsmw_rec{40,80,120,160}/`.
