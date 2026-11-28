# CDF high-BA TPH: leave-one-site-out from the existing 20 intervals

Status: **negative for shipping; positive signal on the 60–90 m²/ha sites.** `cdf-v3` stays.

## 1. The validation built from existing data

The calibration set already has 20 CDF intervals at BA ≥ 60 m²/ha, on five sites (labelled A–E
here; one is the dense BA >100 stand). A leave-one-site-out (LOOCV) fold was run on that subset:
each site is held out once, the other four are train. No new data was requested.

## 2. LOOCV TPH MAE by held-out site

| Candidate | A (BA>100) | B | C | D | E | Mean TPH MAE | Mean BA MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `cdf-v3` | 43.7 | 49.4 | 39.6 | 25.4 | 77.7 | **47.2** | 2.34 |
| all-species MORTMULT 0.25 | 44.9 | 42.4 | 26.1 | 10.4 | 85.9 | **41.9** | **2.07** |
| 60+ ingress ×2 + MORTMULT 0.5 | 47.0 | 34.4 | 27.6 | 10.4 | 82.5 | **40.4** | **2.24** |
| 60+ ingress ×2 | 47.0 | 37.4 | 31.1 | 17.4 | 81.1 | 42.8 | 2.34 |
| 60+ ingress ×3 | 50.3 | 32.4 | 27.6 | 12.4 | 84.1 | 41.4 | 2.34 |
| all-species MORTMULT 0.5 | 43.5 | 47.4 | 36.1 | 20.4 | 77.5 | 45.0 | 2.24 |

Two candidates improve both mean BA and mean TPH: **all-species MORTMULT 0.25** and **60+ ingress
×2 + MORTMULT 0.5**. The signal is on the 60–90 sites (B–D); the dense >100 site is flat-to-worse.

## 3. The full clean fold rejects the scoped term

The signal was turned into a BA-scoped engine term (W34): CDF, 60 < BA ≤ 90, mortality ×0.5. On the
clean 14-interval held-out CDF fold:

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| `cdf-v3` | **1.318** | **36.10** | 1.827 | 125.15 |
| W34, 60–90 ×0.5 | 1.377 | 36.96 | 1.827 | 125.15 |

Both held-out measures get worse. The dense stand's early 60–85 m²/ha intervals are already
**over**-predicted for TPH, while the separate 60–81 sites are under-predicted. A BA-scoped
mortality term cannot separate them, so the LOOCV mean improvement does not transfer.

## 4. Consequence

No CDF parameter ships from this step. The existing data can measure the 60–90 problem, but it
also contains the opposite-sign dense-stand history; the two cannot be reconciled with a
stand-level BA rule. The next test should condition on stand structure (QMD/TPH) rather than BA
alone, and must still pass the full held-out fold.

## Reproduce

- High-BA subset: `~/workspace/bwbs-work/calib-cdf-highba/` (20 intervals, 5 sites).
- LOOCV runs: `probe_cdf_loocv_*`.
- Full clean fold: `probe_cdf_w34x05/` against `probe_cdf_clean_cdf/`.
