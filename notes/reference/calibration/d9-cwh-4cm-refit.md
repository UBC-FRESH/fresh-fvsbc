# D9.6 CWH 4 cm refit with small-tree growth

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper `0.21.4`; dataset `min_dbh=4.0`.

## Why this exists

D9.5 found that the 4 cm CWH refit with only `BAIMULT`/`MORTMULT` failed Fraser. The 4–9 cm
subplot component is the difference. The next lever is the small-tree diameter-growth model, not a
higher large-tree multiplier.

`REGDMULT` and `REGHMULT` are now supported in the bundle/probe keyword path. `REGDMULT` applies to
the small-tree model; its fields are year/cycle, species, multiplier.

## Candidate

Fixed candidate, not refit per holdout:

- `BAIMULT 7.0` for FD, HW, CW, BG, PW
- `MORTMULT 0.30` for eleven species
- `REGDMULT 2.0` for FD, HW, CW, BG, PW
- no ingrowth

This was selected after the 4 cm grid; it is a pilot, not a pre-registered certificate.

## Results

All folds are PSP 4 cm except the non-PSP external cohort. Baselines are the same folds with no
calibration.

| Holdout | Model | n | BA bias | BA % | BA MAE | TPH bias | TPH % | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | baseline | 38 | -11.10 | -17.4% | 11.10 | -134.4 | -9.1% | 248.7 |
| Arrowsmith | 4 cm pilot | 38 | -1.84 | -2.9% | 3.49 | -18.7 | -1.3% | 208.2 |
| Fraser | baseline | 11 | -18.10 | -27.2% | 18.10 | -400.4 | -22.3% | 463.6 |
| Fraser | 4 cm pilot | 11 | -2.19 | -3.3% | 7.31 | -105.5 | -5.9% | 298.3 |
| Haida Gwaii | baseline | 15 | -6.60 | -9.0% | 8.53 | -10.3 | -1.1% | 80.0 |
| Haida Gwaii | 4 cm pilot | 15 | +0.47 | +0.6% | 4.66 | +73.9 | +7.9% | 106.3 |
| temporal >=2000 | baseline | 252 | -20.16 | -27.4% | 21.24 | -174.3 | -12.3% | 304.3 |
| temporal >=2000 | 4 cm pilot | 252 | +2.47 | +3.4% | 9.76 | +170.9 | +12.1% | 364.5 |
| non-PSP external | baseline | 209 | -10.10 | -19.4% | 10.65 | -184.4 | -8.4% | 301.6 |
| non-PSP external | 4 cm pilot | 209 | -0.66 | -1.3% | 5.45 | +33.5 | +1.5% | 280.6 |

Every fold is inside BA ±3 m2/ha and TPH 15%. The temporal TPH margin is close (12.1%), and the
Fraser TPH MAE remains high. The large `BAIMULT` is still a structural correction; `REGDMULT 2.0`
is what fixes Fraser.

## Decision

**CWH 4 cm pilot bundle issued:** `d7-cwh-4cm-bundle.json`. It is unsigned, not a certificate. It
supersedes the D9.5 “no 4 cm bundle” decision for CWH only. The 2 cm CWH pilot remains a separate
artifact.

Known risks:

- `BAIMULT 7.0` is high; `REGDMULT 2.0` is also a structural multiplier.
- The candidate was selected after seeing spatial folds; non-PSP external is the independent check.
- Only BA/TPH were evaluated; QMD, height, and volume are not yet validated.
- The bundle does not enforce `min_dbh`; the caller must use a 4 cm tree list.
- No reviewer signature.

Evidence: `d7-cwh-4cm-summary.csv`, `d8-review-manifest.json`.
