# D9.53 CURRMORT unit fix: DBH classes are inches

Status: **the earlier CURRMORT vector used centimetre bins; FVS MPB classes are inch bins**
Date: 2026-11-08
Build: D9.46 BC MPB extension

## 1. Root cause

`fvs/lpmpb/colind.f` assigns classes as:

```
IVAL = IFIX(DBH)
INDEX = IVAL/2 + MOD(IVAL,2)
```

The class boundaries are **inches** (2-inch classes from 1 to 20 inches), not centimetres.

The D9.52 vector aggregated observed dead PL by centimetre bins: 0-3, 3-5, ... cm. That puts
mortality in the wrong MPB classes. On BC metric data, DBH must be converted to inches before the
class is assigned.

## 2. Corrected test

For `4024547|1|2001|2006`, the observed dead PL was aggregated by inch classes using
`DBH / 2.54`. The resulting CURRMORT vector was scaled and run:

| Multiplier | MPB dead fraction |
| ---: | ---: |
| 1× | 48.3% |
| 2× | 57.9% |
| 3× | 63.7% |
| 5× | 71.1% |
| 10× | 80.5% |
| 20× | 87.5% |

Observed mortality is 96.0%. The earlier centimetre-bin vector at 1× was 12.6%; the inch-class
vector at 1× is **48.3%**. The unit fix is the main correction.

A multiplier is still needed, but the response is now in the right range and is monotonic.

## 3. Interpretation

- `CURRMORT` is the correct lever.
- The major error was the DBH unit/class mapping, not the MPB module.
- A severity multiplier on the inch-class vector can be calibrated on training stands; 20× already
  reaches 87.5% on this stand.
- The exact multiplier must be fit across training stands and held out, not selected from this case.
- The 10-year cap remains separate; use five-year intervals for this calibration.

## 4. Next

1. Recompute inch-class CURRMORT vectors for all five-year high-PL training stands.
2. Fit one severity multiplier on training; hold out Williams Lake/SBPS stands.
3. Check non-PL BA/TPH.
4. Apply the calibrated vector to the post-2000 PL test.
5. Keep the 10-year cap out of the fitting window.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
