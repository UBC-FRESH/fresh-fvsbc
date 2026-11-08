# D9.55 INITMORT is the outbreak severity lever

Status: **CURRMORT is only current mortality; INITMORT controls the multi-year outbreak**
Date: 2026-11-08
Build: D9.46 BC MPB extension

## 1. Correction

The MPB rate-of-loss model has two distinct mortality inputs:

- `CURRMORT` — **current** mortality by DBH class, applied when the stand has current MPB damage;
- `INITMORT` — **initial mortality** rates by DBH class, used to start and carry an outbreak.

The D9.52–D9.54 work put observed dead PL into `CURRMORT`. That affects the first year, not the
multi-year outbreak. It is why a 50× multiplier was needed and why the response saturated.

`INITMORT` is the correct control for simulated outbreak severity.

## 2. Test

Using the inch-class observed vector on the five-year high-PL stands:

| Multiplier | Typical MPB dead fraction |
| ---: | ---: |
| 0.05× | 69.7–100% |
| 0.10× | 100% |
| 0.20× | 100% |
| 1.00× | 100% |

`INITMORT` is extremely sensitive and saturates quickly. On `4024547`, 0.05× gives 77.6% and 0.10×
gives 100%; observed is 96.0%. On `4024380`, 0.05× already gives 100%; observed is 80.6%.

## 3. Interpretation

- The keyword/class/unit fix is now complete: `INITMORT` + inch classes.
- The remaining calibration is a **single severity vector/multiplier on INITMORT**, not `CURRMORT`.
- The response is steep; a scalar multiplier alone may not fit all stands. The class vector likely
  needs per-class calibration, or `PRBSCALE`/outbreak timing.
- `CURRMORT` remains the right input for stands with existing MPB damage codes; `INITMORT` is for
  starting an outbreak in a clean stand.

## 4. Next

1. Fit INITMORT at 0.03–0.08 on training high-PL stands.
2. Recompute the vector with the exact class mapping and tree weights.
3. Hold out Williams Lake/SBPS.
4. Check non-PL BA/TPH.
5. Use `CURRMORT` only when the tree list carries current MPB damage codes.
6. Keep five-year intervals; the 10-year cap remains separate.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
