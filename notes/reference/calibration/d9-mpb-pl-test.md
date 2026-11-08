# D9.48 MPB extension on a post-2000 PL stand

Status: **kill path is active but default outbreak parameters produce almost no PL mortality**
Date: 2026-11-08
Case: `runtime/d7-100mile/runs/bamax30-4033913_1_2006_2013`
Build: D9.46 BC MPB extension

## 1. Test stand

`4033913|1|2006|2013`, SBPSmk, 100 Mile area:

- 3,609 trees/ha at start;
- 9% PL in the stand;
- 13 PL trees in the tree list;
- 131.15 live PL trees/ac at the start of the MPB table.

The BC projection completes with and without MPB.

## 2. MPB response

`MPBSTART 1`, `BEETLES 100`, `PRBSCALE 1.0`, `MAXYEARS 10`:

- activity log: `MPB MPBSTART 2006 DONE IN 2006`;
- outbreak summary: `WAS THERE AN OUTBREAK = YES`;
- final PL table: **131.15 live, 0.38 dead** — about 0.3% PL mortality.

Sensitivity:

- `BEETLES` 100, 1,000, 5,000, and 10,000 all produce the same 0.38 dead PL.
- `POPDYN` produces zero PL kill in this case.
- `MANSTART` and `INVMORT` also produce 0.38 dead PL.

So the extension and outbreak scheduler are active, but the default rate-of-loss path is not
generating the observed post-2000 PL collapse.

## 3. Interpretation

- This is not a build problem; the module runs.
- This is an outbreak-parameter/host-severity problem. The stand also has only 9% PL, so it may not
  be a severe MPB stand.
- A global `BEETLES` value does not control the rate-of-loss model; the relevant levers are likely
  `CURRMR`, `ACTSURF`, `PRBSCALE`, and the damage-code path.
- The next calibration must use **high-mortality PL stands**, not this low-PL stand.

## 4. Decision

- Do not tune MPB on this case.
- Select post-2000 PL intervals with observed PL mortality well above background, ideally >20–30%.
- Use some stands to set outbreak parameters and hold out others.
- Test `CURRMR`, `ACTSURF`, and population-dynamics settings against the observed PL kill.
- Keep the provincial background model and local calibration for non-PL species.
- No integration or bundle.

## 5. Limits

- One low-PL stand; not representative of the severe MPB stands.
- No damage-code data in this tree list.
- The BC species mapping is a first implementation.
- No holdout calibration yet.

## 6. Claim boundary

This is a runtime and sensitivity test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
