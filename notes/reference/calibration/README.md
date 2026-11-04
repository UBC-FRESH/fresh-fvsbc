# BC calibration dataset: aggregate reference tables

Built on 2026-11-02 from the public FAIB PSP archive with
`python scripts/build_calibration_dataset.py`. These are the aggregate tables;
the tree-level tables (`visits.csv`, `intervals.csv`, `tree_survival.csv`) stay
outside the repository because they carry site identifiers.

## What is here

| File | What it holds |
| --- | --- |
| `bec_coverage.csv` | Sites, visits, repeat sites, intervals, live/dead/missing/damaged trees by BEC |
| `bec_envelope.csv` | BA p50/p90/p99/max, mean TPH and mean volume by BEC |
| `bec_species_envelope.csv` | The same envelope by BEC and species group |
| `species_crosswalk.csv` | Observed PSP species, the FVS code when known, the calibration group |
| `manifest.json` | Input sizes and SHA-256, row counts, interval bounds, supported zones |
| `pilot-bundle.json` | The unsigned calibration-bundle contract pilot |
| `kc-pilot-bundle.json` | The KC v2c regional pilot bundle; unsigned, PL at its bound |
| `kc-protocol.md` | The repeatable KC pilot protocol and its claim boundary |
| `kc-replication.md` | The KC pilot results, diagnostics, uncertainty, and effort |
| `domain-plan.csv` | The 12 calibration domains and their sample sizes |
| `full-domain-design.md` | The domain design, power thresholds, pre-registered validation, and W2–W6 sequence |
| `w2-upstream-package.md` | The upstream work package for the five zones and 19 subzones |
| `cciss-leads.md` | The CCISS code/data leads, species priority, and BEC coverage for W2 |
| `w2-species-bec-crosswalk.csv` | Every candidate species, its FVS code or missing status, zones, ratings, and priority |
| `w2-bec-gap.csv` | Every BC BGC unit, its resolution status, site-series count, PSP coverage, and missing species |
| `w2-crosswalk.md` | The W2.1 method, counts, and claim boundary |
| `w2-source-audit.md` | The W2.2 pinned-source audit and go/no-go |
| `w2-source-gaps.csv` | The component-by-component source gap matrix |
| `w2-subzone-patch.md` | The W2.3 subzone patch, 19 provisional defaults, build, smoke result, and echo caveat |
| `w2-subzone-defaults.csv` | The 19 subzones, tokens, PSP p99/max, and provisional BAMAX |
| `w2-subzone-smoke.csv` | The 19 smoke cases: BEC echo, BAMAX label and value, and expected value |
| `w2-subzones.patch.gz` | The Habtyp/Sitset patch against the pinned source |
| `w2-five-zone-defaults.csv` | The 32 five-zone `BAMAX` candidates from the all-zone build, with confidence |
| `w2-five-zone.patch.gz` | The five-zone parser/defaults patch, applied after the W3.1 boundary fix |
| `w2-five-zone-prototype.md` | The 32-label build/smoke result and the parser defects it found |
| `w2-five-zone-smoke.csv` | One row per five-zone label: expected/echoed BAMAX and database |
| `w2-five-zone-species.md` | The seven donor aliases, the species smoke, and the output-code caveat |
| `w2-five-zone-species-smoke.csv` | One row per missing species: donor, BEC/BAMAX echo, output code, database |
| `w3-bec-boundary.md` | The W3.1 `KAM`+`MS` boundary finding and fix |
| `w3-habtyp-boundary.patch.gz` | The Habtyp zone-boundary patch, applied after W2.3 |
| `w4-sbps-small-tree.patch.gz` | The SBPS small-tree height-model selection fix, applied after W3.1 |
| `d6-sbps-growth.md` | The D6.1 SBPS diameter-growth diagnosis and next instrument |
| `d6-small-tree-growth.md` | The D6.2 small-tree growth threshold, one-tree matrix, and corrected build comparison |
| `d6-small-tree-output.md` | The D6.3 finding that the growth model is normal and the DBH/output state explodes |
| `d6-sbps-small-tree.md` | The D6.4 SBPS overflow finding, patch, corrected baseline, and claim boundary |
| `d6-sbps-fixed.csv` | The four corrected SBPS baseline rows |
| `d7-sbps-readiness.md` | The D7.1 SBPS calibration-readiness probe, negative result, and next steps |
| `d7-sbps-candidates.json` | The fixed D7.1 SBPS candidate set |
| `d7-sbps-probe-summary.csv` | The D7.1 train/test probe summary |
| `d7-sbps-probe-by-bec.csv` | The D7.1 probe summary by BEC |
| `d7-sbps-site-index.csv` | The D7.1 site-index control showing that BC ignores `SITECODE` |
| `d7-idfdk-readiness.md` | The D7.3 IDFdk calibration-readiness probe, spatial holdout, and no-bundle result |
| `d7-idfdk-candidates.json` | The fixed D7.3 IDFdk candidate set |
| `d7-idfdk-probe-summary.csv` | The D7.3 train/test probe summary |
| `d7-idfdk-probe-by-bec.csv` | The D7.3 probe summary by BEC |
| `d7-idfdk-ingrowth.md` | The D7.4 public-data ingrowth model, spatial holdout pass, and claim boundary |
| `d7-idfdk-ingrowth.json` | The D7.4 BEC x species annual recruitment rates |
| `d7-idfdk-ingrowth-candidates.json` | The D7.4 candidate with the default `BAMAX 53` |
| `d7-idfdk-ingrowth-probe-summary.csv` | The D7.4 train/test ingrowth probe summary |
| `d7-idfdk-ingrowth-probe-by-bec.csv` | The D7.4 ingrowth probe summary by BEC |
| `d7-consolidation-plan.md` | The five-work-package D7 consolidation plan and status |
| `d7-consolidation.md` | The D7.6 bundle, holdout, periodic, domain, and density results |
| `d7-idfdk-bundle.json` | The D7.4/D7.6 pilot bundle with the ingrowth section |
| `d7-sbs-bundle.json`, `d7-sbs-summary.csv` | The D7.7 SBS MORTMULT 2.0 pilot and spatial holdout |
| `d7-cwh-screen.md`, `d7-cwh-summary.csv`, `d7-cwh-bundle.json` | The D8.2 CWH growth pilot: three TSA + temporal holdouts, high BAIMULT; unsigned |
| `d8-bwbs-screen.md`, `d8-bwbs-summary.csv`, `d8-bwbs-bundle.json` | The D8.3 BWBS growth pilot: three TSA holdouts, high BAIMULT and low MORTMULT; unsigned |
| `d8-cdf-screen.md` | The D8.5 CDF screen: one TSA, site fold 0 fails BA; no bundle |
| `d8-mh-cma-screen.md` | The D8.6 MH/CMA screens: GBR North fails; CMA validation-only; no bundle |
| `d8-review-packet.md`, `d8-review-manifest.json`, `d8-sbs-second-holdout.csv` | D8.7 review packet for IDFdk/SBS/CWH; SBS Prince George second holdout |
| `d7-idfdk-binned-bundle.json` | The density/QMD-binned IDFdk pilot bundle |
| `d7-idfdk-bundle-summary.csv`, `d7-idfdk-kamloops-summary.csv`, `d7-idfdk-temporal1990-summary.csv`, `d7-idfdk-binned-summary.csv`, `d7-idfdk-periodic-summary.csv` | The D7.6 validation summaries |
| `d7-ingrowth-screen-by-zone.csv`, `d7-ingrowth-screen-by-bec.csv`, `d7-all-zone-ingrowth.json` | The all-zone domain screening tables and rates |
| `baseline_summary.csv` | The uncalibrated backtest, one row per BEC |
| `baseline_by_tsa.csv`, `baseline_by_species.csv`, `baseline_by_dbh.csv`, `baseline_by_ba.csv` | The same backtest grouped by TSA, species group, DBH class, and BA class |
| `baseline_skipped_becs.csv`, `baseline_skip_reasons.csv` | The intervals the variant could not resolve |
| `baseline_report.md` | The baseline report and its limits |
| `baseline_v3.md` | The W3.1 full-domain baseline report |
| `baseline_summary_v3.csv`, `baseline_by_tsa_v3.csv`, `baseline_by_species_v3.csv`, `baseline_by_dbh_v3.csv`, `baseline_by_ba_v3.csv` | The W3.1 residual tables |
| `baseline_skipped_becs_v3.csv`, `baseline_skip_reasons_v3.csv` | The W3.1 skip tables |
| `all-zone-baseline/d5-all-zone-baseline.md` | The D5 provincial baseline report |
| `all-zone-baseline/baseline_by_zone.csv` | D5 residual summary by BEC zone |
| `all-zone-baseline/baseline_five_zone.csv` | D5 five-zone per-BEC residuals |
| `all-zone-baseline/baseline_outliers.csv` | The 12 largest BA deviations, aggregate-safe columns |
| `all-zone-baseline/baseline_summary.csv`, `baseline_by_*.csv` | The D5 per-BEC and grouped residual tables |
| `all-zone-baseline/d6-five-zone-baseline.md` | The D6 five-interval-per-BEC five-zone baseline, residuals, and species decision |
| `all-zone-baseline/d6-five-zone-summary.csv` | The D6 five-zone per-BEC residual summary |
| `all-zone-baseline/d6-five-zone-by-species.csv` | The D6 five-zone residuals by dominant species group |
| `all-zone-baseline/d6-all-zone-summary.csv` | The D6 all-zone per-BEC rerun after the SBPS fix |

