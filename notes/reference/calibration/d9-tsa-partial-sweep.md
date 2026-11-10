# D9.106 partial-pooled local calibration sweep

Status: **shrunk local rules evaluated on all 40 TSA labels**
Date: 2026-11-10
Workflow: `workflows/freshforge/partial_sweep.yaml`
Summary: `d9-tsa-partial-sweep.csv`

## 1. Method

The hard local offsets from D9.105 were shrunk by:

```text
shrink = n / (n + 500)
```

where `n` is the calibration group tree count. A group with 500 trees gets half
the raw offset; large groups keep most of it. One-sided and symmetric triggers
are unchanged. Twenty sites are used where available; small TSAs use
`min(20, sites − 1)`.

No card was changed and no rule was applied.

## 2. Headline

| Rule | Improved | Of 40 | Median delta log loss |
| --- | ---: | ---: | ---: |
| Partial one-sided | 16 | 40 | +0.00058 |
| Partial symmetric | 24 | 40 | -0.00193 |

For comparison, the hard rules improved 12/40 and 22/40 with median deltas
+0.00098 and −0.00117.

Partial pooling makes the symmetric rule slightly more often helpful and
reduces several bad small-sample outcomes, but it is not a cure.

## 3. What improved

- Partial symmetric helps **24/40**, versus 22/40 hard.
- It reduces the damage at Kalum, Soo, Bulkley, and Invermere.
- It gives Invermere a small positive correction where the hard rule did not.
- It keeps most large-sample gains, with slightly less gain at Lakes, Boundary,
  and Strathcona.

## 4. What did not improve

- Kingcome (+0.110) and Bulkley (+0.053) remain the worst degradations.
- Soo remains +0.020.
- These are small-site cases with fewer than 20 calibration sites; the reduced
  support is the likely cause.

## 5. 100 Mile and Invermere

**100 Mile**

| Mode | Base log loss | Partial log loss | Delta |
| --- | ---: | ---: | ---: |
| Partial one-sided | 0.3877 | 0.3851 | −0.0026 |
| Partial symmetric | 0.3877 | 0.3715 | **−0.0162** |

**Invermere**

| Mode | Base log loss | Partial log loss | Delta |
| --- | ---: | ---: | ---: |
| Partial one-sided | 0.4403 | 0.4372 | −0.0031 |
| Partial symmetric | 0.4403 | 0.4360 | −0.0043 |

Partial pooling makes Invermere modestly better; it remains a weak card.

## 6. Full comparison

`*` = fewer than 20 target sites.

| TSA | Sites | Base log loss | Hard symmetric Δ | Partial symmetric Δ |
| --- | ---: | ---: | ---: | ---: |
| Lakes TSA | 24 | 0.744 | -0.0903 | -0.0754 |
| Strathcona TSA | 35 | 0.449 | -0.0506 | -0.0485 |
| Quesnel TSA | 182 | 0.439 | -0.0300 | -0.0320 |
| GBR South TSA | 28 | 0.386 | -0.0308 | -0.0298 |
| Fort Nelson TSA | 96 | 0.465 | -0.0302 | -0.0272 |
| Nass TSA* | 6 | 0.343 | -0.0077 | -0.0185 |
| GBR North TSA | 111 | 0.500 | -0.0178 | -0.0171 |
| Revelstoke TSA | 25 | 0.389 | -0.0190 | -0.0170 |
| 100 Mile House TSA | 126 | 0.388 | -0.0165 | -0.0162 |
| Lillooet TSA* | 9 | 0.577 | -0.0186 | -0.0161 |
| Fort St. John TSA | 76 | 0.375 | -0.0169 | -0.0142 |
| Boundary TSA | 216 | 0.399 | -0.0114 | -0.0101 |
| MacKenzie TSA | 236 | 0.394 | -0.0090 | -0.0091 |
| Williams Lake TSA | 208 | 0.439 | -0.0077 | -0.0087 |
| Morice TSA | 77 | 0.386 | -0.0049 | -0.0067 |
| Cascadia TSA | 109 | 0.361 | -0.0065 | -0.0055 |
| Robson Valley TSA | 24 | 0.455 | -0.0023 | -0.0050 |
| Invermere TSA | 98 | 0.440 | +0.0001 | -0.0043 |
| Kootenay Lake TSA | 88 | 0.404 | -0.0032 | -0.0039 |
| Fraser TSA | 219 | 0.327 | -0.0013 | -0.0026 |
| Arrow TSA | 276 | 0.338 | -0.0011 | -0.0013 |
| Haida Gwaii TSA | 532 | 0.348 | -0.0014 | -0.0012 |
| Merritt TSA | 141 | 0.397 | -0.0009 | -0.0011 |
| Prince George TSA | 257 | 0.352 | +0.0006 | -0.0004 |
| Okanagan TSA | 431 | 0.345 | +0.0012 | +0.0001 |
| Kamloops TSA | 328 | 0.387 | +0.0011 | +0.0001 |
| Cranbrook TSA | 163 | 0.349 | +0.0011 | +0.0002 |
| Arrowsmith TSA | 360 | 0.288 | +0.0011 | +0.0004 |
| North Island TSA | 505 | 0.286 | +0.0016 | +0.0008 |
| Dawson Creek TSA | 129 | 0.402 | +0.0024 | +0.0011 |
| Mid Coast TSA* | 3 | 0.415 | +0.0022 | +0.0011 |
| Kispiox TSA | 88 | 0.326 | +0.0024 | +0.0013 |
| Pacific TSA | 162 | 0.267 | +0.0023 | +0.0017 |
| Cassiar TSA | 32 | 0.224 | +0.0025 | +0.0022 |
| Sunshine Coast TSA | 133 | 0.302 | +0.0035 | +0.0027 |
| Golden TSA | 23 | 0.366 | +0.0132 | +0.0104 |
| Kalum TSA | 104 | 0.460 | +0.0212 | +0.0145 |
| Soo TSA* | 18 | 0.585 | +0.0232 | +0.0203 |
| Bulkley TSA* | 16 | 0.366 | +0.0546 | +0.0533 |
| Kingcome TSA* | 17 | 0.294 | +0.1099 | +0.1105 |

## 7. Interpretation

- Partial pooling is a modest net improvement, especially for unstable small
  groups.
- It does not rescue the smallest TSAs; they need domain pooling or more data.
- The next structural lever is regional/BEC-subzone effects for the larger weak
  cases, not a stronger shrinkage constant.
- All results are evidence; reviewers decide what to apply.

## 8. Claim boundary

Calibration evaluation only. No review decision, bundle, certificate, yield,
AAC, legal, or whole-block claim.
