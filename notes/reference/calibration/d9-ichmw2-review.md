# ICHmw2 Arrow/Cascadia candidate review packet

Status: ready for independent review; **signed_off is false**
Date: 2026-11-06
Candidate: `d9-ichmw2-candidate-bundle.json`
Issues: #432, #434, #440

This packet is for the reviewer. The agent cannot sign a calibration; review and sign-off are human
responsibilities.

## 1. What is being reviewed

An unsigned candidate bundle for:

- BEC `ICHmw2`;
- TSA: Arrow and Cascadia only;
- DBH >= 4 cm;
- well-sampled evidence: sites with at least five intervals;
- untreated;
- `BAIMULT 0.75` for FD, HW, CW, BG, PW, PL, SE, BL, LW, AT, AC;
- no ingrowth, mortality, height, or other multiplier;
- pins: PyFVS `e95172b`, FVS `ef5fa847`, variant `bc`, wrapper `0.21.4`.

The bundle cannot enforce the five-interval evidence limit. That is a review point, not a hidden
runtime check.

## 2. Evidence

99 sites / 569 intervals, all PSP 4 cm.

| Metric | Bias | MAE | Band |
| --- | ---: | ---: | --- |
| BA | -0.23% | 2.84 m2/ha | ±10% |
| TPH | -3.44% | 216 TPH | ±15% |
| QMD | +2.33% | 1.23 cm | ±10% |
| Matched top height | -0.61% | 0.86 m | ±10% |
| Merchantable volume (`MCuM`; `TCuM` +9.9%) | -7.54% | 46.1 m3/ha | ±10% |

Site pass: **91 / 99** for BA ±10% and TPH ±15%.

Temporal fixed-parameter check:

| Period | n | BA | TPH | QMD | Top height | Volume |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| year0 >= 2000 | 28 | +2.0% | -1.95% | +4.6% | -1.8% | -2.8% |
| year0 >= 2005 | 12 | +2.0% | -13.1% | +6.0% | -1.6% | +0.4% |

## 3. Spatial holdout

`BAIMULT` selected on Arrow only (66 well-sampled sites) chose **0.75** (63/66 pass). Frozen and
tested on Cascadia (33 sites): **29/33 pass**, BA **+1.1%**, TPH **−3.1%**. See
`d9-ichmw2-holdout.md`.

## 4. Review questions

- [ ] Is the ICHmw2 / Arrow / Cascadia domain the right claim boundary?
- [ ] Is `BAIMULT 0.75` inside its bounds and not at a bound?
- [ ] Is the five-interval evidence limit acceptable, given that the bundle cannot enforce it?
- [x] The Arrow-only selection transfers to Cascadia: 0.75, 29/33 pass.
- [ ] Is the temporal check strong enough, given that the 2005 test has only 12 intervals?
- [ ] Are QMD, matched top height, and PSP volume convincing enough to deploy?
- [ ] Should Okanagan and Kootenay Lake remain excluded?
- [ ] Should the claim say "candidate," not "calibration" or "certificate"?
- [ ] Is a third-TSA or independent PSP cohort required before use?

## 5. Known limits

- The candidate was selected on all well-sampled sites; it is not a pre-registered nested result.
- Arrow selects 0.75 and Cascadia is a true spatial holdout, but there is no third TSA.
- Okanagan and Kootenay Lake are excluded.
- The bundle does not enforce the >=5-interval evidence limit.
- Non-PSP volume is not used because the volume standards differ.
- The review is unsigned; no certificate.

## 6. Sign-off

| Field | Value |
| --- | --- |
| Reviewer | _pending_ |
| Date | _pending_ |
| Decision | _pending_ |
| Claim changes required | _pending_ |

Do not set `signed_off: true` without this table filled and the bundle regenerated with the reviewer
and date.
