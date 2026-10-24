# ADR 0007: The standalone binary is not buildable from the pinned source

Status: superseded by ADR 0008 on 2026-10-24.
Date: 2026-10-24
Issues: #19 (P3.2)
Related: ADR 0004, ADR 0006

## Context

`P2.2` deferred one subtask to `P3`: reading `FVS_Compute` and `FVS_Summary_Metric`, which PyFVS makes
unreachable by occupying the `DATABASE` output block. `P2`'s close-out recommended building the
standalone `FVSbc` executable as the route to them, on the grounds that the official test cases invoke
`../../bin/FVSbc`, which accepts a `DATABASE` block.

`P3.2` tested that recommendation. It does not survive contact with the source. The FVS project's own
`bin/makefile` builds `FVSbc` from `bin/FVSbc_sourceList.txt`, and the build fails in three seconds:

```text
tregro.f:3:10:
    3 |       use fvs_step, only: GCB_INCR
      |          1
Fatal Error: Cannot open module file 'fvs_step.mod' for reading at (1): No such file or directory
```

The cause is structural. `base/tregro.f` and `base/grincr.f` in the **pinned** FVS source carry
`use fvs_step` — PyFVS's own API module, which lives in the fork's `src/api/`, is not in the FVS source
tree, and is not in `FVSbc_sourceList.txt`. Adding it is not a one-line change: `fvs_step` uses
`tree_data` and `globals`, `globals` is **generated** from `globals.f90.in` by the meson build, and
`snag_data` sits behind the same layer. PyFVS's meson build has no `executable()` target — it produces the
Python extension and nothing else. So the pinned source can build the extension and cannot build the
standalone program.

The same test also answered the other half of the question. PyFVS's API exposes **data arrays in memory** —
`carbon_summary`, `downwood_summary`, the tree and snag and mortality arrays — and **no DSN or output
database configuration at all**. So the tables cannot be requested through the FFI either, and the
standalone program was the only route to them.

## Decision

**Superseded.** The conclusion below is true of the pinned branch and false of FVS: upstream `main`
builds the standalone, and ADR 0008 records the recipe. The Decision is kept as written because a
superseded ADR is evidence of what was believed and why.

**The standalone binary is not a route this project can take from the pinned source**, and `P3.2` is
re-scoped accordingly:

1. `FVS_Summary_Metric` is **not needed**: the in-memory summary that `FVS.summary` returns carries the
   same per-period quantities, and `P2` already reads it.
2. `FVS_Compute` is **recorded as unavailable through this project's route**, with this ADR as the
   reason, rather than left as an open subtask that reads like unfinished work.
3. The output contract's rule 1 and its "Not verified" list name the limit and cite this ADR.

## Consequences

- A caller who needs `FVS_Compute` has no supported path in this project. That is a real limitation and
  the reason this ADR exists rather than a note.
- The alternative that would restore it is re-integrating PyFVS's API layer into the FVS makefile build,
  including generating `globals`, which is a patch to the fork's build system and not to the FVS source.
  It is not attempted here because nothing in the project's scope needs `FVS_Compute` yet.
- `P2`'s close-out recommendation is **disproved by test**, and the report stays as written with this ADR
  as its correction, following the rule that a closed report is evidence rather than a draft.

## Alternatives considered

- **Add `src/api/fvs_step.f90` to `FVSbc_sourceList.txt`.** Rejected: it pulls in `tree_data` and a
  generated `globals`, and `globals` has no makefile rule. That is a build-system change, not a source-list
  entry.
- **Build from an upstream FVS commit before PyFVS's API integration.** Rejected: the pin is
  `ef5fa84`, which *is* the fork's submodule commit and carries the integration. An earlier commit would
  not be the pinned source, and this project records the pin rather than guessing at an ancestor.
- **Patch PyFVS to expose the output DSN through its API.** Rejected for now: it is an upstream change,
  it needs its own approval under ADR 0001's open policy, and it is larger than the need.
- **Keep the subtask open as unfinished work.** Rejected: an item that cannot be done by the stated route
  is a limit, and a limit recorded in the contract is more honest than a checklist item that never closes.
