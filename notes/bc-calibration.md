# BC-wide calibration programme

Workstream: W1 foundation
Status: active
Date: 2026-11-02
Parent issue: #289
Child issues: #290, #291, #292, #293, #294, #295
Branch: `feature/bc-calibration`
Scope decision: all of BC, including the five zones the variant does not resolve today

This note is the plan of record for the programme. It is written before the
work, so that the maintainer can approve or reject the scope before a parent
issue, a branch, or a commit exists. It follows the post-`P62` convention: a
named workstream, a branch, and a pull request, without a numbered phase.

## The ask

Make `fresh-fvsbc` usable for growth-and-yield work across British Columbia, not
only for the stand or BEC where it was last tested.

In this plan, **calibrate** means four things:

1. Fit and validate the FVS-BC parameters that control site capacity, mortality,
   and growth against BC remeasurement data.
2. Make a calibrated parameter set selectable, versioned, and provenance-bearing
   in `fresh-fvsbc`.
3. State the domain in which each set is valid: BEC, region, species, size, and
   management regime.
4. Refuse a run outside that domain, or flag it, rather than returning a
   plausible-looking number.

It does **not** mean editing the FVS Fortran in this repository. The Fortran lives
in the pinned PyFVS fork and its FVS source submodule, per ADR 0001. A needed
source change is made there and pinned here.

## What the evidence says about "all of BC"

The required scope is **all of BC**. The BC variant does not cover all of BC
today, so the programme has two tracks: calibrate the domain the variant already
represents, and extend the variant to the domain it does not.

`canada/bc/habtyp.f` accepts three region tokens, `CAR`, `KAM`, and `NEL`, and
seven BEC zones: `ESSF`, `ICH`, `IDF`, `MS`, `PP`, `SBS`, and `SBPS`.
`canada/bc/sitset.f` assigns default maximum basal area for the same seven zones.
`CWH`, `CDF`, `BWBS`, `CMA`, and `MH` are absent. When a supplied string does not
resolve, `HABTYP` calls its error path and leaves the BEC at its documented
default, `ICHmw2/01`.

The public FAIB PSP archive in this workspace on 2026-11-02 holds 7,341 sites and
23,956 visits. Of those, 4,430 sites, and 3,186 sites with at least two visits,
fall in the seven supported zones. Forty-seven BEC variants have at least 15 sites
with repeat measurements. The unsupported zones hold 2,911 sites: `CWH` 2,335,
`BWBS` 534, `CDF` 26, `MH` 13, and `CMA` 3.

The two tracks are:

| Track | Domain | What it takes | Where it happens |
| --- | --- | --- | --- |
| Calibration | The seven zones the variant resolves | Calibration, validation, and a parameter library | `fresh-fvsbc`, using the pinned build |
| Extension | `CWH`, `CDF`, `BWBS`, `CMA`, `MH` | A variant extension: species, site index, mortality, growth, and BEC tables, then calibration | The PyFVS/FVS fork first, then `fresh-fvsbc` for the wrapper and the pin |

The second track is **required**, not conditional. It is not a calibration task
and it cannot be promised by `fresh-fvsbc` alone: the Fortran lives upstream, and
the five zones need species and model parameters the BC variant does not carry
today. W2 is therefore a bounded feasibility and extension workstream with an
explicit go/no-go. "All of BC" is the goal; the go/no-go records what the upstream source
can actually support, and what it would cost to get the rest.

## What the KC pilot already proved

The AFRF Knife Creek pilot is the worked example, and it changes the shape of this
plan. It found that the runbooks wrote `STDINFO 712,CHS131`, which FVS-BC does not
parse as an IDF code. The parser falls back to `ICHmw2/01`, whose default maximum
basal area is 89 m2/ha, not the IDFdk3 default of 53. The same 1993 Knife Creek
tree list grows to 77.4 m2/ha under the legacy string and 49.6 m2/ha under
`CAR IDFdk3/01`. The corrected 24-plot and six-AU runs produce roughly 353 to 589
m3/ha at 200 years, against 750 to 1,232 m3/ha on the old curves. That is a 40 to
55 percent correction, not a tuning detail.

