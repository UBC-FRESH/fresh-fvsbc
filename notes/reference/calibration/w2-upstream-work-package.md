# W2 upstream work package: the five zones the BC variant does not resolve

Status: proposed, not started
Date: 2026-11-02
Task: W1.6 (#295), W2 package
Parent programme: #289
Gate: a pinned upstream extension, or a documented go/no-go with cost and evidence

This package answers one question: **can the pinned FVS-BC variant represent `CWH`, `CDF`, `BWBS`,
`CMA`, and `MH`?** It is a bounded feasibility and extension workstream, not a promise. A documented
"not feasible without X" is a valid result and better than a claim the model cannot support.

## 1. The gap, in the source

The W1.1 review read the pinned source. The five zones are absent at four layers:

| Layer | Source | What it does today | What is missing |
| --- | --- | --- | --- |
| BEC grammar | `canada/bc/habtyp.f` | Accepts three regions (`CAR`, `KAM`, `NEL`) and seven zones (`ESSF`, `ICH`, `IDF`, `MS`, `PP`, `SBS`, `SBPS`); a code that does not resolve calls the error path and leaves the documented default `ICHmw2/01`. | `CWH`, `CDF`, `BWBS`, `CMA`, `MH` and their subzones/series. |
| Capacity defaults | `canada/bc/sitset.f` | `SELECT CASE (BEC%Zone)` sets `BAMAX`/`SDIDEF` for the seven zones; an unmatched zone falls to `BAMAX = 10` with a warning. | Defaults for the five zones, their subzones, and series. A silent 10 m2/ha is not acceptable. |
| Version 2 calibration | `canada/bc/becset.f` | Calibration cases are keyed to named PP, MS, and ESSF site series; the model has no case for the five zones. | BEC-specific calibration cases, or a documented donor and its limits. |
| Species | `canada/bc/bcspp.f`, `canada/bc/blkdat.f` | Maps input species to BC's 15. Many codes map to index 14 (other conifer) or 15 (other hardwood); `species_crosswalk.csv` has 37 observed PSP codes, 24 outside BC's 15 and marked `UNKNOWN`. | A decision per species: add it, map it to a documented donor, or record it as unsupported. |

The mortality, height-growth, and diameter-growth coefficients live in `canada/bc/morts.f`,
`canada/bc/htgf.f`, and `canada/bc/dgdriv.f`. They are species- and site-series-specific arrays, not
a generic curve. **The five zones need an audit of those arrays, not only a parser entry.** A parser
patch that lets `CWH` through and then uses interior spruce coefficients would be worse than the
current refusal: it would produce a plausible number with no evidence.

## 2. What the data can support

The W1.2 coverage table counts the five zones but contributes no interval, tree-survival, or envelope
row, because the variant cannot run them:

| Zone | BEC variants | Sites | Repeat sites | What it means |
| --- | ---: | ---: | ---: | --- |
| `CWH` | 22 | 2,335 | 2,178 | The largest unsupported zone by an order of magnitude; the first target. |
| `BWBS` | 5 | 534 | 336 | A real second target; boreal mixedwood and white spruce. |
| `CDF` | 1 | 26 | 21 | Small but distinct; likely a validation-only zone even after the extension. |
| `MH` | 3 | 13 | 12 | Small; a parser and species test, not a calibration domain. |
| `CMA` | 1 | 3 | 2 | Too few sites for a calibration; a parser-only pilot or a documented non-target. |

The unsupported zones have **2,911 sites** in total, in `CWH`, `CDF`, `BWBS`, `CMA`, and `MH`.
The rest of the W1.2 archive is already in the seven supported zones. The sample is not random: the
PSP plots over-represent older, accessible stands, and `CWH` is the largest but also the most
heterogeneous. The W2 answer must state the sample limit, not only the site count.

## 3. Work packages

### W2.1 BEC grammar and defaults

- Extend `HABTYP`'s zone and subzone tables for `CWH`, `CDF`, `BWBS`, `CMA`, and `MH`, including the
  region tokens the five zones use.
- Add `SITSET` cases for the zone/subzone/series combinations that have a documented maximum basal
  area. A missing series gets a **named** default and a warning, never the silent 10 m2/ha.
- Add `BECSET` cases only where a coefficient exists. If a zone has no calibrated case, the
  extension must say so at run start, not fall through to an interior case.
- Extend `fresh_fvsbc.bec.BecCode` and its tests so the parser and the Fortran table cannot drift.

**Acceptance:** each zone parses at least one real series; a malformed code is refused; a missing
series is reported by name; no run reaches `BAMAX = 10` without a warning.

### W2.2 Species crosswalk

- Triage the 24 `UNKNOWN` codes in `species_crosswalk.csv`. For each, decide: add a species, map to
  a documented donor, or mark unsupported.
- Estimate the species coverage by live basal area in each zone. The target is **at least 90 percent
  of live BA covered by an explicit decision**, or the uncovered share is stated.
- Adding a species changes `MAXSP`, the coefficient arrays, and the volume equations; treat it as a
  model change, not a string alias.
- Keep the crosswalk table in the repository; it is aggregate and public.

**Acceptance:** every observed code in the five zones has a decision; the coverage share is reported;
no `UNKNOWN` code is silently dropped.

### W2.3 Site index and the BEC × species table

- Join the PSP site index to the site-level extract. The W1.4 baseline used `SITECODE FD,20` as a
  placeholder; that is not a site-index measurement.
- Build a BEC × species site-index table with counts and uncertainty. Use it to set `SITECODE` in the
  W2 test cases.
- Compare the new defaults with `sitset.f`'s `BAMAX`/`SDIDEF` values; a mismatch is a finding, not a
  reason to overwrite the model.

**Acceptance:** every W2 test case names its site-index source; the placeholder is gone; the table
carries counts and a checksum.

### W2.4 Mortality and growth coefficients

- Audit `morts.f`, `htgf.f`, `dgdriv.f`, and `becset.f` for zone- and species-specific arrays.
- Add a coefficient only where the public source or a documented analysis supports it. Do not copy
  an interior coefficient into a coastal or boreal zone because it is the nearest available.
- Run a 50-interval baseline per zone with no calibration. The purpose is to check the tree list,
  the BEC, and the default trajectory, not to fit a parameter.
- Record every coefficient source and the FVS commit in the W2 report.

**Acceptance:** a 50-interval baseline runs in each zone; the initial stand is reproduced within the
W1.4 tolerance (initial BA MAE no worse than 1.0 m2/ha); the trajectory is reported without a
calibration claim.

### W2.5 Build, oracle, and pin

- Build the extension in the PyFVS fork with the patch sets in ADR 0004 and ADR 0006.
- Add a `CWH` case to the standalone oracle. The comparison must use the same `DSNin` route and the
  same `tree_num` reading as the existing harness.
- Compare `FVS_TreeList_Metric` and `FVS_Summary_Metric` value for value. A difference is attributed
  or the gate fails.
- Pin the fork and the FVS source commit in `fresh-fvsbc`; record the built variant in provenance and
  release notes.
- Build a wheel with the existing `wheels.yml` path; the extension is Fortran, so the wheel is the
  install.

**Acceptance:** a clean clone applies both patch sets, builds, produces the one CWH case, and the
package records the pins. The oracle matches or the difference is explained.

## 4. Gate: go/no-go

W2 passes only when all of these hold:

| Gate | Test | If it fails |
| --- | --- | --- |
| G1 grammar | Each of the five zones parses a real series; a malformed code is refused. | Parser work continues; no calibration. |
| G2 defaults | Each zone has a documented `BAMAX`/`SDIDEF` for at least one series; no silent 10. | Stop; the zone cannot be run honestly. |
| G3 species | At least 90 percent of live BA has an explicit species decision, or the gap is stated. | Narrow the zone or stop. |
| G4 baseline | A 50-interval no-cut baseline runs; initial BA MAE no worse than 1.0 m2/ha. | Investigate the tree list/BEC before any fit. |
| G5 oracle | One case per zone matches `FVS_TreeList_Metric` and `FVS_Summary_Metric`. | Attribute the difference or stop. |
| G6 build | Clean clone + patch sets + pin reproduces the build; provenance records both commits. | Fix the build before a release. |
| G7 cost | The work stays within the approved ceiling. | Stop and report the overrun. |

A **partial pass** is allowed only with the maintainer's approval: for example, `CWH` passes and
`CMA` is documented as not calibratable because it has three sites. The programme then claims only
what passed.

## 5. Cost estimate

The KC pilot is the unit of work: one domain, 24 plots, one region, two BEC variants. It cost about
**one compute day** for the runs and the grid, and **two to three reviewer days** to check the BEC,
the envelope, the bounds, and the claim.

W2 is not five times that. The parser, build, patch set, and oracle are shared, but each zone needs
its own species, site-index, and coefficient review. A planning estimate, to be refined after the
source audit:

| Item | Engineer days | Reviewer days |
| --- | ---: | ---: |
| Shared parser, build, oracle, pin | 5–8 | 3–5 |
| `CWH` (species, site index, coefficients, baseline) | 5–8 | 4–6 |
| `BWBS` | 3–5 | 3–4 |
| `CDF` | 2–3 | 2–3 |
| `MH` | 1–2 | 1–2 |
| `CMA` | 0.5–1 (or document as non-target) | 0.5–1 |
| **Total** | **15–25** | **10–15** |

The estimate is a ceiling for a bounded spike, not a quote. If the species or coefficient evidence is
not in the public source, the cost is open-ended and the answer is "not feasible without X"; the
gate stops there.

## 6. Risks

| Risk | Why it matters | What reduces it |
| --- | --- | --- |
| The missing coefficients are not recoverable from the public source | A parser patch alone would produce plausible numbers with no evidence. | The source audit comes first; the gate can return "not feasible without X". |
| The five zones are structurally different from the interior | FVS-BC is an even-aged individual-tree model; coastal and boreal stands may be uneven-aged or mixed. | State the structural limit; stratify by regime; do not claim a selection-system model. |
| The PSP sample is not random | CWH over-represents older, accessible stands. | Report the sample limit; use TSA and variant holdouts. |
| Species additions are a model change | `MAXSP`, coefficient arrays, and volume equations all move. | Treat each addition as a reviewed change with its own test. |
| Site index is not joined | The capacity default would stay a placeholder. | Build the BEC × species table before the baseline. |
| Upstream source drifts | The pinned tables may not match the code. | Record the FVS commit and patch sets with every build. |
| Review capacity is the bottleneck | A calibration without review is not a certificate. | Name the reviewers before W2 starts. |

## 7. Open questions for the maintainer

1. Is the cost ceiling in section 5 approved, or should W2 be a smaller CWH-only spike?
2. Is `CMA` a non-target because it has three sites, or must it be parsed only?
3. Which reviewer signs the W2 go/no-go?
4. If G3 fails for a zone, is the answer "narrow the zone" or "commission a new species model"?
5. If G4 fails, does W2 stop or continue to W4 with a stated baseline failure?

## References

- `notes/bc-calibration.md`: the programme plan and the W1.6 task.
- `notes/reference/calibration/domain-design.md`: the domain and power design.
- `notes/reference/calibration/bec_coverage.csv`: the five zones' site and repeat counts.
- `notes/reference/calibration/species_crosswalk.csv`: the 24 unknown species codes.
- `notes/adr/0001-fork-pyfvs-as-the-build-and-ffi-layer.md`: the fork and the source submodule.
- `notes/adr/0004-the-fvsbc-build-recipe.md`: the build recipe.
- `notes/adr/0006-the-build-recipe-is-two-patch-sets.md`: the two patch sets.
- `notes/adr/0008-the-standalone-build-uses-upstream-main.md`: the standalone oracle.
