# SBSmc2 variance-aware ingress shape

Status: **shipped in 0.41.7; verified from PyPI.** Engine unchanged at 0.4.14. Tier stays C (unsigned).

## 1. The matched fold

The random SBSmc2 split left the held-out stands more under-stocked than train. Splitting the 126
sites by mean BA0 (five quantile bins, 20% within each) matches the folds and gives the shipped
0.41.6 configuration at **+2.2 BA / −386 TPH** (test BA MAE 7.89, TPH 828; train 8.09, 610).

## 2. Why a global scale fails

Global recruitment scales 0.6–1.6 improve the held-out TPH but worsen the train TPH MAE: the
train fold is already at or above the observed stem count in most bins. The per-bin MAE response
between scale 0.4 and 0.8 gives:

| BA bin | Train TPH MAE (0.4 → 0.8) | Test TPH MAE (0.4 → 0.8) |
| --- | ---: | ---: |
| 10–20 | 1,949 → 1,831 | 482 → 1,028 (n=1) |
| **20–30** | **1,060 → 1,053** | **1,799 → 1,557** |
| 30–40 | 527 → 574 | 1,206 → 1,118 |
| 40–60 | 483 → 499 | 393 → 467 |
| 60+ | 342 → 362 | — |

Only **BA 20–30** improves train MAE at the higher scale (and it improves held-out MAE too). The
others add variance on train.

## 3. The change

In `sbsmc2-v3`, the recruitment rates for the **20–30 m²/ha BA bin are doubled**; every other bin
stays at the recruitment v1 scale of 0.4.

## 4. Evidence (matched stratified fold)

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.41.6 | test | +2.17 | 7.89 | −386 | 828 |
| **0.41.7** | **test** | **+2.22** | **7.84** | **−323** | **794** |
| 0.41.6 | train | +1.58 | 8.09 | −272 | 610 |
| **0.41.7** | **train** | **+1.61** | **8.10** | **−210** | **609** |

Held-out BA and TPH MAE both improve; train TPH improves and train BA is flat (+0.01).

## 5. What remains

The remaining −386 TPH is spread across the other BA bins, where a recruitment boost increases
train variance. Further improvement needs either a stand-level (not bin-level) ingress model or
more held-out sites; the bin shape is at its current limit.

## Reproduce

- Stratified split: `~/workspace/bwbs-work/sbsmc2_test_sites_strat.txt`.
- Scale grid: `probe_strat_sc{40,60,80,100,120}/`.
- Variance-aware run: `probe_strat_varfit2/` and `probe_sbsmc2_v2final/`.
