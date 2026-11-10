# D9.92 MacKenzie background candidate

Status: **the northern boreal layer is frozen; PL gap documented**
Date: 2026-11-09
Workflow: `workflows/freshforge/mackenzie_background.yaml`
Model: `mackenzie-background-v0`

## 1. Why MacKenzie

MacKenzie is the ninth background candidate and the first northern boreal test.
It has 88,810 tree intervals across 236 sites in SBSmk/SBSwk/BWBSdk/ESSFmv,
distinct from Prince George's SBS and the southern Interior candidates.

FD has only 271 target trees and is omitted; PL, SE, HW, and OTHER are above the
500-tree support minimum.

## 2. Result

Fitted without MacKenzie:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| PL | 38,249 | 0.179 | 0.107 | 0.812 | 0.411 |
| SE | 13,996 | 0.128 | 0.107 | 0.738 | 0.346 |
| HW | 25,444 | 0.182 | 0.180 | 0.813 | 0.377 |
| OTHER | 11,121 | 0.161 | 0.250 | 0.673 | 0.440 |
| **ALL** | **88,810** | **0.170** | **0.146** | **0.761** | **0.395** |

## 3. Symmetric local rule

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.146 | 0.170 | 0.761 | 0.395 |
| Symmetric local | 0.156 | 0.170 | 0.778 | **0.385** |

OTHER overpredicts by about 9 points and PL underpredicts by about 7. The D9.96
audit showed that the two-sided rule is the right correction: log loss improves
by 0.009. The card records the rule and marks it recommended, but deployment
offsets are not embedded.

## 4. Checked run

```sh
freshforge run workflows/freshforge/mackenzie_background.yaml --workdir . \
  --evidence runtime/freshforge-mackenzie-evidence.json
```

Result: node `fit_and_freeze_mackenzie` success; metrics and model card written;
zero diagnostics.

## 5. Interpretation

- MacKenzie adds northern boreal coverage, but its aggregate AUC (0.761) is
  weaker than the best candidates.
- PL is the main failure: 0.107 predicted vs 0.179 observed.
- OTHER overpredicts and is partly corrected by the local rule.
- Do not use a global PL multiplier; the PL gap needs a boreal-specific term.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
