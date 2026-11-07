> **D9.24 correction:** corrected NATURAL units give in-sample BA -4.2%/TPH -0.8%, 25/25 sites. The old nested/temporal evidence predates the unit fix and must be re-run. See `d9-ingrowth-unit-impact.md`.

# D7.19 SBPSmk/Quesnel mature closed-canopy candidate

Status: **post-hoc candidate; corrected units pass fixed-parameter LOSO/temporal, nested selection still fails 7/38**
Date: 2026-11-04
Issue: #393
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Bundle: `d7-sbpsmk-mature-bundle.json`
Evidence: `d7-sbpsmk-mature-loso-summary.csv`, `d7-sbpsmk-mature-temporal-summary.csv`,
`d7-sbpsmk-mature-bundle-temporal-summary.csv`

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
| **Test (train-only rates)** | **23** | **23** | **-3.31%** | **+0.17%** |
| **Test (bundle as shipped)** | **23** | **23** | **-3.43%** | **-1.01%** |

Every test interval is within BA ±10% and TPH ±15%.

The table uses train-only rates. The bundle ships rates fit on all 48; rerunning the bundle with
`--test-year-from 1990` gives test **BA -3.43%, TPH -1.01%**, 23/23 sites passing. The worst
absolute BA is 8.72% and the worst absolute TPH is 8.10%; they are different sites. That is the
shipped fit; it is still a post-hoc comparison.

## 4. Site-grouped LOSO

25 folds, one held-out site each; ingrowth refit without the held-out site. BAMAX, BAIMULT, and the
domain are fixed from all data, so this validates the ingrowth refit, not those choices.

| Check | Result |
| --- | ---: |
| Pooled BA | -4.71% |
| Pooled TPH | -3.93% |
| Worst-site BA (signed) | -8.72% |
| Worst-site TPH (signed) | -13.66% |
| Sites passing | **25 / 25** |

The pooled and every-site checks pass for the fixed parameter set. They are not an independent
validation of that set.

## 5. Nested selection (D7.22, corrected units)

The corrected-unit nested selection chooses BAMAX80/BAIMULT1.25/QMD15 in four folds and
BAMAX75/QMD15 in one. Held-out: BA -2.0%, TPH +0.6%, **31/38 sites pass**; worst site BA 25.1% /
TPH 61.6%. The every-site criterion still fails. The fixed-parameter candidate is not upgraded.

## 6. Nested selection (old units, historical)

Five site-grouped folds; BAMAX/BAIMULT/QMD selected on training sites only, BA fixed at 20. The
procedure selected BAMAX 80 / BAIMULT 1.25 in all folds; held-out sites gave BA -4.84%, TPH -7.92%,
with **25 of 28 sites passing**. The worst site is BA 25.1% / TPH 63.4%. This **fails** the
every-site criterion; the candidate is not upgraded. See `d7-sbpsmk-nested.md`.

## 6. External screen (D7.23)

The fixed candidate was applied without refitting to 4 Williams Lake and 3 100 Mile House SBPSmk
intervals at QMD >= 17 / BA >= 20. Pooled BA is **+11.03%**, TPH **+7.97%**; only 3 of 7 sites pass.
Williams Lake is BA +16.2%; 100 Mile House is TPH +15.5%. This is a screen, not a validation, but it
fails the BA band. The candidate remains Quesnel-only. See `d7-sbpsmk-external.md`.

## 7. Candidate bundle

`d7-sbpsmk-mature-bundle.json` is an **unsigned candidate**:

- domain `SBPSmk`, `qmd_min: 17.0`, `ba_min: 20.0`;
- `BAMAX 75` and `BAIMULT 1.25`;
- Quesnel ingrowth;
- reviewer unreviewed, `signed_off: false`.

The bundle schema enforces the TSA, QMD, and BA boundaries, so a stand outside either is refused
before the run. Provenance records the stand values and the bundle minima.

## 8. Reproduce

Temporal, bundle as shipped:

```bash
python scripts/run_calibration_probe.py \
  --data-dir runtime/sbpsmk-quesnel --psp-dir "$FAIB_PSP_DIR" \
  --out-dir runtime/d7-sbpsmk-mature-bundle-temporal --domain SBPSmk \
  --per-bec 1000 --min-qmd 17 --min-ba0 20 \
  --candidates notes/reference/calibration/d7-sbpsmk-mature-candidates.json \
  --bundle notes/reference/calibration/d7-sbpsmk-mature-bundle.json \
  --test-year-from 1990
```

`probe.json` records `test_year_from` and a checksum over the interval identifiers and initial/final
values; the checksum matches the bundle's `training.data_checksum`.

The 25-fold LOSO loop is tracked:

```bash
python scripts/run_site_grouped_probe.py \
  --data-dir runtime/sbpsmk-quesnel --psp-dir "$FAIB_PSP_DIR" \
  --out-dir runtime/d7-sbpsmk-mature-loso --domain SBPSmk \
  --per-bec 1000 --min-qmd 17 --min-ba0 20 \
  --candidates notes/reference/calibration/d7-sbpsmk-mature-candidates.json
```

It fits ingrowth on the training sites for each held-out site and writes `loso-summary.csv`;
the aggregate is `d7-sbpsmk-mature-loso-summary.csv`.

## 9. Limits

- The domain and parameters are post-hoc; only ingrowth was held out.
- Corrected units give fixed-parameter LOSO BA -4.17%/TPH -0.77%, 25/25 sites; temporal test BA -2.73%/TPH +4.83%.
- Corrected nested selection still fails 7/38 held-out sites.
- Nested parameter/domain selection fails the every-site criterion (25/28 sites).
- The external Williams Lake / 100 Mile screen fails BA (+11.03% pooled); the candidate is
  Quesnel-only.
- The bundle checksum covers interval identifiers and initial/final values, not pandas float formatting.
- The BA gate uses the unrounded tree list; FVS writes tree counts `F6.0`. Two of the 48 accepted
  intervals start at FVS BA 19, so the gate is not exact at the 20 m2/ha boundary.
- The domain covers one TSA / one BEC.
- The four low-QMD, high-productivity sites are excluded; they still have no working model.
- 25 sites and 48 intervals are enough for a candidate, not a certificate.
- The temporal test has 23 intervals from one later measurement decade; 12 test sites also have
  training intervals.
- Requires `fresh-fvsbc 0.21.4`; `0.21.3` loads the bundle but ignores the QMD and BA fields.
- There is no independent third TSA or independent reviewer.
- This does not pool with the SBPSdc/Quesnel candidate.

## 10. Review checklist

- [ ] Accept the post-hoc QMD/BA domain as defensible for mature SBPSmk stands.
- [ ] Confirm `QMD >= 17` and `BA >= 20` are enforced in the bundle and provenance.
- [ ] Confirm `BAMAX 75` and `BAIMULT 1.25` are inside declared bounds.
- [ ] Confirm the temporal split is time-based.
- [ ] Confirm the LOSO rates are fold-specific.
- [ ] Confirm the test sites were not used to select BAMAX, BAIMULT, or the domain. **Currently not
      satisfied;** the nested check in D7.22 fails 3 of 28 sites.
- [ ] Confirm the claim says candidate, not certificate.
- [ ] Decide whether a second TSA is required before any deployment.

## 11. Claim boundary

This is an unsigned, post-hoc candidate. The parameters and domain were not held out, the nested
selection check fails 3 of 28 sites, and the external screen fails BA. It does not support a yield,
AAC, legal, or whole-block claim, and it is not a certificate.
