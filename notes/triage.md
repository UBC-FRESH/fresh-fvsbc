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
| 2 | `IF` blocks are refused, not written | **accepted** | A nested keyword model, ended by `ENDIF` | `COMMENT`, `COMPUTE` and `DATABASE` are written since `P7`, and `FMIN` since `P17`. **`IF` wraps keywords rather than lines**, so it needs a nested structure the model does not have, and it is refused by name. **Reopened by a caller who needs conditional keywords** |
| 3 | The second official case, `YSM-SkyRanch`, differs on three stands | **accepted** | A 2022 build of the variant, which this project has no path to | 328 of 375 rows are identical and the three that differ are the densest. The residual is attributed to an upstream change between the fixture's revision and the pinned source. Proving it needs the 2022 source, which is **not reachable by any path this project has**: the BC variant is not in `meson_options.txt` at that revision and `src/api/fvs_step.f90` did not exist (`CHANGE_LOG.md`, `P2.3`). **Reopened if a 2022 build becomes reachable by some path**, or if a caller reports a difference the first case would not catch |
| 4 | The oracle is a 2022 fixture, and the FVS project's own checker skips this variant | **accepted** | Nothing: it is a property of the evidence | Agreement with a 2022 fixture is evidence with a bound, not proof, and the fixture is what the FVS project ships. **Reopened by a newer official fixture**, which the project would adopt and re-run |
| 5 | The residual on three dense stands is attributed, not proven | **accepted**, merged into row 3 | The same 2022 build | It is the same question as row 3 and counting it twice would inflate the list. Reopened with row 3 |
| 6 | `scripts/check_workflow.py` does not catch a POSIX temporary path in a tracked file | **fixed** in `P7.2` (#45) | Done: the pattern, its false-positive evidence, and nine tests | The gate catches a home-directory path and not a temporary one, and four such paths were in a tracked note until `P3`'s close-out. It is small, but **a new pattern can false-positive on legitimate prose**, so it needs its own evidence rather than a line in a maintenance phase. Reopened by `P7`'s scope decision |
| 7 | `run.py`'s drive body is covered only where the extension is built | **accepted** | The extension in the coverage job | The build job covers the body and the quality gate is met at 98 percent overall. Closing it properly means installing a Fortran build in the coverage job, which is a CI decision with a real cost. **Reopened if the drive body changes**, because then the uncovered lines are the ones that just changed |
| 8 | A parameter passed to the command cannot contain a comma | **accepted** | A different argument syntax | It is documented, and the API has no such limit. **Reopened by a caller who needs a comma**, because the workaround is to use the API |
| 9 | At `-O0` the variant writes no database at all | **accepted** | Nothing: it is a build requirement | The optimiser is not optional, and ADR 0008 records it for the standalone and `P4`'s report for the extension. **Reopened if a build at `-O0` ever works**, which would mean the requirement was a different flag |
| 10 | The package needs a separately built extension | **accepted** | A build integration, which is a different project | This package wraps a pinned build of one variant; building FVS is PyFVS's and ADR 0004's concern. **Reopened if the project ever distributes a wheel**, where the dependency has to be expressed |
| 11 | The reader exposes thirty-one of the database's 44 tables | **accepted** | Testing a table, then exposing it | Output contract rule 3 keeps an untested table out of the public API. Fourteen are exposed, and the rest are not all reachable: some take a `DATABASE` option, carbon takes `CARBREPT` and consumption `SIMFIRE` inside an `FMIN` block, the burn report's gate cannot be satisfied by valid input, five tables have a writer nothing calls, and the rest are candidates that each need a case (`notes/reference/table-reachability.md`). **What is left is a decision about which tables are worth a case, not 30 tests.** Reopened by a caller who needs one of them |
| 12 | The `nemora` adapter requires `species` and `tree_age` from the caller | **accepted** | A species-assignment capability | `nemora` emits neither, and assigning a species is a modelling question with a research burden. The adapter fails rather than defaulting, which is the honest behaviour. **Reopened by a caller who asks for species assignment**, not by one who has populations without species: every `nemora` population has none, so that condition would fire on the normal case and would make the row unowned |

## Found, and not yet fixed

- **The oracle comparison is attributed, and it now says what it means.** `P49` finished the
  comparison `P45` and `P46` left running. **Every model value agrees** — `FVS_Summary_Metric` and
  `FVS_TreeList_Metric` match value for value, including all 3,996 per-tree rows — and the `0 of 5`
  was **not** source drift. What it was:
  - **The output `DATABASE` block must open before a case begins.** Reading a stand from an input
    database calls `FORKOD` with no location code and logs `FVS03`; logging it writes to the output
    database and starts the case, and a `DATABASE` block naming `DSNOut` is then refused with
    `FVS16` and **ignored**. The harness's block was being ignored, so the standalone's tables came
    from the *default* options rather than from the run's own block.
  - **`tree_num` is not `plot * 1000 + tree`.** `BC_TREFMT` reads `I4` for the plot, tabs back to
    column 1, then reads `I7` for the tree, and Fortran ignores embedded blanks: plot 1 tree 1 is
    **11**, not 1001. The harness zero-filled them and wrote a tree id that does not exist.
  - **`CaseID` is minted per run**, so two builds can never agree on it. It is no longer compared,
    and neither are `RunDateTime`, `KeywordFile`, `Version` or `RV`.
  - **What the harness cannot explain still fails it.** `FVS_Cases.SamplingWt` is explained
    (`DBSCASE(2)` only updates a case row that already exists, and the two drivers create it at
    different points); every other difference is reported by column and fails the run, and an
    explanation that stops applying is reported as `stale` rather than silently dropped.
- **`FVS_Regen_SitePrep` differs from the standalone, and it is the model rather than the writer.**
  The oracle's first genuine difference, found by `P58`. The same case prints `PCT: 74 20 6` in this
  package's `.out` and `PCT: 100 0 0` in the standalone's, in the same `SITE PREP SUMMARY` block.

  `P59` ruled out everything observable:

  - **Not the stand variables.** `ESPREP` predicts the default probabilities from `ASPECT`, `SLOPE`,
    `BA` and `ELEV`; both runs echo `ASPECT 0.`, `SLOPE 5%`, `ELEVATION 1158.2`, and both write 4,146
    tree rows with one plot.
  - **Not the seed.** `RANNSEED` 1, 2 and 3 give the same `74 20 6` and `76 20 4` for this package's
    run, so the result is deterministic for a given input.
  - **Not the writer.** `DBSSITEPREP` stores what `estab.f` hands it, and the `.out` prints the same
    numbers from the same call.

  What is left is `estab.f`'s site-prep selection: it fills `SUMPRE` from draws out of `WK6`, the
  pre-generated uniform array, and `PcntNone/PcntMech/PcntBurn` are those counts as percentages after
  plot replication (`DUPNPT = NPTIDS*IDUP`). **The most likely cause is that the two drivers consume
  different numbers of draws from the stream before `estab.f` runs** — the standalone reads its trees
  through a `DATABASE` block and this package through a tree-list file — so the same seed lands on
  different draws. That is a hypothesis, not a finding: the draws themselves were not compared.

  **What this does not affect:** the regeneration tally, the tree list, the summary and every other
  table in the same run match. `PcntNone/PcntMech/PcntBurn` are the only columns that move, and they
  are three integers describing a random allocation, not a projection.

  **Reopened by comparing the `WK6` draws the two runs actually used**, which needs the draw index
  logged from both.
- **The fire-model keywords were unvalidated, and that is fixed.** `P50` found that `FMIN`'s body was
  written as **raw lines**, so a caller spaced the fields by hand. A mis-spaced line is not refused —
  `SNAGCLAS  0.0   10.0  20.0  40.0` reaches FVS as class 2 `20.0` and class 3 `0.0`, with no error.
  The block now holds **keywords**, written by the same writer as everything else and checked against
  `fmin.f`'s own fifty-five, and a fire-model keyword outside the block is refused. That is what made
  the snag, down-wood and carbon tables reachable: **eight of nine comparable tables now match**.
- **The fuels and potfire tables vanish if the `FMIN` block follows `INVYEAR`, and that is fixed.**
  `FUELOUT` and `POTFIRE` set `IFLALB` and `IPFLMB` to `IY(1)` when they are read, and `fmdout.f` and
  `fmpofl.f` treat **any positive value as "suppress this report"**. Read after `INVYEAR`, they switch
  their own reports off: the run succeeds, `FVS_Fuels_Metric`, `FVS_PotFire_Metric` and
  `FVS_PotFire_Cond_Metric` are simply absent, and nothing says so. **The official case never hits it**
  because its inventory year comes from the input database rather than an `INVYEAR` keyword, so the
  year is still zero when the block is read — which is why the defect has gone unnoticed upstream. The
  validator now warns, and with the block first the four fire tables are written and **agree with the
  standalone value for value**.
- **`FVS_InvReference` is written by the standalone on every run and never by this package's build.**
  It is the one exposed table no run of this package produces. `P61` narrowed it as far as observation
  from outside the binary allows:

  - **Not the source.** `dbsreference.f` and `dbscase.f` are byte-identical between the pin and
    upstream, and the compiled `dbsreference_` is **the same size in both binaries** — 5,097 bytes.
  - **Not the driver or the inputs.** This package's driver now reads the stand through the *same*
    `DSNin` route the standalone uses, with the same keyword file structure, and still writes no such
    table.
  - **Not the handle, and not the case row.** `DBSSTATS` is called from `CALL STATS`, the statement
    immediately before `CALL DBSREFERENCE` in `fvs.f`, and a run with `INVSTATS` and `STATS` **does**
    write `FVS_Stats_Species_Metric`. So at the point `DBSREFERENCE` runs, the output database is
    open and `DBSCASE(1)` has created the case row.

  That leaves a **runtime-state difference inside the routine itself**, which is not observable from
  outside: its silent exits are `fsql3_tableexists` reporting the table as present and the `CREATE`
  returning an error, and nothing distinguishes them without a log line. **Establishing which needs a
  build of the fork with one added write**, which is a change in the pinned fork and not here.

  **Reopened by a build with that line**, or by an upstream fix.
- **A run that logs nothing was reported as failed, and that is fixed.** FVS writes `FVS_Error` only when
  it has something to log; the reader treated an absent table as a failure to read, on the stated premise
  that the extension wrote it on every run. A 999-tree single-plot case disproved the premise: FVS logged
  nothing, wrote no table, and the package reported a good run as failed. `read_errors` now answers an
  absent table with an empty frame of its columns, so silence reads as a clean run.

- **The web service has no authentication of its own, by design.** The dev container is
  pre-authenticated — JupyterHub proxies the port — so the service is deployed with `--host 0.0.0.0
  --allow-remote --root-path <proxy prefix>`, and the proxy authenticates. This is a **deployment
  assumption, not a defect**, and the refusal message says so. **Reopened if the service is ever bound to
  an interface a proxy does not front.**
- **One plot holds at most 999 trees, and a real BC stand can carry more.** The 2022 workshop's own case has
  1540 trees in a single plot; the adapter now refuses it by name, with the reason. Fixing it means
  subdividing a stand into plots, which changes what the statistics mean, so it is a modelling decision
  rather than a repair. **Reopened by a caller who needs a stand above 999 trees in one plot.**

- **The remaining tables are not all reachable, and the reason differs by table.** `P24` settled it
  mechanically: 25 of the 30 have a writer and a call site, five have a writer that nothing calls, and the
  burn report's gate needs an invalid input. **This corrects an earlier entry in this file** that said the
  dwarf-mistletoe and root-disease writers do not exist — they do, as `DBSMIS1` and `DBSRD1`; the grep
  that "proved" otherwise searched for the wrong symbol names. Evidence in
  `notes/reference/table-reachability.md`.

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
