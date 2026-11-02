# W2 species and BEC crosswalk

Status: W2.1 evidence; leads, not a growth calibration
Date: 2026-11-02
Sources: `bcgov/ccissr`, BC Data Catalogue (OGL-BC)
Tables: `w2-species-bec-crosswalk.csv`, `w2-bec-gap.csv`

This crosswalk turns the CCISS species and BEC tables into the two lists W2
needs: **which species are missing from the BC variant**, and **which BEC units
the variant cannot resolve**. It is a suitability crosswalk, not a growth model.

## 1. Method

1. Read the CCISS species table
   (`Tree speciesand codes_2.0_25Aug2021.csv`), the BC BGC units
   (`WNA_BGCs_Info_v12_15.csv`, `State == "BC"`), the site-series names
   (`SiteSeries_names_v12_15.csv`), and the suitability table
   (`suitability_v13_9.csv`).
2. Keep suitability ratings **E1, E2, or E3**; drop E4/E5 and missing.
3. Map each CCISS code to an FVS `JSP` code, or mark it `MISSING`.
4. Test each BGC label with `fresh_fvsbc.bec.BecCode`:
   - `supported` — the zone and subzone resolve;
   - `missing-subzone` — the zone resolves, the subzone does not;
   - `missing-zone` — the zone does not resolve.
5. Join the PSP coverage (`bec_coverage.csv`) to mark which units actually have
   sites and intervals.

The species table marks some codes `Exclude = x` (for example `Lt` tamarack).
The crosswalk keeps them, marks `excluded_in_cciss = x`, and gives them a lower
priority rather than dropping them silently.

## 2. Species crosswalk

`w2-species-bec-crosswalk.csv` has one row per candidate species:

| Column | Meaning |
| --- | --- |
| `cciss_code` | CCISS tree code |
| `common_name`, `scientific_name` | The species |
| `native` | `N`, `P`, or `E` from the CCISS table |
| `lifeform` | `1` conifer, `2` broadleaf |
| `excluded_in_cciss` | `x` when the source excludes the code |
| `fvs_code` | The FVS `JSP` code, or blank |
| `status` | `FVS`, `MISSING`, or `COLLISION` |
| `zones` | BC zones where the species has E1–E3 ratings |
| `e1_e3_ratings` | Number of BC site-series ratings at E1–E3 |
| `priority` | `high`, `medium`, or `low` |

**124 candidate species.** Seven are high priority and missing from the BC
variant:

| Code | Species | Zones | E1–E3 ratings |
| --- | --- | --- | ---: |
| `DR` | red alder | CDF, CWH | 164 |
| `SS` | Sitka spruce | CWH, MH | 153 |
| `BA` | amabilis fir | CWH, ESSF, ICH, MH | 142 |
| `HM` | mountain hemlock | CWH, ESSF, ICH, MH | 133 |
| `YC` | yellow-cedar | CWH, ESSF, MH | 115 |
| `SB` | black spruce | BWBS, ESSF, ICH, SBPS, SBS, SWB | 96 |
| `MB` | bigleaf maple | CDF, CWH, IDF | 62 |

`Lt` tamarack is medium priority and is excluded in the CCISS species table.
`Sx` interior spruce, `Sw` white spruce, and `Ss` Sitka spruce are the spruce
group; the crosswalk marks `Ss` missing and `Sx`/`Sw`/`Sb` as missing with a note
that `SE` may substitute for a first pass. The final decision is W2.3's.

**Code collision:** CCISS `Oc` is coast redwood; FVS `OC` is "other conifer".
The crosswalk marks `Oc` as a collision, not an FVS code.

## 3. BEC gap

`w2-bec-gap.csv` has one row per BC BGC unit:

| Column | Meaning |
| --- | --- |
| `bcg` | BGC label |
| `zone` | BEC zone |
| `status` | `supported`, `missing-subzone`, `missing-zone` |
| `domain` | The W1.6 calibration domain, when one applies |
| `site_series` | Site-series count in CCISS |
| `psp_sites`, `psp_intervals` | The PSP archive's coverage for that label |
| `missing_species` | Species with E1–E3 ratings there that the variant lacks |

Counts over the 218 BC BGC units:

| Status | Units | With PSP data |
| --- | ---: | ---: |
| `supported` | 125 | — |
| `missing-subzone` | 40 | 18 with intervals |
| `missing-zone` | 53 | 29 with sites |

The W1.4 baseline saw 19 missing subzones; 18 are in CCISS, and `ESSFmv` is not.
The five unsupported zones have 32 BEC labels in the PSP archive; 29 are in
CCISS. The extra CCISS units are non-forested, alpine, or outside the PSP
archive; they are still listed so the source audit sees the full BEC space.

`CMA` has three BC units and no suitability rows. It is out of scope without
expert input.

## 4. What this changes in W2

- The coastal species gap is **seven high-priority species**, not a generic
  "coastal mix": `DR`, `SS`, `BA`, `HM`, `YC`, `MB`, plus `SB` for the boreal
  zone.
- The 18 missing subzones with PSP data are mostly a **BEC/site-series table
  gap**, not a new-species gap; the interior 15 plus `BA`/`HM` cover them.
- `Sx`/`Sw`/`Sb`/`Ss` need a decision: distinct species codes, or a single
  spruce code with a documented substitution.
- `Pj` and `Bb` are not high priority in the BC-only data.
- The crosswalk does **not** supply growth, mortality, volume, or site-index
  parameters. Those still need the FVS source tables and the PSP calibration.

## 5. Reproduce

```bash
git clone --depth 1 https://github.com/bcgov/ccissr
# read:
#   data-raw/data_tables/Tree speciesand codes_2.0_25Aug2021.csv
#   data-raw/data_tables/WNA_BGCs_Info_v12_15.csv
#   data-raw/data_tables/SiteSeries_names_v12_15.csv
#   tables/versioned/suitability_v13_9.csv
#   notes/reference/calibration/bec_coverage.csv (from W1.2)
```

The filters are the five steps in §1. The species and BEC tables are OGL-BC;
the `ccissr` code is Apache-2.0. The raw tables are not committed; only the
derived crosswalk is.

## 6. Claim boundary

This is a **suitability** crosswalk. A species can be ecologically suitable and
still lack the FVS growth, mortality, volume, or site-index parameters. W2.1
says which species and BEC units need attention; it does not say the variant can
grow them correctly.
