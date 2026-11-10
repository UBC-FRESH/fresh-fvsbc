# Reviewer instructions: Quesnel and Okanagan candidates

Version: `d9-candidate-review-v0`
Package: `d9-candidate-review-package.md`
Manifest: `review-manifest.json`

## 1. Role and time box

You are the independent reviewer. You are not the author of these candidates.
Spend one bounded session, about two to four hours, and report what the evidence
supports. Do not reopen the modelling programme.

You are reviewing the frozen cards, workflows, and claims. You are not approving
a bundle, a certificate, or production use.

## 2. Before you start

1. Check out the review pull request commit.
2. Run `sha256sum -c`-style verification against `review-manifest.json`, or
   recompute the listed hashes with `sha256sum <path>`.
3. Read `d9-candidate-review-package.md`, `d9-review-addendum-1.md`, and the four candidate artifacts:
   - `quesnel-candidate/model-card.json`
   - `quesnel-candidate/JOINT-REPORT.md`
   - `quesnel-candidate/small-tree-boundary.json`
   - `okanagan-candidate/model-card.json`

The raw PSP and site-level inputs are external and are not in this repository.
If you do not have them, audit the code, cards, and aggregate tables; state that
you did not rerun the fits.

## 3. What to check

### 3.1 Holdout integrity

- Confirm the target TSA is removed from the training frame before fitting.
- Check every preprocessing decision that touches the target: imputation
  medians, scaling, zone levels, feature construction, and calibration.
- The known concern is `bp.load()`: it fills missing crown, SI, H-D, and growth
  values with medians computed on the full frame before the target split.
  Decide whether this is a **blocker**, a **major** finding, or acceptable with a
  stated limitation. If it is a blocker, say exactly which values must be
  train-only.

### 3.2 Metrics and coefficients

- Check that the model-card metrics match `metrics.csv` and the workflow outputs.
- Spot-check one species group: feature names, scaler length, coefficient
  length, and a prediction path.
- Confirm the Okanagan card used a target-excluded fit and the Quesnel card did
  not silently reuse the Okanagan fit.
- Do not tune the model on the target to make a metric look better.

### 3.3 Calibration semantics

- The Quesnel conditional rule estimates one species-group intercept on target
  sites.
- Confirm the card and report call this **deployment-time calibration**, not a
  held-out result.
- Confirm Okanagan explicitly does **not** apply local calibration.

### 3.4 MPB segment

- Confirm the workflow uses an external case file, so the tracked tree contains
  no site key.
- Confirm the interval is split so the MPB cycle does not exceed ten years.
- Confirm the `INITMORT` vector is local and scaled; there is no provincial
  multiplier.
- Confirm the aggregate result is presented as a diagnostic, not a yield claim.

### 3.5 Small-tree boundary

- Read `quesnel-candidate/small-tree-boundary.json`.
- Confirm the node fails if live PL above 15 cm exceeds 1.0/ac or maximum live
  DBH exceeds 20 cm.
- Confirm the panel table is aggregate and has no site keys.

### 3.6 Claims

- Confirm every artifact says diagnostic candidate, not bundle or certificate.
- Confirm no artifact claims yield, AAC, legal, or whole-block validity.
- Confirm excluded work (100 Mile, IDFdk, ICHmw2, CWH, SBPSmk) stays excluded.

## 4. Severity

Use these labels:

- **blocker** — a claim is unsupported or the target leaked; do not pass.
- **major** — a material error or missing evidence; pass only with a named fix.
- **minor** — clarity, reproducibility, or documentation issue.

For every finding, give the exact path and line, the evidence command, and the
smallest fix. Do not edit the candidate artifacts in place.

## 5. Decision

Return exactly one:

- **pass** — the package supports the stated candidate claims.
- **pass with conditions** — the claims hold only after the named corrections.
- **fail** — the evidence does not support the claims.

A pass is a gate to the next decision, not a bundle approval.

## 6. Report format

Write `notes/reports/d9-candidate-review-<reviewer>.md` with:

```text
Reviewer:
Commit:
Decision:
Scope reviewed:
Not reviewed:
Findings:
  - severity:
    path:
    evidence:
    fix:
Known concern disposition:
Claim check:
```

Also post a short summary on the review issue. If you cannot access the external
data, say so in `Not reviewed`; do not infer a pass from unavailable evidence.

## 7. Out of scope

Do not add a TSA, open a global screen, tune a multiplier, rerun a test-set
search, or approve a bundle. Those are separate tasks.
