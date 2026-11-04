# D9.9 BEC coverage matrix

Status: planning artifact
Date: 2026-11-04
Data: `psp4` reference, `min_dbh=4.0`
Evidence: `d9-bec-coverage.csv`

## 1. What the data covers

The 4 cm PSP reference has:

- **17,132 intervals**
- **5,732 sites**
- **139 BEC labels**
- 15 zone groups

| Zone | Intervals | Sites | BEC labels |
| --- | ---: | ---: | ---: |
| CWH | 7,122 | 2,178 | 21 |
| ICH | 3,149 | 950 | 26 |
| IDF | 2,126 | 797 | 18 |
| SBS | 1,931 | 717 | 18 |
| MSd | 966 | 270 | 7 |
| BWB | 707 | 336 | 5 |
| ESS | 609 | 277 | 30 |
| SBP | 296 | 126 | 4 |
| CDF | 94 | 21 | 1 |
| MSx | 68 | 36 | 3 |
| MHm | 28 | 10 | 2 |
| PPx | 27 | 10 | 2 |
| CMA | 6 | 2 | 1 |
| MHw | 3 | 2 | 1 |

The full matrix is `d9-bec-coverage.csv`. It records intervals, sites, median mortality fraction,
high-disturbance fraction, and the current artifact status for every BEC label.

## 2. Largest individual BECs

| BEC | Intervals | Sites | Current status |
| --- | ---: | ---: | --- |
| CWHvm1 | 1,535 | 506 | CWH 4 cm pilot; BA/TPH only |
| CWHxm2 | 1,244 | 276 | CWH 4 cm pilot; BA/TPH only |
| CWHwh1 | 1,128 | 414 | CWH 4 cm pilot; BA/TPH only |
| ICHmw2 | 978 | 225 | uncalibrated |
| CWHvh | 744 | 273 | CWH 4 cm pilot; BA/TPH only |
| CWHxm1 | 645 | 129 | CWH 4 cm pilot; BA/TPH only |
| CWHdm | 616 | 162 | CWH 4 cm pilot; BA/TPH only |
| MSdm1 | 591 | 133 | uncalibrated |
| ICHmw | 364 | 119 | uncalibrated |
| IDFdk2 | 353 | 124 | IDFdk ingrowth pilot; not certified |
| SBSmw | 343 | 110 | uncalibrated |
| SBSmk1 | 327 | 118 | Quesnel post-hoc; other TSA validation-only |

## 3. What this says

- Sample size is not the bottleneck for CWH, ICH, IDF, or SBS.
- CWH is the largest block, but its 4 cm pilot fails height and volume; finish that before expanding CWH.
- The highest-sample uncalibrated BECs are **ICHmw2**, **MSdm1**, and **SBSmw**.
- The IDFdk labels already have an ingrowth pilot, but not a certified calibration.
- Low-sample zones (CMA, MHw, PPx, MHm) need partial pooling or validation-only status; they cannot support independent calibration.

## 4. Next order

1. **CWH height/volume**: test `HTGMULT`/`REGHMULT`; do not add more BAIMULT.
2. **ICHmw2**: 978 intervals / 225 sites; next full template.
3. **MSdm1**: 591 / 133.
4. **SBSmw**: 343 / 110; keep separate from SBPS.
5. **IDFdk2/IDFdk3**: use the existing ingrowth work but add capacity/height.
6. Low-sample zones: partial pooling, nearest-neighbour, or validation-only.

The matrix is a planning input, not a claim that any BEC is calibrated.

## 5. Claim boundary

This is a coverage and status inventory. It does not support a yield, AAC, legal, or whole-block
claim.
