# D9.109 BEC-unit local calibration

Status: **BEC-unit-by-group calibration evaluated on all 40 TSA holdouts**
Date: 2026-11-10
Workflow: `workflows/freshforge/bec_unit_calibration.yaml`
Summary: `d9-bec-calibration.csv`

## 1. Method

For each TSA holdout:

- fit the current target-excluded base model;
- use the D9.107 BEC units;
- estimate unit-by-group offsets on the calibration sites;
- fall back to parent-zone-by-group offsets when a unit has too little support;
- shrink every offset by `n / (n + 500)`;
- evaluate one-sided and symmetric triggers over 40 site splits.

No card was changed.

## 2. Headline

| Rule | Improved | Of 40 | Median delta log loss |
| --- | ---: | ---: | ---: |
| BEC one-sided | 14 | 40 | +0.00063 |
| BEC symmetric | 24 | 40 | -0.00222 |

For comparison, TSA partial symmetric improved 24/40 with median −0.00193. BEC
units are slightly better on the median but have a different distribution.

## 3. Largest BEC gains

| TSA | Delta log loss |
| --- | ---: |
| Lakes | −0.0784 |
| Quesnel | −0.0547 |
| Strathcona | −0.0491 |
| GBR South | −0.0316 |
| Fort Nelson | −0.0272 |
| GBR North | −0.0248 |
| Nass | −0.0185 |
| Revelstoke | −0.0147 |

## 4. Largest BEC degradations

| TSA | Delta log loss |
| --- | ---: |
| Kingcome | +0.0754 |
| Bulkley | +0.0503 |
| Soo | +0.0282 |
| Golden | +0.0215 |
| Merritt | +0.0057 |

Kingcome and Bulkley still have poor discrimination after correction; their
unit-level offsets are not stable with 16–17 sites.

## 5. 100 Mile and Invermere

| TSA | TSA partial Δ | BEC Δ |
| --- | ---: | ---: |
| 100 Mile House | −0.0162 | −0.0116 |
| Invermere | −0.0043 | −0.0108 |

BEC calibration helps Invermere more than the TSA-local rule, and remains
positive for 100 Mile.

## 6. Full comparison

`*` = fewer than 20 target sites.

| TSA | Sites | Base log loss | TSA partial Δ | BEC symmetric Δ |
| --- | ---: | ---: | ---: | ---: |
| Lakes TSA | 24 | 0.744 | -0.0754 | -0.0784 |
| Quesnel TSA | 182 | 0.439 | -0.0320 | -0.0547 |
| Strathcona TSA | 35 | 0.449 | -0.0485 | -0.0491 |
| GBR South TSA | 28 | 0.386 | -0.0298 | -0.0316 |
| Fort Nelson TSA | 96 | 0.465 | -0.0272 | -0.0272 |
| GBR North TSA | 111 | 0.500 | -0.0171 | -0.0248 |
| Nass TSA* | 6 | 0.343 | -0.0185 | -0.0185 |
| Revelstoke TSA | 25 | 0.389 | -0.0170 | -0.0147 |
| Fort St. John TSA | 76 | 0.375 | -0.0142 | -0.0139 |
| Robson Valley TSA | 24 | 0.455 | -0.0050 | -0.0119 |
| 100 Mile House TSA | 126 | 0.388 | -0.0162 | -0.0116 |
| Invermere TSA | 98 | 0.440 | -0.0043 | -0.0108 |
| MacKenzie TSA | 236 | 0.394 | -0.0091 | -0.0099 |
| Lillooet TSA* | 9 | 0.577 | -0.0161 | -0.0081 |
| Boundary TSA | 216 | 0.399 | -0.0101 | -0.0078 |
| Morice TSA | 77 | 0.386 | -0.0067 | -0.0070 |
| Fraser TSA | 219 | 0.327 | -0.0026 | -0.0055 |
| Cascadia TSA | 109 | 0.361 | -0.0055 | -0.0046 |
| Kootenay Lake TSA | 88 | 0.404 | -0.0039 | -0.0031 |
| Williams Lake TSA | 208 | 0.439 | -0.0087 | -0.0030 |
| Haida Gwaii TSA | 532 | 0.348 | -0.0012 | -0.0014 |
| Prince George TSA | 257 | 0.352 | -0.0004 | -0.0009 |
| Arrow TSA | 276 | 0.338 | -0.0013 | -0.0006 |
| Okanagan TSA | 431 | 0.345 | +0.0001 | -0.0004 |
| Cranbrook TSA | 163 | 0.349 | +0.0002 | +0.0000 |
| Kispiox TSA | 88 | 0.326 | +0.0013 | +0.0003 |
| Arrowsmith TSA | 360 | 0.288 | +0.0004 | +0.0006 |
| Kamloops TSA | 328 | 0.387 | +0.0001 | +0.0008 |
| Mid Coast TSA* | 3 | 0.415 | +0.0011 | +0.0011 |
| Dawson Creek TSA | 129 | 0.402 | +0.0011 | +0.0014 |
| North Island TSA | 505 | 0.286 | +0.0008 | +0.0018 |
| Cassiar TSA | 32 | 0.224 | +0.0022 | +0.0020 |
| Pacific TSA | 162 | 0.267 | +0.0017 | +0.0022 |
| Sunshine Coast TSA | 133 | 0.302 | +0.0027 | +0.0039 |
| Kalum TSA | 104 | 0.460 | +0.0145 | +0.0056 |
| Merritt TSA | 141 | 0.397 | -0.0011 | +0.0057 |
| Golden TSA | 23 | 0.366 | +0.0104 | +0.0215 |
| Soo TSA* | 18 | 0.585 | +0.0203 | +0.0282 |
| Bulkley TSA* | 16 | 0.366 | +0.0533 | +0.0503 |
| Kingcome TSA* | 17 | 0.294 | +0.1105 | +0.0754 |

## 7. Interpretation

- BEC-unit calibration is a viable hierarchy; it is not uniformly better than
  TSA-local correction.
- It substantially reduces some regional misses and helps Invermere.
- Small units can overfit: Kingcome and Bulkley remain bad.
- The next refinement is a unit-support rule stronger than 500 trees, or
  pooling units more aggressively before estimating offsets.
- Reviewers judge which calibration layer is useful.

## 8. Claim boundary

Calibration evaluation only. No review decision, bundle, certificate, yield,
AAC, legal, or whole-block claim.
