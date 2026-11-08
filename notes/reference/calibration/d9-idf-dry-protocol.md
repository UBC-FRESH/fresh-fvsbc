# D9.58 IDFdry direct-calibration protocol

Status: **pre-registered before fitting; no result yet**
Date: 2026-11-08
Data: PSP 4 cm (`psp4`), domain `IDFdry`
Candidates: `d9-idf-dry-candidates.json`

D9.55 puts IDFdry in `D-needs-work`: the identity default is BA −11.0% and TPH −6.6% on the
independent non-PSP screen. This protocol tests a simple fixed BA/mortality correction before any
structural work.

## 1. Domain and sample

`IDFdry` is the domain grouping in `w2-bec-gap.csv`. It contains IDFdh, IDFdm, IDFdw, IDFmw2,
IDFww, IDFxh, IDFxw, and IDFxx2; it excludes IDFdk and IDFxm.

The 4 cm PSP table gives 1,167 raw intervals and 387 sites; the standard filters leave **968
eligible intervals and 353 sites**. The five-per-BEC sample is used, as in D9.55 and D9.57.

## 2. Spatial holdout

**Test: Kamloops TSA.** It is the largest eligible IDFdry TSA (237 intervals), so the choice is
pre-registered on sample size. The site list is frozen in the runtime directory, not tracked.

The training fold is every other TSA. The test fold is read once after the training choice is
frozen.

## 3. Candidate grid

| Label | BAIMULT | MORTMULT |
| --- | ---: | ---: |
| baseline | 1.0 | 1.0 |
| ba125-m10 | 1.25 | 1.0 |
| ba150-m10 | 1.5 | 1.0 |
| ba200-m10 | 2.0 | 1.0 |
| ba300-m10 | 3.0 | 1.0 |
| ba150-m075 | 1.5 | 0.75 |
| ba200-m075 | 2.0 | 0.75 |
| ba300-m075 | 3.0 | 0.75 |

The species list is FD, HW, CW, BG, PW, PL, SE, BL, LW, AT, AC. A species outside it inherits the
default. No `REGDMULT`, `HTGMULT`, `BAMAX`, or ingrowth parameter is varied.

## 4. Selection rule

On the training fold only, keep candidates inside BA ±3 m2/ha or ±10 percent and TPH ±15 percent;
minimize `max(abs(ba_pct)/10, abs(tph_pct)/15)`; break ties by the higher BA site-pass count, then
TPH site-pass count. If none passes, the result is no candidate.

The selected candidate is frozen before the Kamloops and external rows are read.

## 5. Test and external check

The frozen candidate is run once on Kamloops and once on the repeated non-PSP IDFdry cohort (five
intervals per BEC, 4 cm). Both use the D9.55 bands and site bootstrap. QMD, height, volume, and
species composition are not claimed.

## 6. Claim boundary

This is a direct-calibration screen for one domain. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate. A passing result is an unsigned candidate at most;
a failing result is recorded as a negative result.
