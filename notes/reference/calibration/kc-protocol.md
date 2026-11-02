# The KC pilot protocol

Status: protocol for a regional pilot, not a calibration certificate
Date: 2026-11-02
Scope: the repeatable steps the AFRF Knife Creek pilot used, with its evidence
and its failures stated.

This note is the protocol W1.5 takes from the KC work. The pilot is the worked
example, not a province-wide parameter set. Its value is the **loop**: validate
the BEC, build the provincial tables, measure a baseline, fit within bounds,
validate on held-out sites and years, and record the claim boundary.

## 1. The KC pilot in one page

| Item | Value |
| --- | --- |
| Data | 24 AFRF Knife Creek PSP plots, 1993–2013, uneven-aged IDFdk3/IDFxm |
| Legacy BEC | `STDINFO 712,CHS131`, which FVS resolves to `ICHmw2/01`; default maximum BA 89 m²/ha |
| Corrected BEC | `STDINFO` fields `CAR` and `IDFdk3/01`; default maximum BA 53 m²/ha |
| Actual 1993 tree list, 200 years, no cut | legacy 77.4 m²/ha, 150 ft top height, 401 TPH; corrected 49.6 m²/ha, 99 ft, 258 TPH |
| 24-plot 1993–2013 backtest, legacy | BA bias +1.04 m²/ha, TPH bias +421.8 |
| 24-plot 1993–2013 backtest, corrected | BA bias −1.29 m²/ha, TPH bias +249.5 |
| 24-plot 200-year corrected, no cut | max BA mean 50.0 m²/ha (45–67); volume 447–589 m³/ha |
| Six-AU corrected, 200-year no cut | volume 353–589 m³/ha, against 750–1,232 on the old curves |
| Managed, year 170 | volume 339–517 m³/ha, against 614–917 |
| First multi-entry, year 30 | volume 163–196 m³/ha, against 219–287 |
| v2c multipliers | FD BAIMULT 1.20 / MORTMULT 2.80; SE 1.3948 / 3.8261; PL 1.0 / 8.0; HW 1.0 / 1.2012 |
| Convergence | 28 iterations, max parameter change 0.0009, loss change 3.6×10⁻⁵ |

The v1 set was fitted while the projection used `ICHmw2/01`; that is why the
lodgepole pine multiplier hit its 8.0 bound. The corrected-BEC rerun is a
diagnostic, not an independent calibration. The pilot also produced a tree-level
survival model: 328 IDFdk3/IDFxm intervals, 186 sites, 46,756 live tree records,
5,988 deaths. Observed annual mortality is FD 0.58%, PL 3.15%, HW 2.65%, SE
1.06% in IDFdk3; FVS's base PL rate at 30–40 m²/ha and 10–25 cm is 0.445%
against an observed 4.49%. The PL gap is real; the ratio is not constant by
size or BA.

## 2. What the pilot proves

- **The BEC input is the first calibration decision.** A wrong code changes the
  capacity envelope and the whole trajectory; the corrected run removes the
  implausible 77 m²/ha asymptote.
- **The tree list and the interval construction reproduce the observed initial
  stand.** The generic baseline in W1.4 confirms this at scale: initial BA MAE
  0.93 m²/ha across 89 intervals.
- **A species-group multiplier can move the trajectory, but it is not a
  calibration by itself.** The KC v2c set improves some groups and fails on
  lodgepole pine, which sits at a bound.
- **Capacity and mortality are separate objects.** `BAMAX` sets the density at
  which mortality rises; `MORTMULT` scales mortality. One cannot substitute for
  the other.
- **The long-run curve is a plausibility test, not a fitting target.** Fitting to
  a desired 200-year trajectory is circular.

## 3. What it does not prove

- It is **not a province-wide calibration**. It is 24 plots in one IDF area.
- It is **not independent-site validation**. The 2024 Marshall remeasurement is a
  temporal holdout on the same plots; the FAIB 92-plot check mixes IDF variants.
- It does **not make FVS-BC a selection-system model**. FVS-BC is even-aged;
  Knife Creek is uneven-aged.
- The site series is `/01` for every plot. The plot-level site series is not in
  the extract, so the capacity target is a documented diagnostic default.
- The PL multiplier at 8.0 is a bounded proxy for mountain pine beetle and other
  losses, not a biological mortality rate.
- It is **not a legal, AAC, or whole-block claim**.

## 4. The protocol

### Step 0 — Freeze the data

- Record the four FAIB files' sizes and SHA-256 in a manifest.
- Record the FVS and PyFVS pins, the built variant list, and the dataset build
  parameters.
- Keep site-level extracts out of the tracked tree; publish aggregates only.

### Step 1 — Resolve the BEC and the site series

