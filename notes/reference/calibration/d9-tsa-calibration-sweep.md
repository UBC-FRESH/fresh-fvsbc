# D9.103 full TSA calibration sweep

Status: **all 40 TSA labels have a current-recipe calibration result**
Date: 2026-11-10
Workflow: `workflows/freshforge/tsa_sweep.yaml`
Summary: `d9-tsa-calibration-sweep.csv`

## 1. What was run

The current target-excluded growth-free recipe was run on every TSA label in the
usable PSP table. No local calibration was applied. The sweep records base
aggregate and per-group metrics, including small groups.

- **40** TSA labels
- **212** aggregate/group rows
- **12** already have frozen cards
- **28** are sweep-only in this pass

This is evidence for reviewers. It does not make a review decision.

## 2. Summary

| Measure | Value |
| --- | ---: |
| Median AUC | 0.772 |
| AUC range | 0.560–0.874 |
| TSA labels with AUC ≥ 0.75 | 24 / 40 |
| TSA labels with AUC ≥ 0.80 | 10 / 40 |
| Median log loss | 0.386 |
| Log-loss range | 0.224–0.744 |
| TSA labels with log loss ≤ 0.35 | 13 / 40 |

Small TSAs have wide uncertainty; the table is not a ranking.

## 3. Full table

Sorted by aggregate log loss. `Card` means a frozen candidate card exists; it
does not mean reviewed or bundled.

| TSA | n | Observed | Predicted | AUC | Log loss | Card |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Cassiar TSA | 2,876 | 0.071 | 0.051 | 0.728 | 0.224 | no |
| Pacific TSA | 49,638 | 0.125 | 0.132 | 0.874 | 0.267 | no |
| North Island TSA | 156,358 | 0.130 | 0.120 | 0.852 | 0.286 | yes |
| Arrowsmith TSA | 111,381 | 0.112 | 0.095 | 0.817 | 0.288 | no |
| Kingcome TSA | 6,467 | 0.108 | 0.095 | 0.791 | 0.294 | no |
| Sunshine Coast TSA | 58,458 | 0.132 | 0.131 | 0.830 | 0.302 | no |
| Kispiox TSA | 34,177 | 0.162 | 0.173 | 0.868 | 0.326 | no |
| Fraser TSA | 87,931 | 0.137 | 0.150 | 0.801 | 0.327 | yes |
| Arrow TSA | 130,716 | 0.125 | 0.101 | 0.737 | 0.338 | yes |
| Nass TSA | 969 | 0.127 | 0.174 | 0.780 | 0.343 | no |
| Okanagan TSA | 134,149 | 0.147 | 0.144 | 0.792 | 0.345 | yes |
| Haida Gwaii TSA | 110,904 | 0.142 | 0.110 | 0.788 | 0.348 | yes |
| Cranbrook TSA | 52,683 | 0.150 | 0.137 | 0.812 | 0.349 | yes |
| Prince George TSA | 93,137 | 0.139 | 0.115 | 0.764 | 0.352 | yes |
| Cascadia TSA | 51,582 | 0.139 | 0.105 | 0.746 | 0.361 | no |
| Bulkley TSA | 2,116 | 0.105 | 0.091 | 0.560 | 0.366 | no |
| Golden TSA | 3,028 | 0.130 | 0.139 | 0.713 | 0.366 | no |
| Fort St. John TSA | 23,001 | 0.156 | 0.122 | 0.771 | 0.375 | no |
| Morice TSA | 19,971 | 0.138 | 0.180 | 0.658 | 0.386 | no |
| GBR South TSA | 40,730 | 0.155 | 0.081 | 0.811 | 0.386 | no |
| Kamloops TSA | 68,739 | 0.161 | 0.146 | 0.773 | 0.387 | yes |
| **100 Mile House TSA** | 32,394 | 0.162 | 0.121 | 0.766 | 0.388 | no |
| Revelstoke TSA | 2,701 | 0.160 | 0.095 | 0.780 | 0.389 | no |
| MacKenzie TSA | 89,081 | 0.169 | 0.146 | 0.762 | 0.394 | yes |
| Merritt TSA | 49,728 | 0.188 | 0.161 | 0.814 | 0.397 | no |
| Boundary TSA | 63,017 | 0.169 | 0.118 | 0.776 | 0.399 | yes |
| Dawson Creek TSA | 31,433 | 0.190 | 0.190 | 0.790 | 0.402 | no |
| Kootenay Lake TSA | 24,376 | 0.184 | 0.161 | 0.775 | 0.404 | yes |
| Mid Coast TSA | 1,437 | 0.156 | 0.126 | 0.684 | 0.415 | no |
| Quesnel TSA | 70,989 | 0.161 | 0.247 | 0.704 | 0.439 | yes |
| Williams Lake TSA | 38,812 | 0.172 | 0.118 | 0.721 | 0.439 | no |
| Invermere TSA | 25,615 | 0.164 | 0.161 | 0.704 | 0.440 | no |
| Strathcona TSA | 13,042 | 0.187 | 0.086 | 0.800 | 0.449 | no |
| Robson Valley TSA | 4,199 | 0.199 | 0.239 | 0.746 | 0.455 | no |
| Kalum TSA | 12,468 | 0.189 | 0.171 | 0.792 | 0.460 | no |
| Fort Nelson TSA | 23,055 | 0.207 | 0.205 | 0.735 | 0.465 | no |
| GBR North TSA | 29,868 | 0.231 | 0.149 | 0.745 | 0.500 | no |
| Lillooet TSA | 1,997 | 0.260 | 0.248 | 0.592 | 0.577 | no |
| Soo TSA | 3,283 | 0.246 | 0.172 | 0.621 | 0.585 | no |
| Lakes TSA | 3,807 | 0.371 | 0.186 | 0.602 | 0.744 | no |

## 4. Hundred Mile House

The mortality recipe produces a usable diagnostic signal:

| Quantity | Value |
| --- | ---: |
| n | 32,394 |
| observed | 0.162 |
| predicted | 0.121 |
| AUC | 0.766 |
| log loss | 0.388 |

The earlier 100 Mile retraction was an **SBPS ingrowth** candidate result, not a
mortality calibration failure. The current mortality sweep includes 100 Mile and
does not need the ingrowth candidate to proceed.

## 5. Quesnel note

The sweep's Quesnel all-group row (n=70,989, AUC 0.704, log loss 0.439) is not the
frozen Quesnel non-PL candidate (AUC 0.792, log loss 0.408). The all-group row
includes PL, which the frozen candidate excludes.

## 6. Strong and weak ends

Strongest aggregate rows: Cassiar, Pacific, North Island, Arrowsmith, Kingcome,
Sunshine Coast, Kispiox, Fraser.

Weakest aggregate rows: Lakes, Soo, Lillooet, GBR North, Fort Nelson, Kalum,
Robson Valley, Strathcona, Invermere, Williams Lake.

These are descriptive, not blockers. Reviewers decide usefulness.

## 7. Claim boundary

Calibration-quality evidence only. Not a bundle, certificate, yield, AAC, legal,
or whole-block claim.
