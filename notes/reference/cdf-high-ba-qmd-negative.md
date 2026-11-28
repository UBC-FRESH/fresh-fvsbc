# CDF high-BA, small-QMD mortality: a four-interval term, not shippable

Status: **negative for shipping.** The term improves the expanded fold and LOOCV, but the gain is
one held-out interval and the 14-interval fold is inert. The engine is reverted.

## 1. The term

The BA-only term could not separate the dense, large-QMD history from the smaller-QMD high-BA
stands. A structure-scoped term was tested (W35):

```
CDF, BA > 60 m2/ha, 29 <= QMD <= 33 cm:  mortality X = X * 0.25
```

QMD is computed in `morts.f` from the same metric BA and stems/ha already used for the BA class.

## 2. Leave-one-site-out (20 intervals at BA >= 60, five sites)

| Build | Mean TPH MAE | Mean BA MAE |
| --- | ---: | ---: |
| `cdf-v3` | 47.16 | 2.34 |
| W35 | **38.52** | **1.85** |

By held-out site: the dense >100 site and the large-QMD site are unchanged; two 60–71 m²/ha sites
improve sharply; the 63–81 site with QMD 22–29 is slightly worse (80.5 vs 77.7).

## 3. Expanded clean CDF fold (31 test / 52 train intervals)

The 14-interval fold contains only the dense site and three BA 40–44 intervals, so W35 is inert
there. The full clean CDF sample (same two screens) contains the target band:

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| `cdf-v3` | 2.489 | 201.406 | 2.032 | 164.062 |
| W35 | **2.457** | **200.826** | **1.979** | **163.253** |

Both measures improve in both folds. But the term changes only **four intervals**:

| Fold | Interval | QMD | TPH error (before → after) | BA error |
| --- | --- | ---: | ---: | ---: |
| test | one 67 m²/ha stand | 29.8 | −25.4 → −7.4 | −4.31 → −3.31 |
| train | 64 m²/ha | 30.7 | −34.6 → −10.6 | −3.42 → −2.42 |
| train | 71 m²/ha | 32.4 | −44.6 → −12.6 | −3.83 → −1.83 |
| train | 81 m²/ha | 29.5 | −3.0 → +17.0 | −0.89 → +1.11 |

The entire held-out gain is one interval. The QMD band was selected after inspecting the residuals
of the same five sites, so the leave-one-site-out result is not an independent test of the band.

## 4. Decision

No engine or bundle change ships. A term fitted to four intervals is not held-out evidence; the
next step is to add more high-BA, QMD 29–33 intervals from the full PSP inventory (the calibration
sample currently caps at 30 intervals per BEC) or to fit QMD structurally before selecting a band.

## Reproduce

- LOOCV: `probe_cdf_w35_<site>/` against `probe_cdf_loocv_<site>_cdf/`.
- Expanded fold: `probe_cdf_w35_expanded/` against `probe_cdf_base_expanded/`.
- 14-interval fold: `probe_cdf_clean_cdf/` (unchanged).

## 5. Sample expansion does not add intervals

The CDF inventory has 26 header sites, 21 with two or more visits, all already in the calibration
dataset (94 intervals). The BA ≥60 / QMD 29–33 band has **four intervals at three sites** even with
`--per-bec 200`. CWH has 609 intervals in the band, but the same term worsens CWH (test
3.381/171.4 → 3.467/173.4; train 4.270/269.1 → 4.415/271.8). See
`cdf-sample-expansion-negative.md`.
