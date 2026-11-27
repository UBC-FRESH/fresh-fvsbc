# Held-out check: MS, ESSF, and PP

Status: **the V3 gains hold out of sample; no bundle is warranted.**

## 1. What was checked

W15/W16/W17 measured their folds on the intervals the rows were fitted from. That is in-sample. This
check splits each zone's sites deterministically (CRC32 of the site id, 20% held out) and runs the
same intervals against two engines: the W14 state (V2 for all three zones) and the current state.

| Zone | Sites | Held-out sites | Held-out intervals |
| --- | ---: | ---: | ---: |
| MS | 307 | 59 | 19 |
| ESSF | 278 | 45 | 42 |
| PP | 10 | 2 | 5 |

The rows were not refitted on train only, so the trees of the held-out settings were part of the fit;
the split removes the stand-level overlap but not that. The numbers below are therefore an upper
bound on the gain, and still worth having.

## 2. Results

| Zone | Build | Test BA bias | Test MAE | Test TPH MAE |
| --- | --- | ---: | ---: | ---: |
| MS | V2 | −9.25 | 9.25 | 327 |
| MS | **V3** | **−2.99** | **3.80** | **258** |
| ESSF | V2 | −8.05 | 8.58 | 592 |
| ESSF | **V3** | **−3.07** | **5.49** | **530** |
| PP | V2 | −3.73 | 3.73 | 187 |
| PP | **V3** | **−2.53** | **2.53** | **114** |

MS improves by 6.3 m²/ha of bias and 5.5 of MAE; ESSF by 5.0 and 3.1; PP by 1.2 and 1.2. The
direction and rough size survive the split, which is what the in-sample folds could not show.

## 3. No bundle

A candidate sweep on the same split (`BAIMULT` 2/4/6, `MORTMULT` 1.5/2.5) moves BA and TPH in
opposite directions:

| Zone | Candidate | Test BA | Test MAE | Test TPH MAE |
| --- | --- | ---: | ---: | ---: |
| MS | base | −2.99 | 3.80 | 258 |
| MS | `BAIMULT 4` | −2.20 | 3.62 | 268 |
| ESSF | base | −3.07 | 5.49 | 530 |
| ESSF | `BAIMULT 4` | −2.07 | 5.01 | 544 |
| PP | base | −2.53 | 2.53 | 114 |
| PP | `BAIMULT 4` | −1.53 | 1.65 | 122 |

Every BA multiplier buys BA bias with a worse tree count: the stand is made to fit the basal area by
growing fewer, larger trees. That is the compensation pattern the project has been trying to leave
behind, and the TPH errors are already the larger of the two. **No bundle for MS, ESSF, or PP**, and
the support reasons stay "unsigned".

## 4. What this changes

- The W15–W17 claims are restated with the held-out numbers in `w15-ms-v3.md`, `w16-essf-v3.md`, and
  `w17-pp-v3.md`: the tables there are in-sample, and the held-out check is the one to quote.
- The remaining −3 m²/ha in each zone is a growth/mortality-shape gap, not something a multiplier
  should paper over.
- A refit on train-only pairs (excluding the held-out sites' trees) is the way to remove the leakage
  in the bound; it is listed as the next honest step if these zones get a bundle review.
