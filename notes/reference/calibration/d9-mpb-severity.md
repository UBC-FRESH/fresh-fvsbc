# D9.54 MPB severity fit after the inch-class correction

Status: **inch classes improve the fit, but a 50x multiplier is a unit signal, not a biological parameter**
Date: 2026-11-08
Build: D9.46 BC MPB extension

## 1. Design

Training: three IDFdk3 100 Mile five-year high-PL intervals.
Holdout: SBSdw1/SBSdw2/SBPSmk Williams Lake five-year high-PL intervals.

`CURRMORT` values were aggregated by the exact inch-class mapping, scaled by a common multiplier,
and run with `MPBSTART` and `MAXYEARS 10`.

## 2. Result

| Interval | Set | Observed | 20× | 50× |
| --- | --- | ---: | ---: | ---: |
| `4024547` | train | 0.960 | 0.875 | 0.916 |
| `4024546` | train | 0.955 | 0.853 | 0.879 |
| `4024754` | train | 0.944 | 0.632 | 0.646 |
| `4032478` | holdout | 0.964 | 0.921 | 0.928 |
| `4024340` | holdout | 0.960 | 0.945 | 0.950 |
| `4024380` | holdout | 0.806 | 0.718 | 0.719 |

A common 50× multiplier gives credible holdout mortality for `4032478` and `4024340`
(0.928 and 0.950), and `4024380` is low (0.719 vs 0.806). Training `4024754` remains an outlier
(0.646 vs 0.944).

## 3. Important interpretation

The 50× multiplier is not a credible biological severity parameter. It is evidence that the MPB
extension still has a **metric/imperial unit mismatch** beyond the DBH class:

- `COLIND` uses inches;
- `CURRMORT` is in trees per acre per year;
- `STNDSIZE` is acres;
- beetle populations and surface are imperial.

The BC variant feeds metric DBH, TPH, and hectares. Converting only the DBH class reduced the
error but did not remove it. A 50× factor is compensating for the remaining conversion, not
measuring beetle severity.

## 4. Fix

1. Build a metric-to-imperial shim at the MPB boundary:
   - DBH cm → inches;
   - TPH → TPA;
   - hectares → acres;
   - surface units.
2. Re-run with a 1× observed `CURRMORT` vector.
3. If 1× reproduces the observed class mortality, calibrate only the biological severity on top.
4. Keep five-year intervals; do not use the 50× value as a model parameter.
5. Hold out Williams Lake/SBPS and check non-PL BA/TPH.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
