# D9.3 DBH-limit audit: the non-PSP TPH gap is a tagging-limit mismatch

Date: 2026-11-04. Public standards read and quoted below.

## Sources

**Provincial Monitoring Ground Sampling Procedures and Appendices, version 4.0 (April 2024)**
https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/stewardship/forest-analysis-inventory/ground-sample-inventories/provincial-monitoring/standards/provincial_monitoring_ground_sampling_procedures_and_appendices_ver40.pdf

- §3.1: tree-detail plots are a 5.64 m fixed-radius plot for trees **≥4.0 cm DBH** and an 11.28 m
  fixed-radius plot for trees **≥9.0 cm DBH**; small trees are **<4.0 cm DBH**.
- §6.6 “PSP Specific Remeasurement Procedures”: **main tree plot DBH limit 4.0 cm; subplot tagging
  limit 2.0 cm**; the small-tree plot is the same as CMI. The PSP third small-tree tally class has
  an upper limit of **2.0 cm**, not 4.0 cm.

**Vegetation Resources Inventory Ground Sampling Procedures (2018)**
https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/nr-laws-policy/risc/vri_ground_sampling_procedures_2018.pdf

- Tree-detail plot: **live and dead trees 4.0 cm DBH and larger**.
- Small-tree tally: live trees **<4.0 cm DBH** and >10 cm in length.

The standards therefore **do not have a common DBH lower limit**:

| Program | Main tree plot | Subplot / tree detail | Small tree |
| --- | ---: | ---: | ---: |
| PSP | ≥4.0 cm | **≥2.0 cm** | <2.0 cm third class |
| CMI / YSM / VRI / NFI | ≥9.0 cm | **≥4.0 cm** | <4.0 cm |

The earlier note calling the temporary-VRI TPH difference a “weight mismatch” was wrong. It is a
**diameter-limit / aggregation mismatch**.

## Evidence from the downloaded data

Local PSP tree detail contains 2–4 cm trees:

- mean live TPH at **≥2 cm**: 1,959.8
- mean live TPH at **≥4 cm**: 1,706.8
- mean live TPH at **≥9 cm**: 1,148.0

Temporary VRI tree detail compared with the compiled summary:

| DBH cutoff | BA bias | BA MAE | TPH bias | TPH MAE |
| ---: | ---: | ---: | ---: | ---: |
| ≥4 cm | +2.81 | 31.11 | +2,779 (+79%) | 2,977 |
| ≥7 cm | -1.61 | 28.47 | +868 (+25%) | 1,392 |
| ≥9 cm | -5.87 | 26.28 | +15 (+0.4%) | 1,043 |

The entire +79% TPH discrepancy is in the **4–9 cm subplot component**. It vanishes at the 9 cm
main-tree limit. This is consistent with a compiled-summary/tree-detail DBH-limit difference, not
random counting quality. The exact compiled `STEMS_HA_LS` scope still needs confirmation from the
compilation code or a field-standard crosswalk, but the direction and magnitude are now explained.

## What this invalidates

The raw non-PSP external validation in D9.2 used **PSP-calibrated bundles trained on 2+ cm TPH**
against **non-PSP tree detail at 4+ cm**. That comparison is not denominator-compatible:

- PSP observed TPH includes 2–4 cm trees.
- CMI/YSM/VRI tree detail starts at 4 cm.
- Temporary VRI tree detail starts at 4 cm; small trees are separate tally classes.

Therefore the D9.2 external table is **provisional and not a valid cross-domain TPH comparison**.
The CWH external improvement may still be real, but it must be rerun on a harmonized target.

## Required fix

Choose one common target and rebuild both sides:

1. **Recommended first target: ≥4.0 cm.**
   - Filter PSP tree lists and observed TPH/BA to ≥4 cm.
   - Non-PSP and temporary VRI are already ≥4 cm in tree detail.
   - Rebuild intervals, refit or explicitly re-evaluate bundles, and rerun external validation.
   - This loses PSP 2–4 cm stems; document that choice and the TPH denominator.

