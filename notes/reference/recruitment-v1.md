# Recruitment v1: BEC × species × BA-bin new-tree TPH

Status: **built and validated on a BEC-stratified site holdout; unsigned pilot, tier C.**
Date: 2026-11-25. Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Bundle: `recruitment-bc-v1-bundle.json`.

## 1. What it is

A BC-wide recruitment model for FVS's `ESTAB` block. New trees are the trees present at the second
visit whose `TREE_NO` was not present at the first, resolved through the donor species layer. The
annual rate is a **mean** new TPH by:

- BEC label (e.g. `BWBSmw`, `SBSdw2`), not TSA;
- FVS species (all fifteen codes, not the four calibration groups);
- initial-BA bin: `0-10, 10-20, 20-30, 30-40, 40-60, 60+ m2/ha`.

`recruitment_table` and `fit_rates` now carry all fifteen species; the default remains the four
calibration groups for existing callers.

## 2. Fit and holdout

17,145 intervals, 5,732 sites, all forested zones. CMA is excluded (out of scope). The split is
BEC-stratified: every fourth site in each BEC is held out (1,493 test sites, 4,429 test intervals).

| Measure | Held-out result |
| --- | ---: |
| Observed new TPH mean | 416 |
| Predicted new TPH mean (data model) | 388 |
| Bias | -28 (-6.8%) |
| Correlation | 0.33 |

The interval variance is large (MAE ~427 TPH); the model is an expected-rate model, not an
interval-level predictor.

## 3. Multi-cycle FVS validation

The model is applied through the bundle's ingrowth block with three cycles. On the same held-out
sample:

| Run | Test TPH bias | Test TPH % | Train TPH bias |
| --- | ---: | ---: | ---: |
| no ingrowth | -138 | -7% | -173 |
| model, scale 1.0 | +271 | +26% | +262 |
| **model, scale 0.4** | **+26** | **+1.3%** | **+1.3** |

The scale of 0.4 was fitted on the training split and evaluated on the held-out sites. It is a
calibration to the FVS run, not to the raw data: the data model is already 7% low, while FVS
undershoots TPH by 138 without ingrowth and overshoots when the full observed rate is added.

## 4. The year-0 correction

Establishment at the inventory year makes FVS re-select its sample trees, which distorted the earlier
ingrowth runs. `estab_keyword` now skips the first cycle for a multi-cycle projection and spreads the
same total TPH over cycles 2..N. A single-cycle block still establishes at cycle 1 and is not the
recommended use.

## 5. Claim boundary

- **C**: unsigned, mean-rate, BEC/species/BA-bin; no QMD bin, seed year, climate, or dispersal.
- Use the **multi-cycle** harness; a single-cycle `ESTAB` is not validated.
- The scale is a fitted calibration; a change to the growth/mortality engine should refit it.
- CMA is excluded; CMA remains X.

## 6. Reproduce

`tests/test_recruitment_v1.py` loads the bundle and checks the multi-cycle block. The builder and the
holdout split live with the calibration work; the bundle carries the rates and the scale.
