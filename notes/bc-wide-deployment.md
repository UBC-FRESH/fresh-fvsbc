# Deploying FVS-BC across British Columbia

Status: active plan
Owner: the maintainer and the agent
Parent issue: to be created from this note
Goal: **a runnable, calibrated, validated FVS-BC for every BC BEC unit and every provincial tree species.**

This is not a feasibility study and the five missing zones are not a no-go. They are work packages. We have the
public PSP archive, the CCISS crosswalk, the BC BEC space, the FVS source, and a build recipe. The unknown is
coefficient quality, not access.

## 1. Definition of done

1. **Coverage.** Every BEC unit in the provincial PSP archive resolves, or is refused with a named reason. The
   five zones and their 53 CCISS BGC units are included, not excluded.
2. **Species.** Every provincial tree species in the PSP/CCISS data has an FVS code or a documented donor
   mapping. The seven high-priority missing species are modelled explicitly where the evidence supports it.
3. **Runnable.** A clean wheel builds and runs a case in every zone, and the run echoes its BEC and default
   `BAMAX`.
4. **Baseline.** An uncalibrated all-zone baseline exists, with a residual atlas by BEC, TSA, species, size, and
   density.
5. **Calibration.** Capacity, mortality, and growth parameters are fitted by domain/species group, with no
   parameter at a bound and with cross-validation.
6. **Validation.** Each domain has an independent holdout and a certificate that states its claim boundary.
7. **Deployment.** `pip install "fresh-fvsbc[fvs]"` runs all certified domains; the envelope validator flags or
   refuses an out-of-domain run; provenance records the bundle and pins.
8. **Operations.** The web UI, CLI/API, docs, release process, and review cadence are in place.

## 2. The strategy: prototype now, calibrate next

We do **not** wait for a perfect species model before making the province runnable. We stage it:

- **Stage A — donor-alias prototype.** Keep the 15 `JSP` species. Map the seven missing species to the nearest
  donor (`Ss`/`Sb`→`SE`, `Ba`→`BG`, `Hm`→`HW`, `Yc`→`CW`, `Dr`→`AT`, `Mb`→`AC`). Add the five zone tokens
  and provisional `BAMAX` from the PSP envelope. Build and smoke. This is a **prototype**, not a certificate.
- **Stage B — true species tables.** Add the seven species to `MAXSP` and every model component only after the
  prototype shows which donor aliases fail. This is a parameter-development task, with the PSP data as the
  fitting source and the literature as the prior.
- **Stage C — calibration.** Fit the species/zone multipliers within bounds; validate on held-out sites, TSAs,
  BEC variants, and years.
- **Stage D — deployment.** Release the certified bundle set, the envelope validator, and the web surface.

This is how the seven supported zones were built: first make it run, then measure, then fit, then certify.

## 3. Work packages

| ID | Work package | Output | Gate |
| --- | --- | --- | --- |
| D1 | All-zone dataset and envelope | `all-zone` coverage, envelope, species envelope for the five zones; p99/max by BEC | Data builds; five-zone rows exist; no site IDs tracked |
| D2 | BEC parser and defaults | Five zone tokens and the 32 PSP BEC labels in `habtyp.f`; `BAMAX` cases in `sitset.f`; wrapper `BecCode` | Every label parses; every default is source-backed or explicitly provisional; no 10 m2/ha silent fallback |
| D3 | Species alias prototype | Wrapper `DONOR_SPECIES` and `bcspp.f` donor mappings for the seven species; crosswalk table with the donor and the reason | Every PSP species in the five zones maps to a code; the mapping is recorded |
| D4 | Build and smoke | Patched PyFVS/FVS fork; built BC wheel; one case per zone/label | Every smoke case echoes BEC and BAMAX and writes a database; existing zones unchanged |
| D5 | Provincial baseline | All-zone uncalibrated baseline; residual atlas by BEC/TSA/species/size/density | Initial stand check; envelope flags; every unsupported unit named |
| D6 | Parameter development | True species tables or accepted donors; mortality/growth/crown/bark/volume/regeneration coefficients with sources | A 50-interval baseline per zone; initial BA MAE no worse than the W1.4 0.93 m2/ha; donor substitutions stated |
| D7 | Calibration and validation | Domain/species bundles; independent holdouts; certificates | No parameter at a bound; pre-registered thresholds; certificate per domain |
| D8 | Deployment and operations | Wheel pin, envelope validator, CLI/API, web UI, docs, review cadence | Clean install runs every certified domain; provenance names the bundle; release approved |