The pilot also produced a mortality model and a multiplier set that gives
plausible yields for Knife Creek, but it is not a province-wide calibration:

- the KC v1/v2c multipliers were fitted on 24 plots, in sample;
- the lodgepole pine multiplier sits at its upper bound;
- the first fit was made while the projection carried the wrong BEC default;
- the corrected-BEC rerun is a diagnostic, not an independent validation;
- FVS-BC is an even-aged individual-tree model and Knife Creek is uneven-aged, so
  the pilot does not validate a selection-system model.

What generalizes is the **loop**, not the parameters: validate the BEC, establish
the capacity envelope, fit mortality and growth multipliers within pre-set bounds,
validate on held-out sites and years, and record the claim boundary. That loop is
the core of this plan. The KC parameter set is a regional pilot and a test case
for the machinery, not a provincial answer.

## What the package gets wrong today

`docs/reference/keywords.rst` says a caller does not supply a BEC value and that
`SITECODE` supplies the habitat data. The source says otherwise. Option 14 in
`canada/bc/initre.f` concatenates the first two `STDINFO` fields and calls
`HABTYP`; option 138, `SETSITE`, does the same when a habitat type is entered.
`HABTYP` resolves a region, zone, subzone, and `/series`, and falls back to
`ICHmw2/01` on failure. The contract page is therefore incomplete at best and
wrong at worst.

The package's own examples use `STDINFO=712,CHS131`, the same string the KC pilot
found to be an ICH default. A user who copies the README is not running the BEC
they think they are running. This is the first thing W1 fixes, because every
calibration comparison is meaningless until the input is the input the caller
intended.

## The programme

W1 is the foundation. The later workstreams are a sequence, not a single branch,
and each is recorded in `ROADMAP.md` when its predecessor closes.

| Workstream | Name | Question it answers | Exit evidence |
| --- | --- | --- | --- |
| W1 | BC-wide calibration foundation | Can the package take a valid BC BEC, ingest the provincial data, represent a parameter set, measure a baseline, and state the upstream gap? | Contracts, dataset, schema, baseline, upstream work package, and design |
| W2 | Full-domain coverage | Can the variant represent `CWH`, `CDF`, `BWBS`, `CMA`, and `MH`? | A pinned upstream extension, or a documented go/no-go with cost and evidence |
| W3 | Full-domain baseline | Where does uncalibrated FVS-BC fail across the full domain? | Residual atlas by BEC, TSA, species, size, and density |
| W4 | Domain calibration | What capacity, mortality, and growth parameters are identifiable in each domain? | Versioned bundles with cross-validation and no parameter at a bound |
| W5 | Independent validation | Does each bundle transfer to held-out sites, TSAs, and years? | Certificates with a claim boundary per domain |
| W6 | Calibration release | Can a user select a certified bundle and get provenance? | Release, docs, CLI/API surface, and envelope validator |

W1 does not fit a province-wide parameter set. It builds the machinery, the
baseline, and the upstream work package that make W2 to W5 possible. Fitting
before the baseline would repeat the KC mistake in a larger frame.

## W1 tasks

### W1.1 (#290) Make the BC input contract true, and remove the silent BEC fallback

- [x] Read `canada/bc/initre.f` options 14 and 138, `canada/bc/habtyp.f`,
  `canada/bc/sitset.f`, and `canada/bc/becset.f` at the pinned FVS source commit,
  and record the exact grammar and the default path.
- [x] Add a `BecCode` value object with region, zone, subzone, and series; parse
  and render the `STDINFO` form; reject an unsupported zone, a missing series, or
  a malformed code by name.
- [x] Make `run_case` validate the BEC before the child process starts, and record
  the validated BEC in the provenance record.
- [x] Correct `docs/reference/keywords.rst`, `docs/usage.rst`, the README, and the
  smoke-run examples that use `712,CHS131`.
