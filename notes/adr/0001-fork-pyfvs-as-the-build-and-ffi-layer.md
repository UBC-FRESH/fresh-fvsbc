# ADR 0001: Fork PyFVS as the FVS build and FFI layer

Status: proposed
Date: 2026-10-21
Issues: TBD

## Context

`fvsbc` wraps the BC variant of the Forest Vegetation Simulator (FVS). FVS is Fortran. The BC variant
lives under `canada/bc/` in the official USDA repository, but the official build does not produce it:
its source list is `canada/bin/FVSbcc_notReady.txt`, and there is no `bin/FVSbc_sourceList.txt`. No
official BC binary exists.

`PyFVS` already owns the build and foreign-function layer for FVS. It is MIT-licensed, it was pushed to
in October 2026, and it ships an `FVS` class with a step and cycle API, dataframe tree-list
initialization, within-cycle callbacks, and keyword handling. It builds FVS from a fork,
`forest-modeling/ForestVegetationSimulator`, pinned on the branch `pyfvs-features`, and it publishes to
PyPI and conda-forge.

Two gaps decide this ADR:

- `PyFVS` does not build the BC variant. Its variant list is
  `pn, wc, so, op, oc, ec, ca, nc, bm, ie, ci, ak, ws`. The code `ca` is Central America
  (`ca/common/`), not Canada.
- The FVS source fork already carries what the BC build needs: `bin/FVSbc_sourceList.txt` and a
  `canada/bc/` tree of 41 files on the branch `pyfvs-features`. A branch named `bc_sourcelist` corrected
  the Canadian source lists and then excluded the BC variant from the build.

So the expensive layer exists and the BC work does not. We must be able to change the build without
waiting for an upstream release, and we must pin exact versions for reproducible science.

Evidence:

- Official FVS repository, BC source list marked not ready:
  `https://github.com/USDAForestService/ForestVegetationSimulator/blob/main/canada/bin/FVSbcc_notReady.txt`
- `PyFVS` variant list: `https://github.com/forest-modeling/PyFVS/blob/main/meson_options.txt`
- `PyFVS` FVS submodule, pinned to `pyfvs-features`:
  `https://github.com/forest-modeling/PyFVS/blob/main/.gitmodules`
- BC source list present on the FVS fork:
  `https://github.com/forest-modeling/ForestVegetationSimulator/blob/pyfvs-features/bin/FVSbc_sourceList.txt`
- The BC work and its exclusion: the branch `bc_sourcelist` in
  `forest-modeling/ForestVegetationSimulator`
- The fork this ADR creates: `https://github.com/UBC-FRESH/PyFVS`

## Decision

We fork `forest-modeling/PyFVS` to `UBC-FRESH/PyFVS` and consume it as a pinned build and FFI layer.

- `fvsbc` pins the fork by commit, never by a floating branch, and records that commit, the FVS source
  submodule commit, and the built variant list in its provenance.
- `fvsbc` adds `bc` to the fork's variant matrix and owns the BC layer above it: BC keywords, species
  and BEC handling, and tidy simulation I/O.
- Patches to the fork stay minimal and remain candidates to send upstream. The fork exists so we are not
  blocked on someone else's schedule.

## Consequences

- We reuse a maintained MIT layer instead of writing Fortran bindings, and we gain full control of the
  build.
- We now maintain a fork and must track upstream. A release of `fvsbc` depends on a release of the fork,
  which depends on a commit of the FVS source submodule. Three versions move together.
- Distribution carries a Fortran build. Wheels, or a documented binary recipe, become part of the
  release work.
- Not yet verified: no `FVSbc` has been built; whether adding `bc` to the variant matrix is sufficient is
  unknown; the `bc_sourcelist` work is unreviewed and its author's intent is not established.
- Two decisions follow and need their own ADRs: that `fvsbc` is a standalone package rather than a
  module of an existing package, and the policy for contributing patches upstream.

## Alternatives considered

- Depend on `PyFVS` from PyPI or conda-forge. Rejected: it does not build the BC variant, and we cannot
  wait for an upstream release to carry our BC build changes.
- Write the FFI and build layer ourselves. Rejected: duplicates a maintained, MIT-licensed layer. The
  value in `fvsbc` is the BC semantics, not the bindings.
- Vendor the `PyFVS` source into `fvsbc`. Rejected: it hides divergence from upstream and weakens
  attribution.
- Add `PyFVS` as a git submodule of `fvsbc`. Rejected: this lab uses submodules for data, not for code
  (see `femic`). A pinned dependency states the relationship more clearly.
- Wait for the USDA repository to promote BC out of `_notReady`. Rejected: no schedule, and it does not
  deliver the BC Python layer.
