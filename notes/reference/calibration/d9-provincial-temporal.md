# D9.45 post-2000 provincial mortality validation

Status: **the temporal failure is a PL/MPB disturbance, not a general model failure**
Date: 2026-11-08
Code: `bcmort_provincial_temporal.py`
Evidence: `d9-provincial-temporal-summary.csv`

## 1. Design

Train the D9.42 provincial model on intervals ending by 2000; test on intervals starting in 2000 or
later. All species groups share the same covariate design and BEC-zone effects.

## 2. Result

| Group | n | AUC | Mean predicted | Observed | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| FD | 25,441 | 0.735 | 0.146 | 0.125 | 0.358 |
| PL | 20,523 | **0.447** | **0.189** | **0.506** | **1.319** |
| SE | 13,358 | 0.691 | 0.145 | 0.171 | 0.463 |
| HW | 34,237 | 0.731 | 0.176 | 0.167 | 0.436 |
| OTHER | 29,910 | 0.687 | 0.191 | 0.189 | 0.483 |
| ALL | 123,469 | **0.640** | 0.173 | 0.220 | 0.581 |

## 3. Interpretation

- The non-PL groups retain credible discrimination (AUC 0.69–0.74) and roughly calibrated means.
- PL is the failure: observed mortality is 0.506, predicted 0.189, and AUC is 0.447. This is the
  post-2000 mountain pine beetle collapse, not a generic provincial model failure.
- The pooled ALL row is dominated by PL log loss. Reporting only the pooled number hides the seam.
- Calibrating a global year or TSA intercept would smear a disturbance signal across all species.
  It would not be the right model.

## 4. Decision

- Treat PL post-2000 mortality as a **disturbance process**, not background mortality.
- The BC FVS source has an `MPB` keyword and a full `fvs/lpmpb` extension, but the shipped BC source
  list uses the stub `fvs/base/exmpb.f`. The BC variant has no active MPB module.
- The next core upgrade is to supply BC MPB block data and link the real MPB extension, then test
  it against these post-2000 PL intervals.
- Do not integrate the provincial background model as a PL post-2000 calibration.
- No bundle.

## 5. Limits

- One temporal split; MPB is not identified by a beetle covariate, only by the PL pattern.
- Other disturbances (fire, wind, defoliators) can also enter the post-2000 test.
- The provincial model still uses observed growth.
- The MPB extension requires species block data and keyword settings for BC; not yet built.

## 6. Claim boundary

This is a diagnostic validation. It does not support a yield, AAC, legal, or whole-block claim, and
it is not a certificate.
