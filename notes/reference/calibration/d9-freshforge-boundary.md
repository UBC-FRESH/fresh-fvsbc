# D9.83 FreshForge small-tree boundary

Status: **the sub-threshold PL residual is now a checked workflow boundary**
Date: 2026-11-09
Workflow: `workflows/freshforge/quesnel_mpb_segment.yaml`
Card: `quesnel-candidate/small-tree-boundary.json`

## 1. What the node does

`freeze_boundary.py` reads the aggregate 16-case panel from
`d9-small-tree-panel-summary.csv`. The table has one row per external case and
no site key. It checks:

- no missing or negative values;
- total live PL above 15 cm is at most 1.0/ac; and
- maximum live PL DBH is at most 20 cm.

If a check fails, the node fails. Otherwise it writes a frozen boundary card
with the panel summary, checksum, pins, and the rule not to tune MPB for small
PL.

## 2. Frozen card

| Quantity | Value |
| --- | ---: |
| panel cases | 16 |
| mean final live PL/ac | 12.15 |
| maximum final live PL/ac | 58.91 |
| maximum surviving PL DBH | 16.66 cm |
| live PL above 15 cm | 0.04/ac |
| status | `frozen_boundary` |

The card is `quesnel-candidate/small-tree-boundary.json`.

## 3. Checked run

```sh
freshforge run workflows/freshforge/quesnel_mpb_segment.yaml --workdir . \
  --evidence runtime/freshforge-quesnel-mpb-evidence.json --summary
```

Result: status `success`; both `run_segment` and `freeze_boundary` succeeded with
zero diagnostics.

## 4. Interpretation

- The boundary is now executable, not just prose: a panel that develops
  material live PL above 15 cm fails the node.
- The residual is a separate mortality gap; it is not an INITMORT tuning target.
- The Quesnel candidate remains non-PL background plus large-tree MPB.

## 5. Claim boundary

This is a diagnostic model boundary. It does not support a yield, AAC, legal,
whole-block, or certificate claim.
