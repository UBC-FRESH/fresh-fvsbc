# SBSmc2 independent sites: none exist locally

Status: **confirmed data block.** No code or bundle change.

## 1. The raw PSP SBSmc2 inventory

`faib_header.csv` lists **182 SBSmc2 sites** (`BEC_ZONE=SBS`, `BEC_SBZ=mc`, `BEC_VAR=2`).
The calibration interval set contains **126** of them. The other **56**:

- all have exactly **one visit** and one measurement year (`faib_sample_byvisit`), and
- all have tree rows at that visit, but no remeasurement.

With one visit there is no growth interval, so none can serve as a held-out growth fold.

## 2. Age / site-index keyed term

The fold's tree lists are built with a constant `tree_age = 60` and `SITECODE ("PL", "18")`;
the probe's `keywords_for` does not pass per-interval age or site index. An age- or SI-keyed
mortality/ingress term therefore collapses to a constant in the fold and cannot be identified.
Passing observed site index per interval is a **fold-methodology change** that would alter the
baseline (the rows themselves use SI), not a shape test.

## 3. What this means

The SBSmc2 residual (+2.2 m²/ha / −323 TPH) cannot be pushed further with the local data:

- The 126 remeasured sites have been re-split (random and BA-stratified); both splits leave a
  BA 40–65 sign divergence.
- BA-bin and QMD-based shapes have both been tested and fail.
- No independent remeasurement sites exist; the 56 extras are single-visit.
- Age/SI shapes are not identifiable without per-interval inputs.

Progress needs one of:

1. **Independent remeasured SBSmc2 sites** (a second measurement campaign), or
2. **Per-interval site index and age** in the fold plus a deliberate fold-methodology change, or
3. a decision to accept the matched-fold estimate (+2.2/−323) as final.

## Reproduce

- Header inventory: `faib_header.csv` filter above; calibration sites from
  `~/workspace/bwbs-work/calib/intervals.csv`.
- Visit counts: `faib_sample_byvisit.csv`.
