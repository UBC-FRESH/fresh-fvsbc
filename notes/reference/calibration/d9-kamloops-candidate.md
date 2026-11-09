# D9.87 Kamloops background candidate

Status: **the southern-interior background layer is frozen; local rule evaluated, not applied**
Date: 2026-11-09
Workflow: `workflows/freshforge/kamloops_background.yaml`
Model: `kamloops-background-v0`

## 1. Why Kamloops

Kamloops is the fourth background candidate and the second southern-interior
test. It has 68,739 tree intervals across 328 sites in IDF/ICH/ESSF, with all
five species groups above the 500-tree support minimum.

PL overpredicts by about 6 points, so this candidate also tests whether the
conditional local rule can correct a real group-level miss.

## 2. Result

Fitted without Kamloops:

| Group | n | Observed | Predicted | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 34,135 | 0.133 | 0.104 | 0.803 | 0.320 |
| PL | 10,784 | 0.242 | 0.302 | 0.751 | 0.515 |
| SE | 5,875 | 0.154 | 0.133 | 0.714 | 0.430 |
| HW | 9,834 | 0.144 | 0.096 | 0.753 | 0.376 |
| OTHER | 8,111 | 0.194 | 0.186 | 0.680 | 0.480 |
| **ALL** | **68,739** | **0.161** | **0.146** | **0.773** | **0.387** |

## 3. Conditional local rule

The 20-site/40-split evaluation:

| Set | Mean predicted | Observed | AUC | Log loss |
| --- | ---: | ---: | ---: | ---: |
| Base | 0.146 | 0.161 | 0.773 | **0.387** |
| Conditional local | 0.142 | 0.161 | 0.771 | 0.389 |

The rule reduces the aggregate overprediction but slightly worsens log loss. It
is evaluated and **not applied**.

## 4. Checked run

```sh
freshforge run workflows/freshforge/kamloops_background.yaml --workdir . \
  --evidence runtime/freshforge-kamloops-evidence.json
```

Result: node `fit_and_freeze_kamloops` success; metrics and model card written;
zero diagnostics.

## 5. Interpretation

- The growth-free background model is usable on a second southern-interior TSA,
  but the Kamloops miss is larger than Quesnel, Okanagan, or North Island.
- PL is the clear group-level problem: 0.302 predicted vs 0.242 observed.
- A single group intercept is not enough to improve the held-out log loss.
- Do not apply the local rule or add a global multiplier.

## 6. Claim boundary

Diagnostic candidate layer only. Not a yield, AAC, legal, whole-block, or
certificate claim.
