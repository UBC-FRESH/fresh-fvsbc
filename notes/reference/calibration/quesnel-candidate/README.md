# Quesnel non-PL background candidate

Candidate id: `quesnel-sbsmw-background-v0`  
Status: **prototype candidate layer, unsigned, not a bundle**  
Date: 2026-11-08

## Scope

Quesnel TSA non-PL background mortality:

- FD, SE, HW, OTHER;
- growth-free provincial mortality model;
- all periods and post-2000 evaluation;
- PL excluded because it is the MPB seam.

This is a candidate **layer**, not a complete Quesnel calibration and not a
certificate.

## Evidence

| View | n | Observed | Predicted | AUC | Brier | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All periods | 20,047 | 0.163 | 0.153 | 0.792 | 0.114 | 0.408 |
| Post-2000 | 3,918 | 0.220 | 0.191 | 0.713 | 0.153 | 0.486 |

All-period mean is within 1 point. Post-2000 AUC 0.713, mean under by about
3 points; FD/HW drive the bias.

## Separate PL/MPB layer

- Large-tree MPB: 85–91% dead at 0.08× INITMORT in the corrected one-cycle
  Quesnel segment.
- Small-tree residual: 7–15%, entirely 5–15 cm PL.
- Base FVS also leaves those small PL.
- This is a small-tree mortality gap, not MPB severity.

## Decisions

- Freeze this non-PL background as the first candidate layer.
- Keep PL/MPB separate.
- Do not add a global Quesnel or temporal multiplier.
- Do not issue a bundle.
- No new diagnostic seams until the joint Quesnel report exists.

## Known limits

- One target TSA.
- PL/MPB is not integrated into the candidate.
- The MPB extension is an external build patch.
- The 10-year MPB cap and small-tree residual remain.
- No temporal production validation.

## Joint report

See `JOINT-REPORT.md` for the assembled scope, metrics, PL/MPB separation, and decisions.

## Reproduction

- D9.42 provincial model: `../d9-provincial-crown-si.md`
- Quesnel closure: `../d9-quesnel-closure.md`
- Growth ablation: `../d9-growth-ablation.md`
- Quesnel non-PL: `../d9-quesnel-nonpl.md`
- Quesnel temporal: `../d9-quesnel-temporal.md`
- Quesnel MPB segment: `../d9-quesnel-mpb-segment.md`
- Small-tree residual: `../d9-quesnel-small-tree-base.md`
- MPB build patch: `../../../patches/mpb-bc/`

## Claim boundary

This does not support a yield, AAC, legal, or whole-block claim, and it is not
a certificate.
