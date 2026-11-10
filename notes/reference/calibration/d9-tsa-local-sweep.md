# D9.105 local-rule sweep across all TSA labels

Status: **both local rules evaluated on all 40 TSA labels**
Date: 2026-11-10
Workflow: `workflows/freshforge/local_sweep.yaml`
Summary: `d9-tsa-local-sweep.csv`

## 1. What was run

For every TSA label, the target-excluded growth-free fit was scored in three
modes:

- base;
- one-sided 20-site rule;
- symmetric 20-site rule.

40 site splits, group minimum 500 trees. TSAs with fewer than 20 sites used
`min(20, sites − 1)` calibration sites; those rows are marked `*`.

No frozen card was changed and no rule was applied automatically.

## 2. Headline

| Rule | Improved | Of 40 | Median delta log loss |
| --- | ---: | ---: | ---: |
| One-sided | 12 | 40 | +0.0010 |
| Symmetric | 22 | 40 | -0.0012 |

Symmetric helps more often, but it is not universal. One-sided helps only
overpredicted cases; it does nothing for underpredicted TSAs.

## 3. Largest improvements

**Symmetric**

| TSA | Delta log loss |
| --- | ---: |
| Lakes | −0.0903 |
| Strathcona | −0.0506 |
| GBR South | −0.0308 |
| Fort Nelson | −0.0302 |
| Quesnel | −0.0300 |
| Revelstoke | −0.0190 |
| Lillooet | −0.0186 |
| 100 Mile House | −0.0165 |

**One-sided**

| TSA | Delta log loss |
| --- | ---: |
| Quesnel | −0.0303 |
| Lillooet | −0.0128 |
| Nass | −0.0077 |
| Strathcona | −0.0067 |
| Fort Nelson | −0.0054 |
| Morice | −0.0052 |
| GBR South | −0.0041 |
| 100 Mile House | −0.0023 |

## 4. Largest degradations

**Symmetric**

| TSA | Delta log loss |
| --- | ---: |
| Kingcome | +0.1099 |
| Bulkley | +0.0546 |
| Soo | +0.0232 |
| Kalum | +0.0212 |
| Golden | +0.0132 |

**One-sided**

| TSA | Delta log loss |
| --- | ---: |
| Kingcome | +0.1107 |
| Bulkley | +0.0503 |
| Soo | +0.0405 |
| Lakes | +0.0239 |
| Kalum | +0.0139 |

The small-site cases drive several of the degradations; Kingcome, Bulkley, and
Soo have 16–18 sites and reduced calibration support.

## 5. 100 Mile and Invermere

**100 Mile House**

| Mode | Mean | AUC | Log loss | Delta |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.121 | 0.766 | 0.388 | — |
| One-sided | 0.113 | 0.777 | 0.385 | −0.0023 |
| Symmetric | 0.145 | 0.790 | 0.371 | **−0.0165** |

The mortality card responds positively to symmetric local calibration.

**Invermere**

| Mode | Mean | AUC | Log loss | Delta |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.161 | 0.704 | 0.440 | — |
| One-sided | 0.135 | 0.703 | 0.440 | −0.0007 |
| Symmetric | 0.153 | 0.694 | 0.440 | +0.0001 |

Invermere remains weak in every mode.

## 6. Full per-TSA table

`*` = fewer than 20 target sites; calibration support is reduced.

