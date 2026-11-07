# D9.27 IDFdk recruitment re-fit after the unit fix

Status: **pooled re-fit works; site distribution does not**
Date: 2026-11-07
Data: IDFdk, 4 cm PSP, training excludes 100 Mile House TSA
Evidence: `d9-idfdk-refit-summary.csv`

The old IDFdk rates were fit as means and then under-delivered by the TPA bug. After the D9.24 unit
fix, the old rates overshoot. This re-fits the rates from the same training intervals with
mean/median summarization and with all trees vs trees >=4 cm.

## Result

Training: 22 intervals / 15 sites. Test: 7 intervals / 5 sites (100 Mile House).

| Rates | Test BA | Test TPH | Test sites | Train BA | Train TPH | Train sites |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Old mean, corrected | −5.6% | +8.6% | 4/5 | −0.3% | +37.4% | 8/15 |
| Mean, all trees | −5.6% | +1.0% | 2/5 | −0.3% | +19.6% | 3/15 |
| **Median, all trees** | **−6.0%** | **−13.3%** | **4/5** | **−0.3%** | **+7.5%** | **8/15** |
| Mean, >=4 cm | −6.0% | −5.2% | 3/5 | −0.3% | +13.5% | 7/15 |
| Median, >=4 cm | −6.0% | −15.1% | 4/5 | −0.3% | +1.2% | 10/15 |

The pooled thresholds pass for `median-all` and `mean-4`, but the **site pass count is poor**:
4/5 test and 8/15 train for `median-all`; 10/15 train for `median-4`, but its test TPH is −15.1%.

## Decision

- Do not issue a new IDFdk bundle from these rates.
- The old IDFdk bundle and binned bundle remain stale/pilot.
- A mean/median rate table is too blunt. The next step is the `BCINGR` hurdle/ZINB model with
  density and seed-source covariates, as designed in D9.25.

## Claim boundary

This is a re-fit screen. It does not support a yield, AAC, legal, or whole-block claim.
