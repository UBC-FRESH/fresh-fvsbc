# D9.57 ESSFdry direct-calibration protocol

Status: **pre-registered before fitting; no result yet**
Date: 2026-11-08
Data: PSP 4 cm (`psp4`), domain `ESSFdry`
Candidates: `d9-essf-dry-candidates.json`

D9.55 puts ESSFdry in `D-needs-work`: the identity default fails the independent non-PSP screen
(BA −22.4%, TPH −16.5%). This protocol tests whether a simple, fixed growth/mortality multiplier can
repair that failure without a site-specific refit. It is a screen, not a certificate.

## 1. Domain and sample

`ESSFdry` is the domain grouping in `w2-bec-gap.csv`, not a literal BEC prefix. Filtering the 4 cm
PSP interval table by that mapping gives:

- 253 raw intervals, 112 sites, 13 BEC labels;
- 177 eligible intervals after the standard filters (initial BA at least 15 m2/ha, initial QMD at
  least 6 cm, mortality no more than 40 percent);
- 87 eligible sites.

The five-per-BEC sample keeps the run comparable with the D9.55 external screen.

## 2. Spatial holdout

**Test: Okanagan TSA, 23 eligible sites.** Train: every other TSA. Okanagan is the largest ESSFdry
TSA in the eligible sample, so it is a pre-registered choice based on sample size, not a result.

The site list is frozen in the runtime directory before the run; it is not tracked because it
carries site identifiers. No candidate is refit on Okanagan, and the test fold is read once after
the training choice is frozen.

## 3. Candidate grid

The grid is deliberately small: BAIMULT 1.5, 2.0, 3.0, and 4.0 at MORTMULT 1.0; and BAIMULT 2.0,
3.0, and 4.0 at MORTMULT 0.5. The identity default is the baseline row.

The species list is the union used in the candidate file: FD, HW, CW, BG, PW, PL, SE, BL, LW, AT,
AC. A species not in the list inherits the uncalibrated default; that is recorded rather than hidden.

No `REGDMULT`, `HTGMULT`, `BAMAX`, or ingrowth parameter is varied in this screen. The question is
whether the simplest BA/mortality correction is enough.

## 4. Selection rule

On the **training fold only**:

1. Keep candidates whose BA bias is within ±3 m2/ha or ±10 percent and whose TPH bias is within
   ±15 percent.
2. Among those, minimize the larger normalized absolute bias:
   `max(abs(ba_pct) / 10, abs(tph_pct) / 15)`.
3. Break ties by the higher BA site-pass count, then by the higher TPH site-pass count.

If no candidate passes both training bands, the result is **no candidate** and the domain remains
`D-needs-work`. The selected candidate is frozen before the Okanagan and external rows are read.

## 5. Test and external check

Frozen candidate is run once on:

- Okanagan TSA (spatial holdout);
- the repeated non-PSP ESSFdry cohort, five intervals per BEC, 4 cm.

Both use the same BA/TPH bands and site bootstrap as D9.55. QMD, height, volume, and species
composition are not claimed unless separately validated.

## 6. Claim boundary

This is a direct-calibration screen for one domain. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate. A passing result would be an unsigned candidate
bundle at most; a failing result is equally useful and will be recorded as a negative result.
