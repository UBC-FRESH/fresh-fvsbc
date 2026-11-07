# D9.14 ICHmw2 candidate QMD, height, and volume validation

Status: **all PSP metrics pass; unsigned candidate**
Date: 2026-11-06
Bundle: `d9-ichmw2-candidate-bundle.json`
Evidence: `d9-ichmw2-validation-summary.csv`

The ICHmw2 Arrow/Cascadia well-sampled candidate was validated on QMD, matched top height, and
merchantable volume using the existing FVS runs.

## 1. Result

99 sites / 569 intervals:

| Metric | Bias | MAE |
| --- | ---: | ---: |
| BA | -0.23% | 2.84 m2/ha |
| TPH | -3.44% | 216 TPH |
| QMD | +2.33% | 1.23 cm |
| Matched top height | -0.61% | 0.86 m |
| Merchantable volume | -7.54% | 46.1 m3/ha |

All PSP metrics are inside ±10%. Volume is robust to the FVS column: `MCuM` −7.5% and
`TCuM` +9.9%, both inside ±10%. See `d9-volume-metric-audit.md`.

Temporal test:

| Period | n | BA | TPH | QMD | Top height | Volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| year0 >= 2000 | 28 | +2.0% | -1.95% | +4.6% | -1.8% | -2.8% |
| year0 >= 2005 | 12 | +2.0% | -13.1% | +6.0% | -1.6% | +0.4% |

## 2. Decision

The candidate now has BA/TPH/QMD/top-height/volume evidence on well-sampled PSP sites. It remains:

- unsigned;
- TSA-scoped to Arrow/Cascadia;
- DBH >=4 cm;
- limited to sites with >=5 intervals (not enforced by the bundle);
- not a certificate.

## 3. Limits

- The candidate was selected on the same well-sampled sites; the temporal check is fixed-parameter.
- Arrow and Cascadia are both in the candidate domain, so there is no third-TSA holdout.
- Okanagan and Kootenay Lake are excluded.
- Volume is PSP merchantable volume; non-PSP volume is not used because the standards differ.
- The >=5-interval evidence limit is not a runtime domain check.

## 4. Claim boundary

This is an unsigned candidate for well-sampled ICHmw2 Arrow/Cascadia stands. It does not support a
yield, AAC, legal, or whole-block claim, and it is not a certificate.
