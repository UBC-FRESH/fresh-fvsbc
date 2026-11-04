# D8.5 CDF screening: one TSA, no robust site-fold candidate

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper `0.21.4`. Public tree detail only.

## Data

CDF has one label, `CDFmm`, with 94 intervals and 21 sites. Every interval is in the **Arrowsmith
TSA**, so there is no independent TSA holdout. The site folds are deterministic sorted-site
5-folds; fold 0 (5 sites) and fold 1 (4 sites) were inspected before any parameter selection.

## Result

| Model | Fold | n | BA bias | BA % | TPH bias | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | all | 88 | -10.47 | -20.2% | -34.1 | -2.6% |
| one candidate | all | 88 | -2.27 | -4.4% | +110.3 | +8.4% |
| baseline | site fold 0 | 31 | -15.96 | -25.7% | -23.9 | -1.8% |
| one candidate | site fold 0 | 31 | **-6.80** | **-10.9%** | +124.9 | +9.5% |
| baseline | site fold 1 | 12 | -9.56 | -18.7% | -71.3 | -9.5% |
| one candidate | site fold 1 | 12 | -2.73 | -5.3% | +0.3 | +0.0% |

The all-interval result looks acceptable, but the held-out site fold 0 misses BA by 6.8 m2/ha.
Raising `BAIMULT` to 12 brings fold 0 BA to -2.48 but training BA to +3.51, and 12 is an
unacceptable multiplier for a certificate.

## Decision

**No CDF bundle.** The apparent all-interval fit is a site-composition effect; one TSA and 21 sites
do not support a spatial claim. CDF stays a screening result until an independent TSA or a
site-level covariate is available. Do not select a BAIMULT from the all-interval row.

No files beyond this report; the candidate is not promoted.