- Write the region in `STDINFO` field 1 and the BEC/series in field 2, as
  `CAR IDFdk3/01`.
- Validate the code with `fresh_fvsbc.bec.BecCode`; refuse a code that would
  silently fall back to `ICHmw2/01`.
- Record the site series source. If it is a diagnostic default, say so.
- Check whether the variant resolves the subzone. In the W1.4 baseline, 19 BEC
  variants were skipped because their subzone is not in `HABTYP`; those need the
  W2 upstream extension.

### Step 2 — Build the analysis tables

- Visit summaries: live BA, TPH, volume, top height, QMD.
- Intervals: consecutive visits, 2–40 years; dead BA/TPH; net and gross BA rate.
- Tree survival: live at the start, status at the end (`live`, `dead`,
  `missing`); missing is not dead.
- QA: expansion factors, duplicate tree IDs, non-positive BA/TPH, species
  crosswalk.

### Step 3 — Establish the capacity envelope

- Use the empirical p99 and maximum by BEC, and by BEC × species group.
- Treat the range as an envelope, not a point: the published default, the p99,
  the observed maximum, and any independent local source.
- Run a `BAMAX` grid (e.g., 53, 56, 60, 63, 66) and report the asymptote, time to
  90% of the cap, mortality at the cap, and volume asymptote.
- Never silently clip an output. Flag it.

### Step 4 — Measure the baseline

- Grow each interval from its first measurement with no cut and no calibration.
- Compare the initial stand (a construction check) and the next measurement.
- Report by BEC, TSA, species group, DBH class, and BA class.
- Flag any prediction above the p99 or the observed maximum.

### Step 5 — Fit within bounds

- Fit `BAIMULT` and `MORTMULT` by species group, with `BAMAX` fixed from Step 3.
- Do not fit growth and mortality to the same BA trajectory without a separate
  constraint; they are confounded.
- Bounds: soft 0.5–3.0, hard 0.25–4.0 for a final set. A parameter at a bound is
  a failure signal, not a result.
- Objective: weighted squared log ratio of predicted to observed annual
  mortality by stratum, plus BA/TPH trajectory error, plus a penalty for
  deviation from 1.0. Choose the weights before fitting.
- Damping: 0.6 per iteration, as the KC pilot used.
- Convergence: maximum relative parameter change < 0.02 and loss change < 1e-4,
  or a stated iteration cap (KC used 28 of 30).
- Record every evaluation and the final covariance or bootstrap intervals.

### Step 6 — Check identifiability

- Profile likelihood or posterior intervals.
- Correlation between `BAMAX` and `MORTMULT`.
- Sensitivity to interval length, plot inclusion, and starting values.
- If an optimum hits a bound, reject the parameterisation and move to a
  structural alternative: species/size-specific multipliers, a source-level
  change, or a different data set.

### Step 7 — Validate independently

- Spatial holdout: leave one TSA out.
- Subzone holdout: fit IDFdk3, test IDFxm, and vice versa where the sample
  allows.
- Temporal holdout: fit before a fixed year, test after.
- Site-grouped cross-validation: no site in both train and test.
- Report bias, RMSE, calibration slope/intercept, envelope exceedance, and
  uncertainty.
- No independent validation, no calibration claim.

### Step 8 — Package the result

- Write a `CalibrationBundle` with the pins, domain, parameters, bounds, data
  checksum, split, objective, convergence, review, and claim.
- Record the bundle id in provenance.
- Publish a report that states what was fitted, what was held out, what failed,
  and what the result does not cover.

## 5. Effort

The KC pilot is one domain: 24 plots, one region, two BEC variants. It cost
roughly one day of compute for the runs and the grid, and two to three reviewer
days to check the BEC, the envelope, the bounds, and the claim. A province-wide
programme with 89 BEC variants is not 89 times that: the tables and the harness
are shared, but each domain needs its own fit, holdout, and review. The W1.6
design is where the domain grouping and the effort estimate are fixed.

## 6. Claim boundary

The KC pilot supports this statement and no more:

> In the AFRF Knife Creek IDFdk3/IDFxm plots, the legacy `712,CHS131` string ran
> `ICHmw2/01` and produced a 77 m²/ha trajectory that is outside the local
> envelope. Correcting the BEC to `CAR IDFdk3/01` lowers the no-cut asymptote to
> about 50 m²/ha and changes the 200-year volume by roughly 40–55%. A species-group
> multiplier set can move the trajectory, but the lodgepole pine multiplier sits
> at its bound and the set is not independently validated. It is a regional pilot,
> not a province-wide calibration.

The parameters are in `kc-pilot-bundle.json`. They are unsigned and carry the
bound warning on purpose.
