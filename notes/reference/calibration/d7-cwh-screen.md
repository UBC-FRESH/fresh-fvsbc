# D8.2 CWH growth pilot: three spatial holdouts and a temporal holdout

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper `0.21.4`. Public tree detail only.

## Starting point

The first CWH screen (D8.0) showed that missing ingrowth was not the BA problem:

| Model | Fold | BA bias (m2/ha) | BA % | TPH bias | TPH % |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | Arrowsmith test | -11.10 | -17.4% | -134.4 | -9.1% |
| ingrowth | Arrowsmith test | -11.10 | -17.4% | -130.6 | -8.9% |
| ingrowth + MORTMULT 0.25 | Arrowsmith test | -7.00 | -11.0% | -64.9 | -4.4% |

The BA miss was growth/capacity. Applying `BAMAX` or `BAIMULT` only to FD/PL/SE/HW changed almost
nothing because the CWH sample also carries **CW**, **BG**, and **PW**.

## Final candidate

Fixed, not refit per holdout:

- `BAIMULT 7.0` for `FD`, `HW`, `CW`, `BG`, `PW`
- `MORTMULT 0.45` for `FD`, `PL`, `SE`, `HW`, `CW`, `BG`, `PW`, `LW`, `BL`, `AT`, `AC`
- no ingrowth; no `BAMAX` change

The multiplier is high and is the main claim risk. It is inside the bundle bounds (`BAIMULT`
0.25-8, `MORTMULT` 0.25-4), not at a bound, but it is not a routine value. It compensates the
structural coastal-growth underprediction; it is not evidence that the BC growth equations are right.

## Results

Three spatial TSA holdouts plus a temporal split. The temporal split uses every eligible CWH
interval starting in 2000 or later; the bundle parameters are unchanged.

| Holdout | Fold | n | BA bias | BA MAE | BA % | TPH bias | TPH MAE | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | test | 38 | -2.68 | 3.96 | -4.2% | -35.5 | 209.6 | -2.4% |
| Arrowsmith | train | 67 | +1.09 | 5.75 | +1.5% | -41.4 | 382.4 | -2.5% |
| Fraser | test | 10 | -2.46 | 7.49 | -3.8% | -85.0 | 340.1 | -6.6% |
| Fraser | train | 95 | -0.05 | 4.85 | -0.1% | -34.4 | 317.7 | -2.1% |
| Haida Gwaii | test | 15 | -0.00 | 4.65 | -0.0% | +48.7 | 115.0 | +5.1% |
| Haida Gwaii | train | 90 | -0.32 | 5.18 | -0.5% | -53.9 | 354.0 | -3.2% |
| temporal >= 2000 | test | 243 | +0.66 | 9.68 | +0.9% | +209.2 | 454.0 | +14.6% |

All four test folds are inside the BA ±3 m2/ha and TPH 15% thresholds. The temporal TPH fold is close
to the 15% limit. Baselines on the spatial folds were BA **-11.10 / -14.86 / -6.60** and TPH
**-9.1% / -19.2% / -2.6%**; the temporal baseline was BA **-19.84 (-26.5%)** and TPH -7.9%.

## Decision

**CWH pilot bundle issued:** `d7-cwh-bundle.json`. It is unsigned, not a certificate. The high
`BAIMULT` and the temporal TPH margin are explicit claim risks. A reviewer sign-off and an independent
leave-one-BEC holdout remain before any release claim.

The earlier no-bundle screen is retained in the D8.0 Change Log; D8.1/D8.2 supersede its decision.
