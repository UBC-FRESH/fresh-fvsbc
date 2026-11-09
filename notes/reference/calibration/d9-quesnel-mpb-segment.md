# D9.66 Quesnel MPB segment test

Status: **the 10-year MPB segment reaches most of the observed Quesnel PL collapse**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Cases: `4031355|1|2000|2013`, `4031394|1|2001|2014`

## 1. Why segment

Quesnel high-PL intervals are 13–14 years. The MPB extension has a 10-year outbreak cap, and
raising the cap double-counts dead trees. The test therefore uses two projection cycles:

- 10-year MPB/INITMORT segment;
- remaining 3–4-year background tail.

## 2. Result: MPB segment at 2010/2011

Observed PL mortality is 100% at the end of these intervals.

| Case | Initial live PL/ac | 0.04× live | 0.06× live | 0.08× live | 0.08× dead fraction |
| --- | ---: | ---: | ---: | ---: | ---: |
| `4031355` | 165.12 | 41.68 | 33.56 | 28.91 | 82.5% |
| `4031394` | 185.75 | 29.13 | 21.99 | 18.32 | 90.1% |

The 10-year MPB segment at 0.08× already removes 82–90% of the initial PL. The remaining 3–4-year
background tail is not included in those numbers.

## 3. Interpretation

- Segmenting long Quesnel intervals is the right workaround for the 10-year cap.
- INITMORT severity at 0.06–0.08 reaches most of the observed PL collapse before the tail.
- The remaining tail and final live PL need to be extracted before claiming a match.
- This is a stronger result than the pooled Quesnel post-2000 model, where PL was 0.295 vs 0.588
  observed.

## 4. Next

1. Extract final live PL/BA/TPH from the two-cycle projection.
2. Compare the final 2013/2014 values to the observed tree list.
3. Add the 3–4-year background tail explicitly.
4. Keep the local INITMORT severity; do not use a province-wide multiplier.
5. Then assemble the joint Quesnel non-PL + PL MPB report.

## 5. Claim boundary

This is a diagnostic segment test. It does not support a yield, AAC, legal, or whole-block claim, and
it is not a certificate.
