# D9.111 nested support-aware calibration policy

Status: **the first policy that improves 33 of 40 TSA holdouts without severe harm**
Date: 2026-11-10
Workflow: `workflows/freshforge/support_policy.yaml`
Summary: `d9-support-policy.csv`

## 1. Policy

For each TSA, outer site folds measure performance. Inner site folds choose one
of:

- base;
- TSA partial symmetric local;
- BEC-unit partial symmetric local with parent-zone fallback.

The chosen mode is estimated on the outer training sites and scored on the outer
holdout. Outer holdout rows do not choose the mode.

## 2. Headline

| Measure | Value |
| --- | ---: |
| TSA holdouts improved | **33 / 40** |
| TSA holdouts worse | 5 / 40 |
| Median delta log loss | **−0.00574** |
| Mean delta log loss | **−0.01355** |

Fold choices: base 26, TSA partial 49, BEC partial 123.

This is a real improvement over the fixed rules:

- hard TSA symmetric: 22/40 improved, median −0.00117;
- partial TSA symmetric: 24/40, median −0.00193;
- BEC symmetric: 24/40, median −0.00222.

## 3. Largest gains

| TSA | Delta log loss |
| --- | ---: |
| Lakes | −0.0880 |
| Kalum | −0.0589 |
| Quesnel | −0.0471 |
| Strathcona | −0.0465 |
| Fort Nelson | −0.0335 |
| GBR North | −0.0302 |
| GBR South | −0.0293 |
| Williams Lake | −0.0273 |
| Fort St. John | −0.0226 |
| 100 Mile House | −0.0204 |
| Invermere | −0.0169 |

## 4. Remaining degradations

| TSA | Delta log loss | Note |
| --- | ---: | --- |
| Kingcome | +0.0062 | 17 sites |
| Cassiar | +0.0040 | 32 sites, low event rate |
| Golden | +0.0016 | 23 sites |
| Arrowsmith | +0.0013 | small loss |
| Bulkley | +0.0003 | 16 sites |

These are small losses, not the +0.05 to +0.11 failures of the fixed rules.

## 5. Small TSAs

`*` = fewer than 20 target sites.

- Mid Coast, Nass, Bulkley: choose base; no harm.
- Lillooet and Soo: choose TSA partial and improve.
- Kingcome: small degradation (+0.006), still far better than the hard rule
  (+0.11).

The policy is allowed to choose base when support is insufficient.

## 6. Full table

| TSA | Sites | Base log loss | Policy | Delta | Selected mode |
| --- | ---: | ---: | ---: | ---: | --- |
| Lakes TSA | 24 | 0.744 | 0.656 | -0.0880 | bec_partial_symmetric |
| Kalum TSA | 104 | 0.460 | 0.401 | -0.0589 | bec_partial_symmetric |
| Quesnel TSA | 182 | 0.439 | 0.392 | -0.0471 | bec_partial_symmetric |
| Strathcona TSA | 35 | 0.449 | 0.402 | -0.0465 | bec_partial_symmetric |
| Fort Nelson TSA | 96 | 0.465 | 0.431 | -0.0335 | tsa_partial_symmetric |
| GBR North TSA | 111 | 0.500 | 0.470 | -0.0302 | bec_partial_symmetric |
| GBR South TSA | 28 | 0.386 | 0.357 | -0.0293 | bec_partial_symmetric |
| Williams Lake TSA | 208 | 0.439 | 0.412 | -0.0273 | bec_partial_symmetric |
| Fort St. John TSA | 76 | 0.375 | 0.353 | -0.0226 | bec_partial_symmetric |
| 100 Mile House TSA | 126 | 0.388 | 0.367 | -0.0204 | bec_partial_symmetric |
| Boundary TSA | 216 | 0.399 | 0.381 | -0.0174 | tsa_partial_symmetric |
| Invermere TSA | 98 | 0.440 | 0.423 | -0.0169 | bec_partial_symmetric |
| MacKenzie TSA | 236 | 0.394 | 0.377 | -0.0166 | bec_partial_symmetric |
| Kamloops TSA | 328 | 0.387 | 0.371 | -0.0154 | bec_partial_symmetric |
| Morice TSA | 77 | 0.386 | 0.375 | -0.0107 | bec_partial_symmetric |
| Cascadia TSA | 109 | 0.361 | 0.352 | -0.0089 | bec_partial_symmetric |
| Soo TSA* | 18 | 0.585 | 0.576 | -0.0089 | tsa_partial_symmetric |
| Fraser TSA | 219 | 0.327 | 0.319 | -0.0089 | bec_partial_symmetric |
| Revelstoke TSA | 25 | 0.389 | 0.380 | -0.0082 | tsa_partial_symmetric |
| Prince George TSA | 257 | 0.352 | 0.346 | -0.0063 | bec_partial_symmetric |
| Robson Valley TSA | 24 | 0.455 | 0.450 | -0.0051 | bec_partial_symmetric |
| Merritt TSA | 141 | 0.397 | 0.392 | -0.0050 | tsa_partial_symmetric |
| Kootenay Lake TSA | 88 | 0.404 | 0.400 | -0.0042 | tsa_partial_symmetric |
| Haida Gwaii TSA | 532 | 0.348 | 0.345 | -0.0033 | bec_partial_symmetric |
| Arrow TSA | 276 | 0.338 | 0.335 | -0.0029 | bec_partial_symmetric |
| Lillooet TSA* | 9 | 0.577 | 0.575 | -0.0028 | tsa_partial_symmetric |
| Kispiox TSA | 88 | 0.326 | 0.323 | -0.0028 | tsa_partial_symmetric |
| Okanagan TSA | 431 | 0.345 | 0.342 | -0.0026 | bec_partial_symmetric |
| Dawson Creek TSA | 129 | 0.402 | 0.400 | -0.0018 | tsa_partial_symmetric |
| Sunshine Coast TSA | 133 | 0.302 | 0.301 | -0.0010 | bec_partial_symmetric |
| North Island TSA | 505 | 0.286 | 0.285 | -0.0009 | bec_partial_symmetric |
| Pacific TSA | 162 | 0.267 | 0.267 | -0.0005 | bec_partial_symmetric |
| Cranbrook TSA | 163 | 0.349 | 0.349 | -0.0003 | tsa_partial_symmetric |
| Mid Coast TSA* | 3 | 0.415 | 0.415 | +0.0000 | base |
| Nass TSA* | 6 | 0.343 | 0.343 | +0.0000 | base |
| Bulkley TSA* | 16 | 0.366 | 0.366 | +0.0003 | base |
| Arrowsmith TSA | 360 | 0.288 | 0.289 | +0.0013 | bec_partial_symmetric |
| Golden TSA | 23 | 0.366 | 0.368 | +0.0016 | base |
| Cassiar TSA | 32 | 0.224 | 0.228 | +0.0040 | base |
| Kingcome TSA* | 17 | 0.294 | 0.301 | +0.0062 | bec_partial_symmetric |

## 7. Interpretation

- The support-aware nested policy is the first broadly useful calibration layer.
- It fixes the fixed-rule failure mode by refusing local correction when the
  inner folds do not support it.
- It still has small losses, so it is not perfect.
- The policy should be frozen as the next calibration contract, with the 70 BEC
  units and TSA reporting overlay.

## 8. Claim boundary

Calibration evaluation only. No card changed, no bundle, certificate, yield,
AAC, legal, or whole-block claim.
