# D8.3 BWBS growth pilot: three TSA holdouts

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper `0.21.4`. Public tree detail only.

## Design

BWBS has 5 labels and 710 intervals. The probe uses a deterministic **20-per-BEC** sample: 96
intervals, split by TSA. The candidate is fixed; it is not refit for each holdout.

- `BAIMULT 5.5` for FD, PL, SE, HW, AT, BL, CW, BG, PW
- `MORTMULT 0.2` for the same nine species
- no ingrowth; no `BAMAX` change

`BAIMULT 5.5` is high. The lower mortality is also outside the routine 0.5-2 range. Both are
inside the bundle bounds, but this is a pilot correction, not evidence that the BWBS growth path is
right.

## Result

| Holdout | Fold | n | BA bias | BA MAE | BA % | TPH bias | TPH MAE | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dawson Creek | test | 38 | +2.09 | 6.18 | +4.8% | +248.7 | 461.4 | +11.7% |
| Dawson Creek | train | 56 | -1.92 | 5.62 | -5.3% | -191.4 | 777.2 | -7.8% |
| Cassiar | test | 4 | +1.58 | 1.58 | +7.7% | +69.3 | 79.6 | +6.6% |
| Cassiar | train | 90 | -0.38 | 6.03 | -0.9% | -17.2 | 674.9 | -0.7% |
| Fort St. John | test | 13 | -1.74 | 7.39 | -3.8% | -532.5 | 1,234.0 | -14.7% |
| Fort St. John | train | 81 | -0.07 | 5.60 | -0.2% | +69.8 | 555.7 | +3.3% |

Baselines on the same tests were BA **-10.88 / -4.67 / -13.28** and TPH **-4.7% / -6.9% /
-23.2%**. All pilot folds are inside BA ±3 m2/ha and TPH 15%.

## Decision

**BWBS pilot bundle issued:** `d8-bwbs-bundle.json`. It is unsigned, not a certificate. The
Fort St. John TPH result is close to the limit, and the Cassiar test has only four intervals. A
temporal holdout, a leave-one-BEC holdout, and reviewer sign-off remain before any release claim.

This is a **growth/mortality** pilot, not an ingrowth model. The previous BWBS all-zone ingrowth
screen over-recruited the domain and is not used.

Evidence: `d8-bwbs-summary.csv`.
