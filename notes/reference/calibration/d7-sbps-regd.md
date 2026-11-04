# D7.24 REGDMULT does not fix the SBPSmk site failures

Status: **negative result**; no bundle
Date: 2026-11-04
Issue: #421
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Evidence: `d7-sbps-regd-summary.csv`

The CWH 4 cm pilot (D9.6) showed that a small-tree growth multiplier (`REGDMULT`) can fix a
4–9 cm component that a large-tree `BAIMULT` cannot. This tests the same lever on the SBPSmk/Quesnel
site failures.

## 1. Design

- Domain: SBPSmk/Quesnel, QMD >= 13, BA >= 15, mortality fraction <= 0.4.
- 113 intervals / 43 sites.
- Base: `BAMAX 75`, `BAIMULT 1.25`, Quesnel ingrowth.
- `REGDMULT` 1.5, 2.0, 3.0, 4.0 for PL, SE, BL, FD, HW; then PL-only and SE-only variants.
- No temporal or site split here; this is a lever screen on the same sample.

## 2. Result

| Candidate | BA | TPH | Worst BA | Worst TPH | Sites passing |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base, no REGDMULT | -2.8% | -5.8% | 25.1% | 62.6% | **39 / 43** |
| REGDMULT 1.5 | -0.5% | -6.2% | 25.1% | 62.6% | 36 / 43 |
| REGDMULT 2.0 | +2.5% | -6.6% | 31.2% | 62.6% | 32 / 43 |
| REGDMULT 3.0 | +10.7% | -7.6% | 66.7% | 62.6% | 22 / 43 |
| REGDMULT 4.0 | +21.6% | -8.5% | 113.2% | 62.6% | 16 / 43 |
| PL-only 2.0 | +1.5% | -6.5% | 31.2% | 62.6% | 33 / 43 |
| SE-only 2.0 | -1.9% | -6.0% | 25.1% | 62.6% | 38 / 43 |

No variant improves the site-pass count. The pooled BA can be pushed toward zero, but the worst
sites get worse and TPH does not move. The four failing sites are not a small-tree diameter-growth
problem alone.

## 3. Decision

- No SBPSmk bundle.
- Do not tune `REGDMULT` further on these sites.
- The CWH small-tree lever does not transfer as a global SBPS multiplier.
- The remaining failure is site-level variation, not a missing global growth multiplier.

## 4. What would be different

A per-site or covariate model would need to explain why these four sites grow faster than their
QMD/BA peers. `REGDMULT` cannot do that globally. A future attempt needs an independent cohort or a
site-level covariate, not another multiplier sweep.

## 5. Claim boundary

This is a negative lever screen. It does not support a yield, AAC, legal, or whole-block claim.
