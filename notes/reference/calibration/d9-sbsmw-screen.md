# D9.16 SBSmw screen: stop the global BEC multiplier work

Status: **no bundle; global multiplier screens closed**
Date: 2026-11-06
Data: SBSmw, 4 cm PSP, 343 intervals / 110 sites
Evidence: `d9-sbsmw-screen-summary.csv`

## 1. Sample

- 343 intervals / 110 sites.
- Quesnel 62 sites, Prince George 47, Cascadia 1.
- Most sites have 3–4 intervals; there are no well-sampled 5+ interval sites.

## 2. Result

| Candidate | BA | TPH | Sites passing | Worst BA | Worst TPH |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | −9.3% | −8.0% | 31 / 109 | 134% | 50% |
| BAIMULT 0.75 | −10.4% | −7.3% | 25 / 109 | 131% | 54% |
| BAIMULT 1.25 | −8.1% | −8.7% | 37 / 109 | 139% | 47% |
| **BAIMULT 2** | **−4.6%** | **−10.6%** | **49 / 109** | 148% | 41% |
| BAIMULT 4 | +4.2% | −14.9% | 42 / 109 | 178% | 37% |
| BAIMULT 6 | +12.8% | −18.3% | 22 / 109 | 204% | 37% |

The best candidate still leaves 60 sites failing, and the worst BA error is 148–204%. Higher
multipliers make the aggregate look better while blowing up individual sites.

## 3. Decision

- No SBSmw bundle.
- Stop global BEC multiplier screens.
- The remaining problem is structural or data-level: submodel refitting, internal increment
  calibration, or site-level data issues.
- The only new positive candidate remains ICHmw2 Arrow/Cascadia.

## 4. Next

1. Independent review of the ICHmw2 candidate.
2. Structural work: refit the relevant BC submodels or implement internal increment calibration.
3. Keep CWH 4 cm as a pilot; resolve external volume standard separately.

## 5. Claim boundary

This is a negative calibration screen. It does not support a yield, AAC, legal, or whole-block claim.