- [x] Test that a valid `CAR IDFdk3/01` run echoes `BEC=IDFdk3/01`; that a bare
  `IDFdk3` is refused; that `712,CHS131` is refused; and that an invalid input
  exits 2 before FVS is launched.
- [x] Record the decision as an ADR: the BEC is a required, validated input, and
  the package does not inherit FVS's silent default.

Acceptance: a run with `CAR IDFdk3/01` echoes that BEC; a run with an invalid code
is refused with a message that names the accepted grammar; the docs no longer say
the caller does not supply a BEC.

Status: **implemented on `feature/bc-calibration`**, pending review. The real run
echoed `BEC=IDFdk3/01` and `MAXIMUM BASAL AREA ... 53.0 SQ M/HA`; `712,CHS131`
exited 2 and wrote no run directory; the provenance record carries
`"bec": "CAR IDFdk3/01"`. Dashboard: `OVERALL: GREEN`.

### W1.2 (#291) Build the provincial calibration dataset

- [ ] Ingest the FAIB PSP header, visit, plot, and tree files into a documented,
  reproducible dataset; keep site-level extracts outside the tracked tree.
- [ ] Build visit summaries, remeasurement intervals, and tree-survival rows;
  crosswalk PSP species to FVS species; attach BEC, TSA, and ownership; flag
  harvest, fire, insect, and other disturbance where the data allow.
- [ ] Publish aggregate coverage and envelope tables under `notes/reference/`,
  with counts and checksums, and no site identifiers or personal paths.
- [ ] Run QA checks: expansion factors, negative or zero basal area, duplicate
  tree IDs, missing versus dead trees, interval length, and species that do not
  crosswalk.
- [ ] Write the data dictionary and manifest, including the inclusion rules and
  the years used.

Acceptance: the ingest reproduces 7,341 sites and 23,956 visits; 4,430 sites are
in the supported zones; at least 3,000 have repeat measurements; the BEC coverage
table is published; the QA report names every exclusion; the tracked files contain
no site-level records.

### W1.3 (#292) Define the calibration parameter contract

- [ ] Define a versioned JSON schema for a calibration bundle: id and version;
  FVS and PyFVS pins; domain (region, BEC, species group, DBH class, management
  regime); parameters and units; bounds; training and validation split; data
  checksums; objective; convergence diagnostics; reviewer sign-off; claim
  boundary.
- [ ] Implement load, validate, and render: a bundle becomes an ordered keyword
  set (`BAMAX`, `SDIMAX`, `BAIMULT`, `MORTMULT`, and any other supported
  parameter), with BC's metric units and the documented keyword order.
- [ ] Refuse a bundle outside its declared domain, a parameter outside its bounds,
  a missing pin, or a missing checksum; warn when a parameter sits at a bound.
- [ ] Record the bundle id in the provenance record and in the run directory.
- [ ] Test the round trip, the domain refusal, the unit error, the bound warning,
  and the keyword order.
- [ ] Record the decision as an ADR: a calibration bundle is data, not code; the
  package applies it but does not fit it.

Acceptance: a pilot bundle loads, validates, renders, and appears in provenance;
an out-of-domain or out-of-bounds bundle is refused by name.

### W1.4 (#293) Build the baseline backtest and the envelope oracle

- [ ] Run uncalibrated FVS-BC on a stratified sample of PSP intervals across the
  supported zones and TSAs, initialized from the first measurement and grown to
  the second with no cut and no calibration.
- [ ] Compare BA, TPH, QMD, top height, volume, and annual mortality by BEC, TSA,
  species group, DBH class, and basal-area class.
- [ ] Build an empirical envelope table (p99 and maximum) by BEC and species, and
  a post-run validator that flags an output outside it; never silently clip.
- [ ] Test that the validator flags the legacy 77 m2/ha KC case and passes the
  corrected 50 m2/ha case; fail closed when the envelope table is missing.
- [ ] Write the baseline report with residual plots and a statement of what the
  sample does and does not represent.

