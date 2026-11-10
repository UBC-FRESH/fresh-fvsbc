# D9.107 BEC ecological stratification audit

Status: **the ecological hierarchy is audited; TSA is no longer the candidate unit**
Date: 2026-11-10
Workflow: `workflows/freshforge/bec_stratification.yaml`
Audit: `d9-bec-stratification.csv`
Units: `d9-bec-strata.csv`

## 1. What was built

BEC codes were parsed into:

- zone, e.g. `CWH`, `ICH`, `SBS`;
- subzone, e.g. `CWHvm`, `ICHmw`, `SBSwk`;
- variant, e.g. `CWHvm1`, `ICHmw2`, `SBSwk1`.

The audit tabulates intervals, events, sites, species groups, and the smallest
group at each level. It then assigns rows to pooled ecological units:

- variant if at least **5,000 intervals and 20 sites**;
- otherwise parent subzone if at least **10,000 intervals and 40 sites**;
- otherwise parent zone;
- any remaining unit below **5,000 intervals** falls back to its zone.

No model was fit.

## 2. Result

| Level | Units | Median intervals | Median sites |
| --- | ---: | ---: | ---: |
| Variant | 56 | 20,326 | 58.5 |
| Subzone | 3 | 6,072 | 19 |
| Zone | 11 | 10,902 | 40 |
| **Total** | **70** | **15,533** | **56** |

Support:

| Measure | Count |
| --- | ---: |
| Units with ≥5,000 intervals | 66 / 70 |
| Units with ≥10,000 intervals | 47 / 70 |
| Units with ≥20 sites | 64 / 70 |
| Units with ≥50 sites | 40 / 70 |
| Units with every species group ≥100 trees | 49 / 70 |
| Units with every species group ≥500 trees | **22 / 70** |

The total-sample-size problem is largely solved at the unit level. The
**species-group** support problem is not: only 22 units have every group above
500 trees.

## 3. Zone view

| Zone | Intervals | Sites | Events | Smallest group |
| --- | ---: | ---: | ---: | ---: |
| ESSF | 31,072 | 173 | 5,468 | 346 |
| ICH | 15,827 | 76 | 2,724 | 1,943 |
| IDF | 15,353 | 86 | 1,916 | 106 |
| CWH | 13,314 | 68 | 2,278 | 5 |
| SBS | 12,584 | 72 | 2,654 | 280 |
| SBPS | 10,902 | 27 | 1,787 | 183 |
| MS | 6,504 | 40 | 1,188 | 9 |
| MH | 3,667 | 12 | 314 | 93 |
| PP | 2,885 | 10 | 278 | 4 |
| BWBS | 1,657 | 9 | 297 | 130 |
| CMA | 579 | 2 | 26 | 111 |

The small zones — CMA, BWBS, PP, MH — are the remaining total-support cases and
should pool upward in the model.

## 4. What this means

- BEC units are ecological and generally large; this is a better hierarchy than
  TSA.
- The unit-level sample size is adequate for most variants.
- Species-group support still needs partial pooling. A single variant can have
  thousands of intervals but a thin PL, SE, or HW group.
- TSA remains useful for reporting and leave-one-TSA-out checks, but not as the
  model unit.
- The next model should use varying intercepts for BEC unit × species group,
  with partial pooling for thin groups and small zones.

## 5. Checked run

```sh
freshforge run workflows/freshforge/bec_stratification.yaml --workdir . \
  --evidence runtime/freshforge-bec-stratification-evidence.json
```

Result: audit success; 70 units; zero diagnostics.

## 6. Claim boundary

Hierarchy audit only. No model fit, review decision, bundle, certificate, yield,
AAC, legal, or whole-block claim.
