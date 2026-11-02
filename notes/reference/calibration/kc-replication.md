# KC pilot replication

Status: regional pilot report; not a calibration certificate
Date: 2026-11-02
Protocol: `notes/reference/calibration/kc-protocol.md`
Bundle: `notes/reference/calibration/kc-pilot-bundle.json`

This report records the KC pilot's evidence as it stands. The pilot ran in the
AFRF Knife Creek instance and the WS4 workspace; this repository carries the
protocol, the bundle contract, and the aggregate evidence, not the site-level
PSP extract.

## The BEC correction

The runbooks wrote `STDINFO 712,CHS131`. The two fields do not resolve to a BEC;
`canada/bc/habtyp.f` falls back to `ICHmw2/01`, whose default maximum basal area
is 89 m²/ha. The working form is `CAR IDFdk3/01`, with a maximum of 53 m²/ha.

The decisive test is the real 1993 Knife Creek tree list, grown 200 years with
no cut and no calibration:

| Run | Max BA (m²/ha) | Final TPH | Top height |
| --- | ---: | ---: | ---: |
| legacy `712,CHS131` | 77.4 | 401 | 150 ft |
| corrected `CAR IDFdk3/01` | 49.6 | 258 | 99 ft |

The legacy 77.4 m²/ha reproduces the disputed trajectory; the corrected run
removes it. The change is not only a cap: top height and TPH move too.

## The 24-plot backtest, 1993–2013

| Run | BA bias (m²/ha) | BA MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| legacy | +1.04 | 3.94 | +421.8 | 514.6 |
| corrected | −1.29 | 2.96 | +249.5 | 421.5 |

The correction reduces the TPH overshoot and the BA MAE; it does not remove the
positive TPH bias. That residual is the mortality-calibration target.

The 24 plots are uneven-aged and every plot was assigned `IDFdk3/01` in this
run, because the plot-level site series is not yet joined. The backtest is a
diagnostic, not validation.

## The long-run diagnostic

The six AU corrected-BEC no-cut runs produce 200-year volumes of **353–589
m³/ha**, against **750–1,232** on the old ICH-default curves. Managed year-170
volume is **339–517**, against **614–917**. The first multi-entry volume is
**163–196**, against **219–287**. The correction is roughly a 40–55% change in
the long-run yield, not a tuning detail.

The 24 corrected-BEC plots give a 200-year maximum BA mean of **50.0 m²/ha**
(range 45–67) and volume **447–589 m³/ha**.

## The parameter set

The v2c set is a regional pilot, not a calibration:

| Group | `BAIMULT` | `MORTMULT` | Note |
| --- | ---: | ---: | --- |
| FD | 1.20 | 2.80 | v2c regional refit |
| SE | 1.3948 | 3.8261 | v1 value retained |
| PL | 1.00 | **8.00** | at the bound; proxy for MPB and other losses |
| HW | 1.00 | 1.2012 | v1 value retained |

The v1 set was fitted while the projection carried the wrong BEC. The PL
multiplier at 8.0 is the symptom: the model was fighting the wrong capacity
envelope. The bundle keeps the 8.0 value and declares the 8.0 bound, so the
loader warns that the parameter is not identified.

## The mortality target

The tree-level survival model used 328 IDFdk3/IDFxm intervals, 186 sites, 46,756
live tree records, and 5,988 deaths. Observed annual mortality in IDFdk3 is:

| Species group | Annual mortality |
| --- | ---: |
| FD | 0.58% |
| PL | 3.15% |
| HW | 2.65% |
| SE | 1.06% |

FVS's base PL rate at 30–40 m²/ha and 10–25 cm is 0.445% against an observed
4.49%. The gap is real and species-specific; a single multiplier is a blunt
instrument. The preliminary cloglog model predicts PL about 17× FD at DBH 17 and
BA 35, but overpredicts overall mortality by about 18%, mostly high-BA FD. It is
a target model, not an FVS parameter set.

## What is regional, structural, and unidentified

| Kind | What it is |
| --- | --- |
| Regional | The FD and SE multipliers; the IDFdk3 capacity near 53 m²/ha |
| Structural | The PL mortality gap; FVS-BC has no active MPB module, and no multiplier can create the observed collapse |
| Unidentified | The PL 8.0 multiplier; the IDFxm capacity default; the per-plot site series |
| Not tested | Independent sites; whole TSAs; the coastal and boreal zones (W2) |

## Uncertainty and claim boundary

- The 2024 Marshall remeasurement is a temporal holdout on the same plots, not
  an independent site. It supports total TPH but not the species-level fit.
- The FAIB 92-plot check mixes IDF variants and is encouraging, not decisive.
- The plots are uneven-aged; FVS-BC is even-aged. The pilot does not validate a
  selection-system model.
- The site series is `/01` for every plot; the capacity target is a documented
  diagnostic default.
- No legal, AAC, or whole-block claim is made.

The defensible statement is the one in `kc-protocol.md` §6: the legacy BEC ran
`ICHmw2/01`; the corrected BEC removes the 77 m²/ha asymptote and changes the
long-run volume by roughly 40–55%; a species-group multiplier set can move the
trajectory but is not independently validated; PL is at a bound.
