# D7.3 SBPS TPH component

Status: candidate parameter set passes the D7 probe holdout; **not a bundle or certificate**
Date: 2026-11-03
Issue: #351
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: all-zone calibration dataset, all eligible SBPSdc and SBPSmk intervals
Evidence: `d7-tph-summary.csv`, `d7-tph-by-bec.csv`, `d7-tph-candidates.json`

D7.2 found that `BAMAX` alone moves BA but leaves TPH low. This probe tests whether lowering
`MORTMULT` supplies the missing TPH without breaking the BA fit.

## 1. Sample and split

The eligibility rules and site-grouped split are D7.2's. `SBPSdc` has 39 intervals / 13 sites;
`SBPSmk` has 187 / 84. `SBPSxc` and `SBPSmc` are out: the first failed both BA and TPH, the second
has one interval and is validation-only.

Six candidates combine `BAMAX` 40/45/50 with `MORTMULT` 0.5/0.75/1.0 for `PL` and `SE`. No
`BAIMULT` or `HTGMULT`.

## 2. Result

The candidate `BAMAX=50, MORTMULT=0.5` (`PL` and `SE`) passes both pre-registered bias tests on the
held-out sites:

| BEC | Test intervals | BA bias | BA MAE | TPH bias | TPH % |
| --- | ---: | ---: | ---: | ---: | ---: |
| `SBPSdc` | 16 | +1.97 | 6.14 | -270.7 | -11.2% |
| `SBPSmk` | 63 | +2.38 | 5.72 | -63.7 | -3.4% |

The thresholds are BA bias within ±3 m2/ha (or 10%) and TPH bias within 15%. Both pass. `MORTMULT
0.5` is inside the bundle bound `[0.25, 4.0]`; `BAMAX 50` is inside `[25, 89]`. Neither is at a
bound.

The surface is not a single optimum. `BAMAX=45, MORTMULT=0.5` also passes both BECs
(`SBPSdc` +1.59 / -12.4%; `SBPSmk` +2.00 / -4.6%), and `BAMAX=50, MORTMULT=0.75` passes
(`SBPSdc` +1.03 / -14.2%; `SBPSmk` +1.39 / -6.5%). The candidates trade BA against TPH.

Training error is worse than test error for `BAMAX=50, MORTMULT=0.5` (`SBPSdc` training BA bias
+7.21; `SBPSmk` +3.96), so the held-out result alone does not establish a slope of 1 or an
intercept of zero.

## 3. Decision

The candidate set is **promoted to D7.4 validation**, not to a bundle and not to a certificate:

- `BAMAX=50`
- `MORTMULT=0.5` for `PL` and `SE`
- domain: `SBPSdc` and `SBPSmk`, untreated

D7.4 must:

1. check calibration slope and intercept, not only bias;
2. test more independent sites, especially `SBPSdc`, which has 13;
3. keep `SBPSxc` out and `SBPSmc` validation-only;
4. issue a signed bundle only after review, with the parameter bounds and claim boundary.

## 4. Claim boundary

This is a probe result. It does not change a default, does not certify SBPS, and does not support a
yield, AAC, legal, or whole-block claim. The defensible statement is narrow: on the held-out sites
in this sample, one `BAMAX`/`MORTMULT` candidate meets the pre-registered BA and TPH bias thresholds
for `SBPSdc` and `SBPSmk`.
