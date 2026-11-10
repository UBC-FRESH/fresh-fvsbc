# D9.102 review addendum 1

Status: **addendum to the pending Quesnel/Okanagan review**
Date: 2026-11-10
Review package: `d9-candidate-review-package.md`
Manifest: `review-manifest.json`

## 1. Scope unchanged

This addendum does **not** expand the review. The decision remains about:

- Quesnel non-PL background `quesnel-sbsmw-background-v0`;
- Quesnel large-tree MPB and small-tree boundary;
- Okanagan background `okanagan-background-v0`.

No new candidate is added to the review.

## 2. Imputation concern

The package disclosed that `bp.load()` uses full-frame medians for missing
crown/SI/H-D/growth values. D9.101 quantified the effect.

Eleven candidates were rerun with target-excluded medians:

| Quantity | Maximum absolute delta |
| --- | ---: |
| mean prediction | **6.6×10⁻⁹** |
| log loss | **5.1×10⁻⁹** |

No Quesnel or Okanagan card changed. At card precision, the metrics are
identical.

The optional mechanism is available:

- `bp.load(exclude_tsa=...)`;
- `fit_candidate.py --imputation train`.

If the reviewer requires the strict form, the refresh is a bounded rerun, not a
model change.

## 3. Calibration semantics

- Quesnel: one-sided conditional rule; target-site deployment calibration, not a
  held-out base-model improvement.
- Okanagan: no local calibration; the target-excluded layer is used directly.
- The symmetric rule is for Boundary and MacKenzie, which are outside this review.

Policy: `CALIBRATION-POLICY.md`.

## 4. Deployment evidence

These artifacts do not change the review decision:

- `candidate-registry.json`: checksummed set of 12 candidates;
- `score_inventory.py`: raw rows to `eta`;
- `deployment_calibration.py`: supported 20-site offsets from a scored table.

They are included so the reviewer can see that the deployment path is explicit
and separate from the review gate.

## 5. Reviewer action

Use this addendum as evidence for the existing decision. The allowed decisions
are unchanged:

- `pass`;
- `pass with conditions`;
- `fail`.

A pass is not a bundle approval.

## 6. Claim boundary

Diagnostic review evidence only. No yield, AAC, legal, whole-block, bundle, or
certificate claim.
