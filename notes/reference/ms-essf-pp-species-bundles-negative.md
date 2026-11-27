# MS / ESSF / PP: species-level bundle selection does not pass

Status: **negative result.** No bundle; the V3 support reasons stay "unsigned".

## 1. Setup

Held-out split from `heldout-ms-essf-pp.md` (CRC32 site split, 20%):

| Zone | Test intervals | Train intervals | Test BA bias / MAE | Test TPH bias / MAE |
| --- | ---: | ---: | ---: | ---: |
| MS | 19 | 115 | −2.99 / 3.80 | −46 / 258 |
| ESSF | 42 | 260 | −3.07 / 5.49 | −314 / 530 |
| PP | 5 | 20 | −2.53 / 2.53 | −86 / 114 |

All three under-predict BA and TPH, so the untested direction is **more growth + less mortality**
(the earlier sweep only used `MORTMULT` 1.5/2.5, which *increases* mortality).

## 2. Uniform combos

`BAIMULT` 1.5–3 with `MORTMULT` 0.3–0.7, all species:

| Zone | Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| MS | base | 3.80 | 258.3 | 5.92 | 751.6 |
| MS | 2.0 / 0.5 | 3.34 | 247.4 | 6.13 | 801.0 |
| ESSF | base | 5.49 | 530.2 | 6.31 | 553.4 |
| ESSF | 3.0 / 0.5 | 4.67 | 503.4 | 6.63 | 572.0 |
| PP | base | 2.53 | 114.2 | 2.59 | 54.0 |
| PP | 3.0 / 0.5 | 1.45 | 113.0 | 1.58 | 56.1 |

Held-out improves in every zone; the **train** fold (the selection set) moves the other way.

## 3. Dominant-species targets

Species weighted by live TPH: MS PL 46% / BL 19% / SE 16% / FD 11%; ESSF BL 61% / SE 24% /
PL 9%; PP FD 81% / PY 12%.

| Zone | Candidate | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| MS | base | 3.80 | 258.3 | 5.92 | 751.6 |
| MS | dom 2.0 / 0.5 | 3.29 | 249.3 | 6.13 | 801.7 |
| MS | dom `MORTMULT` 0.5 | 3.62 | 248.9 | 6.24 | 804.6 |
| ESSF | base | 5.49 | 530.2 | 6.31 | 553.4 |
| ESSF | dom 2.0 / 0.5 | 4.96 | 502.9 | 6.56 | 571.5 |
| PP | base | 2.53 | 114.2 | 2.59 | 54.0 |
| PP | dom `BAIMULT` 2 | 2.13 | 115.7 | 2.28 | **52.9** |
| PP | dom 2.0 / 0.5 | 1.73 | 113.6 | 2.08 | 57.0 |

No candidate improves both BA and TPH on **both** folds. PP `BAIMULT 2` is the closest: train
improves on both, held-out BA improves, held-out TPH worsens by 1.5. That is a 5-interval test set,
and shipping it would be selecting on the held-out fold.

## 4. Conclusion

Selecting on train picks the base in all three zones. The held-out improvements are real but come
with train regressions — a split divergence, not a calibration parameter. The remaining −3 m²/ha
is a growth/mortality shape gap; a multiplier would paper over it, which is the pattern this
project has been trying to leave behind.

No bundle for MS, ESSF, or PP.

## Reproduce

- `~/workspace/bwbs-work/probe_{ms,essf,pp}_combo/` (uniform; 938 / 2,114 / 175 rows).
- `~/workspace/bwbs-work/probe_{ms,essf,pp}_dom/` (dominant species; 536 / 1,208 / 100 rows).
- Base rows match `heldout-ms-essf-pp.md`.