## Counts

| Quantity | Value |
| --- | ---: |
| Sites in the archive | 7,341 |
| Visits in the archive | 23,956 |
| Sites in the seven supported zones | 4,430 |
| Visits in the supported zones | 13,191 |
| Plot visits with live trees | 13,966 |
| Interval pairs, 2 to 40 years | 9,186 |
| Tree-survival rows | 1,031,828 |
| Tree-survival rows with a damage code | 54,269 |
| BEC variants in the coverage table | 153 |
| BEC variants in the envelope table | 121 |
| BEC × species envelope rows | 594 |
| Observed PSP species codes | 37 |

The unsupported zones (`CWH`, `CDF`, `BWBS`, `CMA`, `MH`) are counted in
`bec_coverage.csv` but contribute no interval, tree-survival, or envelope row.
They need the upstream extension in W2 before they can be calibrated.

## QA and exclusions

- **Supported zones only for tree tables.** 2,911 sites are in `CWH`, `CDF`,
  `BWBS`, `CMA`, or `MH`; they are counted in the coverage table but contribute
  no interval, tree-survival, or envelope row.
- **A tree needs a DBH, a live/dead code, and a positive expansion factor.**
  Rows with a missing DBH, a non-`L`/`D` code, or a zero expansion factor are
  dropped before the visit summaries.
