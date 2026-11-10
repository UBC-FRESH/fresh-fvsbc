# D9.98 candidate registry

Status: **the frozen candidate set has a checksummed registry**
Date: 2026-11-10
Registry: `candidate-registry.json`
Table: `CANDIDATE-REGISTRY.md`
Workflow: `workflows/freshforge/candidate_registry.yaml`

## 1. What the registry records

For each frozen candidate:

- model id and target TSA;
- supported groups and scope;
- aggregate interval count;
- calibration rule from the frozen policy;
- review status;
- card path and SHA-256;
- metrics path and SHA-256.

It contains no site-level rows.

## 2. Current set

| Count | Status |
| ---: | --- |
| 12 | frozen candidates |
| 2 | `review_pending` (Quesnel, Okanagan) |
| 10 | `not_in_current_review` |

The registry has 12 candidates. Invermere is absent by policy.

## 3. Scope corrections

- Quesnel is recorded as **non-PL background**, even though the fitted card
  contains a PL coefficient block.
- North Island, Fraser, Haida Gwaii, and MacKenzie record their omitted groups.
- Supported symmetric rules are Boundary and MacKenzie; optional rules follow
  the calibration policy.

## 4. Checked run

```sh
freshforge run workflows/freshforge/candidate_registry.yaml --workdir . \
  --evidence runtime/freshforge-candidate-registry-evidence.json
```

The check fails if a card, checksum, policy mapping, review status, or Markdown
row is stale.

## 5. Claim boundary

Registry only. No bundle, certificate, yield, AAC, legal, or whole-block claim.
The Quesnel/Okanagan review package is unchanged.
