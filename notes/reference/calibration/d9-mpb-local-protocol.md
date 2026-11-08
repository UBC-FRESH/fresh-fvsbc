# D9.59 local MPB severity calibration protocol

Status: **target-TSA calibration is the defensible MPB layer; Williams Lake needs a covariate**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Panel: 12 five-year high-PL intervals

## 1. Protocol

Do not use a provincial INITMORT multiplier. For a target TSA:

1. Collect high-PL five-year intervals from the target TSA.
2. Build the inch-class observed `INITMORT` vector for each interval.
3. Fit one multiplier from a fixed grid (0.02–0.08) on a calibration subset.
4. Apply it to held-out target intervals.
5. Report the local sample size and uncertainty.
6. Check non-PL BA/TPH.

This is a local severity layer, not a global mortality multiplier.

## 2. Panel result

| TSA | High-PL intervals | Local leave-one-out MAE |
| --- | ---: | ---: |
| 100 Mile | 4 | **0.043** |
| Williams Lake | 8 | **0.134** |

A target-TSA scalar works for the 100 Mile panel. Williams Lake remains heterogeneous; individual
errors reach about 0.20, so one scalar is too coarse there.

## 3. Decision

- 100 Mile: local INITMORT scalar is acceptable for the prototype.
- Williams Lake: require a severity covariate model (PL BA/TPH, QMD, percent PL, BEC) or finer
  local strata.
- Do not use a province-wide INITMORT multiplier.
- Do not integrate or issue a bundle.
- Next: fit the Williams Lake severity covariate, then couple FVS-predicted growth and rerun the
  Quesnel closure.

## 4. Limits

- Twelve five-year high-PL intervals.
- Williams Lake spans SBSdw1/SBSdw2/SBPSmk; a single TSA scalar is too coarse.
- No non-PL check in this note; it remains required for every run.
- No temporal or long-interval validation.

## 5. Claim boundary

This is a diagnostic calibration protocol. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