- **An interval must be 2 to 40 years.** Shorter intervals are measurement
  noise; longer ones mix several disturbances and a climate trend.
- **Missing is not dead.** A tree absent from the second visit is `missing`
  and is excluded from the mortality numerator but kept in the tree count.
- **Species that do not crosswalk are kept and marked.** 24 of the 37 observed
  PSP codes are outside BC's 15; they stay in `species_crosswalk.csv` with
  `known=False` and `group=UNKNOWN` rather than being folded into another group.
- **Damage is a partial disturbance flag.** `damage=True` means one of the five
  `DAM_AGN*` columns is positive. The extract has no reliable harvest or fire
  history, so an analyst must exclude a known harvest interval separately.

## Baseline backtest

The 2026-11-02 baseline ran **89 intervals across 89 BEC variants**, one per
variant, with no cut and no calibration. **Nineteen variants were skipped**
because the variant does not resolve their subzone; they are listed in
`baseline_skipped_becs.csv`. **The initial stand is reproduced closely**: mean
BA bias -0.87 m2/ha, median -0.64, MAE 0.93, which is the check that the tree
list construction is sound. **The end of the interval is not**: 5 predictions
are above the observed maximum and 1 is above the p99. The worst are `SBPSmc`
(predicted 11,214 m2/ha against 30.6 observed) and `SBPSdc` (4,705 against
11.2). The default mortality does not remove enough small-tree density in those
cases. The grouped summaries also carry annual **net** BA and TPH change; the
gross mortality table is not requested by this baseline. The per-interval table
stays in the runtime directory because its `interval_id` carries a site
identifier; only the grouped tables are tracked.

## The IDF check

The ingest can be checked against the independent IDF audit in the WS4
workspace. For `IDFdk3` this dataset gives:

| Statistic | This dataset | WS4 IDF audit |
| --- | ---: | ---: |
| BA p50 | 26.1 | 26.1 |
| BA p90 | 43.6 | 43.6 |
| BA p99 | 54.1 | 54.1 |
| BA max | 63.7 | 63.7 |
| Mean TPH | 2,820 | 2,820 |
| Mean volume | 134.2 | 134.2 |

The agreement is exact to the published precision, which is the check that the
weights, species filters, and interval construction are the same as the audit's.
It is not a calibration and it is not independent of the archive: both read the
same PSP snapshot.

## All-zone build (2026-11-03)

The `--all-zones` build reads every PSP site instead of only the seven supported zones. It covers **7,341
sites, 23,956 visits, 3,205,741 tree rows, 17,151 intervals, and 1,814,527 tree-survival rows** across all
**153 BEC variants**. The five previously excluded zones now have envelope rows:

| Zone | Labels | Sites | Repeat sites | Intervals | BA p99 range | BA max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `CWH` | 22 | 2,335 | 2,178 | 7,124 | 88.5–165.7 | 230.2 |
| `CDF` | 1 | 26 | 21 | 94 | 111.9 | 153.1 |
| `BWBS` | 5 | 534 | 336 | 710 | 51.4–69.6 | 71.6 |
| `CMA` | 1 | 3 | 2 | 6 | 93.2 | 93.2 |
| `MH` | 3 | 13 | 12 | 31 | 83.8–122.5 | 123.6 |

The tree-level all-zone tables stay outside the repository. The aggregate tables are in `all-zone/`, and
`w2-five-zone-defaults.csv` gives each label a provisional `BAMAX` (PSP p99) and a confidence tier.

## Known limits

