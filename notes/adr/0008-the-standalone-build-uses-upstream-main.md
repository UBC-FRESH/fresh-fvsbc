# ADR 0008: The standalone build uses upstream `main`

Status: accepted on 2026-10-24. Refined by ADR 0009, which does not adopt it.
Date: 2026-10-24
Issues: #19 (P3.2)
Corrects: ADR 0007

## Context

ADR 0007 concluded that the standalone `bin/FVSbc` is not buildable from the pinned source, and proposed
re-scoping `P3.2` to record the two output tables as unavailable. **That conclusion was too broad.** It is
true of the pinned branch, which depends on PyFVS's API in four places. It is not true of upstream FVS.

Tested in a worktree at upstream `main` (`28fda8ed`, 2026-10-07):

- The twelve-item BC patch **applies with exit 0**. No rebase was needed, and none of the twelve items has
  been made obsolete by the 2026 releases.
- `volume/NVEL` is a **submodule**, `FMSC-Measurements/VolumeLibrary`, and it is uninitialised by default,
  which is why `main` appeared to have no `.inc` files. `git submodule update --init` provides all 26.
- Three flags in `bin/makefile` are wrong for this variant.

The result: `bin/FVSbc` builds in nine seconds and runs the official `StandStructure` case with exit 0,
writing **`FVS_Compute` (160 rows)** and **`FVS_Summary_Metric` (164 rows)** — the two tables `P2` could not
reach. `FVS_Cases` holds four rows, one per stand, and `FVS_Error` is absent.

## Decision

The standalone is built from **upstream `main`**, not the pin:

1. Clone `forest-modeling/ForestVegetationSimulator` at `28fda8ed`, then
   `git submodule update --init --recursive`.
2. Apply `notes/reference/fvsbc-patchset.diff.gz`. It is unchanged, and it applies cleanly to `main`.
3. Apply `notes/reference/fvsbc-standalone-patchset.diff.gz`, three changes to `bin/makefile`:
   - **`-O2`.** Without it, **every keyword in the file reads as blank** and FVS reports
     `FVS01 ERROR: INVALID KEYWORD WAS SPECIFIED` for all of them, on the official case as much as on ours.
     This is the cause of the note in `P2.3`'s record that "at `-O0` the variant processes no stand at all,
     a robustness limit whose cause is not established". The cause is established now, and it is not a
     modelling limit: it is a miscompilation at `-O0`.
   - **`-fallow-argument-mismatch`**, for gfortran 13 on FVS's older Fortran.
   - **`-ffpe-trap=...` removed.** The makefile traps floating-point exceptions and this variant raises one
     legitimately, so the run core-dumps at exit 136 with a partially written database. The meson build
     does not trap, which is why the extension never showed it.
4. `make -C bin FVSbc`.

The standalone is **not** built from the pin, because the pin's `base/tregro.f` and `base/grincr.f` call
PyFVS's `fvs_step`, `prtrls_wrap`, and `fvsSetCmdLineC`. Guarding the first was a patch; the other two are
the command-line parser and a data-copy hook, and restoring them is reversing a maintainer's refactor
rather than adapting to it.

## Consequences

- **Two FVS revisions are now a fact, not a choice.** The extension must come from the pin, because PyFVS's
  meson build compiles `fvs_step` against it. The standalone must come from `main`, because the pin cannot
  build it. The provenance contract names one `fvs_source_commit`; it must name **which revision produced
  which artefact**. That is a contract change, and `P3.4` carries it.
- The standalone is a **second build path** and needs its own CI job, or it rots the moment nobody looks.
  The job builds it and runs the official case, asserting the two tables have rows.
- `ADR 0007`'s Decision is superseded. Its Context stands as the record of why the pin fails.
- The three flags are latent defects in the FVS makefile for this variant and are worth offering upstream
  under ADR 0001's open policy.

## Alternatives considered

- **Build from the pin and restore what was moved out.** Rejected: three restorations, one of which is the
  command-line parser and one of which pulls in the whole data layer. That is reversing a refactor.
- **Keep `ADR 0007`'s re-scope and record the tables as unavailable.** Rejected: it is false. The tables are
  available, and the only obstacle was an uninitialised submodule and three flags.
- **Copy `wdbkwtdata.inc` into the tree instead of initialising the submodule.** Rejected: an earlier
  attempt did exactly that, and it worked, but it hides the real dependency. The submodule is the answer.
