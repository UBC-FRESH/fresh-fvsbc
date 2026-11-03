# D7.9 100 Mile temporal holdout

Status: **not validated**; the temporal test has one eligible interval and it fails BA
Date: 2026-11-03
Issue: #366
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSmk` / `100 Mile House TSA`; 16 intervals, 10 sites
Evidence: `d7-100mile-temporal-summary.csv`, `d7-100mile-temporal.json`

D7.8's candidate passed a site-grouped holdout. This is the required temporal holdout: train rates on
earlier intervals, test on later ones.

## 1. Split

- Train: intervals starting in **1998 or earlier** (10 intervals).
- Test: intervals starting in **2001 or later** (6 intervals).
- The temporal rates are in `d7-100mile-temporal.json`; the candidate is `BAMAX 25` plus those rates,
  with no MORTMULT/BAIMULT/HTGMULT.

## 2. Result

| Fold | n | BA bias | BA % | TPH bias | TPH % |
| --- | ---: | ---: | ---: | ---: | ---: |
| train <= 1998 | 10 | +16.18 | +62.5% | +36.8 | +1.4% |
| test >= 2001, all | 6 | +23.72 | +174.3% | +653.7 | +33.1% |
| test >= 2001, eligible | **1** | +7.51 | +33.4% | -173.2 | -5.95% |

The all-test row is dominated by high-mortality stands: five of the six later intervals have dead BA
of 53–97% of initial BA. Those are disturbances, not calibration targets.

The only eligible later interval has BA **+33.4%**, outside the ±10% band. TPH is -5.95%, inside the
band, but one interval cannot validate the candidate.

## 3. Decision

The 100 Mile candidate is **not validated temporally and no bundle is issued**.

- The temporal sample has one eligible later interval; that is too small for a claim.
- The candidate remains the best site-grouped result (D7.8), not a certificate.
- The failure is a **data gap**, not evidence that the candidate is wrong: 100 Mile has only 10 sites
  and the later visits are dominated by mortality events.

## 4. Next

1. Acquire newer or additional 100 Mile remeasurements, or a second TSA with a usable temporal
   split; the current extract cannot supply one.
2. Until then, keep the D7.8 result as a **candidate** with the site-grouped claim boundary.
3. If more data arrive, rerun this exact split before creating a bundle.
4. Do not replace the temporal test with another site split and call it temporal.

## 5. Claim boundary

This is a validation attempt. It does not certify 100 Mile, does not change a default, and does not
support a yield, AAC, legal, or whole-block claim. The only positive statement remains the D7.8
site-grouped candidate.
