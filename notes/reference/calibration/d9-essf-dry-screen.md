# D9.57 ESSFdry direct-calibration screen: negative

Status: **no candidate; ESSFdry remains `D-needs-work`**
Date: 2026-11-08
Protocol: `d9-essf-dry-protocol.md` (pre-registered in `1df08fd`)
Candidates: `d9-essf-dry-candidates.json`
Evidence: `d9-essf-dry-selection.json`, `d9-essf-dry-probe-summary.csv`

The pre-registered grid was run before any test result was read. The selected candidate improves
the default but fails the spatial holdout and the external BA band, so it is not promoted.

## 1. Sample

The D9.55 domain mapping gives 253 ESSFdry intervals and 112 sites. The standard filters leave 177
eligible intervals and 87 sites. The five-per-BEC sample used for the probe has **52 intervals and
32 sites**.

The Okanagan TSA holdout contained 23 eligible sites, but the per-BEC cap selected only **6
intervals from 4 Okanagan sites**. That is the main design weakness: the spatial test is much
smaller than the 23-site pool.

## 2. Training result and selection

The training fold has 46 intervals. The selection rule kept candidates inside both training bands
and minimized the larger normalized absolute bias.

| Candidate | BA % | TPH % | Site pass BA / TPH | Selected |
| --- | ---: | ---: | ---: | --- |
| baseline | −19.12 | −8.74 | 8/28 / 11/28 | no |
| BAIMULT 1.5 / MORTMULT 1.0 | −17.94 | −8.85 | 9/28 / 11/28 | no |
| BAIMULT 2.0 / MORTMULT 1.0 | −16.82 | −8.99 | 9/28 / 10/28 | no |
| BAIMULT 3.0 / MORTMULT 1.0 | −14.81 | −9.23 | 8/28 / 10/28 | no |
| BAIMULT 2.0 / MORTMULT 0.5 | −9.71 | +0.49 | 10/28 / 12/28 | no |
| BAIMULT 3.0 / MORTMULT 0.5 | −6.86 | +0.37 | 10/28 / 11/28 | no |
| **BAIMULT 4.0 / MORTMULT 0.5** | **−3.78** | **+0.54** | **9/28 / 11/28** | **yes** |

The training fold has 28 sites. The full values are in `d9-essf-dry-selection.json`.

## 3. Spatial test

The frozen candidate, BAIMULT 4.0 / MORTMULT 0.5, was run once on the Okanagan holdout:

| Fold | n | BA bias | BA % | TPH bias | TPH % | Site pass BA / TPH |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Okanagan test | 6 | −4.18 | **−10.16** | +291.89 | **+15.42** | 1/4 / 2/4 |

Both BA and TPH are outside the pre-registered bands. The small test is not strong evidence against
the model in general, but it is enough to refuse a promotion under the rule that was fixed before
the run.

## 4. External check

The frozen candidate was then run on the repeated non-PSP ESSFdry cohort (62 intervals, 56 sites;
the two `ESSFwmw` intervals excluded by the installed build limitation recorded in D9.55).

| Cohort | Model | BA % (95% CI) | TPH % (95% CI) | Site pass BA / TPH |
| --- | --- | ---: | ---: | ---: |
| non-PSP ESSFdry | identity default | −22.4 (−25.3 to −19.6) | −16.5 (−19.3 to −13.7) | 4/56 / 28/56 |
| non-PSP ESSFdry | BAIMULT 4.0 / MORTMULT 0.5 | **−11.8 (−14.7 to −9.2)** | **−11.4 (−14.3 to −8.4)** | 20/56 / 36/56 |

The candidate improves both metrics and moves TPH inside the band, but BA remains outside ±10
percent. The external BA failure is the second independent reason not to promote it.

## 5. Decision

- **No ESSFdry candidate bundle.**
- Keep ESSFdry in `D-needs-work`.
- The BAIMULT 4.0 / MORTMULT 0.5 combination is a **screen result**, not a parameter recommendation.
- The spatial test was too small because the per-BEC cap selected four Okanagan sites; a future run
  should use a site-grouped holdout or a larger per-TSA sample.
- The next ESSFdry attempt should test structural levers or a subzone/species split, not simply a
  larger global BAIMULT.

## 6. Limits

- Only 52 training/test intervals; the spatial test has four sites.
- BA/TPH only; QMD, height, volume, and species composition were not validated.
- The species list is eleven codes; a species outside it inherits the default.
- The external cohort is not a probability sample of ESSFdry.
- No candidate was written as a bundle, so there is no checksum, domain, or provenance record to
  review.

## 7. Claim boundary

This is a negative direct-calibration screen. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate.
