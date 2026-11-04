# D8.7 review packet: IDFdk, SBS, and CWH pilots

Status: **unsigned; ready for an independent reviewer.** No human signature is fabricated.
Date: 2026-11-04. Wrapper `0.21.4`, extension `fresh-fvsbc-pyfvs 0.4.1`.
Manifest: `d8-review-manifest.json`.

## Bundles in scope

| Domain | Bundle | Best evidence | Main risk |
| --- | --- | --- | --- |
| IDFdk | `d7-idfdk-binned-bundle.json` | 100 Mile BA -1.90 / TPH -4.3%; Kamloops TPH +14.1%; temporal TPH +14.7% | holdouts close to the TPH limit |
| SBS | `d7-sbs-bundle.json` | 100 Mile BA -1.8% / TPH +3.7%; Prince George BA -7.6% / TPH -10.8% | MORTMULT 2.0; only two spatial holdouts |
| CWH | `d7-cwh-bundle.json` | Arrowsmith, Fraser, Haida Gwaii, and temporal >=2000 all pass | high BAIMULT 7.0; temporal TPH +14.6% |

The manifest records each bundle's SHA-256. A reviewer must verify these before signing.

## SBS second holdout

The existing SBS bundle was run unchanged on the five-per-BEC sample with **Prince George TSA**
held out (19 test intervals / 57 training intervals).

| Model | Fold | n | BA bias | BA % | TPH bias | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | test | 19 | +0.01 | +0.0% | -36.5 | -1.5% |
| SBS pilot | test | 19 | -2.94 | -7.6% | -265.9 | -10.8% |
| baseline | train | 57 | +0.25 | +0.7% | +143.7 | +6.7% |
| SBS pilot | train | 57 | -2.22 | -5.7% | -20.9 | -1.0% |

The pilot passes the same thresholds as the 100 Mile holdout. Prince George's baseline was already
near zero, so this is a robustness test, not a second independent failure fix. Evidence:
`d8-sbs-second-holdout.csv`.

## Review checklist

1. Verify the bundle checksums against `d8-review-manifest.json`.
2. Confirm each bundle's domain and any QMD/BEC boundary.
3. Recompute or inspect the summary CSV behind each row.
4. Confirm the claim boundary says **unsigned pilot**, not certificate.
5. Accept, narrow, or reject each domain separately.

## Current decision

`decision: pending`; `signed_off: false`; `reviewer: null`.

Acceptance of this packet would not make the models certified until a named reviewer signs the
manifest and the bundle `review.signed_off` fields are changed. The CWH high `BAIMULT` and the
IDFdk/SBS TPH margins are the items to challenge first.
