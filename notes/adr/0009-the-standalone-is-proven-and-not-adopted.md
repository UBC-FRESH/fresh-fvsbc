# ADR 0009: The standalone is proven and not adopted

Status: accepted on 2026-10-24.
Date: 2026-10-24
Issues: #19 (P3.2)
Refines: ADR 0008

## Context

ADR 0008 established that the standalone `bin/FVSbc` builds from upstream `main` and writes
`FVS_Compute` and `FVS_Summary_Metric`. Both were then verified: the official case gives 160 and 164 rows,
and this project's synthetic case gives **21 summary rows through the standalone against 21 through the
extension**.

Two things were established after that, and they change what the standalone is for.

1. **`FVS_Compute` is not a general output table.** It holds the user's `COMPUTE` expressions: one row per
   stand-period, one column per expression. The official case has 160 rows because it has 4 stands, 40
   periods, and three expressions (`SmVol`, `MdVol`, `LgVol`); an empty, properly terminated block defines
   nothing and the table is not created. This project defines no `COMPUTE` expressions, so the table does
   not exist for its runs and there is nothing in it to read.
2. **`FVS_Summary_Metric` was never out of reach.** The extension returns the same per-period quantities
   from `FVS.summary` in memory, and the two routes agree on the synthetic case.

So `P2.2`'s deferred subtask, "read `FVS_Compute` and `FVS_Summary_Metric`", was a **false requirement**:
one table does not apply to this project, and the other was already available through the route the
project uses.

## Decision

The standalone is **proven and not adopted**. ADR 0008's recipe and `fvsbc-standalone-patchset.diff.gz`
are kept, so anyone can rebuild it in minutes, and **no CI job, no provenance change, and no contract
surface depend on it**.

## Consequences

- **The two-revision problem disappears.** The provenance contract keeps its single `fvs_source_commit`,
  because only one build is a project artefact. `P3.4` no longer carries a contract change for it.
- `P2.2`'s deferred subtask is **resolved by explanation**, and `outputs.rst` is corrected: it stops
  listing `FVS_Compute` among the tables the reader should expose, and it says why.
- The `-O0` note in `P2.2`'s record now has a cause: at `-O0` every keyword in the file reads as blank. That
  was a build-flag defect, not a modelling limit, and the record's "robustness problem" was the wrong
  reading of it.
- The three makefile flags are latent defects in the FVS makefile for this variant. They are worth
  offering upstream under ADR 0001's open policy, and ADR 0008 records them.

## Alternatives considered

- **Adopt it and add a CI job.** Rejected: nothing in the project's scope needs it, a second build path
  with no consumer is a liability that will rot whether or not it has a job, and the two revisions
  complicate the provenance contract for no current benefit.
- **Discard the recipe.** Rejected: the recipe cost a day and is the only route to `FVS_Compute` if a
  caller ever defines compute expressions. Keeping it costs one compressed patch and one ADR.
- **Keep `P2.2`'s subtask open as unfinished.** Rejected: it asks for something that does not exist for
  this project's runs, and an item that can never close is not a checklist item.
