# D7.14 Quesnel high-QMD temporal validation and candidate bundle

Status: **post-hoc candidate**; site and temporal checks pass for a fixed BAMAX, not independently validated
Date: 2026-11-03
Issue: #378
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
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

Both train and test are inside the pre-registered bands (BA ±10%, TPH ±15%). Every test interval is
inside both bands.

The temporal split is time-based, but it is **not site-independent**: the test intervals come from
sites that also contribute training intervals. Together with the fact that `BAMAX 75` was selected on
the same sites, this is a post-hoc check, not an independent validation.

## 3. Candidate bundle

`d7-quesnel-highqmd-bundle.json` is an **unsigned candidate bundle**:

- domain: `CAR`, `Quesnel TSA`, `SBPSdc`, untreated;
- parameter: `BAMAX 75`, bounds 25–89;
- pins: PyFVS `e95172b`, FVS `ef5fa847`, variant `bc`, wrapper `0.21.4`;
- review: `signed_off: false`;
- claim: candidate for Quesnel SBPSdc with initial QMD >= 13.

`load_bundle` accepts it and renders the BAMAX keyword.

**Schema status:** `domain.qmd_min` and `domain.tsas` are enforced; the candidate bundle carries
`qmd_min: 13.0` and `tsas: ["Quesnel TSA"]`.

## 4. What this is not

- Not a certificate; the bundle is unsigned and unreviewed.
- Not an independent validation: BAMAX and the domain were selected on the same sites.
- Not a Quesnel-wide model; the `QMD < 13` sites remain validation-only.
- Not a multi-cycle establishment model; the temporal test is one-step intervals.
- Not valid for disturbance intervals: the evidence excludes `dead_ba / ba0 > 0.4`, but the bundle
  cannot enforce that filter.
- Not a province-wide claim.

## 5. Next

1. Run a nested selection or an independent TSA/cohort before upgrading the claim.
2. Review and sign the candidate bundle only after that.
3. Keep the `QMD < 13` sites validation-only.

## 6. Claim boundary

On Quesnel SBPSdc stands with initial QMD at least 13 cm, `BAMAX 75` meets the pre-registered BA and
TPH biases in a site-grouped and a temporal check. The parameter and domain were selected on the same
sites, so this is a post-hoc candidate, not an independently validated calibration or a
yield/AAC/legal claim.
