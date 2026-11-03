# D7.8 100 Mile-specific ingrowth candidate

Status: **candidate passes the site-grouped LOSO**; temporal holdout D7.9 failed/unavailable; not a bundle or certificate
Date: 2026-11-03
Issue: #362
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: `SBPSmk` / `100 Mile House TSA`; 16 intervals, 10 sites
Evidence: `d7-100mile-ingrowth-loso-summary.csv`, `d7-100mile-ingrowth.json`

D7.7 showed the exact missing component: `BAMAX 25` fixes BA but leaves TPH low. This adds
100 Mile-specific recruitment instead of lowering mortality.

## 1. Candidate

- `BAMAX 25`
- no `BAIMULT`, `MORTMULT`, or `HTGMULT`
- 100 Mile-specific `ESTAB` recruitment, by species group, in `d7-100mile-ingrowth.json`

The canonical rates are trained on all 16 intervals / 10 sites:

| Group | Annual TPH |
| --- | ---: |
| FD | 4.00 |
| HW | 13.29 |
| PL | 75.71 |
| SE | 11.36 |

The validation rates are trained per fold, excluding the held-out site.

## 2. Result

Six leave-one-site-out folds, seven eligible test intervals:

| Metric | Value | Threshold |
| --- | ---: | --- |
| BA bias | +2.60 m2/ha | ±3 m2/ha |
| BA percent | +8.4% | ±10% |
| TPH bias | -253.5 | — |
| TPH percent | -13.1% | ±15% |

**Both BA and TPH pass.** This is the first 100 Mile candidate to do so on a site-grouped holdout.

## 3. What makes it different

- D7.7 `BAMAX 25` alone: BA +4.3%, TPH -29.5%.
- D7.7 `BAMAX 30` alone: BA +23.6%, TPH -14.5%.
- This candidate: BA +8.4%, TPH -13.1%.

The recruitment model closes the TPH gap without pushing BA out of its band. It does not use a
mortality multiplier; the D7.4 diagnosis was right about the mechanism.

## 4. Limits

- One TSA, 10 sites, 7 eligible intervals. The six folds are site-grouped, but the sample is small.
- The PL recruitment rate is high (75.7 TPH/year); a temporal holdout is required before a bundle.
- The canonical rates are fitted on all 100 Mile intervals; the LOSO evidence uses fold-specific
  rates, so the deployment numbers still need a frozen train/test split.
- The model is one `ESTAB` block at cycle 1; multi-cycle establishment is D8 work.
- No bundle, certificate, default change, or yield/AAC/legal claim.

## 5. Next

1. Temporal holdout within 100 Mile: D7.9 found only one eligible later interval and it fails BA (+33.4%). More data are required.
2. Freeze the rate model and add it to the bundle schema with an `ESTAB` section.
3. If the temporal holdout passes, issue a **100 Mile candidate bundle**, still not a certificate.

## 6. Claim boundary

On six site-grouped folds in 100 Mile House TSA, `BAMAX 25` plus a public-data 100 Mile-specific
recruitment model meets the pre-registered BA and TPH bias thresholds. It is a candidate, not a
certified calibration.
