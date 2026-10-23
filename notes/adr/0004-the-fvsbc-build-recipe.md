# ADR 0004: The `FVSbc` build recipe

Status: accepted on 2026-10-23, when the maintainer approved `P2`'s close-out report. Renamed by ADR 0005.
Date: 2026-10-21
Issues: #13

## Context

ADR 0001 forked PyFVS as the build and FFI layer, and recorded one central uncertainty: whether adding
`bc` to the PyFVS variant matrix is sufficient, or whether the FVS source submodule needs a patch. It
named the answer as a prerequisite for every later phase.

The `P2.2` build spike answered it. The evidence, with the exact commands and their output, is in
`notes/reference/fvsbc-build-spike.md`. In summary:

- Adding `bc` to the variant matrix is **not** sufficient. Four defects stood in the way.
- **All four are fixed.** The variant compiles, links, produces
  `fvsbc.cpython-312-x86_64-linux-gnu.so`, and the module imports.
- The fourth was the one that blocked the import: PyFVS's `src/api/fvs_step.f90` calls `cubrds`, which 23
  variants define and the BC variant does not. Item 5 below is its fix. **An earlier version of this
  paragraph said the fourth still blocked the import**, while the Decision listed the fix; the
  contradiction was corrected here, before the ADR was accepted rather than after.

## Decision

The `FVSbc` build is a patched fork. The patch set is nine modified files and one new file, twenty
insertions against eight deletions, relative to `ef5fa84`. It is exported at
`notes/reference/fvsbc-patchset.diff.gz`, which was checked to apply cleanly to that commit and to
reproduce the working tree byte for byte. It is gzipped rather than stored as bare text because the fork's
sources use CRLF, so a faithful diff contains carriage returns, which this repository's validator rejects
in tracked files. To rebuild:

```bash
gunzip -c notes/reference/fvsbc-patchset.diff.gz > /tmp/fvsbc.patch
git -C <fvs-checkout> apply /tmp/fvsbc.patch
```

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
   accumulated, and clear `MCFV` where the tree loop converges. Without it, `OMCCUR` is built from an array
   BC never sets, so merchantable volume reports as zero. See `notes/reference/fvsbc-smoke-run.md`, and
   `notes/reference/fvsbc-validation.md` for the confirmation against the oracle.
7. **`bin/FVSbc_sourceList.txt` (again).** Point `dbsqlite/dbstreesin.f`, `rd/rdin.f`, and `rd/rdsout.f` at
   their `metric/` twins. BC's metric `INTREE` calls `DBSTREESIN` with 30 arguments where the base routine
   expects 33, so the callee wrote through three argument slots that did not exist and `TreeSQL` segfaulted
   on the first tree. Ontario, the closest working metric variant, makes the same `rd/` choices.
8. **`metric/dbsqlite/dbstreesin.f`.** Normalize `# IF` / `# ELSE` / `# ENDIF` to `#if` / `#else` /
   `#endif`. Every sibling metric file uses cpp style; this one alone used FVS's own preprocessor style, so
   it had never compiled under the `-cpp` build.
9. **`metric/base/evldx.f`.** Widen the parameter-reference range from `INSTR.LT.7000` to `INSTR.LT.9000`.
   `common/OPCOM.F77` sets `MAXPRM=7999`, so the narrower range rejected every reference at index 6000 and
   above as an undecipherable op-code. That disabled `COMPUTE` and every `IF` block in the variant.
10. **`metric/vbase/disply.f`.** Pass 22, not 20, as the leading dimension of `IOSUM` to `SUMOUT`.
    `common/OUTCOM.F77` declares `IOSUM(22,MAXCY1)` and `SUMOUT` takes the leading dimension as an
    argument, so the stride-20 call mis-read every column of every row after the first.
11. **`metric/strp/estab.f` and `metric/strp/esuckr.f`.** Reset `MCFV` for a newly established tree, as the
    surrounding code already resets `CFV`. Without it a new tree inherits the previous occupant's
    merchantable volume, which reports as merchantable volume exceeding total volume.
12. **`metric/dbsqlite/dbsmis.f`.** Add the missing `fsql3_exec(IoutDBref,"Begin;"//CHAR(0))` to
    `DBSMIS2`. It is the only one of the four `DBSMIS*` routines that issues a `Commit;` without a
    preceding `Begin;`, so its commit fails with "cannot commit - no transaction is active". The routine
    treats that as fatal, clears `IDM2`, and never writes the table again, which is why
    `FVS_DM_Stnd_Sum_Metric` held one row per stand instead of one per stand per report period.

Items 6, 8, 9, 10, and 11 are all the same class of defect: a newer per-tree or per-cycle array was
introduced, and one of the places that initialises or indexes it was never updated.

Two things this ADR explicitly does **not** do:

- It does not add the `volume/` subsystem. BC does not need the NVEL volume library. It needs one data
  file's directory on the include path, which entry 4 provides.
- It does not delete the `fire/cfim` sources. That was tried, and it is wrong: it trades a compile error
  for a link error, because `canada/fire/bc/fmcfim.f` calls `cfim_driver`.

The fork is pinned by commit, as ADR 0001 requires. The patches live in the fork; a copy is exported into
`fvsbc` at `notes/reference/fvsbc-patchset.diff.gz` so that the recipe survives the working tree, which is
a scratch clone.

## Consequences

- `fvsbc` builds the variant and the module imports, exposing `fvs_init`, `fvs_grow`, and `fvs_end` from
  `fvs_step`. The build is reproducible from a documented recipe.
- The fork now diverges from its upstream in nine files. A rebase onto a newer `pyfvs-features` must carry
  the patch set forward.
- The `fire/cfim` patch is arguably an upstream defect: both Canadian source lists carry sources that no US
  variant compiles, so PyFVS has never built them on Linux. The patch is a two-symbol compiler definition
  that the source already anticipated. The upstream policy is still open, and ADR 0001 records it as such.
- The build takes several minutes and needs gfortran, meson, ninja, and patchelf. `fvsbc`'s own CI does not
  build it yet, and wiring that is `P3` work.
- The variant is no longer unvalidated. The FVS project's own `StandStructure` comparison passes with zero
  differing lines across all four stands, and `YSM-SkyRanch` matches on 328 of 375 rows. See
  `notes/reference/fvsbc-validation.md`.

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
