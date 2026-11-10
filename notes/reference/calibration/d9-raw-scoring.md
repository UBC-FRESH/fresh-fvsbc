# D9.100 raw inventory scoring

Status: **new candidate cards carry preprocessing metadata; raw feature rows can be scored**
Date: 2026-11-10
Script: `score_inventory.py`
Workflow: `workflows/freshforge/score_inventory.yaml`

## 1. What changed

`fit_candidate.py` now stores a `preprocessing` block in new model cards:

- feature recipe version;
- imputation medians for crown, SI, H-D, and growth;
- BEC zone list;
- missing flags;
- species-to-group map;
- the full-frame imputation caveat.

Boundary and MacKenzie were regenerated with this block. The coefficients and
aggregate metrics are unchanged.

## 2. Raw scoring contract

Input columns:

```text
site, plot, dbh, ba0, tph0, height, damage, growth, crown, si, zone
```

plus either `group` or `species`.

The scorer:

1. maps species to group if needed;
2. fills missing crown/SI and H-D/growth with the card medians;
3. computes QMD, relative DBH, and H-D;
4. builds the growth-free design in card order;
5. applies the group scalers and coefficients;
6. writes `site, plot, group, eta`.

It does not fit or tune a model.

## 3. Checked tests

`tests/test_score_inventory.py`:

- scores raw rows to finite `eta`;
- maps species codes through the card;
- rejects an older card without preprocessing metadata.

`tests/test_deployment_calibration.py` still passes.

## 4. Imputation caveat

The card medians are the frozen full-frame values. The candidate review package
already flags full-frame median imputation as a possible leakage concern. This
step makes the deployment path usable; it does not resolve that review finding.

## 5. Workflow

```sh
freshforge run workflows/freshforge/score_inventory.yaml --workdir . \
  --evidence runtime/freshforge-score-inventory-evidence.json
```

The workflow expects `runtime/inventory.csv` and writes
`runtime/scored-inventory.csv`. The scored table can feed the deployment offset
estimator.

## 6. Claim boundary

Raw scoring only. Not a bundle, certificate, yield, AAC, legal, or whole-block
claim. The Quesnel/Okanagan review package is unchanged.