Acceptance: the baseline report and envelope table exist; the validator flags the
known bad case; the run orchestration returns the flag without changing the
numbers.

### W1.5 (#294) Replicate the KC pilot as a protocol, not a parameter set

- [ ] Re-run the KC pilot from the raw PSP records with the corrected BEC and the
  current pilot bundle; record the exact yields, diagnostics, and uncertainty.
- [ ] Write the repeatable protocol: BEC resolution, capacity target, objective,
  bounds, damping, convergence, and holdout split.
- [ ] Compare the result with the KC v1/v2c results, and say which parts are
  regional, which are model-structural, and which are not identified.
- [ ] Estimate the compute and reviewer effort per domain, using the KC run as the
  unit of work.

Acceptance: a replication report, a protocol note, and an effort estimate; the
report says plainly that KC is a pilot and not a province-wide certificate.

### W1.6 (#295) Design the full-domain calibration and the upstream work package

- [ ] Group the 47 data-rich BEC variants into a small number of calibration
  domains by BEC zone, subzone, region, and species composition; do not propose
  153 separate models.
- [ ] Do a sample-size and power table: which domains can identify capacity,
  mortality, and growth; which are validation-only; which are out of scope.
- [ ] Write the W2 upstream work package for `CWH`, `CDF`, `BWBS`, `CMA`, and
  `MH`: the missing species, site-index, mortality, growth, and BEC tables; the
  source files; the build and test plan; the risks; and the acceptance criteria
  for a pinned extension.
- [ ] Pre-register the primary metrics, spatial and temporal holdouts, and
  acceptance thresholds before any fitting.
- [ ] Propose W2 to W6 with tasks, gates, and reviewer sign-off.
- [ ] Review the design with the named reviewers, and record disagreements and
  resolutions rather than averaging them away.

Acceptance: a coverage and power matrix, an upstream work package with a go/no-go
gate, a pre-registered validation design, and a workstream proposal that the
maintainer can approve or reject.

## What W1 does not do

- It does not fit a province-wide parameter set. That is W4.
- It does not claim that an uncalibrated or pilot-calibrated run is valid across
  BC. That claim needs W5's independent validation.
- It does not edit the FVS Fortran. A source change is a PyFVS/FVS change, pinned
  here.
- It does not release a package. W6 does.
- It does not extend the variant to `CWH`, `CDF`, `BWBS`, `CMA`, or `MH`. W2 is
  the required upstream feasibility and extension workstream, and it may return
  a documented "not feasible without X" rather than a working extension. That answer
  is still evidence, and it is better than claiming coverage the model does not
  have.

## Data governance

The FAIB PSP archive is public, but the site-level extract is not automatically
safe to commit. The repository is public and `AGENTS.md` says to treat BC
inventory data as restricted until proven open. The plan therefore separates:

- **Tracked:** aggregate counts, envelopes, coefficients, residual summaries,
  checksums, and synthetic fixtures.
- **Not tracked:** site identifiers, coordinates, ownership details, and raw tree
  records.

Every published table names its source, its extract date, and its checksum. A
reviewer must be able to reproduce the aggregate from the public source without
the repository carrying the site-level data.

## Validation design

The design is fixed before fitting, not after looking at the results.

**Primary metrics**

- Annual mortality rate bias by species group and DBH class.
- Next-measurement BA and TPH bias and RMSE.
- QMD, top height, and volume bias and RMSE.
- Calibration slope and intercept for observed versus predicted mortality.
- Envelope exceedance rate: output above the p99 and above the observed maximum.
- Parameter-at-bound indicator.

**Holdouts**

- Leave-one-TSA-out, for the TSAs with enough intervals.
- Leave-one-BEC-variant-out within a domain.
- Temporal holdout: fit on intervals ending before a fixed year, test after it.
- Site-grouped cross-validation: no site appears in both training and test.
- Species holdout where the sample supports it, especially for the minor species.

**Provisional acceptance thresholds, to be agreed before fitting**

