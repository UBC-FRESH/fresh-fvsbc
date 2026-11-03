# D7.8 CWH screening: the wrapper opens, the BA plane does not

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper source at `feature/cwh-five-zone` (five-zone tokens
added). Public tree detail only.

## Question

The all-zone ingrowth screen improved CWH TPH from -151 to -16 but left BA at -16.3. Can a CWH
domain model pass the same pre-registered BA and TPH biases as IDFdk and SBS?

## Design

- 21 CWH labels, 7,124 intervals. A five-per-BEC sample gives 105 intervals; the Arrowsmith TSA
  is held out (38 test intervals / 18 sites, 67 training intervals).
- Training rates use the 5,393 eligible CWH intervals (BA0 >= 15 m2/ha, QMD >= 6 cm, dead BA <=
  40% of BA0, new trees <= 50% of TPH0), a median annual rate, and a 5 TPH/year cap. The cap is
  needed because CWHws2 contains regeneration/partial-cut intervals with 75-330 new HW/ha/year.
- The ingrowth-only bundle has no capacity parameter. Candidate `MORTMULT` values test whether the
  BA miss is a mortality problem.

## Result

| Model | Fold | BA bias (m2/ha) | BA MAE | BA % | TPH bias | TPH MAE | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | train | -13.84 | 14.35 | -19.0% | -278.9 | 354.4 | -17.0% |
| baseline | test | -11.10 | 11.10 | -17.4% | -134.4 | 248.7 | -9.1% |
| ingrowth | train | +14.12 | 41.23 | +19.4% | -272.4 | 350.1 | -16.6% |
| ingrowth | test | -11.10 | 11.10 | -17.4% | -130.6 | 244.9 | -8.9% |
| ingrowth + MORTMULT 0.25 | train | -6.91 | 8.85 | -9.5% | -61.8 | 386.4 | -3.8% |
| ingrowth + MORTMULT 0.25 | test | -7.00 | 7.10 | -11.0% | -64.9 | 225.9 | -4.4% |

`BAMAX` 120/150 and `BAIMULT` 1.3/1.5 did not move the CWH BA test residual; `MORTMULT 0.25`
improves both BA and TPH but still misses BA by 7.0 m2/ha (11%). The training BA sign flips with
the capped ingrowth model, so the rate surface is not stable enough to promote.

## Decision

**No CWH bundle.** The BA miss is a growth/capacity bias, not missing recruitment; the ingrowth
model cannot supply the 11 m2/ha. `MORTMULT 0.25` is outside the ordinary calibration range and
still fails, so it is not a candidate. CWH remains a screening result until a BA-capacity model is
fitted per BEC with an independent holdout.

The D8 wrapper change is independent: CWH, CDF, BWBS, CMA, and MH now parse in the wrapper. That
makes a five-zone run possible; it does not make CWH calibrated.

Evidence: `d7-cwh-summary.csv`.
