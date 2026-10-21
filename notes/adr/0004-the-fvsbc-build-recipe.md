# ADR 0004: The `FVSbc` build recipe

Status: proposed
Date: 2026-10-21
Issues: #12

## Context

ADR 0001 forked PyFVS as the build and FFI layer, and recorded one central uncertainty: whether adding
`bc` to the PyFVS variant matrix is sufficient, or whether the FVS source submodule needs a patch. It
named the answer as a prerequisite for every later phase.

The `P2.2` build spike answered it. The evidence, with the exact commands and their output, is in
`notes/reference/fvsbc-build-spike.md`. In summary:

- Adding `bc` to the variant matrix is **not** sufficient. Four defects stand in the way.
- Three are fixed and the build completes: the variant compiles, links, and produces
  `fvsbc.cpython-312-x86_64-linux-gnu.so`.
- The fourth blocks the import. PyFVS's `src/api/fvs_step.f90` calls `cubrds`, which 23 variants define
  and the BC variant does not.

## Decision

The `FVSbc` build is a patched fork, and the patch set is fixed at three changes:

1. **`meson_options.txt`.** Add `'bc'` to the `fvsvariants` `choices`. The `value` default is unchanged, so
   the fork still builds the US variants by default.
2. **`bin/FVSbc_sourceList.txt`.** Delete the 12 `../fire/cfim/` entries. They are Windows-only, and no US
   variant's source list carries them.
3. **`meson.build` and `canada/bc/blkdat.f`.** Drop `canada/bc/BCPLOT.F77` from the f2py signature input,
   and delete the vestigial `INCLUDE 'BCPLOT.F77'` from `blkdat.f`. The file is still compiled.

The `cubrds` gap is **not** decided here. It is an integration gap between PyFVS's API and the BC variant,
and it has three plausible resolutions: supply a BC `cubrds`, guard the call, or establish that `cfvol`
covers what `cubrds` provides. `P3` settles it, with a preference for the least invasive change.

The fork is pinned by commit, as ADR 0001 requires. The patches live in the fork, not in `fvsbc`.

## Consequences

- `fvsbc` can build the variant, which was in doubt. The build is reproducible from a documented recipe.
- The fork now diverges from its upstream in four files. A rebase onto a newer `pyfvs-features` must carry
  the patch set forward.
- Three of the four patches are candidates to send upstream, and the second is arguably a defect in the
  fork's own source list. The upstream policy is still open, and ADR 0001 records it as such.
- Until `cubrds` is settled, `FVSbc` cannot be imported, so no run is possible and none of the contracts'
  open questions can be answered.
- The build takes several minutes and needs gfortran, meson, ninja, and patchelf. `fvsbc`'s own CI does not
  build it yet, and wiring that is `P3` work.

## Alternatives considered

- **Depend on a released PyFVS wheel.** Rejected in ADR 0001, and the spike confirms it: no release builds
  the BC variant.
- **Patch the FVS source submodule instead of the fork.** Rejected: three of the four patches belong to
  PyFVS's own build files, and the fourth is a one-line removal in a variant source file that the submodule
  does not own exclusively.
- **Convert `canada/bc/blkdat.f` from `BLOCK DATA` to `SUBROUTINE`, as `pn` and seven other variants have.**
  Rejected as unnecessary: the `BLOCK DATA` form parses once the vestigial include is gone, and `ak` proves
  that by building with a `BLOCK DATA` `blkdat.f`.
- **Drop the `volume/` sources from the comparison.** The BC source list has 1 `volume/` entry where `pn`
  has 155. This was investigated and left as a question, not a defect: the BC variant has its own
  `cfvol.f` and `vols.f`. Recorded in the spike note.
