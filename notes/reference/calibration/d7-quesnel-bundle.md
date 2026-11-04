# D7.14 Quesnel high-QMD temporal validation and candidate bundle

Status: **site-grouped and temporal validation both pass**; unsigned candidate bundle, not a certificate
Date: 2026-11-03
Issue: #378
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: Quesnel SBPSdc, initial QMD >= 13
Evidence: `d7-quesnel-highqmd-temporal-summary.csv`, `d7-quesnel-highqmd-bundle.json`

D7.13 found a Quesnel high-QMD candidate that passed every site fold. This is the temporal holdout
and the packaging step.

## 1. Temporal split

- Train: intervals starting **1981 or earlier** — 14 intervals / 6 sites.
- Test: intervals starting **1990 or later** — 6 intervals / 6 sites.
- Candidate: `BAMAX 75`, no other multipliers.

## 2. Result

| Fold | n | BA % | TPH % |
| --- | ---: | ---: | ---: |
| train <= 1981 | 14 | -5.47% | -10.07% |
| test >= 1990 | 6 | +5.38% | +3.80% |
| all | 20 | -2.11% | -6.29% |

Both train and test are inside the pre-registered bands (BA ±10%, TPH ±15%). Every test site is
inside both bands in the D7.13 site-grouped run.

This is the first Quesnel domain with both a site-grouped and a temporal pass.

## 3. Candidate bundle

`d7-quesnel-highqmd-bundle.json` is an **unsigned candidate bundle**:

- domain: `CAR`, `SBPSdc`, untreated;
- parameter: `BAMAX 75`, bounds 25–89;
- pins: PyFVS `e95172b`, FVS `ef5fa847`, variant `bc`;
- review: `signed_off: false`;
- claim: candidate for Quesnel SBPSdc with initial QMD >= 13.

`load_bundle` accepts it and renders the BAMAX keyword.

**Schema limit:** the current bundle domain has no `QMD` field. The `QMD >= 13` boundary is in the
claim and note, not enforced by the loader. A caller must enforce it, or the schema needs a
`qmd_min` field before this is a self-contained bundle.

## 4. What this is not

- Not a certificate; the bundle is unsigned and unreviewed.
- Not a Quesnel-wide model; the `QMD < 13` sites remain validation-only.
- Not a multi-cycle establishment model; the temporal test is one-step intervals.
- Not a province-wide claim.

## 5. Next

1. Add `qmd_min` (or an equivalent size/density domain field) to the bundle schema and provenance,
   with tests.
2. Review and sign the candidate bundle if the boundary is enforceable.
3. Run the same temporal check on a second TSA/domain before calling the calibration stable.

## 6. Claim boundary

On Quesnel SBPSdc stands with initial QMD at least 13 m2/ha, `BAMAX 75` meets the pre-registered BA
and TPH biases in both a site-grouped and a temporal holdout. It is an unsigned candidate, not a
certified calibration or a yield/AAC/legal claim.
