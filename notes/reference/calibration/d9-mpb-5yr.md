# D9.51 MPB on five-year high-PL intervals

Status: **the real extension kills PL, but severity is still too low on five-year high-PL stands**
Date: 2026-11-08
Build: D9.46 BC MPB extension

## 1. Why five-year intervals

D9.50 found that `colmod.f` caps an MPB outbreak at 10 years. Raising the cap double-counts dead
trees. To calibrate without that bug, this test uses post-2000 PL intervals of five years or less.

## 2. Cases

| Interval | BEC | TSA | PL dead/live | Observed PL mortality |
| --- | --- | --- | ---: | ---: |
| `4024547\|1\|2001\|2006` | IDFdk3 | 100 Mile | 48/50 | 96.0% |
| `4024546\|1\|2001\|2006` | IDFdk3 | 100 Mile | 64/67 | 95.5% |
| `4024754\|1\|2001\|2006` | IDFdk3 | 100 Mile | 68/72 | 94.4% |
| `4032478\|1\|2001\|2006` | SBSdw1 | Williams Lake | 81/84 | 96.4% |
| `4024340\|1\|2002\|2007` | SBSdw2 | Williams Lake | 97/101 | 96.0% |
| `4024380\|1\|2002\|2007` | SBPSmk | Williams Lake | 104/129 | 80.6% |

## 3. Result

MPB run: `MPBSTART`, `BEETLES 1000`, `STNDSIZE 100`, `HABSUIT 1.0`, `MAXYEARS 15`.

| Interval | MPB live/dead PL/ac | MPB dead fraction | Observed |
| --- | ---: | ---: | ---: |
| `4024547` | 177.23 / 25.12 | 12.4% | 96.0% |
| `4024546` | 226.33 / 44.82 | 16.5% | 95.5% |
| `4024754` | 308.41 / 23.44 | 7.1% | 94.4% |
| `4032478` | 254.51 / 85.44 | 25.1% | 96.4% |
| `4024340` | 236.87 / 171.87 | 42.1% | 96.0% |
| `4024380` | 457.76 / 104.76 | 18.6% | 80.6% |

The extension kills PL, but far below the observed collapse on these five-year stands. The response
is stand-dependent; it is not simply a missing host or a broken scheduler.

## 4. Interpretation

- The high-PL 13-year cases looked closer mainly because the 10-year outbreak had more years to
  accumulate mortality.
- Five-year high-PL stands show the severity gap directly: MPB kills 7–42% versus 80–96% observed.
- `BEETLES` alone does not explain the gap.
- The next levers are outbreak severity/current-mortality settings (`CURRMR`/`ACTSURF`) and a proper
  host/severity calibration, not another global background multiplier.

## 5. Decision

- Use five-year high-PL intervals for severity calibration; they avoid the 10-year cap.
- Keep the 13-year cases as a separate long-interval limitation.
- Fit one severity configuration on training stands and hold out others.
- Check non-PL BA/TPH on every run.
- No integration or bundle.

## 6. Limits

- Six five-year high-PL cases, all in IDFdk3/SBSdw/SBPSmk.
- `CURRMR`/`ACTSURF` syntax has not yet been validated.
- The BC species map is a first implementation.
- No holdout calibration yet.

## 7. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
