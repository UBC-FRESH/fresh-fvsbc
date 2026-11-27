# `sbsmc2-v3`: the full-subzone growth correction

Status: **shipped in 0.41.5; verified from PyPI.** Engine unchanged at 0.4.13. Tier stays C (unsigned).

## 1. The sample problem

The SBS fold sampled `per_bec 10` across all subzones, leaving **10 SBSmc2 intervals**. The data
has **249 intervals on 126 sites**. A dedicated 20% site split (42 held out / 163 train) shows the
full subzone at **+11.6 m²/ha BA / −1,064 TPH**, not the sampled +1.5/−81. The old claim was
sample-specific.

## 2. What did not work

Lighter <10 cm mortality (clean `morts.f` term) cut the TPH error but raised BA — more small stems
survive, so the over-BA grows. A size-specific BL 10–20 cm growth/mortality grid moved the two
errors in opposite directions. The subzone needed a lever that lowers BA **and** raises TPH.

## 3. The change

All-species growth reduction — `BAIMULT 0.3` — lowers BA and raises TPH together (less growth
means less self-thinning). Train-only selection picked 0.3; the held-out fold confirms it.

The shipped `sbsmc2-v3` bundle also carries the recruitment v1 ingrowth block, so it is
self-contained.

## 4. Evidence

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| base | test | +11.6 | 14.04 | −1,064 | 1,298 |
| **sbsmc2-v3** | **test** | **+9.1** | **12.52** | **−908** | **1,212** |
| base | train | +5.0 | 8.37 | −297 | 574 |
| **sbsmc2-v3** | **train** | **+2.6** | **7.66** | **−215** | **566** |

Both MAE figures improve on both folds; both biases also improve. The defect is reduced, not
fixed: the subzone remains +9.1 m²/ha / −908 TPH.

## 5. What remains

The remaining over-BA/under-TPH is a small-stem mortality/ingrowth shape problem across the whole
subzone. The growth correction is a partial, validated step. A full fix needs a mortality /
ingrowth model that adds stems without adding basal area, fitted on the representative fold.

## 6. Build and use

Bundle `sbsmc2-v3-ba03-rec-2026-11-27`, domain `SBSmc2`, `BAIMULT 0.3` for all twelve species plus
the recruitment block. Use it instead of `sbs-v3` for SBSmc2 stands. The engine is 0.4.13.

## Reproduce

- Split: `~/workspace/bwbs-work/sbsmc2_test_sites.txt`.
- Grid: `~/workspace/bwbs-work/probe_sbsmc2_growth/`.
- Bundle run: `~/workspace/bwbs-work/probe_sbsmc2_final/`.