| Metric | Target |
| --- | --- |
| BA bias, independent sites | within plus or minus 3 m2/ha or 10 percent |
| TPH bias, independent sites | within 15 percent |
| Mortality calibration slope | 0.8 to 1.2 |
| Mortality intercept | not significantly different from zero |
| Parameters at a bound | none |
| Envelope exceedance, 200-year no-cut | zero above the observed maximum; report p99 exceedance |
| Reproducibility | exact rerun from checksummed data and the recorded FVS commit |

If a domain cannot meet the thresholds, the plan reports that and narrows the
claim. It does not relax the threshold silently.

## Risks and open questions

| Risk | Why it matters | What reduces it |
| --- | --- | --- |
| A run outside the variant's domain is made silently | A user on the coast or in the boreal forest gets an ICH default and does not know it | W1.1 rejects the input; W2 names the upstream gap |
| The KC pilot is overgeneralized | Its multipliers are in-sample and one sits at a bound | W1.5 labels it a pilot; W4 refits per domain |
| The upstream extension is not feasible as scoped | The five zones need species and model parameters the variant lacks; a parser change alone is not enough | W2 is a bounded spike with a go/no-go and a cost, not a promise |
| BEC labels are wrong or too coarse | Calibration strata are only as good as the BEC overlay | W1.2 QA and the W1.6 stratification |
| Site series are unavailable for many plots | The maximum-BA default depends on the series | Use a documented default and flag it; do not invent a series |
| Unrecorded disturbance is counted as mortality | Mortality multipliers absorb fire, harvest, and insects | W1.2 disturbance flags and W1.4 residual review |
| FVS-BC is even-aged and some plots are uneven-aged | A fit on selection stands does not validate a selection model | Stratify by regime and state the claim boundary |
| Sample sizes are thin for some variants | A separate curve would be unstable | W1.6 groups variants into domains and marks validation-only groups |
| Two calibrations are confounded | Growth and mortality multipliers both change BA | Fix growth first or fit jointly with separate data, as the KC protocol proposes |
| The envelope is circular | An envelope from the training plots is not independent | Hold out sites before fitting; report the envelope's own uncertainty |
| Upstream source drifts | The 2011 variant table may not match the pinned code | Review the pinned source and record the commit with every bundle |
| Reviewer time is the bottleneck | A calibration without review is not a certificate | W1.6 names reviewers and estimates effort |

Open decisions for the maintainer:

1. What are the go/no-go criteria, and the cost ceiling, for the W2 upstream
   extension? The scope is all of BC, so this is the decision that determines
   whether the programme can meet it.
2. Is the KC parameter set allowed as a regional pilot, a prior, or neither?
3. Which domain is the first calibration target after the baseline: `IDFdk3`,
   `ICHmw2`, `SBSmc2`, or a mixed group?
4. Who reviews the first certificate, and what is the sign-off record?
5. If W2 returns "not feasible without X", does the programme stop at the
   supported seven zones, or commission X as a separate upstream project?

## Activation

W1 is active. The parent issue is #289, the six child issues are #290 to #295,
and the branch is `feature/bc-calibration`. The next move is W1.1.

## References

- `AGENTS.md`, especially the rules on evidence, scope, provenance, and BC data.
- `ROADMAP.md`, the roadmap and the issue tracker map.
- `notes/reference/deployment-readiness.md`, especially the limits on real use.
- `docs/reference/keywords.rst`, the keyword and BC input contract.
- `notes/reference/fvsbc-validation.md`, the build's own validation evidence.
- `notes/reference/bc-treelist-and-species.md`, the BC tree record and species list.
- `notes/triage.md`, the known gaps and what would reopen them.
- The WS4 workspace's `notes/reference/fvs-mortality-calibration/` and
  `notes/plans/fvs-mortality-calibration-idf.md`, the KC pilot's evidence and
  assumptions register.
- `canada/bc/habtyp.f`, `canada/bc/initre.f`, `canada/bc/sitset.f`, and
  `canada/bc/becset.f` at the pinned FVS source commit.
