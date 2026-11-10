# D9.104 cards for the remaining TSA labels

Status: **40 TSA labels now have base cards**
Date: 2026-11-10
Workflow: `workflows/freshforge/all_tsa_cards.yaml`
Registry: `candidate-registry.json`

## 1. What was added

The current growth-free recipe was run for the 28 TSA labels that had no card:

- no local calibration;
- zero target-support minimum, so small groups remain visible;
- one `metrics.csv` and `model-card.json` per label;
- registry rebuilt to 40 candidates.

The existing 12 cards were not changed.

## 2. New cards

Sorted by base log loss.

| TSA | Model id | n | Observed | Predicted | AUC | Log loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cassiar TSA | `cassiar-background-v0` | 2,876 | 0.071 | 0.051 | 0.728 | 0.224 |
| Pacific TSA | `pacific-background-v0` | 49,638 | 0.125 | 0.132 | 0.874 | 0.267 |
| Arrowsmith TSA | `arrowsmith-background-v0` | 111,381 | 0.112 | 0.095 | 0.817 | 0.288 |
| Kingcome TSA | `kingcome-background-v0` | 6,467 | 0.108 | 0.095 | 0.791 | 0.294 |
| Sunshine Coast TSA | `sunshine-coast-background-v0` | 58,458 | 0.132 | 0.131 | 0.830 | 0.302 |
| Kispiox TSA | `kispiox-background-v0` | 34,177 | 0.162 | 0.173 | 0.868 | 0.326 |
| Nass TSA | `nass-background-v0` | 969 | 0.127 | 0.174 | 0.780 | 0.343 |
| Cascadia TSA | `cascadia-background-v0` | 51,582 | 0.139 | 0.105 | 0.746 | 0.361 |
| Bulkley TSA | `bulkley-background-v0` | 2,116 | 0.105 | 0.091 | 0.560 | 0.366 |
| Golden TSA | `golden-background-v0` | 3,028 | 0.130 | 0.139 | 0.713 | 0.366 |
| Fort St. John TSA | `fort-st-john-background-v0` | 23,001 | 0.156 | 0.122 | 0.771 | 0.375 |
| Morice TSA | `morice-background-v0` | 19,971 | 0.138 | 0.180 | 0.658 | 0.386 |
| GBR South TSA | `gbr-south-background-v0` | 40,730 | 0.155 | 0.081 | 0.811 | 0.386 |
| **100 Mile House TSA** | `100-mile-house-background-v0` | 32,394 | 0.162 | 0.121 | 0.766 | 0.388 |
| Revelstoke TSA | `revelstoke-background-v0` | 2,701 | 0.160 | 0.095 | 0.780 | 0.389 |
| Merritt TSA | `merritt-background-v0` | 49,728 | 0.188 | 0.161 | 0.814 | 0.397 |
| Dawson Creek TSA | `dawson-creek-background-v0` | 31,433 | 0.190 | 0.190 | 0.790 | 0.402 |
| Mid Coast TSA | `mid-coast-background-v0` | 1,437 | 0.156 | 0.126 | 0.684 | 0.415 |
| Williams Lake TSA | `williams-lake-background-v0` | 38,812 | 0.172 | 0.118 | 0.721 | 0.439 |
| **Invermere TSA** | `invermere-background-v0` | 25,615 | 0.164 | 0.161 | 0.704 | 0.440 |
| Strathcona TSA | `strathcona-background-v0` | 13,042 | 0.187 | 0.086 | 0.800 | 0.449 |
| Robson Valley TSA | `robson-valley-background-v0` | 4,199 | 0.199 | 0.239 | 0.746 | 0.455 |
| Kalum TSA | `kalum-background-v0` | 12,468 | 0.189 | 0.171 | 0.792 | 0.460 |
| Fort Nelson TSA | `fort-nelson-background-v0` | 23,055 | 0.207 | 0.205 | 0.735 | 0.465 |
| GBR North TSA | `gbr-north-background-v0` | 29,868 | 0.231 | 0.149 | 0.745 | 0.500 |
| Lillooet TSA | `lillooet-background-v0` | 1,997 | 0.260 | 0.248 | 0.592 | 0.577 |
| Soo TSA | `soo-background-v0` | 3,283 | 0.246 | 0.172 | 0.621 | 0.585 |
| Lakes TSA | `lakes-background-v0` | 3,807 | 0.371 | 0.186 | 0.602 | 0.744 |

## 3. 100 Mile and Invermere

**100 Mile House**

- mortality card: n=32,394, AUC 0.766, log loss 0.388;
- the earlier retraction was the SBPS ingrowth candidate, not mortality;
- the card uses no local calibration.

**Invermere**

- base card: AUC 0.704, log loss 0.440;
- it remains weak and no local rule is applied;
- the card is evidence, not a supported calibration case.

## 4. Policy change

`calibration-policy.json` now records Invermere and 100 Mile as
`evidence_only`:

- base cards exist;
- no local calibration;
- the 100 Mile exclusion applies to the SBPS ingrowth candidate only.

Boundary and MacKenzie remain the supported symmetric cases.

## 5. Checked run

```sh
freshforge run workflows/freshforge/all_tsa_cards.yaml --workdir . \
  --evidence runtime/freshforge-all-tsa-cards-evidence.json
```

- `freeze_missing`: success
- `rebuild_registry`: success
- registry: 40 candidates
- diagnostics: 0

## 6. Claim boundary

Evidence-only cards. No review decision, bundle, certificate, yield, AAC, legal,
or whole-block claim. Reviewers judge usefulness and usability.
