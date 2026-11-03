# D8.1 CWH growth pilot: the BA plane passes with a high growth multiplier

Build: `fresh-fvsbc-pyfvs 0.4.1`; wrapper `0.21.4`. Public tree detail only.

## Starting point

The first CWH screen (D8.0) showed that missing ingrowth was not the BA problem. The wrapper
support was released, but CWH had no bundle:

| Model | Fold | BA bias (m2/ha) | BA % | TPH bias | TPH % |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | Arrowsmith test | -11.10 | -17.4% | -134.4 | -9.1% |
| ingrowth | Arrowsmith test | -11.10 | -17.4% | -130.6 | -8.9% |
| ingrowth + MORTMULT 0.25 | Arrowsmith test | -7.00 | -11.0% | -64.9 | -4.4% |

The BA miss was growth/capacity. `BAMAX` and `BAIMULT` applied only to FD/PL/SE/HW changed almost
nothing; the CWH sample also carries **CW**, **BG**, and **PW**, and the remaining species matter.

## Final candidate

Fixed, not refit per holdout:

- `BAIMULT 6.0` for `FD`, `HW`, `CW`, `BG`, `PW`
- `MORTMULT 0.3` for `FD`, `PL`, `SE`, `HW`, `CW`, `BG`, `PW`, `LW`, `BL`, `AT`, `AC`
- no ingrowth; no `BAMAX` change

The candidate is a **growth correction**: the five-per-BEC sample with all species in the multiplier
still leaves the BA plane flat; adding the CWH species closes it. The multiplier is high and is the
main claim risk. It is inside the bundle bounds (`BAIMULT` 0.25-8, `MORTMULT` 0.25-4), not at a
bound, but it is not a routine value.

## Results

Three TSA holdouts, same fixed bundle. Training intervals are the remaining five-per-BEC sample.

| Holdout | Fold | n | BA bias | BA MAE | BA % | TPH bias | TPH MAE | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | test | 38 | -2.63 | 3.88 | -4.1% | -20.3 | 207.8 | -1.4% |
| Arrowsmith | train | 67 | +0.76 | 5.74 | +1.0% | -2.1 | 406.7 | -0.1% |
| Fraser | test | 10 | -2.66 | 6.89 | -4.1% | -55.3 | 336.6 | -4.3% |
| Fraser | train | 95 | -0.24 | 4.87 | -0.3% | -3.7 | 334.5 | -0.2% |
| Haida Gwaii | test | 15 | -0.00 | 4.84 | -0.0% | +57.0 | 116.4 | +6.0% |
| Haida Gwaii | train | 90 | -0.55 | 5.10 | -0.8% | -19.6 | 371.1 | -1.2% |

All three test folds are inside the BA ±3 m2/ha and TPH 15% thresholds. Baselines on the same
folds were BA **-11.10 / -14.86 / -6.60** and TPH **-9.1% / -19.2% / -2.6%**.

## Decision

**CWH pilot bundle issued:** `d7-cwh-bundle.json`. It is unsigned, not a certificate, and the high
`BAIMULT` is explicitly part of the claim. The next step is an independent temporal or
leave-one-BEC holdout and reviewer sign-off; a CWH release claim waits for that.

The earlier no-bundle screen is retained in the D8.0 Change Log; this D8.1 pilot supersedes its decision.
