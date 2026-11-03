# D7.10 SBPSdc Quesnel capacity

Status: **pooled candidate passes, but one dense small-tree site fails badly**; no bundle
Date: 2026-11-03
Issue: #368
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSdc` / `Quesnel TSA`; 48 intervals, 16 sites; 39 eligible intervals, 13 sites
Evidence: `d7-sbpsdc-capacity-summary.csv`

The 100 Mile playbook is applied to the larger Quesnel SBPSdc sample. This is a capacity screen, not
a bundle.

## 1. Sample

- 48 intervals / 16 sites; multiple remeasurements from 1961 to 2023.
- Eligibility leaves 39 intervals / 13 sites.
- The split is site-grouped; every eligible site is a test fold in the pooled result.

## 2. Result

| BAMAX | BA % | TPH % |
| ---: | ---: | ---: |
| 30 | -17.7% | -36.6% |
| 35 | -8.0% | -28.7% |
| 40 | -1.7% | -23.2% |
| 45 | +2.7% | -19.3% |
| 50 | +6.4% | -16.5% |
| **55** | **+8.9%** | **-14.4%** |
| 60 | +10.8% | -12.8% |
| 65 | +12.3% | -11.6% |

`BAMAX 55` passes both pooled thresholds (BA ±10%, TPH ±15%). `BAMAX 60` misses BA just outside the
10% band. This is a much better pooled fit than 100 Mile.

## 3. The site that breaks it

One dense small-tree site has two intervals with initial QMD 6.8–8.4 and TPH 3,300–5,800. Under
`BAMAX 55` its BA error is **+151%**; the worst-site BA error is far outside the threshold. The
pooled result is carried by the other twelve sites.

The same site also has the largest TPH residual. A single `BAMAX` cannot represent both this
small-tree stand and the established stands around it. Raising eligibility to exclude it would be
test-set tuning, not a fix.

## 4. Decision

- **No Quesnel bundle.**
- `BAMAX 55` is a **pooled candidate** for the established stands, not a domain candidate.
- The dense small-tree site needs a separate stratum or a structural small-tree model; another
  `BAMAX` value is not the lever.
- The next experiment is a **density-stratified capacity**: established stands use `BAMAX 55`;
  small-tree stands (`QMD` below about 9 / high TPH) need their own capacity and recruitment.

## 5. Next

1. Fit a density-stratified rule on training sites only; test it on the held-out site, including the
   dense stand.
2. If the dense stratum cannot be represented, keep it validation-only and report the claim
   boundary; do not hide it by raising `min_qmd` after seeing the result.
3. Then run a temporal holdout on the established Quesnel sites.

## 6. Claim boundary

This is a capacity screen. It does not calibrate Quesnel, change a default, or support a yield, AAC,
legal, or whole-block claim. The pooled `BAMAX 55` result is not a bundle because one site fails by
151%.
