# D7.2 SBPS capacity per BEC

Status: probe complete; **no per-BEC capacity bundle is promoted**
Date: 2026-11-03
Issue: #348
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: all-zone calibration dataset; all eligible SBPS intervals

This is a readiness probe, not a calibration. It tests whether `BAMAX` can be fitted per BEC after
D7.1 showed that one global SBPS set cannot meet the holdout.

## 1. Sample and split

The eligibility rules are D7.1's: initial BA at least 15 m2/ha, initial QMD at least 6 cm, dead BA
at most 40% of initial BA. The full eligible sample is larger than the D7.1 five-per-BEC sample:

| BEC | Intervals | Sites | TSA |
| --- | ---: | ---: | --- |
| `SBPSdc` | 39 | 13 | Quesnel |
| `SBPSmc` | 1 | 1 | Quesnel |
| `SBPSmk` | 187 | 84 | 100 Mile House |
| `SBPSxc` | 6 | 5 | Williams Lake |

Sites are held out, not intervals. Every third site in sorted order is test: 5 of 13 for `SBPSdc`,
28 of 84 for `SBPSmk`, and 2 of 5 for `SBPSxc`. `SBPSmc` is validation-only.

## 2. Candidate set

`BAMAX` 40, 45, 50, and 55; no `BAIMULT` or `MORTMULT`. The best training candidate per BEC is
chosen by BA MAE, then evaluated on the held-out sites. The full table is
`d7-per-bec-summary.csv`; the candidate list is `d7-per-bec-candidates.json`.

## 3. Result

| BEC | Best training | Train BA MAE | Test BA bias | Test BA MAE | Test TPH bias | Test TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `SBPSdc` | `bamax40` | 6.19 | -2.16 | 3.99 | -552.33 | 577.46 |
| `SBPSmk` | `bamax40` | 5.03 | -1.18 | 4.62 | -286.56 | 374.25 |
| `SBPSxc` | `bamax40` | 4.75 | +22.29 | 22.29 | -1,349.69 | 1,349.69 |
| `SBPSmc` | — | — | validation-only | — | — | — |

- `SBPSdc` is the best case: held-out BA bias is within ±3 m2/ha, but TPH is biased -552, far outside
  the 15% threshold.
- `SBPSmk` has held-out BA bias -1.18, but TPH -287, also outside the TPH threshold.
- `SBPSxc` fails both: BA +22.3 and TPH -1,350.
- `SBPSmc` has one eligible interval and cannot train or validate a capacity.

## 4. Decision

**No per-BEC capacity bundle is promoted.** Capacity alone moves BA on `SBPSdc` and `SBPSmk`, but
neither reaches the pre-registered TPH threshold. `SBPSxc` fails both. A BA-only fit is not a
capacity bundle.

The next D7 work is:

1. Treat `SBPSdc` and `SBPSmk` as capacity candidates, but only with a TPH/ingrowth component.
2. Keep `SBPSxc` out of a bundle until its sample supports an independent fit.
3. Keep `SBPSmc` validation-only.
4. Do not pool the SBPS labels; the per-BEC response differs.

The probe is `scripts/run_calibration_probe.py` with `--domain <BEC> --per-bec 1000`. The test site
lists are recorded in the runtime probe JSON, not in this note because they are site identifiers.

## 5. Claim boundary

This is a readiness report. It does not calibrate SBPS, does not change a default, and does not
support a yield, AAC, legal, or whole-block claim. The defensible statement is negative: with a
`BAMAX`-only candidate, `SBPSdc` and `SBPSmk` miss the held-out TPH threshold, and `SBPSxc` misses
both.
