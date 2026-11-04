# D9.1 FAIB non-PSP catalogue: temporary plots and an independent repeat cohort

Checked: 2026-11-04. Source: **Forest Inventory Ground Plot Data and Interactive Map**, Government
of British Columbia / FAIB, Open Government Licence - BC.

- Catalogue: https://open.canada.ca/data/en/dataset/824e684b-4114-4a05-a490-aa56332b57f4
- FTP: https://www.for.gov.bc.ca/ftp/HTS/external/!publish/ground_plot_compilations/
- Data dictionary: `non_PSP_data_dictionary_2026Apr20.xlsx`
- Program page: https://www2.gov.bc.ca/gov/content/industry/forestry/managing-our-forest-resources/forest-inventory/ground-sample-inventories/permanent-sample-plot

No repository data files are copied here; the source files are external public data. SHA-256 of the
downloaded files used for this audit:

```
474760d5c9e5525729fa76c6f9959cd628b808a8147ade0ba6077d5d62be20a0  nonpsp_sample_byvisit.csv
b62239113af2f5ec3e55f9391b5a391273aa17e34ecd08eef802a0ab3f6bd3f8  faib_header.csv
40746f0b8b6ffe75e0c98d4cca9911f6b243ef6bee9a31a5c4dfcd76481ff3f1  faib_plot_header.csv
429e7f18ae2c73a823a232f291b804d10d1973ae81eb81605955b7e170aa3325  faib_tree_detail.csv
d07cfbef725a01e89a8af5f848723b9d7ba7559c8e2ead20dce25c312a312457  faib_compiled_spcsmries.csv
```

## What the catalogue actually contains

| Group | Visits | Sites | Purpose |
| --- | ---: | ---: | --- |
| Temporary VRI phase 2 | 7,200 | 6,684 | one-time 5-point clusters; no sequential visit |
| Temporary SUP | 318 | — | supplemental one-time plots |
| Temporary VLT | 63 | 63 | light/lidar verification; not a full VRI standard |
| Repeated YSM | 2,205 | 1,129 | young stand monitoring |
| Repeated CMI | 1,506 | 995 | change monitoring inventory |
| Repeated NFI | 584 | 254 | national forest inventory |
| Repeated SUP | 75 | — | supplemental repeated visits |

Total non-PSP: **11,951 visits / 9,512 sites**, including **7,581 temporary visits** and **4,370
repeated visits**. Temporary VRI has **151,478 tree-detail rows**; the full non-PSP tree detail is
367,096 rows.

**There is no separate “TSP” table in the current catalogue.** The temporary plots are the VRI
phase-2 temporary 5-point clusters (`SAMPLE_ESTABLISHMENT_TYPE=VRI`, `VISIT_TYPE=TMP`), plus a
small SUP/VLT temporary component. They are not remeasured and therefore cannot identify growth,
mortality, or recruitment.

## Temporary plots: what they are good for

- **Initial-condition validation**: build a tree list, run one cycle, and compare initial BA/TPH/QMD
  with the plot summary.
- **BEC and species coverage**: 112 BEC labels (5,250 sites with a populated BEC) occur in temporary
  VRI; 22 BEC labels are absent from the current PSP interval table.
- **Envelope and applicability bounds**: BA/QMD/species distributions for otherwise thin BECs.
- **Tree-list and species-mapping checks**: a large, spatially broad one-time cohort.
- **Not usable for**: growth multipliers, mortality multipliers, recruitment rates, or any
  change-over-time claim. One visit has no interval.

The 21 new BEC labels are mostly ESSF/ICH/MS/PP/SBS variants with no local PSP intervals. The full
coverage table is `d9-faib-nonpsp-coverage.csv`.

## Repeated non-PSP plots: the actually useful calibration/validation cohort

The same catalogue contains **1,527 sites with at least two repeated visits**, producing:

- **1,919 raw intervals** across 102 BEC labels;
- **1,302 eligible intervals** after BA/QMD/dead-BA screening;
- **1,008 eligible intervals / 820 sites** with a populated BEC;
- **1,076 YSM intervals**, **511 CMI**, **330 NFI**, and 2 SUP.

These are **not PSP** and **do not overlap the current PSP site identifiers**: zero of the 9,512
non-PSP sites match the 7,341 PSP sites. They are an independent cohort from a different sampling
frame. CMI/YSM/NFI are grid-based and have generalized coordinates; VRI temporary plots have real
coordinates.

They should not be merged blindly into training:

