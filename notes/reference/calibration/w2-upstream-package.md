# W2 upstream work package

Status: scoped, not started
Date: 2026-11-02
Parent design: `full-domain-design.md`
Scope: make the BC variant resolve the five zones and the 19 subzones it does not
carry today, or record a go/no-go with the cost.

This is an upstream PyFVS/FVS package, not a `fresh-fvsbc` code change. The
Fortran lives in the pinned fork and its FVS source submodule (ADR 0001); this
repository records the pin and tests the wrapper.

## 1. The gap

`canada/bc/habtyp.f` accepts regions `CAR`, `KAM`, and `NEL`, zones `ESSF`,
`ICH`, `IDF`, `MS`, `PP`, `SBS`, and `SBPS`, and a fixed subzone list. It
returns `ICHmw2/01` on failure. `canada/bc/sitset.f` assigns default maximum
basal area for the same zones, and `canada/bc/becset.f` carries the species and
BEC parameter tables. `canada/bc/blkdat.f` carries 15 species.

| Gap | Evidence | What it blocks |
| --- | --- | --- |
| 5 zones | `CWH`, `CDF`, `BWBS`, `CMA`, `MH` are absent from `HABTYP`; 32 variants, 2,911 sites, 10,765 visits | All coastal and boreal calibration |
| 19 subzones | `ESSFdh1`, `ESSFmv1`, `IDFdh`, `SBSdh1`, `MSxv`, and 14 more are absent from the subzone list; 220 sites, 300 intervals | Subzone-specific calibration in the supported zones |
| Species | The 15 `JSP` codes do not cover seven high-priority species: `Dr`, `Ss`, `Yc`, `Ba`, `Mb`, `Hm`, and `Sb`; `Lt` is medium and excluded in CCISS; `Sx` maps to `SE` | Tree-list ingestion and volume/taper/height growth |
| Site index | `SITECODE`/`SETSITE` carry site species and index, but the coastal/boreal site-index curves are not in the variant | Growth and capacity defaults |
| Mortality | The variant's mortality tables are zone/species specific | A calibrated capacity cannot stand without a mortality response |
| BEC tables | `becset.f` parameters are keyed to the zones/subzones it knows | Species growth and height/diameter curves |

The W1.4 baseline is the evidence that the subzone gap is real: 19 variants were
skipped because `BecCode` refused a code the variant would have defaulted.

## 1.1 Leads from CCISS

The CCISS code and data (`bcgov/ccissr`, BC Data Catalogue, OGL-BC) carry the
species codes, the BEC and site-series tables, and the E1–E3 suitability
ratings for the zones the variant does not resolve. `cciss-leads.md` records
the extraction. The priority list is:

- **Coastal:** `Dr` red alder, `Ss` Sitka spruce, `Yc` yellow-cedar, `Ba`
  amabilis fir, `Mb` bigleaf maple, `Hm` mountain hemlock.
- **CDF:** `Dr` and `Mb`; `Ra` arbutus and `Qg` Garry oak are minor.
- **Boreal:** `Sb` black spruce; `Lt` tamarack is medium and excluded in CCISS;
  `Sx` interior spruce maps to `SE` for a first pass.
- **CMA:** no CCISS suitability rows; out of scope without expert input.

The 19 missing subzones are mostly a BEC/site-series gap, not a new species
gap: 18 are in the CCISS BEC table, with 5–14 site series each.

## 1.2 W2.1 result

`w2-crosswalk.md` and its two CSVs are the first W2.1 output. They cover 124
candidate species, seven high-priority missing species, and 218 BC BGC units:
125 supported, 40 missing subzones (18 with PSP intervals), and 53 missing-zone
units (29 with PSP sites). The raw CCISS tables are not committed.

## 2. Work package

### 2.1 Source audit

- Read `canada/bc/habtyp.f`, `sitset.f`, `becset.f`, `blkdat.f`, `BCPLOT.F77`,
  and the mortality/growth routines at the pinned commit.
- Build a matrix of zone → subzone → species → site-index → mortality/growth
  table, marking what exists, what is missing, and what is a stale default.
- Record the exact source lines and the commit. Do not rely on the 2011 variant
  description alone.

### 2.2 Add the zones and subzones

- Extend the region/zone/subzone lists in `HABTYP` for the five zones and the 19
  subzones.
- Add the default maximum-BA entries in `sitset.f` for the new BEC/site-series
  combinations, or an explicit "no default, require `BAMAX`" path.
- Add the species and BEC parameter entries in `becset.f`.
- Add the species codes to `blkdat.f` (JSP, FIA, plant symbol) and the volume,
  taper, height-growth, and mortality tables.
- Keep the `ICHmw2/01` fallback out of the new paths: a missing default must be
  an error, not a silent substitution.

### 2.3 Build and test

- Fork PyFVS, apply the source patch set, and build the BC variant.
- Add a smoke test for each new zone: a synthetic stand with a valid BEC, one
  cycle, a database, and a metric summary.
- Add a resolution test: every new BEC echoes the code and the default maximum
  BA; a missing series is refused.
- Add a species test: each new species resolves in the tree-list writer and the
  model reads it.
- Add a regression test: the existing seven zones and the official case are
  unchanged.
- Pin the fork commit and the FVS source submodule in `fresh-fvsbc`; update ADR
  0004 and the provenance record.

### 2.4 Validate before calibration

- Compare the new zone's default maximum BA and a no-cut run against the local
  PSP envelope.
- Record the source of every new parameter; a value with no source is not
  accepted.
- Run the W1.4 baseline on the newly resolved domains before fitting anything.

## 3. Acceptance criteria

- A valid `CWH`, `CDF`, `BWBS`, `CMA`, or `MH` BEC resolves; `HABTYP` does not
  fall back to `ICHmw2/01`.
- Each of the 19 subzones resolves, or is explicitly refused with a reason.
- A smoke run in each new zone writes `FVS_Summary_Metric`.
- The tree-list writer resolves the new species, and the model reads them.
- The default maximum BA is echoed and matches the source table.
- The existing seven zones and the official case are unchanged.
- The new pin is recorded in `fresh-fvsbc`, with the source commit and the
  variant list.
- The parameter sources and the reviewer sign-off are recorded.

## 4. Go/no-go

W2 returns one of three answers:

1. **Go:** the source can carry the zone, a smoke run works, and the parameters
   have a defensible source. Then W3–W6 extend to it.
2. **Partial:** some zones are feasible and others are not. The programme
   calibrates the feasible ones and records the rest as out of scope.
3. **No-go:** the source lacks species/parameters the zone needs, or the cost is
   beyond the programme. The programme stays at the seven zones, and the
   five-zone gap is recorded as an upstream research project.

A no-go is a valid result. It is better than a variant that resolves a code and
returns a plausible wrong number.

## 5. Risks and cost

| Risk | Why it matters | What reduces it |
| --- | --- | --- |
| Parameter provenance | A default with no source is a guess | Require a source and a reviewer for every value |
| Source drift | The fork may differ from the inspected tree | Read the pinned commit, not `main` |
| Species crosswalk | A coastal code may map to the wrong `JSP` | Test every code against the tree-list writer |
| Model structure | FVS-BC is even-aged; coastal/boreal stands may be uneven-aged | Stratify and state the claim boundary |
| Data scarcity | Some zones have few PSP intervals | Mark validation-only domains; do not fit a rich model |
| Cost | A full variant extension is source development, not a wrapper task | W2 is a bounded spike with a go/no-go |

The cost is not estimated in days here. The audit in §2.1 produces the estimate;
the programme does not commit to a source-development schedule before that
evidence exists.
