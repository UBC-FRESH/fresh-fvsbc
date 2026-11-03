# D7 consolidation plan

Status: complete; see `d7-consolidation.md` for the evidence
Date: 2026-11-03
Parent: D7.4, `61b6cb1` (#352)

## Why this plan

D7.4 found the TPH fix: public-data recruitment rendered as an FVS `ESTAB`/`NATURAL` block.
The IDFdk spatial holdout passes with BA -1.90 / MAE 1.93 and TPH -207.4 / MAE 370.1 (-8.7%).
The model is a pilot, not a certificate. The five follow-ups below turn it into a reusable,
validated, deployable layer.

## Work packages

| # | Work package | Exit evidence |
| --- | --- | --- |
| 1 | Bundle/provenance ingrowth section | Done: `IngrowthModel` in bundle; pilot bundle runs and provenance names it |
| 2 | Second spatial and temporal holdouts | Done: Kamloops +14.1% TPH, temporal ≤1990 +14.7% TPH; both inside 15% |
| 3 | Periodic establishment | Done: two-cycle run, 8 establishment events, test TPH -8.6% |
| 4 | Reuse on the other domains | Screened: all-zone rates; CWH/BWBS/ICH/IDF/MS improve; SBS has a MORTMULT pilot; SBPSdc/mk candidate; PP validation-only |
| 5 | Density/age-dependent recruitment | Done: binned BA/QMD model, test TPH -4.3% vs -8.7% |

## Sequence

1. Implement the ingrowth model object and bundle schema, with tests.
2. Move the probe to the model object and keep the D7.4 result reproducible.
3. Extend the keyword builder for multiple cycles and test it.
4. Build recruitment tables for all intervals and fit the per-BEC rates.
5. Add a second spatial split and a temporal split for IDFdk.
6. Screen the supported domains; run the five-zone local path with the existing prototype parser.
7. Fit binned BA/QMD rates and compare them on the same holdout.
8. Write the D7.6 report and update the deployment plan.

## Claim boundary

Every result is a pilot until it has an independent validation, a signed bundle, and a second
holdout. The five-zone wrapper remains a release task, not a D7 result.
