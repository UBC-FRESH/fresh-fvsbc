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

The `FVSbc` build is a patched fork. The patch set is four files and nine changed lines, plus one new
file.

1. **`meson_options.txt`.** Add `'bc'` to the `fvsvariants` `choices`. The `value` default is unchanged, so
   the fork still builds the US variants by default.
2. **`meson.build`.** Add `add_project_arguments('-DCMPgcc', '-Dunix', language: 'cpp')`. `fire/cfim` has
   three branches, and the one that declares a plain `extern "C" int cfim_driver_` is guarded by
   `#ifdef CMPgcc` / `#ifdef unix`. Nothing defined `CMPgcc`, so the MinGW branch was taken and the
   Canadian variants could not compile on Linux. Also filter `bcplot.f77` out of the f2py signature input.
3. **`canada/bc/blkdat.f`.** Delete the vestigial `INCLUDE 'BCPLOT.F77'` line.
4. **`bin/FVSbc_sourceList.txt`.** Add six entries: `canada/bc/cubrds.f`, `vdbsqlite/dbsreference.f`, the
   three `dbsqlite/dbs_fiavbc_*.f`, and `volume/NVEL/wdbkwtdata.inc`.
5. **`canada/bc/cubrds.f`.** New. 57 lines, from `wc`, with the `DATA` sizes corrected for `MAXSP=15`.
6. **`canada/bc/vols.f`.** Add `MCFV(I)=WK1(I)` at the two points where the merchantable total is
   accumulated. Without it, `OMCCUR` is built from an array BC never sets, so merchantable volume reports as
   zero. See `notes/reference/fvsbc-smoke-run.md`.

Two things this ADR explicitly does **not** do:

- It does not add the `volume/` subsystem. BC does not need the NVEL volume library. It needs one data
  file's directory on the include path, which entry 4 provides.
- It does not delete the `fire/cfim` sources. That was tried, and it is wrong: it trades a compile error
  for a link error, because `canada/fire/bc/fmcfim.f` calls `cfim_driver`.

The fork is pinned by commit, as ADR 0001 requires. The patches live in the fork, not in `fvsbc`.

## Consequences

- `fvsbc` builds the variant and the module imports, exposing `fvs_init`, `fvs_grow`, and `fvs_end` from
  `fvs_step`. The build is reproducible from a documented recipe.
- The fork now diverges from its upstream in four files. A rebase onto a newer `pyfvs-features` must carry
  the patch set forward.
- The `fire/cfim` patch is arguably an upstream defect: both Canadian source lists carry sources that no US
  variant compiles, so PyFVS has never built them on Linux. The patch is a two-symbol compiler definition
  that the source already anticipated. The upstream policy is still open, and ADR 0001 records it as such.
- The build takes several minutes and needs gfortran, meson, ninja, and patchelf. `fvsbc`'s own CI does not
  build it yet, and wiring that is `P3` work.
- Nothing has been run. A successful import is not evidence that the variant computes correctly.

## Alternatives considered

- **Depend on a released PyFVS wheel.** Rejected in ADR 0001, and the spike confirms it: no release builds
  the BC variant.
- **Delete the `fire/cfim` sources from the BC source list.** Tried and rejected: it clears the compile
  error and breaks the link, because `canada/fire/bc/fmcfim.f` calls `cfim_driver`. The compiler definition
  is the correct fix, and it uses a Linux branch that already exists.
- **Patch `cfim.cpp` to remove `__declspec` and `__stdcall`.** Rejected: unnecessary. Defining `CMPgcc`
  selects a branch that never had them.
- **Guard the three `DBS_FIAVBC_*` calls in `vbase/cuts.f` and `base/fvs.f`.** Rejected: the calls are in
  shared code that both source lists compile, and the routines self-guard on `IVBCATRLST` and `LFIANVB`.
  The only real need was one include directory.
- **Add the whole `volume/` subsystem.** Rejected: 155 entries that the BC variant does not use. It needs
  one data file's directory on the include path.
- **Convert `canada/bc/blkdat.f` from `BLOCK DATA` to `SUBROUTINE`, as `pn` and seven other variants have.**
  Rejected as unnecessary: the `BLOCK DATA` form parses once the vestigial include is gone, and `ak` proves
  it by building with a `BLOCK DATA` `blkdat.f`.