2. **Alternative: ≥2.0 cm.**
   - Add PSP 2–4 cm trees.
   - Add non-PSP small-tree tally counts (class counts, not individual DBH) to observed TPH.
   - Add temporary VRI small-tree counts.
   - FVS tree lists still need individual stems or a documented establishment approximation.

Do not compare raw TPH across programs without stating the DBH denominator. The same applies to
recruitment, mortality, and QMD.

## Code/data changes required

- Add a `min_dbh` build setting; filter tree detail before BA/TPH/interval construction.
- Add a matching `min_dbh` to the probe tree-list path.
- Record `min_dbh` in the dataset manifest and every bundle/validation table.
- Add a test that PSP 2–4 cm trees are excluded at `min_dbh=4.0` and that observed TPH matches the
  filtered tree list.
- Rebuild the PSP reference at 4+ and rerun the external cohort before any calibration claim.

This is a data-standard correction, not a model retune. It must be fixed before the next
full-BC calibration pass.

## 4+ cm fixed-bundle check

The dataset builder and probe now carry `min_dbh`; the PSP reference was rebuilt at `min_dbh=4.0`
(17,132 intervals, 139 BEC labels) and compared with the 4+ non-PSP cohort. The existing bundles
were **not refit**; this is a denominator-sensitivity check, not a 4+ calibration.

| Domain | Holdout | Model | n | BA bias | BA % | TPH bias | TPH % |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| CWH | Arrowsmith TSA | baseline | 38 | -11.10 | -17.4% | -134.4 | -9.1% |
| CWH | Arrowsmith TSA | pilot | 38 | -2.68 | -4.2% | -35.5 | -2.4% |
| CWH | non-PSP external | baseline | 209 | -10.10 | -19.4% | -184.4 | -8.4% |
| CWH | non-PSP external | pilot | 209 | -1.29 | -2.5% | +1.7 | +0.1% |
| SBS | Prince George TSA | baseline | 19 | -0.40 | -1.0% | -33.4 | -2.5% |
| SBS | Prince George TSA | pilot | 19 | -3.09 | -8.0% | -235.4 | -12.9% |
| SBS | non-PSP external | baseline | 253 | +0.05 | +0.2% | -127.3 | -6.5% |
| SBS | non-PSP external | pilot | 253 | -1.37 | -4.4% | -204.2 | -10.4% |

The 4+ rebuild does **not** rescue SBS: its pilot is still worse than baseline on both the PSP
holdout and the independent cohort. CWH remains the only bundle with external skill at 4+; its
`BAIMULT 7.0` risk is unchanged. The next calibration pass must refit at the chosen DBH target, not
just rerun a 2+ bundle.

## CWH 4 cm refit: no bundle

A 12-point global grid (`BAIMULT` 5–8, `MORTMULT` 0.30–0.60) was run on the PSP 4 cm
five-per-BEC sample. Training selection preferred `BAIMULT 6.0 / MORTMULT 0.30`:
Arrowsmith test BA -2.63 / TPH -1.4%, training BA +0.56 / TPH +1.5%, and non-PSP external BA
-1.72 / TPH +1.4% (n=209). But the same fixed candidate **fails the Fraser TSA**:
BA -4.10 (-6.2%), TPH -110 (-6.1%), outside the BA ±3 m2/ha band.

`BAIMULT 8.0 / MORTMULT 0.45` passes Fraser (BA -2.10, -3.2%) and Arrowsmith, but 8.0 is the
bundle upper bound and the candidate is at the bound; training BA is +1.14. That is not acceptable
under the protocol. A high multiplier is again doing structural work.

**No 4 cm CWH bundle at the time of D9.5.** D9.6 later found that `REGDMULT` fixes the Fraser failure and issued a separate 4 cm pilot; the 2 cm CWH pilot remains a separate artifact; its 4 cm external comparison
is a sensitivity check, not a 4 cm calibration. The 4 cm target must be refit with a
Fraser-aware, site-grouped selection and a different growth parameterisation, not a higher global
`BAIMULT`.
