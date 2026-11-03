# W3.1 BEC boundary fix

Status: fixed and built locally as `fresh-fvsbc-pyfvs 0.3.13`; release pending
Date: 2026-11-03
Patch: `w3-habtyp-boundary.patch.gz` (`sha256:30a00a8c167416d1dd0181953613f72ccec676ce1a20acaa861d95068dac99ab`)
Issue: #325

## 1. What the baseline found

The first W3.1 baseline used the published `fresh-fvsbc-pyfvs 0.3.12` and stopped on
the interval `4005767|1|1980|1990`. The requested BEC was `KAM MSxk1/01`; FVS echoed
`MSmm/01`.

The cause is a pre-existing `HABTYP` boundary collision. `FULL` is
`REGION + ZONE + SUBZONE + SERIES`. For region `KAM` and zone `MS`, the boundary is:

```text
K A M M S X K 1 / 0 1
    ^ ^
    M M  <- the 'MM' subzone token matches here
```

`HABTYP` searched the whole string for a two-letter subzone token. `MM` matched across
the region/zone boundary before the real `XK` token was tried. The W2.3 guard did not
cause the collision; it exposed it by refusing the silent `MSmm` result.

This affects the interior `MS` subzones in the `KAM` region, not only `MSxk1`.

## 2. The fix

`w3-habtyp-boundary.patch.gz` changes `canada/bc/habtyp.f`:

- It records the zone length and position with `K` and `JZ`.
- It accepts a subzone token only when it starts at or after `JZ + K`.
- It excludes the region/zone boundary without changing the token list or the
  zone list.

The patch applies after `w2-subzones.patch.gz` to a clean `ef5fa847` worktree. It
changes one file, 10 lines added and 2 removed.

## 3. Evidence

- Before the fix, `KAM MSxk1/01` echoed `MSmm/01` and the baseline stopped.
- After the fix, it echoes `MSxk1/01`; `MSdm1`, `MSdk`, and `CAR MSxk1` also echo
  their requested codes.
- The W2 subzone suite passes all 19 cases on the fixed local build.
- The full W3.1 baseline completes with **108 compared intervals and 0 skipped**,
  up from 89 compared and 19 skipped in W1.4.
- `tests/test_w2_subzones.py` gains the `KAM`/`MS` boundary cases, so a build without
  this patch fails the CI extension job.

## 4. Release boundary

The fixed source is built locally as `fresh-fvsbc-pyfvs 0.3.13`. The published
`0.3.12` still has the collision. The W3.1 result is not reproducible from the
published package until `0.3.13` is on PyPI and the wrapper `fvs` extra moves to it.

This fix changes BEC resolution only. It does not calibrate a parameter, add a zone,
or change growth or mortality.