## 4. What we do first (the next 30 days)

### Week 1 — D1: all-zone dataset

- Add an `--all-zones` path to `build_calibration_dataset.py` / `build_dataset` that reads every site, not only
  the seven supported zones.
- Write `all-zone` coverage, envelope, and species-envelope tables. Keep the tree-level tables out of the repo.
- Extract p99/max `BAMAX` candidates for `CWH`, `CDF`, `BWBS`, `CMA`, and `MH`.
- Record the five-zone site/interval counts and the species present.

**D1 result (2026-11-03):** the all-zone build read **7,341 sites, 23,956 visits, 3,205,741 tree rows**, and
produced **17,151 intervals and 1,814,527 tree-survival rows** across all **153 BEC variants**. The five zones
now have envelope rows:

| Zone | Labels | Sites | Repeat sites | Intervals | BA p99 range | BA max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `CWH` | 22 | 2,335 | 2,178 | 7,124 | 88.5–165.7 | 230.2 |
| `CDF` | 1 | 26 | 21 | 94 | 111.9 | 153.1 |
| `BWBS` | 5 | 534 | 336 | 710 | 51.4–69.6 | 71.6 |
| `CMA` | 1 | 3 | 2 | 6 | 93.2 | 93.2 |
| `MH` | 3 | 13 | 12 | 31 | 83.8–122.5 | 123.6 |

`w2-five-zone-defaults.csv` carries 32 provisional `BAMAX` values with a confidence column. **Fourteen CWH
labels, four BWBS labels, and CDF are high-confidence**; `CWHwh`, `CWHwm`, `CMAunp`, `MHmm2`, and `MHwh1` are
low and are pilot/validation units, not capacity claims.

**Deliverable:** done; the aggregate tables are in `notes/reference/calibration/all-zone/`.

### Week 2 — D2/D3: parser and donor aliases

- Add `CWH`, `CDF`, `BWBS`, `CMA`, `MH` to the BEC parser and the missing subzone tokens.
- Map the seven high-priority species in the wrapper `DONOR_SPECIES` (and the matching `bcspp.f` donor paths); record the mapping in `w2-species-bec-crosswalk.csv`.
- Add `BAMAX` cases for the five zones from the D1 p99 values; mark them provisional.
- Add the wrapper `BecCode` tokens and tests.

**D2/D4 result (2026-11-03):** the parser and defaults are built and smoke-tested. `CWH`, `CDF`,
`BWBS`, `CMA`, and `MH` are in `ZN(12)`; `SZ` is 34 with `DS`, `MS`, `VH`, `VM`, `WS`; `sitset.f` has
all 32 provisional `BAMAX` cases. A clean `fresh-fvsbc-pyfvs 0.4.0` build reports BC OK, and **32/32
labels echo their own BEC and provisional BAMAX and write a database** (`w2-five-zone-smoke.csv`). The
build found three parser defects: the zone loop still stopped at 7, the subzone loop at 29, and the
subzone search matched inside the zone name (`CWH` contains `WH`, `MH` contains `MH`) and the zone
search matched a subzone (`CWHms` contains `MS`). The parser is now anchored to the grammar. The
species smoke is still `FD`; D3 owns the seven donor aliases and species-specific cases. The patch is
`w2-five-zone.patch.gz` and the D6 `w4-sbps-small-tree.patch.gz` are now applied by the CI/wheel
recipe, which builds `0.4.1`; that wheel is released in `0.21.3`, but the wrapper still refuses the
five zones. The build recipe and the wrapper tokens are therefore a release task, not evidence that the
zones are deployed.

**Deliverable:** the 32-label prototype; see `w2-five-zone-prototype.md`.

**D3 result (2026-11-03):** the wrapper now resolves `Ss`, `Sb`, `Ba`, `Hm`, `Yc`, `Dr`, and `Mb`
through an explicit `DONOR_SPECIES` table (`SE`, `SE`, `BG`, `HW`, `CW`, `AT`, `AC`). **7/7 species
smoke pass**: the input code runs, the output `SpeciesFVS` carries the donor, each case echoes its
five-zone BEC and BAMAX, and each writes a database (`w2-five-zone-species-smoke.csv`). The alias is
not silent: it is a public mapping, tested, and the output says which donor it used. True species
tables are D6.

### Week 3 — D4: build and smoke

