# D9.62 expanded SBSdw2 high-PL panel

Status: **SBSdw2 is still heterogeneous; a BEC scalar is not sufficient**
Date: 2026-11-08
Build: D9.46 BC MPB extension
Panel: 7 five-year/six-year SBSdw2 intervals

## 1. Added intervals

The SBSdw2 stratum was expanded from three to seven high-PL intervals:

- `4024340`, `4024339`, `4024338`;
- `4024448`, `4032464`, `4032465`, `4032466`.

All are five or six years, so the 10-year MPB cap is not involved.

## 2. Result

Leave-one-site-out with a single INITMORT multiplier per SBSdw2:

- MAE: **0.139**.
- Best multiplier for most intervals: 0.04.
- Individual errors range from 0.016 to 0.37.

The main outliers:

- `4024448` has only six PL trees; predicted 0.464 vs observed 0.833.
- `4032465` predicted 0.832 vs observed 0.658.
- `4024339` predicted 0.636 vs observed 0.904.

## 3. Interpretation

- `INITMORT` remains the correct lever.
- A single SBSdw2 scalar is not enough; the stratum is heterogeneous in stand structure and/or
  non-MPB mortality.
- The small `4024448` stand is too sparse to carry a calibration weight.
- The next options are:
  1. a stand covariate severity model within SBSdw2;
  2. `ACTSURF` for a direct surface-kill diagnostic;
  3. more SBSdw2 high-PL intervals;
  4. a per-stand local severity, explicitly labelled as such.
- Do not force a global/BEC scalar.

## 4. Decision

- Do not adopt a single SBSdw2 multiplier.
- Keep SBSdw2 as a local calibration stratum requiring more data or a covariate.
- Keep 100 Mile and the other Williams Lake BECs as separate local strata.
- No integration or bundle.

## 5. Claim boundary

This is a diagnostic calibration test. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
