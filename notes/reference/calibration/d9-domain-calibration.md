# D9.110 train-TSA BEC-domain calibration

Status: **domain offsets learned from training TSAs are effectively a no-op**
Date: 2026-11-10
Workflow: `workflows/freshforge/domain_calibration.yaml`
Summary: `d9-domain-calibration.csv`

## 1. What was tried

For each TSA holdout:

- fit the current target-excluded base;
- estimate one-sided and symmetric offsets from the **remaining TSAs**;
- hierarchy: BEC unit by group → parent zone by group → global group;
- shrink by `n / (n + 500)`;
- apply the highest supported domain offset to the target.

No target calibration sites were used.

## 2. Result

| Rule | Improved | Of 40 | Median delta log loss |
| --- | ---: | ---: | ---: |
| Domain one-sided | 4 | 40 | 0.00000 |
| Domain symmetric | 23 | 40 | **−0.000006** |

Most TSAs are unchanged. The largest gain is 100 Mile at −0.015; the rest are
thousandths or less.

## 3. Why

The base model already contains BEC subzone effects. Domain offsets estimated
from the remaining TSAs are therefore close to zero.

For small TSAs with unique BEC units, there is also little training data in the
same unit, so the unit/zone/global fallback has nothing target-specific to use.

## 4. What this means

- Training-domain offsets do not solve the small-TSA problem.
- The remaining error is target-specific, not a missing BEC-domain prior.
- Target-site calibration is the only lever, but it is unreliable below roughly
  20 sites.
- This is a data limitation, not a missing global multiplier.

## 5. Practical policy implication

- Use the base/domain model when a TSA has too few calibration sites.
- Use target-site local correction only where site support is sufficient.
- Report uncertainty and domain context for small TSAs.
- Do not force a local correction that cannot be estimated.

## 6. Checked run

- `run_domain_calibration`: success
- 120 rows
- diagnostics: 0

No card changed. No bundle, certificate, or reviewer decision.
