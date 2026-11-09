# D9.75 MPB wrapper handoff and installed-case test

Status: **the wrapper can run an MPB case from the installed path**
Date: 2026-11-08
Build: D9.73 banked BC MPB patch

## 1. Handoff fix

FVS reads the tree list at `TREEDATA` and runs MPB setup before the projection. A caller-supplied
`MPB` block was being inserted before `TREEFMT`/`TREEDATA`, which produced `FVS11 REQUESTED
EXTENSION IS NOT PART OF THIS PROGRAM` and invalid-keyword errors.

`with_tree_handoff` now inserts `TREEFMT`/`TREEDATA` before the first `PROCESS`, `STOP`, or `MPB`.
The MPB block is written after the tree handoff.

`INITMORT`/`CURRMORT` supplemental records are also padded as ten-column fields instead of a raw
space-separated line.

## 2. Installed-path test

The installed wrapper was exercised with the built MPB extension on `4031355|1|2000|2013`:

- `MPB MPBSTART 2000` is read;
- the activity log records `DONE IN 2000`;
- the rate-of-loss model reports `OUTBREAK IN YEAR = 2000 FOR 10 YEARS`;
- the run writes one case and a two-row summary.

This is a wrapper-path test, not a new calibration result.

## 3. Decision

- Keep the handoff rule: tree list before MPB.
- Keep `INITMORT`/`CURRMORT` supplemental padding.
- The MPB path is now usable through the wrapper and the wheel build.
- No bundle or certificate.

## 4. Limits

- The local test used the built extension in the installed package; CI build gate is the
  reproducibility check.
- MPB severity remains local and separate from the Quesnel background candidate.
- No production sampling or temporal validation.

## 5. Claim boundary

This is an integration test. It does not support a yield, AAC, legal, or whole-block claim, and it is
not a certificate.
