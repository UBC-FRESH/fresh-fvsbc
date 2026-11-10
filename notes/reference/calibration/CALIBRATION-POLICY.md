# D9.97 candidate calibration policy

Status: **frozen deployment calibration policy**
Policy id: `d9-candidate-calibration-v0`
Machine-readable: `calibration-policy.json`

## 1. Purpose

This policy decides when a target-excluded candidate may use a local
calibration intercept. It is a deployment contract for candidate layers, not a
bundle, certificate, or production approval.

## 2. Rules

### Base layer

- Fit without the target TSA.
- Keep the base card as the reference layer.
- Never tune the base model on target metrics.

### One-sided rule

Use only when a supported group **overpredicts** by more than 3 points:

- at least 500 target trees in the group;
- at least 20 target calibration sites;
- estimate one group intercept;
- record the offset, site count, and data checksum.

### Symmetric rule

Use only where the base model materially **underpredicts** and the audit shows a
log-loss improvement:

- at least 500 target trees in the group;
- at least 20 target calibration sites;
- estimate one group intercept whether the group is over- or underpredicted by
  more than 3 points;
- record the offset, site count, and data checksum.

### No global rule

No global multiplier, provincial screen, or test-set tuning is allowed.

## 3. Supported symmetric cases

| Candidate | Base log loss | Symmetric | Delta |
| --- | ---: | ---: | ---: |
| Boundary | 0.3989 | 0.3874 | **−0.0114** |
| MacKenzie | 0.3945 | 0.3854 | **−0.0091** |

Evidence: `d9-symmetric-audit.csv`.

## 4. Other candidate rules

| Candidate | Rule | Note |
| --- | --- | --- |
| Quesnel non-PL | one-sided | review pending; MPB and small-tree boundary separate |
| Okanagan | none | local rule not applied |
| North Island | none | symmetric makes log loss worse |
| Kamloops | none | one-sided and symmetric do not improve |
| Prince George | none | symmetric makes log loss worse |
| Cranbrook | none | symmetric makes log loss worse |
| Arrow | optional symmetric | marginal improvement (−0.0011) |
| Fraser | optional one-sided | marginal improvement (−0.0012) |
| Haida Gwaii | optional symmetric | marginal improvement (−0.0014) |
| Kootenay Lake | optional symmetric | marginal improvement (−0.0032) |

Optional means: use only with 20 sites, record the offsets, and do not silently
apply it to the frozen card.

## 5. Evidence-only cards

D9.104 freezes base cards for the remaining TSA labels, including **Invermere**
and **100 Mile House**. These are evidence-only:

- no local calibration is applied;
- Invermere's weak base metrics remain visible (AUC 0.704, log loss 0.440);
- the 100 Mile exclusion applies to the SBPS ingrowth candidate, not the
  mortality card.

The cards are for the full calibration-quality picture. They are not supported
local-calibration cases.

## 6. Excluded

100 Mile (retracted), IDFdk (no bundle), ICHmw2 (unsigned), CWH volume question,
SBPSmk mature, new TSAs, and global screens.

## 7. Deployment record

A calibrated deployment records:

- candidate model id and card checksum;
- rule (`one_sided` or `symmetric`);
- target TSA and calibration-site count;
- group offsets;
- data checksum;
- no site-level rows in tracked files.

## 8. Claim boundary

Diagnostic candidate calibration policy only. Not a yield, AAC, legal,
whole-block, bundle, or certificate claim.
