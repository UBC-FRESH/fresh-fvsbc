# D7.19 SBPSmk/Quesnel mature closed-canopy candidate

Status: **post-hoc candidate; ingrowth-only holdout**
Date: 2026-11-04
Issue: #393
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Bundle: `d7-sbpsmk-mature-bundle.json`
Evidence: `d7-sbpsmk-mature-loso-summary.csv`, `d7-sbpsmk-mature-temporal-summary.csv`

The D7.18 screen left four low-QMD, high-productivity SBPSmk sites failing. Narrowing to a mature,
closed-canopy stratum identifies a domain that passes site-grouped and temporal validation.

## 1. Domain

- SBPSmk / Quesnel TSA, untreated.
- Initial QMD >= 17 cm.
- Initial BA >= 20 m2/ha.
- 48 intervals / 25 sites, years 1970-1990.
- `QMD < 17` and `BA < 20` are **outside** the claim; they remain validation-only.

This domain is **post-hoc**: it was selected after the D7.18 residual screen, not fixed in advance.
`BAMAX 75`, `BAIMULT 1.25`, and the QMD/BA thresholds were selected using all 48 intervals (and the
wider D7.18 screen). The site-grouped and temporal checks below refit **ingrowth only**; they do not
hold out the parameters or the domain. That is the central limitation of this candidate.

## 2. Parameters

- `BAMAX 75`.
- `BAIMULT 1.25` for PL, SE, BL, FD, HW.
- Quesnel-specific ingrowth, refit on the 48 intervals.
- No mortality or height multiplier.

## 3. Temporal check

Split by measurement year: train 1970/1980, test 1990. The ingrowth rates are train-only; BAMAX,
BAIMULT, and the domain are fixed from all data. Twelve of the 23 test sites also contribute train
intervals, so this is a temporal check, not a site-independent one.

| Fold | Intervals | Sites | BA | TPH |
| --- | ---: | ---: | ---: | ---: |
| Train | 25 | 14 | -5.60% | -5.62% |
| **Test** | **23** | **23** | **-3.31%** | **+0.17%** |

Every test interval is within BA ±10% and TPH ±15%; the worst test site is BA -8.4% / TPH +5.7%.

## 4. Site-grouped LOSO

25 folds, one held-out site each; ingrowth refit without the held-out site. BAMAX, BAIMULT, and the
domain are fixed from all data, so this validates the ingrowth refit, not those choices.

| Check | Result |
| --- | ---: |
| Pooled BA | -4.71% |
| Pooled TPH | -3.93% |
| Worst-site BA | 8.72% |
| Worst-site TPH | 13.66% |
| Sites passing | **25 / 25** |

The pooled and every-site checks pass for the fixed parameter set. They are not an independent
validation of that set.

## 5. Candidate bundle

`d7-sbpsmk-mature-bundle.json` is an **unsigned candidate**:

- domain `SBPSmk`, `qmd_min: 17.0`, `ba_min: 20.0`;
- `BAMAX 75` and `BAIMULT 1.25`;
- Quesnel ingrowth;
- reviewer unreviewed, `signed_off: false`.

The bundle schema enforces the TSA, QMD, and BA boundaries, so a stand outside either is refused
before the run. Provenance records the stand values and the bundle minima.

## 6. Limits

- The domain and parameters are post-hoc; only ingrowth was held out.
- The domain covers one TSA / one BEC.
- The four low-QMD, high-productivity sites are excluded; they still have no working model.
- 25 sites and 48 intervals are enough for a candidate, not a certificate.
- The temporal test has 23 intervals from one later measurement decade; 12 test sites also have
  training intervals.
- Requires `fresh-fvsbc 0.21.4`; `0.21.3` loads the bundle but ignores the QMD and BA fields.
- There is no independent third TSA or independent reviewer.
- This does not pool with the SBPSdc/Quesnel candidate.

## 7. Review checklist

- [ ] Accept the post-hoc QMD/BA domain as defensible for mature SBPSmk stands.
- [ ] Confirm `QMD >= 17` and `BA >= 20` are enforced in the bundle and provenance.
- [ ] Confirm `BAMAX 75` and `BAIMULT 1.25` are inside declared bounds.
- [ ] Confirm the temporal split is time-based.
- [ ] Confirm the LOSO rates are fold-specific.
- [ ] Confirm the test sites were not used to select BAMAX, BAIMULT, or the domain. **Currently not
      satisfied;** this is a post-hoc candidate.
- [ ] Confirm the claim says candidate, not certificate.
- [ ] Decide whether a second TSA is required before any deployment.

## 8. Claim boundary

This is an unsigned, post-hoc candidate. The parameters and domain were not held out; only the
ingrowth refit was. It does not support a yield, AAC, legal, or whole-block claim, and it is not a
certificate.
