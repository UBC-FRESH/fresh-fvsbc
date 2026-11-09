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

## 2. Correction: one cycle, not two

An earlier version of this note used two `TIMEINT` cycles. FVS parsed those records in the wrong
order, so the first "10-year" MPB segment was actually 3 years. The corrected test uses one 13-year
projection; the MPB model internally caps the outbreak at 10 years, and the remaining 3 years are
background.

Corrected 0.08× result at the 10-year MPB segment end:

| Case | Initial live PL/ac | Segment live PL/ac | Segment dead PL/ac | Dead fraction |
| --- | ---: | ---: | ---: | ---: |
| `4031355` | 165.12 | 24.78 | 140.34 | **85.0%** |
| `4031394` | 185.75 | 16.40 | 169.36 | **91.2%** |

Observed PL mortality is 100% at the end of the full interval. The 10-year MPB segment at 0.08×
removes 85–91% of the initial PL.

Final tree-list check at 2013/2014:

- `4031355`: 85.0% dead at 0.08×, 89.6% at 0.15×; observed 100%.
- `4031394`: 91.2% dead at 0.08×, 93.3% at 0.15×; observed 100%.

The tail is included. Increasing INITMORT cannot force the last 7–15 points; the MPB model leaves
some live PL even at 0.15×. The residual is a host/size threshold or non-MPB mortality, not a
missing tail.

## 3. Interpretation

- Segmenting long Quesnel intervals is the right workaround for the 10-year cap.
- The one-cycle projection is the correct way to expose the 10-year MPB segment; the two-cycle
  `TIMEINT` representation was parsed in the wrong order.
- INITMORT severity at 0.08 reaches most of the observed PL collapse before the tail.
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
