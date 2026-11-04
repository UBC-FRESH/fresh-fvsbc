# D9.8 CWH 4 cm validation: BA/TPH pass, height and volume fail

Status: **BA/TPH and matched top height pass; volume external unresolved**
Date: 2026-11-04
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.4`
Evidence: `d9-cwh-4cm-validation-summary.csv`

The D9.6 CWH 4 cm pilot was validated on BA and TPH only. This checks QMD, top height, and volume
on the same holds.

## 1. Result

| Holdout | n | BA | TPH | QMD | Matched top height | Volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Arrowsmith | 38 | -2.9% | -1.3% | -1.1% | -5.3% | -6.5% |
| Fraser | 11 | -3.3% | -5.9% | +0.8% | -8.0% | -7.9% |
| Haida Gwaii | 15 | +0.6% | +7.9% | -0.5% | -3.7% | -3.1% |
| temporal >=2000 | 252 | +3.4% | +12.1% | -5.5% | -9.0% | -8.1% |
| non-PSP external | 209 | -1.3% | +1.5% | -2.2% | -7.2% | **-18.7%** |

BA, TPH, QMD, and matched top height are inside the ±10% bands. PSP volume is inside ±8%; the
non-PSP external volume is -18.7% and remains unresolved.

## 2. Decision

- The CWH 4 cm bundle remains a **pilot**, not a production calibration.
- BA/TPH and matched top height pass; PSP volume is close.
- Do not promote until the non-PSP external volume gap is resolved.
- The earlier max-height multiplier screen is **not evidence**; it compared the wrong metric.

## 3. Limits

- The matched top height is the expansion-weighted average height of the 100 largest-DBH trees/ha,
  matching FVS `TopHt`. The old `max`-height comparison is not valid.
- Volume remains a merchantable-volume comparison; the non-PSP external gap may include a volume
  standard difference.
- The candidate was selected after the 4 cm grid; the non-PSP external cohort is the independent
  check.
- Only one future measurement window is available for the temporal hold.

## 4. Claim boundary

This is a pilot validation. It does not support a yield, AAC, legal, or whole-block claim, and it is
not a certificate.
