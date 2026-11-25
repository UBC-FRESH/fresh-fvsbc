# CMA is out of scope

Status: **decided 2026-11-25.** `CMA` is a deliberate exclusion, not an unsupported gap.

## Decision

CMA is not a forested BEC zone and is immaterial to the modelling projects this package serves. It is
removed from the calibration backlog and graded **X (out of scope)** in `fresh_fvsbc.support`. A run
in CMA still parses, as the wrapper accepts the label, but its provenance says `X`; there is no
calibration claim and no follow-up task.

## What the data showed

The calibration archive holds **two sites, six intervals**, all in one subzone and one TSA:

| Site | BEC | Intervals | BA (start) | TPH | Species |
| --- | --- | ---: | ---: | ---: | --- |
| 4002608 | `CMAunp` | 3 | 92.5 | 1,200 | BA 337, HW 104, PW 8 |
| 4002609 | `CMAunp` | 3 | 86.3 | 820 | BA 264, HW 44 |

Mean DBH 30–36 cm, heights 24–27 m, ages 110–124, North Island TSA. Provisional `BAMAX` for
`CMAunp` is 93.2, so both stands sit at the ceiling and carry almost no growth signal. Two sites
cannot form a site-grouped holdout, and two of the three CMA units have no PSP sites at all.

A multiplier fitted to those two stands would be validation on itself. The W2 audit's "no-go without
an expert input" was right; this decision makes it explicit and final for this project.

## What would reopen it

A real forested CMA use case with independent plots across the CMA units. Until then, do not list CMA
as a calibration gap, do not fit it, and do not present an X-graded CMA run as a model result.
