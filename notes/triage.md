# The backlog: every known gap and its disposition

Every item in `RELEASE_NOTES.md`'s known-gaps list, with a disposition that ends the question. **A gap
that is recorded and owned by nobody is the state this project was in from `P2` to `P6`**, and this table
is what ends it.

Three dispositions, and nothing else:

- **fix now** — a task in the current phase;
- **fix later** — a named phase, or a proposed one;
- **accepted** — with the reason it will not be fixed **and what would reopen it**. A row that cannot
  say what would change its mind is not accepted, it is unowned.

The table is reviewed at the cadence `P6.3` sets, and a disposition changes only in a change set that
says which review changed it.

| # | Gap | Disposition | What it takes | Reason, and what would reopen it |
| --- | --- | --- | --- | --- |
| 1 | `run_case` is not re-entrant in a process, and a run is not thread-safe | **fixed** in `P6.2` (#39), ships in the release after `v0.1.0` | Done: the spike, the decision (ADR 0010), the change, the tests and a mutation | The only gap that returned **silently wrong numbers** from a released package: a second run in one process inherited the first one's Fortran state, and a run changed the caller's working directory. **`v0.1.0` still carries it**, because that release was tagged before the fix; `RELEASE_NOTES.md` describes that release and keeps the row. It leaves the table when the release that carries the fix is published |
| 2 | `IF` blocks are refused, not written | **accepted** | A nested keyword model, ended by `ENDIF` | `COMMENT`, `COMPUTE` and `DATABASE` are written since `P7`. **`IF` wraps keywords rather than lines**, so it needs a nested structure the model does not have, and it is refused by name. **Reopened by a caller who needs conditional keywords** |
| 3 | The second official case, `YSM-SkyRanch`, differs on three stands | **accepted** | A 2022 build of the variant, which this project has no path to | 328 of 375 rows are identical and the three that differ are the densest. The residual is attributed to an upstream change between the fixture's revision and the pinned source. Proving it needs the 2022 source, which is **not reachable by any path this project has**: the BC variant is not in `meson_options.txt` at that revision and `src/api/fvs_step.f90` did not exist (`CHANGE_LOG.md`, `P2.3`). **Reopened if a 2022 build becomes reachable by some path**, or if a caller reports a difference the first case would not catch |
| 4 | The oracle is a 2022 fixture, and the FVS project's own checker skips this variant | **accepted** | Nothing: it is a property of the evidence | Agreement with a 2022 fixture is evidence with a bound, not proof, and the fixture is what the FVS project ships. **Reopened by a newer official fixture**, which the project would adopt and re-run |
| 5 | The residual on three dense stands is attributed, not proven | **accepted**, merged into row 3 | The same 2022 build | It is the same question as row 3 and counting it twice would inflate the list. Reopened with row 3 |
| 6 | `scripts/check_workflow.py` does not catch a POSIX temporary path in a tracked file | **fixed** in `P7.2` (#45) | Done: the pattern, its false-positive evidence, and nine tests | The gate catches a home-directory path and not a temporary one, and four such paths were in a tracked note until `P3`'s close-out. It is small, but **a new pattern can false-positive on legitimate prose**, so it needs its own evidence rather than a line in a maintenance phase. Reopened by `P7`'s scope decision |
| 7 | `run.py`'s drive body is covered only where the extension is built | **accepted** | The extension in the coverage job | The build job covers the body and the quality gate is met at 98 percent overall. Closing it properly means installing a Fortran build in the coverage job, which is a CI decision with a real cost. **Reopened if the drive body changes**, because then the uncovered lines are the ones that just changed |
| 8 | A parameter passed to the command cannot contain a comma | **accepted** | A different argument syntax | It is documented, and the API has no such limit. **Reopened by a caller who needs a comma**, because the workaround is to use the API |
| 9 | At `-O0` the variant writes no database at all | **accepted** | Nothing: it is a build requirement | The optimiser is not optional, and ADR 0008 records it for the standalone and `P4`'s report for the extension. **Reopened if a build at `-O0` ever works**, which would mean the requirement was a different flag |
| 10 | The package needs a separately built extension | **accepted** | A build integration, which is a different project | This package wraps a pinned build of one variant; building FVS is PyFVS's and ADR 0004's concern. **Reopened if the project ever distributes a wheel**, where the dependency has to be expressed |
| 11 | The reader exposes four of the database's 33 tables | **accepted** | Testing a table, then exposing it | Output contract rule 3 keeps an untested table out of the public API. `FVS_Compute` and `FVS_Summary_Metric` were added in `P9` once a `DATABASE` block could ask for them; **the other 29 need their own tests**. Reopened by a caller who needs one of them |
| 12 | The `nemora` adapter requires `species` and `tree_age` from the caller | **accepted** | A species-assignment capability | `nemora` emits neither, and assigning a species is a modelling question with a research burden. The adapter fails rather than defaulting, which is the honest behaviour. **Reopened by a caller who asks for species assignment**, not by one who has populations without species: every `nemora` population has none, so that condition would fire on the normal case and would make the row unowned |

## Found, and not yet fixed

- **The contract's table list is the base schema's, and BC builds the metric one.** Twenty-four names are
  wrong for this variant and at least two real tables are missing. Evidence and scope in
  `notes/reference/table-names.md`; the correction needs the metric schema read in full, because part of
  it is created through a dynamic statement.

## Closed in `P11`

- **The command could not write a keyword block.** `--keyword NAME=FIELD,...` sets fields and a block
  needs lines, so `0.3.0` shipped with no way to ask for a `DATABASE` block and the tables it exposes
  were unreachable from the shell. Found by `P10`'s clean-checkout verification, not by a test. `P11.1`
  adds `--block`, and the test that would have caught it.

## What this does not do

- **It fixes nothing.** `P6.2` is the one fix this phase takes.
- **It does not close a gap.** Every row stays in `RELEASE_NOTES.md` until the change that resolves it
  removes it there.
- **It does not decide `P7`.** Two rows are marked fix-later with a proposed phase, and its scope is the
  maintainer's.

## Proposed: `P7`

Two gaps are worth doing and no phase covers them, and they are the two marked fix-later above:

1. **A keyword model that can hold a block**, so `COMMENT`, `COMPUTE`, `IF` and `DATABASE` can be
   written. This is the largest gap in the public surface: a run that needs `COMPUTE` cannot be
   expressed, and `FVS_Compute` is that table.
2. **The validator's POSIX-temporary-path pattern**, with the false-positive evidence a gate change
   needs.

**The scope is the maintainer's to set**, and this table proposes it rather than assuming it. If `P7` is
not wanted, both rows become accepted with the reason "not scheduled", which is a different statement
from the reasons above and would say so.

## Where a disposition changes

At a review, by a change set that names the review. `P6.3` (#40) sets the cadence and records the first
one; the second is the maintainer's to hold, and a missed review is visible because the record says when
the next one was due.
