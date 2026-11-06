# D9.13 ICHmw2 Arrow/Cascadia well-sampled candidate

Status: **unsigned candidate; BA/TPH/QMD/height/volume pass on well-sampled PSP sites**
Date: 2026-11-06
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Bundle: `d9-ichmw2-candidate-bundle.json`
Evidence: `d9-ichmw2-si-summary.csv`, `d9-ichmw2-screen-summary.csv`

The old "77 failing sites" was dominated by 1–2 interval sites. With a minimum of five intervals
per site, `BAIMULT 0.75` is a defensible candidate for ICHmw2 in Arrow and Cascadia.

## 1. Domain

- BEC `ICHmw2`.
- TSA: Arrow and Cascadia only.
- DBH >= 4 cm.
- Sites with **>=5 intervals**.
- Untreated.

Okanagan, Kootenay Lake, and sites with fewer than five intervals are outside the claim. The
bundle cannot enforce the interval-count limit; that is an evidence restriction, not a runtime check.

## 2. Weighted result

99 sites / 569 intervals.

| Metric | Result |
| --- | ---: |
| BA bias | -0.23% |
| TPH bias | -3.44% |
| BA RMSE | 4.29 m2/ha |
| TPH RMSE | 844 TPH |
| Sites passing BA ±10% / TPH ±15% | **91 / 99** |

Site-cluster bootstrap intervals include zero but exclude large bias; the calibration is not
precisely estimated, but it removes the systematic BA overprediction.

## 3. Temporal check

Fixed `BAIMULT 0.75`:

| Test | Intervals | BA | TPH |
| --- | ---: | ---: | ---: |
| year0 >= 2000 | 28 | +2.0% | -2.0% |
| year0 >= 2005 | 12 | +2.0% | -13.1% |

The 2005 sample is small but remains inside the TPH band.

## 4. Bundle

`d9-ichmw2-candidate-bundle.json`:

- `BAIMULT 0.75` for FD, HW, CW, BG, PW, PL, SE, BL, LW, AT, AC;
- domain: ICHmw2, Arrow/Cascadia, DBH >=4, untreated;
- pins: PyFVS `e95172b`, FVS `ef5fa847`, variant `bc`, wrapper `0.21.4`;
- unsigned, unreviewed, not a certificate.

## 5. Limits

- The candidate was selected on all well-sampled sites; the temporal and cross-TSA checks are not a
  pre-registered nested selection.
- The bundle does not enforce >=5 intervals.
- Okanagan/Kootenay are excluded because they lack sufficient well-sampled sites.
- D9.14 validates QMD, matched top height, and PSP merchantable volume; all are inside ±10%.
- The candidate is not a production or yield claim.

## 6. Validation

D9.14: QMD +2.3%, matched top height -0.6%, volume -7.5%; temporal >=2000 volume -2.8%. See
`d9-ichmw2-validation.md`.

## 7. Spatial holdout

Arrow-only selection chooses 0.75 and transfers to Cascadia: 29/33 sites, BA +1.1%, TPH -3.1%.
See `d9-ichmw2-holdout.md`.

## 8. Claim boundary

This is an unsigned candidate for well-sampled ICHmw2 Arrow/Cascadia stands. It does not support a
yield, AAC, legal, or whole-block claim, and it is not a certificate.
