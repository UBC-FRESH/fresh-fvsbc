# D9.52 CURRMORT severity grid on five-year high-PL stands

Status: **CURRMORT is the correct lever, but observed-class values are not enough**
Date: 2026-11-08
Build: D9.46 BC MPB extension

## 1. The keyword correction

The rate-of-loss MPB path is controlled by `CURRMORT`, not `CURRMR` and not `BEETLES`. The
keyword takes ten DBH-class values: seven on the keyword line, three on the supplemental line.

For each five-year high-PL interval, the observed dead PL per acre per year was computed by DBH
class and used as the `CURRMORT` vector. The vector was then multiplied by 1–5.

## 2. Result

Observed PL mortality is 80.6–96.4%.

| Interval | 1× | 2× | 3× | 4× | 5× |
| --- | ---: | ---: | ---: | ---: | ---: |
| `4024547` | 12.6% | 13.8% | 14.8% | 15.6% | 16.4% |
| `4024546` | 19.4% | 22.4% | 24.3% | 25.5% | 26.3% |
| `4024754` | 15.9% | 20.0% | 22.6% | 24.6% | 26.2% |
| `4032478` | 29.7% | 34.3% | 37.5% | 39.9% | 41.7% |
| `4024340` | 45.3% | 47.2% | 48.1% | 48.6% | 49.0% |
| `4024380` | 30.3% | 35.9% | 39.7% | 42.8% | 45.2% |

The multiplier moves mortality, so `CURRMORT` is the right path, but even 5× is far below the
observed collapse. A single multiplier is not the answer.

## 3. Interpretation

- The keyword and class path are now identified.
- The low response suggests a unit/class mismatch, not a missing module.
- Possible wrong assumptions:
  - `CURRMORT` may be **current mortality per acre**, not a per-year rate.
  - The DBH classes may not map one-to-one from the PSP bins to FVS classes.
  - Dead-tree weighting and area conversion may differ from the PSP expansion.
  - The rate-of-loss model may use `CURRMORT` differently when `LINVMR`/damage codes are absent.
- `ACTSURF` and `INVMORT` are the next direct-kill alternatives.

## 4. Next

1. Verify `CURRMORT` units and DBH-class boundaries against `colmod.f`/`mpsdlp.f`.
2. Recompute the vector with the exact FVS class mapping and tree weights.
3. Test a 10×/20× diagnostic to see whether the model is linear.
4. If `CURRMORT` still cannot reach the observed pattern, use `ACTSURF` for a surface-kill
   diagnostic or `INVMORT` with explicit MPB damage codes.
5. Keep five-year intervals; do not raise the 10-year cap.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
