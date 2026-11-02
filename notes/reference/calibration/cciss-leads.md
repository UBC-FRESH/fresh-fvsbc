# CCISS leads for the missing species

Status: research note; leads, not a data licence
Date: 2026-11-02
Use: W2 upstream package
Sources: `bcgov/CCISS_ShinyApp`, `bcgov/ccissr`, BC Data Catalogue

The CCISS tool is a climate-informed **species suitability** framework, not a
growth model. It cannot supply FVS growth, mortality, volume, or site-index
parameters. It can supply the species list, the BEC and site-series tables, and
the ecological suitability ratings that tell W2 **which species to add and where
they belong**. That is the gap this note fills.

## 1. Where the code and data are

| What | Where | Licence |
| --- | --- | --- |
| Shiny app | `https://github.com/bcgov/CCISS_ShinyApp` | Apache-2.0 |
| R package and tables | `https://github.com/bcgov/ccissr` | Apache-2.0 (DESCRIPTION) |
| BEC tables | BC Data Catalogue, "CCISS Western North America BEC Tables" | Open Government Licence - BC |
| Suitability ratings | BC Data Catalogue, "CCISS Environmental Suitability Ratings" | Open Government Licence - BC |

The app depends on `ccissr` and a remote Postgres/tileserver, so it is not a
local run. The tables are the useful part.

Key files in `ccissr`:

| File | What it holds |
| --- | --- |
| `data-raw/data_tables/Tree speciesand codes_2.0_25Aug2021.csv` | Species code, common name, scientific name, native/exotic, lifeform |
| `data-raw/data_tables/WNA_BGCs_Info_v12_15.csv` | BEC zone/subzone/variant labels, names, BC/AB/US state |
| `data-raw/data_tables/SiteSeries_names_v12_15.csv` | Site-series names by BGC |
| `tables/versioned/suitability_v13_9.csv` | Species suitability by BGC and site series |
| `tables/versioned/Feasibility_v13_7.csv` | Feasibility by BGC and site series |
| `tables/versioned/Edatopic_v13_5.csv` | Edatopic position by site series |
| `data-raw/data_tables/StockingStds/StockStands_v13_1.csv` | Preferred/acceptable species by BGC/site series |
| `data-raw/data_tables/StockingStds/StockingInfo_v13.csv` | Stocking targets and minimums |
| `data-raw/data_tables/StockingStds/StockingHeight_v13.csv` | Stocking height by species/standard |
| `data-raw/data_tables/StockingStds/BEC13crosswalk/LMH77_BGC_su_Crosswalk_v3.csv` | Old-to-new BGC/site-unit crosswalk |
| `tables/regional_updates/Coast_Feb2025.csv` | Coastal feasibility update |

## 2. Coverage in the five missing zones

BC-only units in `WNA_BGCs_Info`:

| Zone | BC BGC units | Site series | Species with E1–E3 | Species missing from FVS-BC |
| --- | ---: | ---: | ---: | --- |
| `CWH` | 19 | 313 | 19 | `Dr`, `Ss`, `Yc`, `Ba`, `Mb`, `Hm` |
| `CDF` | 1 | 14 | 11 | `Dr`, `Mb`; `Ra`, `Qg` minor |
| `BWBS` | 7 | 58 | 8 | `Sb`, `Lt`; `Sx` maps to `SE` |
| `MH` | 8 | 35 | 8 | `Hm`, `Yc`, `Ba`, `Ss` |
| `CMA` | 3 | 0 | 0 | No CCISS suitability rows; out of scope without expert input |

The counts are site-series ratings with suitability E1, E2, or E3, filtered to
BC BGC labels. The top species by rating count are:

- **CWH:** `Cw`, `Hw`, `Dr`, `Ss`, `Yc`, `Pl`, `Ba`, `Ac`, `Mb`, `Hm`.
- **CDF:** `Fd`, `Dr`, `Cw`, `Ac`, `Hw`, `Mb`, `Bg`, `Pl`, `Ra`, `Pw`, `Qg`.
- **BWBS:** `Sx`, `Pl`, `At`, `Ac`, `Sb`, `Bl`, `Ep`, `Lt`.
- **MH:** `Hm`, `Yc`, `Hw`, `Ba`, `Ss`, `Cw`, `Bl`, `Pl`.
- **CMA:** no rows.

