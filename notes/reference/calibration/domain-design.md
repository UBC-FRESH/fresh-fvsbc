# The calibration domains and the W2 gate

Status: proposed for W1.6, pending reviewer sign-off
Date: 2026-11-02
Task: W1.6 (#295)
Parent programme: #289
Branch: `feature/bc-calibration-domains`
Inputs: `bec_coverage.csv`, `bec_species_envelope.csv`, `baseline_summary.csv`
Generated tables: `domain_power.csv`, `domain_summary.csv`

This is the W1.6 design report. It groups the 121 supported BEC variants into calibration domains,
states which domains can identify capacity, mortality, and growth, and pre-registers the validation
design. It does **not** fit a parameter. The companion
[W2 upstream work package](w2-upstream-work-package.md) names what the five missing zones need and the
go/no-go gate.

The design is deliberately a **sample-size and claim-boundary** document. A table of counts is not a
calibration, and the W1.6 acceptance is a design the maintainer can approve or reject, not a result.

## 1. What we have

The W1.2 ingest covers the seven zones the BC variant resolves:

| Quantity | Value |
| --- | ---: |
| BEC variants in the coverage table | 153 |
| Supported variants | 121 |
| Upstream variants (five zones) | 32 |
| Supported variants with at least 15 repeat sites | 47 |
| Supported variants with at least 15 repeat sites and 50 intervals | 39 |
| Intervals in the supported zones | 9,186 |
| Tree-survival rows | 1,031,828 |
| Dead-tree rows | 160,859 |

The 32 upstream variants are counted in `bec_coverage.csv` but contribute no interval or envelope
row, because W1.2 did not run the variant on a zone it cannot resolve. They are W2's scope, not W4's.

## 2. The domains

**A domain is a BEC zone, not an arbitrary pool.** The source's maximum-basal-area and SDI defaults
are keyed by zone, subzone, and site series (`canada/bc/sitset.f`), and the version 2 calibration is
keyed by named site series (`canada/bc/becset.f`). Merging zones would pool defaults the model treats
as different. The design keeps the seven source zones, then uses the sample-size rule to decide
which are calibration domains and which are validation-only.

The rule is pre-registered in `fresh_fvsbc.calibration_domains`:

- **calibration variant**: supported, at least 15 repeat sites, at least 50 intervals.
- **validation-only**: supported, at least 5 repeat sites or at least 10 intervals.
- **insufficient**: supported, but below both.
- **upstream**: a variant in `CWH`, `CDF`, `BWBS`, `CMA`, or `MH`.

The 50-interval threshold is the point at which the approximate basal-area MDE falls near 4 m2/ha
with the baseline's assumed 10 m2/ha standard deviation; the 15-repeat-site threshold keeps a
variant from carrying a domain on one or two sites. Both are design choices, not fitted quantities.
They are fixed here so a later fit cannot select the sample that makes it look best.

### 2.1 The domain table

The full table is `domain_summary.csv`; the per-variant table is `domain_power.csv`.

| zone | variants | calibration | validation-only | insufficient | upstream | sites | repeat sites | intervals | dead trees | capacity-ready | mortality-ready | growth-ready | mortality MDE % | BA MDE m2/ha | baseline flags | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESSF | 36 | 2 | 19 | 15 | 0 | 420 | 279 | 620 | 8,596 | 2 | 1 | 2 | 3.02 | 1.12 | 0 | calibration, narrow |
| ICH | 31 | 12 | 10 | 9 | 0 | 1,269 | 950 | 3,149 | 54,185 | 12 | 12 | 11 | 1.20 | 0.50 | 0 | calibration |
| IDF | 18 | 10 | 7 | 1 | 0 | 973 | 797 | 2,126 | 33,620 | 10 | 10 | 8 | 1.53 | 0.61 | 0 | calibration |
| MS | 11 | 5 | 2 | 4 | 0 | 376 | 307 | 1,037 | 14,837 | 5 | 3 | 3 | 2.30 | 0.87 | 0 | calibration |
| PP | 2 | 0 | 1 | 1 | 0 | 16 | 10 | 27 | 303 | 0 | 0 | 0 | 16.09 | 5.39 | 0 | validation-only |
| SBPS | 4 | 1 | 2 | 1 | 0 | 170 | 126 | 296 | 7,594 | 1 | 1 | 1 | 3.21 | 1.63 | 3 | calibration, narrow |
| SBS | 19 | 9 | 6 | 4 | 0 | 1,206 | 717 | 1,931 | 41,724 | 9 | 8 | 6 | 1.37 | 0.64 | 3 | calibration |
| CWH | 22 | 0 | 0 | 0 | 22 | 2,335 | 2,178 | 0 | 0 | 0 | 0 | 0 | - | - | 0 | upstream |
| BWBS | 5 | 0 | 0 | 0 | 5 | 534 | 336 | 0 | 0 | 0 | 0 | 0 | - | - | 0 | upstream |
| CDF | 1 | 0 | 0 | 0 | 1 | 26 | 21 | 0 | 0 | 0 | 0 | 0 | - | - | 0 | upstream |
| MH | 3 | 0 | 0 | 0 | 3 | 13 | 12 | 0 | 0 | 0 | 0 | 0 | - | - | 0 | upstream |
| CMA | 1 | 0 | 0 | 0 | 1 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | - | - | 0 | upstream |

`baseline flags` counts the W1.4 intervals above the p99 or the observed maximum. SBPS and SBS carry
three each, which is why they are first in the fitting queue despite their smaller variant counts.

### 2.2 The calibration variants

The 39 calibration variants, by domain:

| Domain | Variants |
| --- | --- |
| ESSF | `ESSFwc2`, `ESSFdc3` |
| ICH | `ICHmw2`, `ICHmw`, `ICHmk1`, `ICHdw4`, `ICHxm1`, `ICHdw1`, `ICHmw3`, `ICHmc2`, `ICHmw5`, `ICHwk1`, `ICHmk2`, `ICHdm` |
| IDF | `IDFdk2`, `IDFdk3`, `IDFmw2`, `IDFdm1`, `IDFww`, `IDFdk1`, `IDFdm2`, `IDFxh2`, `IDFxh1`, `IDFdk5` |
| MS | `MSdm1`, `MSdk`, `MSdw`, `MSdm3`, `MSxv` |
| SBPS | `SBPSmk` |
| SBS | `SBSmw`, `SBSmk1`, `SBSwk1`, `SBSmc2`, `SBSwk2`, `SBSmc`, `SBSmk2`, `SBSdw1`, `SBSdw2` |

Eight variants have at least 15 repeat sites but fewer than 50 intervals. They are
**validation-only**, not calibration failures: `SBSdw3` (48 intervals), `IDFxm` (30), `ESSFmv3`
(20), `ESSFdk2` (41), `IDFxx2` (41), `ESSFwm4` (40), `SBPSdc` (49), and `ESSFmh` (28). They can
test a fit but cannot carry one.

### 2.3 What the sample supports

The readiness columns are a **sufficiency** check, not a fitted power calculation:

- **capacity** needs at least 50 intervals, because the empirical envelope and the asymptote are
  stand-level quantities.
- **mortality** needs at least 1,000 dead-tree rows, because a mortality multiplier fitted on fewer
  is dominated by a handful of events.
- **growth** needs at least 100 intervals, because growth is a change between two measurements and
  the interval is the unit of information.

The MDE columns are approximate. The mortality MDE is the minimum detectable relative change in a
binomial rate at 80 percent power and a two-sided 5 percent test, `2.8 / sqrt(dead trees)`. The BA
MDE assumes a between-interval standard deviation of 10 m2/ha and uses `2.8 * 10 / sqrt(intervals)`.
The assumed SD is a design input; the fitted standard errors replace it in W4. A domain that cannot
meet the pre-registered threshold at this sample size is marked validation-only rather than fitted
on a sample that cannot answer the question.

The result is four tiers:

1. **Broad calibration:** ICH (12 variants), IDF (10), SBS (9). These have the sample to fit all
   three parameters and to hold out variants and TSAs.
2. **Calibration with a narrower transfer claim:** MS (5 variants; 3 mortality-ready and 3
   growth-ready), ESSF (2 variants; only 1 mortality-ready), SBPS (1 variant; 1 mortality-ready).
   The domain can be fitted, but the claim is **within the sampled variants**, with leave-one-variant-out
   validation. It cannot support a claim that the whole zone transfers.
3. **Validation-only:** PP (2 variants, 27 intervals, 303 dead rows). It is a real BEC zone with too
   little repeat measurement for a separate fit. It tests a neighbouring dry-forest fit and supplies
   an empirical envelope, nothing more.
4. **Upstream:** CWH, BWBS, CDF, MH, CMA. No interval or envelope row exists because the variant
   does not resolve the zone. W2 is the gate.

### 2.4 The first fitting queue

Order is by readiness, baseline failure, and the protocol we already have:

1. **IDF.** The KC protocol is already worked in this zone (`IDFdk3`/`IDFxm`), 10 calibration
   variants and 2,126 intervals. It is the cheapest first certificate.
2. **ICH.** The largest sample: 12 variants, 3,149 intervals, 54,185 dead rows. It is the broadest
   claim and the most reviewer work.
3. **SBS and SBPS.** The W1.4 baseline flags three intervals in each. SBS is broad (9 variants);
   SBPS is narrow (1 variant) and should be fitted only with a within-variant claim.
4. **MS.** Five variants, 1,037 intervals, 3 mortality-ready. A moderate sample with a
   well-defined montane spruce domain.
5. **ESSF.** Two calibration variants and one mortality-ready variant. High-elevation and
   heterogeneous; fit only after the lower-elevation domains, with a narrow claim.
6. **PP.** Validation-only. Do not fit a separate multiplier set.

W2 should start in parallel with IDF, because it is the long pole and its answer determines whether
"all of BC" is a supported claim or a documented boundary.

## 3. Region and species stratification

The aggregate coverage table does not carry an FVS region token. The source accepts `CAR`, `KAM`, and
`NEL` (`canada/bc/habtyp.f`), but those are input tokens, not an ecological stratification of the PSP
sites. **This design does not invent a region assignment.** Region is a candidate stratifier for the
site-level extract, and `baseline_by_tsa.csv` already shows TSA as the spatial holdout we can use
without publishing site identifiers.

Species composition is a within-domain stratum, not a domain boundary:

- `bec_species_envelope.csv` gives 594 BEC × species-group envelope rows.
- `species_crosswalk.csv` has 37 observed PSP codes, of which 24 are outside BC's 15 species and are
  marked `known=False` / `UNKNOWN`.
- The 15 BC species are the model's species list, not a claim that every coastal or boreal species is
  represented. The W2 work package owns the crosswalk decision.

The fit in W4 is a domain-level fit with BEC, subzone, and species group as covariates. It does not
pool the zone-specific `BAMAX` defaults; it fits multipliers over the domain and reports the
BEC-specific residuals.

## 4. Pre-registered validation design

The design is fixed before fitting. A change after seeing a result is recorded as a pre-registration
amendment, with the reason and the reviewer, not silently applied.

### 4.1 Primary metrics

- Annual mortality-rate bias by species group and DBH class.
- Next-measurement BA and TPH bias and RMSE.
- QMD, top height, and volume bias and RMSE.
- Calibration slope and intercept for observed versus predicted mortality.
- Envelope exceedance: output above the p99 and above the observed maximum.
- Parameter-at-bound indicator.

### 4.2 Holdouts

- **Leave-one-TSA-out** where a domain has at least three TSAs with repeat intervals.
- **Leave-one-BEC-variant-out** within a domain; for ESSF and SBPS this is the primary check,
  because the domain has few calibration variants.
- **Temporal holdout:** fit intervals ending before a fixed year, test after it.
- **Site-grouped cross-validation:** no site appears in both training and test.
- **Species holdout** where the sample supports it, especially the minor species.

### 4.3 Acceptance thresholds

| Metric | Target |
| --- | --- |
| BA bias, independent sites | within plus or minus 3 m2/ha or 10 percent |
| TPH bias, independent sites | within 15 percent |
| Mortality calibration slope | 0.8 to 1.2 |
| Mortality intercept | not significantly different from zero |
| Parameters at a bound | none |
| Envelope exceedance, 200-year no-cut | zero above the observed maximum; report p99 exceedance |
| Reproducibility | exact rerun from checksummed data and the recorded FVS commit |

The sample-size table is the check that the target is achievable before fitting. If a domain cannot
meet the threshold, the plan reports that and narrows the claim; it does not relax the threshold
silently. The MDE columns in `domain_summary.csv` are the pre-fit evidence for that decision.

## 5. W2 to W6

W1 closes with this design. The later workstreams are proposals for the maintainer, not commitments.

| Workstream | Tasks | Gate | Reviewer role |
| --- | --- | --- | --- |
| W2 full-domain coverage | The upstream extension in [the W2 package](w2-upstream-work-package.md): parser, species, site index, mortality, growth, BEC tables, build, oracle, pin. | A pinned extension, or a documented go/no-go with cost and evidence. | FVS/variant engineer and maintainer |
| W3 full-domain baseline | Run the W1.4 baseline on the extended variant; residual atlas by BEC, TSA, species, size, and density; envelope per zone. | Initial BA MAE no worse than the W1.4 0.93 m2/ha; no silent default; every unsupported zone named. | Biometrician and data steward |
| W4 domain calibration | Fit capacity, mortality, and growth per domain; bounds; cross-validation; versioned bundles. | No parameter at a bound; the pre-registered holdouts pass or the claim narrows. | Biometrician and maintainer |
| W5 independent validation | Held-out TSAs, BEC variants, years, and species; certificates with a claim boundary. | The acceptance thresholds in section 4.3. | Independent reviewer |
| W6 calibration release | Bundle selection in the CLI/API, provenance, envelope validator, docs, release. | A user can select a certified bundle and the provenance names it; release approval. | Maintainer |

W2 is the gate that decides whether "all of BC" is a supported claim or a documented boundary. It is
not a calibration task and it cannot be promised from `fresh-fvsbc` alone.

## 6. Reviewer sign-off

The maintainer approved a **role-based review** on 2026-11-02: the four roles are the review
structure, and the named individuals are recorded at W2 kickoff. This is a process decision, not a
claim that four named people signed this design. A named reviewer can reopen any row.

| Role | Name | Decision | Date | Evidence |
| --- | --- | --- | --- | --- |
| Maintainer | the maintainer (this thread) | approved for merge | 2026-11-02 | PR #309 |
| FVS/variant engineer | to be named at W2 kickoff | role accepted | 2026-11-02 | Source audit in the W2 package |
| Biometrician | to be named at W2 kickoff | role accepted | 2026-11-02 | Domain/power table and the pre-registration |
| Data steward | to be named at W2 kickoff | role accepted | 2026-11-02 | `manifest.json`, `bec_coverage.csv`, `species_crosswalk.csv` |

Disagreements are recorded in the table with the role and the resolution. They are not averaged away.

## 7. Open decisions for the maintainer

1. **W2 cost ceiling and go/no-go.** Recommended: a bounded spike with CWH first, a ceiling of
   15–25 engineer days and 10–15 reviewer days, and a stop at the gate if the species/site-index
   evidence is absent. The W2 package states the gate in full.
2. **The KC pilot's status.** Recommended: a regional prior and a protocol test, never a
   province-wide certificate and never a multiplier set transferred to another domain.
3. **The first domain.** Recommended: IDF, because the KC protocol is ready and the sample is
   strong; ICH second; SBS/SBPS third because the baseline flags are worst there.
4. **The reviewers.** The maintainer names the four roles above.
5. **If W2 returns "not feasible without X".** Recommended: stop at the seven supported zones,
   publish the boundary, and commission X as a separate upstream project rather than claiming
   coverage the model does not have.

## 8. Reproduce this design

```bash
PYTHONPATH=src python scripts/build_calibration_domains.py \
  --coverage notes/reference/calibration/bec_coverage.csv \
  --baseline notes/reference/calibration/baseline_summary.csv \
  --out-dir notes/reference/calibration
```

The command rewrites `domain_power.csv` and `domain_summary.csv` from the tracked aggregates. It
does not read the site-level extract and it does not fit a parameter.

## References

- `notes/bc-calibration.md`: the programme plan and the W1.6 task.
- `notes/reference/calibration/README.md`: the dataset, its QA, and its limits.
- `notes/reference/calibration/kc-protocol.md`: the protocol this design reuses.
- `notes/reference/calibration/kc-replication.md`: the KC result and its claim boundary.
- `notes/reference/calibration/baseline_report.md`: the uncalibrated baseline.
- `notes/adr/0001-fork-pyfvs-as-the-build-and-ffi-layer.md`, `0004-the-fvsbc-build-recipe.md`,
  `0006-the-build-recipe-is-two-patch-sets.md`, `0008-the-standalone-build-uses-upstream-main.md`,
  `0011-the-bec-is-a-validated-input.md`, `0012-a-calibration-bundle-is-data.md`.