| TSA | Sites | Base log loss | One-sided Δ | Symmetric Δ | Card |
| --- | ---: | ---: | ---: | ---: | --- |
| Lakes TSA | 24 | 0.744 | +0.0239 | -0.0903 | yes |
| Strathcona TSA | 35 | 0.449 | -0.0067 | -0.0506 | yes |
| GBR South TSA | 28 | 0.386 | -0.0041 | -0.0308 | yes |
| Fort Nelson TSA | 96 | 0.465 | -0.0054 | -0.0302 | yes |
| Quesnel TSA | 182 | 0.439 | -0.0303 | -0.0300 | yes |
| Revelstoke TSA | 25 | 0.389 | -0.0041 | -0.0190 | yes |
| Lillooet TSA* | 9 | 0.577 | -0.0128 | -0.0186 | yes |
| GBR North TSA | 111 | 0.500 | +0.0006 | -0.0178 | yes |
| Fort St. John TSA | 76 | 0.375 | +0.0013 | -0.0169 | yes |
| 100 Mile House TSA | 126 | 0.388 | -0.0023 | -0.0165 | yes |
| Boundary TSA | 216 | 0.399 | +0.0000 | -0.0114 | yes |
| MacKenzie TSA | 236 | 0.394 | -0.0008 | -0.0090 | yes |
| Williams Lake TSA | 208 | 0.439 | +0.0009 | -0.0077 | yes |
| Nass TSA* | 6 | 0.343 | -0.0077 | -0.0077 | yes |
| Cascadia TSA | 109 | 0.361 | +0.0011 | -0.0065 | yes |
| Morice TSA | 77 | 0.386 | -0.0052 | -0.0049 | yes |
| Kootenay Lake TSA | 88 | 0.404 | +0.0007 | -0.0032 | yes |
| Robson Valley TSA | 24 | 0.455 | +0.0007 | -0.0023 | yes |
| Haida Gwaii TSA | 532 | 0.348 | +0.0005 | -0.0014 | yes |
| Fraser TSA | 219 | 0.327 | -0.0007 | -0.0013 | yes |
| Arrow TSA | 276 | 0.338 | +0.0002 | -0.0011 | yes |
| Merritt TSA | 141 | 0.397 | +0.0020 | -0.0009 | yes |
| Invermere TSA | 98 | 0.440 | -0.0007 | +0.0001 | yes |
| Prince George TSA | 257 | 0.352 | +0.0025 | +0.0006 | yes |
| Cranbrook TSA | 163 | 0.349 | +0.0019 | +0.0011 | yes |
| Arrowsmith TSA | 360 | 0.288 | +0.0009 | +0.0011 | yes |
| Kamloops TSA | 328 | 0.387 | +0.0021 | +0.0011 | yes |
| Okanagan TSA | 431 | 0.345 | +0.0013 | +0.0012 | yes |
| North Island TSA | 505 | 0.286 | +0.0014 | +0.0016 | yes |
| Mid Coast TSA* | 3 | 0.415 | +0.0024 | +0.0022 | yes |
| Pacific TSA | 162 | 0.267 | +0.0023 | +0.0023 | yes |
| Dawson Creek TSA | 129 | 0.402 | +0.0030 | +0.0024 | yes |
| Kispiox TSA | 88 | 0.326 | +0.0025 | +0.0024 | yes |
| Cassiar TSA | 32 | 0.224 | +0.0019 | +0.0025 | yes |
| Sunshine Coast TSA | 133 | 0.302 | +0.0030 | +0.0035 | yes |
| Golden TSA | 23 | 0.366 | +0.0094 | +0.0132 | yes |
| Kalum TSA | 104 | 0.460 | +0.0139 | +0.0212 | yes |
| Soo TSA* | 18 | 0.585 | +0.0405 | +0.0232 | yes |
| Bulkley TSA* | 16 | 0.366 | +0.0503 | +0.0546 | yes |
| Kingcome TSA* | 17 | 0.294 | +0.1107 | +0.1099 | yes |

## 7. Interpretation

- Local correction is worth attempting everywhere; it is not worth applying
  everywhere.
- Symmetric improves 22 of 40; one-sided improves 12 of 40.
- Small-site results are unstable and should be read with the site count.
- No rule was embedded in a frozen card.
- Reviewers decide which corrections are useful or usable.

## 8. Claim boundary

Calibration evaluation only. No review decision, bundle, certificate, yield,
AAC, legal, or whole-block claim.
