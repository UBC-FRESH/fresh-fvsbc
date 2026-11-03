# D7.11 Quesnel established-stand capacity boundary

Status: **pooled pass at BAMAX 75, but site folds fail**; no bundle
Date: 2026-11-03
Issue: #371
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSdc` / `Quesnel TSA`; 39 eligible intervals, 13 sites
Evidence: `d7-quesnel-established-summary.csv`

D7.10 found the dense small-tree site fails at `BAMAX 55`. This tests a higher capacity on the
established stands only.

## 1. Strata

- Dense small-tree stratum: initial `QMD < 9` (3 intervals, one site). It is **validation-only**;
  the D7.10 result is BA +151% under `BAMAX 55`.
- Established stratum: `QMD >= 9` (36 intervals, 12 sites).
- `BAMAX 70`, 75, 80; no ingrowth or mortality multiplier.

## 2. Result

| BAMAX | Pooled BA % | Pooled TPH % | Worst site BA % | Worst site TPH % |
| ---: | ---: | ---: | ---: | ---: |
| 70 | +3.1% | -15.0% | 35.2% | 45.0% |
| **75** | **+3.6%** | **-14.5%** | **35.2%** | **44.2%** |
| 80 | +4.2% | -14.1% | 35.2% | 43.5% |

`BAMAX 75` passes both pooled thresholds. It does **not** pass the site-fold test: one established
site has BA +35%, and another has TPH -44%. The pooled pass is not consistent across sites.

The dense stratum is not a small perturbation: it is a different stand structure, and it cannot be
folded into the same BAMAX.

## 3. Decision

**No Quesnel bundle.** `BAMAX 75` is a pooled established-stand reference, not a domain candidate.

The remaining obstacle is **site-to-site variation inside the established stratum**, not the global
capacity. A single BAMAX, even at the upper bound of the tested grid, cannot remove it.

## 4. Next

- Fit a **site-level/density-class effect** on training sites only, for example BAMAX by initial
  QMD/BA class or a hierarchical capacity.
- If no covariate explains the +35% BA and -44% TPH sites, keep those sites validation-only and
  narrow the claim to the sites the model represents.
- Do not raise `QMD` eligibility or drop a site after seeing its residual.
- Re-run the same site-grouped split; then a temporal holdout on the established sites.

## 5. Claim boundary

This is a capacity screen. It does not calibrate Quesnel, change a default, or support a yield, AAC,
legal, or whole-block claim.