- Apply the patch to the PyFVS/FVS fork, build the BC variant, and run one case per zone/label.
- Read the `STDINFO BEC=` and `BAMAX` echoes; run the seven-zone controls.
- Record the new pin and the patch set.

**Deliverable:** a wheel that runs `CWH`, `BWBS`, `CDF`, `MH`, and `CMA`, with the donor aliases stated.

### Week 4 — D5: first provincial baseline

- Run the uncalibrated baseline on the five zones and the seven supported zones.
- Compare initial and next-measurement BA/TPH; build the residual atlas.
- Decide which donor aliases are good enough for Stage B and which need true species tables.

**D5 result (2026-11-03):** the all-zone baseline ran **139 BEC strata, 139 intervals, 0 skipped** on
the 0.4.0 five-zone build. The initial stand is reproduced (BA bias -0.69, MAE 0.84). Excluding SBPS
and envelope-flagged rows, the end-of-interval BA bias is **-5.27 m2/ha** and MAE **8.45** (n=130).
The five zones have **no envelope flags** and moderate BA MAE (CWH 11.75, BWBS 7.93, CDF 18.85, CMA
3.46, MH 11.94). **SBPS is the supported-zone failure**: `SBPSmc` predicts 457,348 m2/ha against
30.65 observed, with `SBPSdc` and `SBPSmk` also above max. The donor aliases produced **0 skips**, so
the species layer works. D6 priority is SBPS small-tree density/mortality, not the coastal donors;
the five-zone sample moves to five intervals per BEC before any true species table is promoted.
`d5-all-zone-baseline.md` is the report.

**Deliverable:** done; the residual atlas is in `notes/reference/calibration/all-zone-baseline/`.

### Week 4 — D6: parameter development

**D6 SBPS result (2026-11-03):** the SBPS explosion was a source defect, not a density or mortality
parameter. `REGENT` selected the hyperbolic SBS/SBPS small-tree height model only when
`BEC%Zone` contained `SBS`; `SBPS` matched neither and took the exponential IDF/ICH branch with
SBS-form coefficients, overflowing to `Infinity`. The five `REGENT` model-selection tests now accept
`SBPS` too. `w4-sbps-small-tree.patch.gz` banks the fix; it is released as
`fresh-fvsbc-pyfvs 0.4.1`. The corrected SBPS baseline is physical but uncalibrated: BA is
`SBPSdc` 28.0 vs 11.23, `SBPSmc` 48.0 vs 30.65, `SBPSmk` 35.0 vs 32.72, and `SBPSxc` 53.0 vs 34.39.
The D7 target is the remaining growth residual, not `MORTMULT` or `BAMAX` alone. See
`d6-sbps-small-tree.md`.

**D6 five-zone result (2026-11-03):** the five-zone baseline at five intervals per BEC ran **153
intervals, 31 labels, 0 skipped intervals** on the 0.4.1 build with the prototype wrapper
tokens. Initial BA bias is **-0.78** and MAE **1.14**. End BA is underpredicted in every zone:
CWH -12.31 / 13.04, CDF -20.45 / 20.45, BWBS -9.47 / 9.47, CMA -5.67 / 5.67, MH -12.46 / 12.80
(bias / MAE, m2/ha). One interval is above p99 and none above the observed maximum. The donor
aliases are exercised heavily (`Ba` 2,448 records, `Ss` 503, `Hm` 289, `Yc` 219, `Dr` 149, `Mb` 129,
`Sb` 67); six intervals have unresolved non-donor trees. **No species is promoted to a true table
yet**: the residuals are a broad growth underprediction, so `Ba`→`BG` and `Hm`→`HW` are the first
D7 candidates only after the shared growth path is tested. See `d6-five-zone-baseline.md`.

**Deliverable:** D6 evidence is complete for the SBPS fix and the five-interval five-zone baseline;
the SBPS wheel is released in `0.21.3`; the five-zone wrapper tokens remain unreleased.

### Week 4 — D7: calibration and validation

