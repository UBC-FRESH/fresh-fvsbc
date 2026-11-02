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
| `species_crosswalk.csv` | Observed PSP species, the FVS code when known, the calibration group |
| `manifest.json` | Input sizes and SHA-256, row counts, interval bounds, supported zones |
| `pilot-bundle.json` | The unsigned calibration-bundle contract pilot |
| `baseline_summary.csv` | The uncalibrated backtest, one row per BEC |
| `baseline_by_tsa.csv`, `baseline_by_species.csv`, `baseline_by_dbh.csv`, `baseline_by_ba.csv` | The same backtest grouped by TSA, species group, DBH class, and BA class |
| `baseline_skipped_becs.csv`, `baseline_skip_reasons.csv` | The intervals the variant could not resolve |
| `baseline_report.md` | The baseline report and its limits |

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
cases. The per-interval table stays in the runtime directory because its
`interval_id` carries a site identifier; only the grouped tables are tracked.

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
