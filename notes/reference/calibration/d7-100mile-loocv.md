# D7.7 leave-one-site-out capacity for 100 Mile

Status: **no capacity candidate meets both BA and TPH across the LOSO folds**; the D7.6 2-interval
result was not stable
Date: 2026-11-03
Issue: #360
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSmk` / `100 Mile House TSA`; 16 intervals, 10 sites
Evidence: `d7-100mile-loocv-summary.csv`, `d7-100mile-loocv-candidates.json`

D7.6's test had only two intervals. This replaces it with a leave-one-site-out evaluation over the
same TSA, using every eligible site as a test fold.

## 1. Sample

- 16 intervals / 10 sites in 100 Mile House TSA.
- Eligibility leaves **7 intervals / 6 sites**; each site is held out once.
- A sensitivity run on all 16 intervals is worse in BA for every candidate; the seven eligible
  intervals are the calibration target, not the young/high-mortality stands.

## 2. Result

Pooled over the six site folds:

| BAMAX | BA bias | BA % | TPH bias | TPH % |
| ---: | ---: | ---: | ---: | ---: |
| 25 | +1.32 | +4.3% | -571 | -29.5% |
| 30 | +7.32 | +23.6% | -281 | -14.5% |
| 32 | +9.03 | +29.2% | -197 | -10.2% |
| 35 | +11.03 | +35.6% | -99 | -5.1% |
| 38 | +12.60 | +40.7% | -24 | -1.3% |
| 40 | +13.32 | +43.0% | +17 | +0.9% |
| 50 | +15.75 | +50.8% | +145 | +7.5% |

- `BAMAX 25` passes the BA threshold (+4.3%) but misses TPH badly (-29.5%).
- `BAMAX 30` passes TPH (-14.5%) but misses BA (+23.6%).
- No `BAMAX` value passes both. The trade-off is monotonic: lowering capacity fixes BA and loses TPH.

The D7.6 `bamax30` test BA of -4.74 on two intervals does not survive LOSO (+23.6%); the two-interval
split was not a stable estimate.

## 3. What this means

A capacity parameter alone cannot represent 100 Mile. The missing component is **recruitment/TPH** at
the low-BAMAX end, not another BAMAX value. The next experiment is a **100 Mile-specific ingrowth
model** trained leave-one-site-out within the TSA, applied with `BAMAX 25`:

- if it raises TPH from -29.5% into the 15% band without pushing BA out of its band, 100 Mile has a
  candidate;
- if not, the residual points at the growth/site-series equation, not a multiplier.

The all-16 sensitivity run is in the runtime probe; it is not a calibration target because it mixes
young/ingrowth and high-mortality stands.

## 4. Claim boundary

This is a screening report. It does not calibrate 100 Mile, does not change a default, and does not
support a yield, AAC, legal, or whole-block claim. The defensible statement is that no BAMAX-only
capacity passes both pre-registered biases across the eligible LOSO folds.
