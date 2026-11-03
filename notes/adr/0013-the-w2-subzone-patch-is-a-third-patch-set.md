# ADR 0013: The W2.3 subzone patch is a third build-time patch set

Status: accepted on 2026-11-03, when the maintainer chose the patch-set route over a new FVS source
fork. Extended by the W3.1 fourth patch set on 2026-11-03; see
`notes/reference/calibration/w3-bec-boundary.md`.
Date: 2026-11-03
Issues: #315
Refines: ADR 0006

## Context

W2.3 adds 19 supported-zone subzones to the BC variant. The change is two Fortran files:
`canada/bc/habtyp.f` gains ten subzone tokens, and `canada/bc/sitset.f` gains the provisional
`BAMAX` cases. The first patch was apply-checked but not built. A build found a defect: the patch
added `SZ(29)` but left `HABTYP`'s loop at `DO I = 1,19`, so the new tokens were never searched. The
corrected patch changes the loop to `DO I = 1,29` and has been built and smoke-tested.

The FVS source lives in `forest-modeling/ForestVegetationSimulator`, and this project's token has
**read-only** access. The project already carries two patch sets (ADR 0006): one at the PyFVS root and
one inside its FVS source submodule. The build applies them at build time; the FVS source pin stays
fixed.

## Decision

The corrected W2.3 patch is a **third build-time patch set**, applied after the other two:

1. `notes/reference/pyfvs-patchset.diff.gz` at the PyFVS checkout.
2. `notes/reference/fvsbc-patchset.diff.gz` inside its FVS source submodule.
3. `notes/reference/calibration/w2-subzones.patch.gz` inside the same submodule.

The FVS source pin remains `ef5fa8470cc89f81ca445e7c906e274f200e80fd`, and the PyFVS pin remains
`e95172b`. The wheel built from the three patch sets is versioned **`0.3.12`** so it cannot be
confused with the published `0.3.11`, which does not carry W2.3. CI and `wheels.yml` apply the third
patch, and the source-build page names it.

The wrapper does **not** accept the 19 subzones until `fresh-fvsbc-pyfvs 0.3.12` is published and the
`fvs` extra pin moves. Accepting them against `0.3.11` would let the unpatched Fortran fall back to
`ICHmw2/01`, which is the exact failure this programme exists to prevent.

## Consequences

- There are three patch sets, not two. ADR 0006's two-root recipe still holds; the third patch is a
  second patch inside the FVS submodule.
- The FVS source pin is unchanged. A reader can reproduce the build from the base pin plus the three
  patch files.
- The wheel version moves to `0.3.12`. The `fvs` extra in `pyproject.toml` stays at `0.3.11` until
  `0.3.12` is published; that is a release action, not part of W2.3.
- The 19 subzones resolve and match their provisional `BAMAX` in a built wheel. The defaults remain
  provisional and W4 owns the final capacity decision.
- The five zones and the seven missing species remain out of scope.

## Alternatives considered

- **Create a `UBC-FRESH/ForestVegetationSimulator` fork and update the submodule pointer.** Rejected
  for this workstream: it creates a new external repository and a second source pin, while the
  project's existing build already carries source patches at build time.
- **Open an upstream PR and wait for it.** Rejected for now: the programme needs a reproducible local
  wheel, and the upstream policy for this variant is not settled.
- **Merge the parser-only change without a build.** Rejected: the `HABTYP` loop defect is exactly what
  a build catches, and an unbuilt patch would have shipped the old default.
