# D9.97 candidate calibration policy

Status: **the candidate calibration contract is frozen**
Date: 2026-11-09
Policy: `CALIBRATION-POLICY.md`
Machine-readable: `calibration-policy.json`
Check: `workflows/freshforge/calibration_policy.yaml`

## 1. What changed

The symmetric audit is now a policy, not a standalone experiment.

- Boundary and MacKenzie are the supported symmetric cases.
- Quesnel remains one-sided for its non-PL background.
- Fraser is optional one-sided.
- Kootenay Lake, Haida Gwaii, and Arrow are optional symmetric.
- North Island, Okanagan, Kamloops, Prince George, and Cranbrook use no local
  rule.
- Invermere is explicitly **not frozen**.

## 2. Invermere decision

Invermere is not worth adding:

| Quantity | Value |
| --- | ---: |
| base AUC | 0.704 |
| base log loss | 0.4403 |
| symmetric local log loss | 0.4404 |

The symmetric rule does not improve it. Freezing it would fill a map, not
improve calibration.

## 3. MacKenzie card update

The D9.92 card recorded the one-sided evaluation. The D9.96 audit showed that
MacKenzie needs the two-sided rule:

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.146 | 0.170 | 0.761 | 0.395 |
| Symmetric local | 0.156 | 0.170 | 0.778 | **0.385** |

The card now records `mode: conditional-symmetric` and `recommended: true`, but
deployment offsets are not embedded.

## 4. Minimums

- 20 calibration sites;
- 500 target trees per group;
- 3-point trigger;
- 40 bootstrap splits for evaluation.

## 5. Checked run

```sh
freshforge run workflows/freshforge/calibration_policy.yaml --workdir . \
  --evidence runtime/freshforge-calibration-policy-evidence.json
```

The check verifies:

- the default rule is `none`;
- only Boundary and MacKenzie are supported symmetric cases;
- both cards carry `conditional-symmetric` and `recommended`;
- both audit deltas are negative;
- Invermere has no frozen card;
- the excluded layers are present.

## 6. Claim boundary

Diagnostic candidate calibration policy only. Not a yield, AAC, legal,
whole-block, bundle, or certificate claim. The Quesnel/Okanagan review package is
unchanged.
