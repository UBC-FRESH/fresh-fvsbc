# D9.58 high-PL MPB panel: twelve stands, local severity still required

Status: **a global INITMORT multiplier does not transfer; local/stand severity remains**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Panel: 12 post-2000 PL intervals of five years or less

## 1. Panel

- Four high-PL five-year intervals in the 100 Mile TSA (IDFdk3).
- Eight high-PL five-year intervals in the Williams Lake TSA (SBSdw1/SBSdw2/SBPSmk).

Observed PL mortality is 80.5–96.4%. `INITMORT` used the inch-class observed vector, scaled from
0.02 to 0.08.

## 2. Global multiplier result

| Set | Best training multiplier | MAE at 0.04 | MAE at 0.08 |
| --- | ---: | ---: | ---: |
| 100 Mile training | 0.08 | 0.226 | 0.043 |
| Williams Lake holdout | 0.04 | 0.091 | 0.104 |

The training optimum and holdout optimum differ. A single global multiplier is not transferable.

## 3. Local leave-one-site-out

Choosing one multiplier from the other sites in the same TSA:

- 100 Mile LOOSO MAE: **0.043**.
- Williams Lake LOOSO MAE: **0.134**.

Local calibration is much better than a cross-TSA global multiplier for 100 Mile, but the Williams
Lake panel is still heterogeneous: individual errors reach 0.20.

## 4. Interpretation

- `INITMORT` is the correct lever and the panel now spans 12 stands.
- Severity is local/stand-dependent; a single provincial multiplier is not defensible.
- A local high-PL sample can fit a TSA-level multiplier, but Williams Lake shows that a single TSA
  scalar is still too coarse for some stands.
- The next step is either a stand covariate severity model or per-target calibration with enough
  local high-PL intervals.
- The 10-year cap remains separate; all panel intervals are five years or less.

## 5. Decision

- Do not adopt a global INITMORT multiplier.
- Require a target-TSA high-PL calibration sample; report its size and uncertainty.
- For a stand-level claim, use a local stand/TSA severity fit, not a province-wide constant.
- No integration or bundle.

## 6. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
