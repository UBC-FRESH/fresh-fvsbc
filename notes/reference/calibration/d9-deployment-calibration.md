# D9.99 deployment calibration helper

Status: **the supported offsets now have a deployment estimator**
Date: 2026-11-10
Script: `deployment_calibration.py`
Workflow: `workflows/freshforge/deployment_calibration.yaml`

## 1. What it does

Given:

- a frozen model card;
- a scored target CSV with `site`, `group`, `eta`, `exposure`, and `dead`;
- the frozen calibration policy;

the helper:

1. resolves the policy rule (`one_sided` or `symmetric`);
2. selects the first 20 sorted sites;
3. estimates one group intercept where the group has at least 500 trees and the
   trigger is met;
4. writes an offset JSON with card/data checksums and group counts;
5. optionally writes calibrated predictions.

No site-level rows are written to tracked files.

## 2. Input contract

The scored table is the upstream output:

```text
site,group,eta,exposure,dead
```

The helper does **not** re-score raw inventory. The frozen cards do not yet store
the preprocessing medians needed to score raw rows; that is a separate
deployment step.

## 3. Policy behavior

- Boundary and MacKenzie: symmetric.
- Quesnel: one-sided.
- Optional candidates: pass `--rule one_sided` or `--rule symmetric`.
- Unmapped cards fail rather than guessing.

## 4. Checked tests

`tests/test_deployment_calibration.py` covers:

- symmetric correction in both directions;
- one-sided correction that skips underprediction;
- too-few-sites rejection;
- unmapped-card rejection;
- applied prediction output.

The tests use synthetic scored rows, not site data.

## 5. Workflow

```sh
freshforge run workflows/freshforge/deployment_calibration.yaml --workdir . \
  --evidence runtime/freshforge-deployment-calibration-evidence.json
```

The workflow expects `runtime/scored-target.csv` and writes aggregate offsets and
predictions under `runtime/`. It is a template until a scored target table is
supplied.

## 6. Claim boundary

Deployment calibration offsets only. Not a bundle, certificate, yield, AAC,
legal, or whole-block claim. The Quesnel/Okanagan review package is unchanged.