- YSM is young-stand-only, so it is a different population from mature PSP.
- CMI/NFI are grid-based and statistically designed; they are not interchangeable with the
  subjectively located PSP.
- Generalized coordinates prevent fine spatial joins; TSA/BEC are still available.
- `PERIOD` and exact visit matching must be used; `VISIT_TYPE=TMP` must never create an interval.

The first use should be **external validation**, not training: it is a genuinely independent check
of the current models. Only after that should a pre-registered combined fit use them as a training
cohort, stratified by program.

## Next pilot

1. Build a non-PSP interval table from the repeated YSM/CMI/NFI visits with the same interval rules
   as the PSP table; record how many visits/BEC labels are lost to missing BEC and period.
2. Run the existing IDFdk, SBS, and CWH bundles on their overlapping non-PSP cells as an
   **independent validation cohort**; do not use the result to retune those bundles.
3. Build initial-condition checks from a sample of temporary VRI plots, especially the 22 BEC labels
   absent from PSP, to test tree-list construction and envelope coverage.
4. Keep temporary VRI out of all growth/mortality/recruitment fitting.

This is a real data boost for coverage and independent validation, but it does not remove the
fundamental limitation: one-time temporary plots cannot calibrate change.

## Preliminary usability checks

### Repeated non-PSP intervals

A prototype build from the repeated YSM/CMI/NFI/SUP visits (filtered to `VISIT_TYPE=REP`, with the
non-numeric plot labels mapped to their five-point plot position) produced **1,733 intervals across
141 BEC labels**. This is a useful external cohort, but it is not yet a finished calibration dataset.

The existing **IDFdk binned bundle** was run on the 50 non-PSP IDFdk intervals:

| Model | n | BA bias | BA % | TPH bias | TPH % |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 50 | -0.50 | -1.9% | -55.1 | -3.6% |
| IDFdk pilot | 50 | -0.58 | -2.2% | +193.6 | +12.7% |

The pilot passes the absolute 15% TPH band but **is worse than baseline on both BA and TPH**. On
this independent non-PSP cohort it has no demonstrated skill. Do not use it as an external
validation pass.

### Temporary VRI tree lists

A preliminary comparison of temporary VRI tree detail with the compiled plot summaries matched
**7,080 visits**. Live BA from the tree list had bias **+2.79 m2/ha (+1.8%)** but MAE **30.9**;
live TPH had bias **+2,759 (+79%)** and MAE **2,956**. The tree expansion/small-tree protocol is not
directly comparable to the compiled stems, so temporary VRI plots require a weight and DBH-limit
harmonization before they can even validate initial conditions. They are **not** a drop-in
calibration boost.

## Independent non-PSP external validation

The prototype repeated non-PSP cohort was run as an external test. All four bundles were fixed; no
parameters were changed. The test intervals are not in the PSP data and were not used to fit any of
these bundles.

| Domain | Model | n | BA bias | BA % | BA MAE | TPH bias | TPH % | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| IDFdk | baseline | 50 | -0.50 | -1.9% | 3.21 | -55.1 | -3.6% | 211.4 |
| IDFdk | pilot | 50 | -0.58 | -2.2% | 3.29 | +193.6 | +12.7% | 265.5 |
| CWH | baseline | 209 | -10.10 | -19.4% | 10.65 | -184.4 | -8.4% | 301.6 |
| CWH | pilot | 209 | -1.29 | -2.5% | 5.53 | +1.7 | +0.1% | 274.1 |
| SBS | baseline | 253 | +0.05 | +0.2% | 6.77 | -127.3 | -6.5% | 280.7 |
| SBS | pilot | 253 | -1.37 | -4.4% | 6.60 | -204.2 | -10.4% | 322.1 |
| BWBS | baseline | 53 | -6.93 | -21.4% | 7.90 | -79.0 | -3.2% | 375.1 |
| BWBS | pilot | 53 | +0.36 | +1.1% | 5.09 | +235.4 | +9.5% | 450.9 |

**CWH is the only pilot that improves both bias and MAE on this independent cohort.** IDFdk, SBS,
and BWBS pass some absolute bands but are worse than baseline on TPH MAE and/or bias. The IDFdk and
SBS pilots have no demonstrated external skill here. This does not erase their PSP holdouts, but it
prevents treating them as general BC-wide calibrations.

CWH's independent result is real but still carries the high `BAIMULT 7.0` risk and needs the
protocol-bound review before promotion.
