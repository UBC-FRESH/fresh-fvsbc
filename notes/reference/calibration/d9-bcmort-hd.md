# D9.35 BCMORT height/DBH screen

Status: **height/DBH helps MSdm1, neutral on SBSmw; calibration still unresolved**
Date: 2026-11-08
Code: `bcmort_hd.py`
Evidence: `d9-bcmort-hd-summary.csv`

## 1. Design

D9.34 added crown class to the BCMORT prototype. This screen adds the tree height at the start
visit and forms height/DBH:

`height_dbh = HEIGHT / (DBH / 100)`

This is a coarse vigor and stability proxy, not a continuous crown ratio. Height is present for
100% of the MSdm1/SBSmw survival rows in this extract.

The local calibration is the D9.32 target-TSA intercept: fit on the source TSA, estimate one
intercept on half the target sites, test the other half, and repeat 40 random site splits.

This is a diagnostic prototype, not an FVS core change.

## 2. Result

| BEC | Train → test | AUC crown → +height/DBH | Log loss crown → +height/DBH | Brier crown → +height/DBH | Mean +height/DBH | Local mean | Local log loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.750 → **0.763** | 0.394 → **0.386** | 0.1233 → **0.1200** | 0.205 | 0.127 | 0.380 |
| MSdm1 | Boundary → Okanagan | 0.681 → **0.684** | 0.416 → **0.412** | 0.1272 → **0.1256** | 0.187 | 0.143 | 0.410 |
| SBSmw | Quesnel → Prince George | 0.760 → 0.758 | 0.382 → 0.382 | 0.1185 → 0.1186 | 0.154 | 0.145 | 0.386 |
| SBSmw | Prince George → Quesnel | 0.721 → 0.721 | 0.463 → 0.463 | 0.1387 → 0.1387 | 0.138 | 0.149 | 0.457 |

Height/DBH improves all three metrics on both MSdm1 directions. It is effectively flat on SBSmw:
Quesnel → Prince George is slightly worse, Prince George → Quesnel is unchanged.

The local target intercept still leaves a calibration gap:

- MSdm1 Okanagan → Boundary: local mean 0.127 vs 0.155 observed.
- MSdm1 Boundary → Okanagan: 0.143 vs 0.160.
- SBSmw Quesnel → Prince George: 0.145 vs 0.165; local log loss 0.386 is worse than the
  uncalibrated 0.382.
- SBSmw Prince George → Quesnel: 0.149 vs 0.186.

## 3. Interpretation

- Height/DBH is a useful MSdm1 covariate, consistent with vigor/stability affecting survival.
- It is not a universal SBSmw covariate; the direction and magnitude are BEC/species dependent.
- It is not a calibration solution. The target mean remains biased after a local intercept, so the
  missing term is still local or hierarchical, not another tree-level ratio.
- A continuous crown ratio is still unavailable in this data; height/DBH is only a proxy.

## 4. Decision

- Add height/DBH to the MSdm1 BCMORT prototype; do not add it as a universal term yet.
- Do not integrate into FVS and do not issue a bundle.
- Continue with hierarchical TSA/site effects and a local target intercept; test growth next.
- No parameter or bundle change.

## 5. Limits

- Only two TSAs per BEC and one height measurement per tree.
- `HEIGHT` is a field value; this screen does not validate its measurement quality or the correct
  functional form.
- The crown model already includes crown class; height/DBH is not independent of site quality.
- The target intercept is a 50/50 site split repeated 40 times, not a production calibration.
- No climate, recent growth, or continuous crown ratio yet.

## 6. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim, and
it is not a certificate.
