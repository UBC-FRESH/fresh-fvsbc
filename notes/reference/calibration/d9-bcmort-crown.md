# D9.34 BCMORT crown-class screen

Status: **crown class improves held-out discrimination in 3/4 directions; calibration still unresolved**
Date: 2026-11-08
Code: `bcmort_crown.py`
Evidence: `d9-bcmort-crown-summary.csv`

## 1. Design

The base BCMORT prototype uses DBH, BAL, initial BA, QMD, relative DBH, damage, and species
group. This screen adds the raw tree crown class at the start visit:

- D = dominant (1), C = codominant (2), I = intermediate (3), S = suppressed (4);
- 98.1% coverage in the MSdm1/SBSmw survival rows;
- missing values are filled with the median and a missing flag is included;
- the target intercept is estimated on half the target sites and tested on the other half, as in
  D9.32.

This is a diagnostic prototype, not an FVS core change.

## 2. Result

| BEC | Train → test | AUC base → crown | Log loss base → crown | Brier base → crown | Mean base → crown | Local mean | Local log loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.721 → **0.750** | 0.411 → **0.394** | 0.1295 → **0.1233** | 0.212 → 0.211 | 0.128 | 0.385 |
| MSdm1 | Boundary → Okanagan | 0.694 → 0.681 | 0.411 → 0.416 | 0.1256 → 0.1272 | 0.179 → 0.195 | 0.144 | 0.413 |
| SBSmw | Quesnel → Prince George | 0.745 → **0.760** | 0.390 → **0.382** | 0.1216 → **0.1185** | 0.155 → 0.154 | 0.145 | 0.385 |
| SBSmw | Prince George → Quesnel | 0.710 → **0.721** | 0.472 → **0.463** | 0.1405 → **0.1387** | 0.142 → 0.138 | 0.149 | 0.457 |

Crown class improves discrimination, log loss, and Brier in three of four directions. It does not
improve MSdm1 Boundary → Okanagan, where all three metrics get slightly worse.

The local target intercept improves the crown model's log loss in three directions and leaves
SBSmw Quesnel → Prince George slightly worse (0.382 → 0.385). It still does not calibrate the
target mean: the local mean is 0.128 vs 0.155 observed for MSdm1 Okanagan → Boundary, and 0.149 vs
0.186 for SBSmw Prince George → Quesnel.

## 3. Interpretation

- Crown class is the first tree-level covariate tested that adds held-out signal beyond DBH/BAL/BA/
  QMD/species. Site index did not.
- The signal is direction-dependent, so it is not a universal TSA-transfer fix.
- Crown class is a coarse ordinal field variable. It is not the continuous crown ratio the FVS
  mortality literature uses, and this screen does not establish the correct functional form.
- The remaining target mean gap is still a local calibration or missing-covariate problem, not a
  reason to add another global multiplier.

## 4. Decision

- Add crown class to the next BCMORT prototype design; do not integrate it into FVS yet.
- Do not promote a bundle or claim a CWH/BCMORT calibration from this screen.
- Continue with hierarchical TSA/site effects and a local target intercept; test a continuous
  crown-ratio or growth covariate next.
- No parameter or bundle change.

## 5. Limits

- Only two TSAs per BEC and one tree-level crown field.
- The crown merge averages duplicate plot/species/DBH records; it is not a tree-identity join.
- The crown model uses the same Poisson hazard and exposure as the base prototype.
- The local intercept is a 50/50 site split, repeated 40 times, not a production calibration.
- No climate, growth, or continuous crown ratio yet.

## 6. Claim boundary

This is a diagnostic prototype. It does not support a yield, AAC, legal, or whole-block claim, and
it is not a certificate.
