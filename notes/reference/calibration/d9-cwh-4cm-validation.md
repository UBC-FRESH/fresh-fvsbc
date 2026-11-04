# D9.8 CWH 4 cm validation: BA/TPH pass, height and volume fail

Status: **pilot only; not production-ready**
Date: 2026-11-04
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Evidence: `d9-cwh-4cm-validation-summary.csv`

The D9.6 CWH 4 cm pilot was validated on BA and TPH only. This checks QMD, top height, and volume
on the same holds.

## 1. Result

| Holdout | n | BA | TPH | QMD | Top height | Volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | 38 | -2.9% | -1.3% | -1.1% | **-16.3%** | -6.5% |
| Fraser | 11 | -3.3% | -5.9% | +0.8% | **-17.5%** | -7.9% |
| Haida Gwaii | 15 | +0.6% | +7.9% | -0.5% | **-13.3%** | -3.1% |
| temporal >=2000 | 252 | +3.4% | +12.1% | -5.5% | **-19.5%** | -8.1% |
| non-PSP external | 209 | -1.3% | +1.5% | -2.2% | **-18.8%** | **-18.7%** |

BA and TPH are inside the bands. QMD is close. **Top height is underpredicted by 13–20% on every
hold**, and volume is underpredicted by 3–19%.

## 2. Decision

- The CWH 4 cm bundle remains a **pilot**, not a production calibration.
- Do not promote it on BA/TPH alone.
- The next lever is height growth, especially `HTGMULT`/`REGHMULT`, not another `BAIMULT` or
  `REGDMULT` sweep.
- Volume follows the height failure; it should not be certified until height is fixed.

## 3. Limits

- The observed top height is the PSP top height, and the predicted value is the FVS metric summary;
  the comparison is like-for-like but not a full height-diameter validation.
- The candidate was selected after the 4 cm grid; the non-PSP external cohort is the independent
  check.
- Only one future measurement window is available for the temporal hold.

## 4. Claim boundary

This is a pilot validation. It does not support a yield, AAC, legal, or whole-block claim, and it is
not a certificate.
