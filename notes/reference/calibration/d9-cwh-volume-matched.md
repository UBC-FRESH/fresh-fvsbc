# D9.33 CWH matched merchantability volume

Status: **merchantability mismatch explains part of the gap; external volume still fails**
Date: 2026-11-08
Evidence: `d9-cwh-volume-matched-summary.csv`
Code: `cwh_volume_matched.py`

## 1. What changed

D9.20 compared FVS `MCuM` with all observed `VOL_MER` trees in the 4 cm tree list. FVS counts
merchantable volume only for trees above its `DBHMIN` (17.5 cm, or 12.5 cm for lodgepole pine).
D9.33 recomputes observed volume from trees at or above the same limit, then compares `MCuM` to
that matched observed volume.

This is an audit, not a parameter change. The CWH 4 cm bundle stays a pilot.

## 2. Result

Positive means FVS is high.

| Holdout | n | `MCuM` vs all trees | `MCuM` vs matched `DBHMIN` |
| --- | ---: | ---: | ---: |
| Arrowsmith | 38 | −6.5% | −4.4% |
| Fraser | 11 | −7.9% | −4.4% |
| Haida Gwaii | 15 | −3.1% | −1.7% |
| temporal ≥2000 | 252 | −8.1% | −5.9% |
| non-PSP external | 209 | −18.7% | **−12.6%** |
| all | 525 | −10.3% | −7.1% |

The merchantability limit explains about 3.1 percentage points of the pooled gap. It does not
remove the external failure: the 209-interval non-PSP cohort is still −12.6%, outside the ±10%
band.

## 3. Interpretation

- PSP matched volume is −1.7% to −5.9%; that is inside the pilot volume band.
- The external non-PSP residual is not a small-tree-list artifact. It is a model, volume-standard,
  or cohort difference that remains unresolved.
- `MCuM` is the correct FVS column for a matched merchantability comparison. `TCuM` is not a
  substitute because it includes trees below the FVS limit and matches the unmasked `VOL_MER` by
  coincidence of definition, not by calibration.
- Do not claim CWH volume certification. The external cohort is still an independent failure.

## 4. Decision

- CWH 4 cm remains an unsigned pilot.
- BA, TPH, QMD, matched top height, and PSP matched volume pass.
- External matched volume is still −12.6%; no promotion, no certificate.
- No parameter change. The bundle's narrative claim is corrected to point at D9.33.

## 5. Limits

- `VOL_MER` is a field volume; the residual can include a volume-standard difference that this
  audit cannot separate from model error.
- The filter uses the documented BC `DBHMIN` (17.5 cm; 12.5 cm PL) and assumes `VOL_MER` uses the
  same 10 cm top as `MCuM`.
- The external cohort is not a random sample of CWH.

## 6. Claim boundary

This is a volume-comparison audit for a pilot. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate.
