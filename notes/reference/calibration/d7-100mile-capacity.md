# D7.6 100 Mile TSA capacity

Status: **no bundle**; the best training candidate fails the test BA threshold, and the test has two
intervals
Date: 2026-11-03
Issue: #357
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSmk` intervals in `100 Mile House TSA` only
Evidence: `d7-100mile-summary.csv`, `d7-100mile-candidates.json`

D7.5 showed that models trained on other TSAs do not transfer to 100 Mile House. This asks whether a
capacity fitted **inside** 100 Mile, with a site holdout, can represent that TSA.

## 1. Sample

- 16 `SBPSmk` intervals, 10 sites in 100 Mile House TSA.
- Eligibility leaves **7 intervals / 6 sites**.
- Every third eligible site is test: **2 sites / 2 test intervals**; the other 4 sites / 5 intervals
  train.

The test is small. A pass here is a screening result, not an independent validation.

## 2. Result

| Candidate | Fold | n | BA bias | BA % | TPH bias | TPH % |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `bamax30` | train | 5 | +12.14 | +42.1% | -374.8 | -17.1% |
| `bamax30` | test | 2 | -4.74 | -13.1% | -45.7 | -3.5% |
| `bamax35` | train | 5 | +15.94 | +55.2% | -187.8 | -8.6% |
| `bamax35` | test | 2 | -1.24 | -3.4% | +121.8 | +9.3% |
| `bamax40` | train | 5 | +18.14 | +62.9% | -71.8 | -3.3% |
| `bamax40` | test | 2 | +1.26 | +3.5% | +237.8 | +18.1% |
| `bamax50` | train | 5 | +20.74 | +71.9% | +55.4 | +2.5% |
| `bamax50` | test | 2 | +3.26 | +9.0% | +370.3 | +28.2% |

The best **training** candidate is `bamax30`; its test BA is **-4.74**, outside the ±3 m2/ha
threshold. `bamax35` happens to pass on the two test intervals, but it is not selected by training
and its training BA is +55%. Picking it would be test-set tuning.

The train BA bias is positive for every candidate while the test bias changes sign; the five training
intervals are not a coherent capacity sample.

## 3. Decision

No 100 Mile capacity bundle is promoted.

- The training fit and test result disagree for every candidate.
- The test contains only two intervals.
- `bamax35` is recorded as a **screening candidate**, not a bundle.
- The next step is more 100 Mile sites or a temporal holdout, not a parameter pick from this split.

## 4. Claim boundary

This is a screening report. It does not calibrate 100 Mile House, does not change a default, and does
not support a yield, AAC, legal, or whole-block claim.