- The envelope is empirical. A high p99 in a data-thin variant is a sample
  property, not a biological maximum; the calibration report must say so.
- The PSP plots are subjectively located and over-represent older, accessible
  stands. They are not a random sample of BC.
- The dataset is a supported-zone dataset. It is not a province-wide dataset
  until W2 extends the variant.
- No parameter is fitted here. The tables are the input to W4.

## Regenerate

```bash
python scripts/build_calibration_dataset.py \
  --psp-dir "$FAIB_PSP_DIR" \
  --out-dir runtime/calibration
```

The command prints the manifest's row counts and writes the six tables plus the
manifest. The SHA-256 values in `manifest.json` identify the snapshot; a different
snapshot with the same row counts still needs a new manifest.

| `d7-sbps-capacity.md` | The D7.2 per-BEC SBPS capacity probe and no-bundle result |
| `d7-sbps-tph.md` | The D7.3 SBPS TPH/MORTMULT probe and candidate parameter set |
| `d7-sbps-ingrowth.md` | The D7.5 SBPS ingrowth TSA-holdout failure and D7.3 retraction |
| `d7-100mile-capacity.md` | The D7.6 100 Mile TSA capacity screening and no-bundle result |
| `d7-100mile-loocv.md` | The D7.7 leave-one-site-out capacity result |
| `d7-100mile-candidate.md` | The D7.8 100 Mile-specific ingrowth candidate that passes both biases |
| `d7-sbps-playbook.md` | Consolidated D7 SBPS record: false starts, LOSO lessons, candidate, and next steps |
| `d7-100mile-temporal.md` | The D7.9 temporal holdout attempt and data-gap result |
| `d7-sbpsdc-quesnel.md` | The D7.10 Quesnel capacity screen and dense-site failure |
| `d7-quesnel-established.md` | The D7.11 established-stand boundary and site-fold failure |
| `d7-quesnel-siteindex.md` | The D7.12 site-index covariate screen and its insufficiency |
| `d7-quesnel-highqmd.md` | The D7.13 high-QMD Quesnel candidate, where every site fold passes |
| `d7-quesnel-bundle.md` | The D7.14 temporal pass and unsigned candidate bundle |
| `d7-quesnel-review.md` | The independent-review packet for the Quesnel candidate bundle |
| `d7-sbpsmk-quesnel.md` | The D7.17 SBPSmk/Quesnel second-domain check and site-fold failure |
| `d7-sbpsmk-quesnel-summary.csv` | The D7.17 BAMAX grid and site-pass counts |
| `d7-sbpsmk-growth.md` | The D7.18 growth-multiplier and ingrowth screen |
| `d7-sbpsmk-growth-summary.csv` | The D7.18 candidate grid and site-pass counts |
| `d7-sbpsmk-mature.md` | The D7.19 mature SBPSmk/Quesnel candidate and validation |
| `d7-sbpsmk-mature-bundle.json` | The unsigned SBPSmk/Quesnel mature candidate bundle |
| `d7-sbpsmk-mature-loso-summary.csv` | The D7.19 site-grouped LOSO aggregate |
| `d7-sbpsmk-mature-temporal-summary.csv` | The D7.19 temporal train/test aggregate |
| `d7-quesnel-highqmd-temporal-summary.csv`, `d7-quesnel-highqmd-bundle.json` | The D7.14 temporal table and candidate bundle |
| `d7-quesnel-highqmd-summary.csv` | The D7.13 BAMAX 70/75/80 domain summary |
| `d7-quesnel-established-summary.csv` | The D7.11 pooled and worst-site summary |
| `d7-sbpsdc-capacity-summary.csv` | The D7.10 BAMAX grid summary |
| `d7-100mile-temporal.json`, `d7-100mile-temporal-summary.csv` | The D7.9 rates and split summary |
| `d7-100mile-ingrowth.json`, `d7-100mile-ingrowth-loso-summary.csv`, `d7-100mile-ingrowth-candidates.json` | The D7.8 rates, LOSO result, and candidate |
| `d7-100mile-loocv-summary.csv`, `d7-100mile-loocv-candidates.json` | The D7.7 LOSO tables and candidate list |
| `d7-100mile-summary.csv`, `d7-100mile-candidates.json` | The D7.6 screening tables and candidate list |
| `d7-sbps-ingrowth.json`, `d7-sbps-ingrowth-summary.csv`, `d7-sbps-ingrowth-candidates.json` | The D7.5 recruitment rates, holdout results, and candidates |
| `d7-tph-summary.csv`, `d7-tph-by-bec.csv`, `d7-tph-candidates.json` | The D7.3 probe tables and candidate list |
| `d7-per-bec-summary.csv`, `d7-per-bec-by-bec.csv`, `d7-per-bec-candidates.json` | The D7.2 per-BEC probe tables and candidate list |
