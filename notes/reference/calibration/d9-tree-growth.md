# D9.37 individual-tree prior growth in BCMORT

Status: **strongest tree-level covariate so far; calibration still needs target data**
Date: 2026-11-08
Code: `bcmort_tree_growth.py`; dataset builder in `src/fresh_fvsbc/calibration.py`
Evidence: `d9-tree-growth-summary.csv`

## 1. Data change

The calibration dataset now carries, in `tree_survival.csv`:

- `TREE_NO`, `species`, and `HEIGHT` for the start tree;
- `prior_dbh` and `prior_year` from the tree's previous live measurement;
- `growth = (dbh - prior_dbh) / (year0 - prior_year)`.

Growth is measured before the survival interval starts. It does not use the current interval's
end status, diameter, or any future visit. Coverage in the MSdm1/SBSmw rows is 56.4%; a missing flag
is included, and missing growth is filled with the median for the screen.

The tree-level dataset stays external. This is a data-contract change, not a new field on a bundle.

## 2. Result

The D9.35 height/DBH model is the baseline. Adding individual-tree prior growth improves every
held-out direction:

| BEC | Train → test | AUC H/D → +growth | Log loss H/D → +growth | Brier H/D → +growth |
| --- | --- | ---: | ---: | ---: |
| MSdm1 | Okanagan → Boundary | 0.770 → **0.776** | 0.383 → **0.375** | 0.1185 → **0.1140** |
| MSdm1 | Boundary → Okanagan | 0.691 → **0.726** | 0.409 → **0.400** | 0.1244 → **0.1219** |
| SBSmw | Quesnel → Prince George | 0.758 → **0.780** | 0.382 → **0.371** | 0.1186 → **0.1151** |
| SBSmw | Prince George → Quesnel | 0.721 → **0.751** | 0.463 → **0.442** | 0.1388 → **0.1332** |

This is the first covariate that improves all three metrics in all four directions. The largest gain
is MSdm1 Boundary → Okanagan (AUC 0.691 → 0.726); SBSmw Prince George → Quesnel improves log loss
from 0.463 to 0.442.

The H/D baseline differs slightly from D9.35 because D9.37 reads the rebuilt `tree_survival` directly
instead of merging the raw height on site/plot/DBH. The growth comparison is within this rebuilt
dataset.

## 3. Calibration

A local target intercept still does not solve the target mean:

- MSdm1 Okanagan → Boundary: local mean 0.124 vs 0.155 observed; log loss 0.370.
- MSdm1 Boundary → Okanagan: 0.144 vs 0.160; log loss 0.397.
- SBSmw Quesnel → Prince George: 0.144 vs 0.165; local log loss 0.375, worse than the uncalibrated
  0.372.
- SBSmw Prince George → Quesnel: 0.145 vs 0.186; log loss 0.438.

Growth improves discrimination and the tree-level hazard, but the target-TSA level still needs local
information. A local intercept can even make SBSmw Quesnel → Prince George slightly worse.

## 4. Decision

- Add individual-tree prior growth to the BCMORT prototype design; keep the rebuilt dataset external.
- Do not integrate into FVS and do not issue a bundle.
- Growth is now the first covariate to test in the hierarchical BCMORT, alongside crown class and
  height/DBH.
- A production calibration still needs target-TSA data; growth does not remove that requirement.
- No parameter or bundle change.

## 5. Limits

- Growth is available for only 56.4% of the MSdm1/SBSmw survival rows. Trees without a prior live
  measurement have no growth; the missing flag is crude.
- The prior interval length varies; growth is divided by years but the measurement interval is not
  otherwise modeled.
- The dataset is only two TSAs per BEC. No temporal or provincial validation yet.
- No climate, continuous crown ratio, or seed-year term.
- The screen is a Poisson hazard with a single growth term, not a full FVS mortality submodel.

## 6. Claim boundary

This is a diagnostic prototype and a data-contract improvement. It does not support a yield, AAC,
legal, or whole-block claim, and it is not a certificate.
