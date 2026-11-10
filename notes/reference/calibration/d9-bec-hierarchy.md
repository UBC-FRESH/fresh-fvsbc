# D9.108 first hierarchical BEC fit

Status: **prototype fit is a null at TSA holdouts**
Date: 2026-11-10
Workflow: `workflows/freshforge/bec_hierarchy_fit`
Summary: `d9-bec-hierarchy-holdout.csv`

## 1. Model

- Species-group fixed covariates, as before.
- Parent BEC zone dummies (11 zones).
- Partial-pooled subzone intercepts, shrink `n / (n + 500)`.
- Two backfitting passes.
- No TSA term in the predictor.

Evaluated on the same 40 leave-one-TSA-out holdouts.

## 2. Result

| Measure | Value |
| --- | ---: |
| TSAs improved on log loss | 13 / 40 |
| Median log-loss delta | **+3×10⁻¹⁰** |
| Largest improvement | Lillooet −0.000062 |
| Largest degradation | Kamloops +0.000377 |

The fit is effectively identical to the current base model.

## 3. Why

The current base model already uses **BEC subzone-letter effects** (`zone` in
`bp.design`), not TSA effects. Replacing those with parent zones plus shrunken
subzone offsets did not add signal.

The null is informative:

- TSA was the wrong **calibration/evaluation** unit.
- The base fit was already ecological.
- The next change should be in the **calibration layer**, not another base
  hierarchy rewrite.

## 4. Boundary and the weak cases

Boundary, Lakes, Lillooet, Soo, Bulkley, GBR North, and Invermere are unchanged
at the fourth decimal. The hierarchy alone does not fix them.

## 5. Interpretation

- This prototype does not justify replacing the current base model.
- The ecological hierarchy remains the right reporting/calibration structure.
- The next useful experiment is **BEC-unit calibration** using the D9.107 units,
  not TSA-local intercepts.
- A later model can add variant-level or region × zone interactions if residual
  analysis supports them.

## 6. Checked run

- `run_hierarchy`: success
- 212 rows
- diagnostics: 0

No card changed. No bundle, certificate, or reviewer decision.