**D7.1 SBPS readiness result (2026-11-03):** no global SBPS bundle is identified. The probe evaluates
a fixed candidate set on **15 eligible intervals** (initial BA >= 15 m2/ha, QMD >= 8 cm, dead BA <=
40% of initial BA) with a site-grouped holdout. The best training compromise, `BAMAX 45` plus
`BAIMULT 0.5` for PL/SE, has held-out BA bias **+6.08 / MAE 8.06** and TPH bias **-214.82 / MAE
214.82**. `BAMAX 55` improves TPH but raises held-out BA bias to **+10.08**; `BAMAX 40` plus
`MORTMULT 2` lowers BA by over-killing TPH (held-out bias **-1,314.82**). The measured PSP site index
is not a lever: FVS reports `SITE INDEX IS NOT USED IN THIS VARIANT`, and the `SITECODE PL <SI>` and
`SITECODE FD,20` runs are identical. `SBPSdc` is already close (baseline BA bias -0.39 / MAE 1.35);
`SBPSmc` has one eligible interval, and the excluded young/high-mortality stands need structural
treatment. The reusable probe is `scripts/run_calibration_probe.py`; the report is
`d7-sbps-readiness.md`. **No parameter changed and no bundle is issued.**

## 5. Data and methods

### Data

- **PSP archive:** 7,341 sites, 23,956 visits; 4,430 sites and 13,191 visits in the seven supported zones;
  2,911 sites and 10,765 visits in the five unsupported zones.
- **Five-zone coverage:** `CWH` 22 BEC labels / 2,335 sites / 2,178 repeat sites; `BWBS` 5 / 534 / 336;
  `CDF` 1 / 26 / 21; `MH` 3 / 13 / 12; `CMA` 1 / 3 / 2.
- **CCISS crosswalk:** 124 candidate species; seven high-priority missing species (`Dr`, `Ss`, `Ba`, `Hm`,
  `Yc`, `Sb`, `Mb`); 53 missing-zone BGC units, 29 with PSP sites.
- **Source:** `habtyp.f` (zones/subzones), `sitset.f` (`BAMAX`), `bcspp.f`/`blkdat.f` (species),
  `morts.f`, `htgf.f`, `dgdriv.f`, `crown.f`, `bratio.f`, `min.f`/taper, `regent.f`, `becset.f`.

### Methods

- **Capacity:** p99 and max BA by BEC from the all-zone dataset; a `BAMAX` grid; report the asymptote and its
  uncertainty.
- **Species:** donor mapping first; true species only where the donor fails a pre-set residual threshold.
- **Mortality:** fit `MORTMULT` by species group and zone using the tree-survival rows; use donor coefficients
  as priors, not as a silent default.
- **Growth:** fit `BAIMULT` and height/diameter growth separately; growth and mortality are confounded.
- **Validation:** leave-one-TSA-out, leave-one-BEC-variant-out, temporal holdout, site-grouped folds, species
  holdout where the sample supports it.
- **Thresholds:** BA bias within ±3 m2/ha or 10%; TPH bias within 15%; mortality slope 0.8–1.2; intercept not
  significantly different from zero; no parameter at a bound; zero predictions above the observed maximum;
  exact reproducibility from checksums and pins.

## 6. Risks, and what we do about them

These are engineering risks, not reasons to stop.

| Risk | Response |
| --- | --- |
| A donor species may grow the wrong way | Measure the donor residual first; promote the species to a true table only where the residual fails. |
| PSP has few CWH/BWBS sites for a species | Pool by species group, use the CCISS suitability and the literature as a prior, and widen the uncertainty. |
| The model is even-aged and some coastal stands are uneven-aged | Stratify by regime and state the claim boundary; do not claim a selection-system model. |
| Adding a species expands `MAXSP` and every array | Do it in one reviewed patch; add one species at a time with a smoke case. |
| Volume/taper and regeneration are not in the PSP extract | Use the FVS donor equations first; add species-specific equations only with a source. |
| The 2,911 unsupported sites are not a random sample | Report the sample limit; use TSA and variant holdouts. |
| Review capacity | Name the reviewer at each gate; the maintainer signs the release. |

## 7. Timeline

| Window | Outcome |
| --- | --- |
| 0–30 days | All-zone dataset, parser, donor aliases, built wheel, first five-zone smoke |
| 1–3 months | All-zone baseline and residual atlas; true species decisions |
| 3–6 months | Mortality/growth/capacity fits for CWH and BWBS; CDF/MH pilots |
| 6–12 months | Independent validation and certificates; CMA decision |
| 12+ months | Provincial release, envelope validator, web deployment, review cadence |

The dates are targets, not promises. The first 30 days are concrete and do not depend on a partner.

## 8. Claim boundary

Until a domain is calibrated and independently validated, its output is **exploratory**. The donor-alias
prototype makes the province runnable; it does not make it calibrated. Every release states which domains are
certified and which are prototype-only. No result is a legal, AAC, or whole-block claim.