This changes the W2 priority. The coastal gap is **six species** (`Dr`, `Ss`,
`Yc`, `Ba`, `Mb`, `Hm`); the boreal gap is **one high-priority** species (`Sb`),
with `Lt` medium and excluded in the species table; the mountain-heather gap is the same coastal species. `Pj` and `Bb` are
not in the BC-only BWBS suitability table; they appear only in cross-border
labels, so they are lower priority than the earlier count suggested.

## 3. The 19 missing subzones

The W1.4 baseline skipped 19 supported-zone subzones. CCISS has 18 of them in
`WNA_BGCs_Info`; `ESSFmv` is not present. The site-series counts are 5 to 14 per
unit. The species set is mostly the interior 15 plus `Ba`, `Hm`, `Pa`, `Sb`, and
`Sx`; the gap is primarily the **BEC/site-series table**, not a new species list.

Examples:

| Subzone | Site series in CCISS | Species in E1–E3 |
| --- | ---: | --- |
| `ESSFwh1` | 10 | interior 15 plus `Ba`, `Hm` |
| `ICHvc` | 13 | `Cw`, `Hw`, `Fd`, `Bg`, `Bl`, `Pl`, `Ba`, `Hm` |
| `IDFxx2` | 14 | `Fd`, `Pl`, `Py`, `Lw`, `At`, `Ep` |
| `MSxv` | 12 | `Sx`, `Pl`, `Bl`, `At`, `Ep` |
| `SBSdh1` | 8 | `Sx`, `Pl`, `At`, `Ep`, `Ac`, `Bl` |

The W2 package should use these tables to add the missing subzone/site-series
entries, then check whether `Ba`, `Hm`, `Pa`, or `Sb` need a species code in that
subzone.

## 4. What CCISS cannot give

- No diameter or height growth equations.
- No mortality or ingrowth parameters.
- No volume, taper, or site-index equations.
- No FVS keyword or tree-list structure.

The `StockingInfo` and `StockingHeight` tables are stocking standards, not growth
curves. They can inform a site-series/species choice, not a `BAIMULT`,
`MORTMULT`, or `BAMAX` value.

For W2, CCISS narrows **which species and BEC units** to add. The growth,
mortality, volume, and site-index parameters still need the FVS source tables,
the BC variant description, and the PSP calibration.

## 5. What to do with it

1. Use the species table to build a crosswalk from CCISS codes to FVS `JSP`
   codes. Mark collisions (`Oc` coast redwood vs FVS `OC` other conifer; `Se` vs
   `Sx`/`Sw`/`Sb`/`Ss`).
2. Use the BC BGC table to add the 19 subzones and the five zones to the W2
   source audit.
3. Use the suitability ratings to rank the species additions. Start with the six
   coastal and `Sb` above; leave `Lt` and the minor Pacific and oak species
   out unless a reviewer asks.
4. Use `StockStands` and `StockingInfo` to cross-check preferred/acceptable
   species by site series.
5. Use `LMH77_BGC_su_Crosswalk_v3` and `Coast_Feb2025` for the BEC13/coastal
   updates.
6. Do not copy the raw tables into the tracked tree. Cite the BC Data Catalogue
   (OGL-BC) and the `ccissr` repository; publish only aggregate, attributed
   facts.

## 6. Reproduce the extraction

```bash
git clone --depth 1 https://github.com/bcgov/ccissr
# the files above are under data-raw/data_tables/ and tables/versioned/
```

The counts in §2 were computed by filtering `suitability_v13_9.csv` to BC BGC
labels from `WNA_BGCs_Info_v12_15.csv` (`State == "BC"`), keeping suitability
1–3, and grouping by `spp`. The site-series counts come from
`SiteSeries_names_v12_15.csv`.

## 7. Licence note

The data is Open Government Licence - British Columbia; the code is Apache-2.0.
Attribution is required for the data. This note records derived counts and
leads, not a copy of the tables.
