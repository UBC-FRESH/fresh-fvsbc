# D7.18 SBPSmk growth multiplier screen

Status: **partial fix; no full-domain bundle**
Date: 2026-11-04
Issue: #390
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Domain: SBPSmk / Quesnel TSA, QMD >= 13
Evidence: `d7-sbpsmk-growth-summary.csv`

D7.17 showed that SBPSmk/Quesnel fails on low-density sites with BA underprediction. This screen
tests a species-level BA increment multiplier, then adds a Quesnel ingrowth model.

## 1. Result

113 intervals / 43 sites; BAMAX 75.

| Candidate | BA | TPH | Worst BA | Worst TPH | Sites passing |
| --- | ---: | ---: | ---: | ---: | ---: |
| BAMAX 75 | -6.1% | -10.2% | 30.6% | 64.6% | 29 / 43 |
| + BAIMULT 1.25 | -3.9% | -10.5% | 27.8% | 64.6% | 35 / 43 |
| + BAIMULT 1.50 | -1.7% | -10.9% | 25.1% | 64.7% | 34 / 43 |
| + BAIMULT 1.25 + ingrowth | -2.8% | -5.8% | 25.1% | 62.6% | **39 / 43** |
| + BAIMULT 1.25 + ingrowth x2 | -1.5% | -1.1% | 25.1% | 60.6% | 38 / 43 |

The BA multiplier closes most of the BA gap; the ingrowth model closes most of the TPH gap. The best
combination still leaves **4 of 43 sites failing**, all low-QMD / high-productivity sites with high
observed net BA rate.

## 2. What the remaining failures look like

The four failures have:

- initial QMD 13.7–15.4 cm;
- initial top height 19.9–25.1 m;
- observed net BA rate 0.55–1.13 m2/ha/yr, versus 0.34 for the passing sites.

They are dense, fast-growing stands. A single growth/recruitment multiplier cannot represent both
them and the older, slower stands. Scaling ingrowth upward improves the pooled TPH but overshoots
some passing sites, so the site-pass count gets worse.

## 3. A narrower domain

Restricting to **QMD >= 17 and initial BA >= 20** leaves 48 intervals / 25 sites. On that subset,
`BAMAX 75 + BAIMULT 1.25 + Quesnel ingrowth` passes every site in-sample (BA -4.0%, TPH +0.3%).
This is a mature, closed-canopy stratum; it excludes the low-BA fast-growth failures.

That subset is a **post-hoc domain**, not yet validated. It needs site-grouped LOSO and a temporal
split before any bundle. D7.19 is that validation.

## 4. Decision

- No SBPSmk full-domain bundle.
- The Quesnel SBPSdc high-QMD candidate remains separate and unsigned.
- A narrower SBPSmk mature-stand candidate is worth testing; do not call it calibrated until the
  site-grouped and temporal checks pass.

## 5. Claim boundary

This is a screen. It does not calibrate SBPSmk, change a default, or support a yield, AAC, legal, or
whole-block claim.
