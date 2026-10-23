# FVS-BC Roadmap

This roadmap is the plan of record and the issue tracker map for FVS-BC. Keep it in step with the GitHub issues, `CHANGE_LOG.md`, and `notes/`. `scripts/check_workflow.py` parses the phase headers, status lines, and checkboxes below, so keep their format.

Every phase starts as `planned` with `Parent issue: TBD`. Activate a phase only after its parent issue exists and the maintainer approves it.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap | #1 | `feature/p0-bootstrap` | complete |
| P1 Scope and design | #5 | `feature/p1-scope-design` | complete |
| P2 Contracts and prototype | #10 | `feature/p2-contracts-prototype` | active |
| P3 Build | TBD | `feature/p3-build` | planned |
| P4 Verify | TBD | `feature/p4-verify` | planned |
| P5 Release and deploy | TBD | `feature/p5-release` | planned |
| P6 Operate and maintain | TBD | `feature/p6-operate` | planned |

## Lifecycle Map

| Stage | Phases | Exit criteria |
| --- | --- | --- |
| Scope and design | P0, P1 | Goal, scope, and out-of-scope items recorded; decisions in ADRs, each accepted or deferred |
| Build | P2, P3 | Each task committed with its task ID; each commit leaves the dashboard green; docs updated in the same change set |
| Verify | P4 | The dashboard and CI pass on the head commit; each acceptance criterion has evidence in the close-out report |
| Release and deploy | P5 | Tag, release notes, and Pages live; a clean checkout verifies them; each release action approved on its own |
| Operate and maintain | P6 | Review cadence held; incoming ideas triaged; retirement decided and recorded as an ADR |
| Retire | P6 (procedure) | Archive notice, final changelog entry, and issues closed |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside the task's issue body. Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and its parent issue closes.

## Phase 0: Bootstrap

Parent issue: #1
Branch: `feature/p0-bootstrap`
Status: complete

Goal: adapt the contract to this project, and make the first pull request reviewable.

- [x] P0.1 Adapt `AGENTS.md` and `README.md` to this project (#2)
- [x] P0.2 Confirm the validator and the docs build pass (#3)

Acceptance criteria:

- `AGENTS.md` states the project-specific rules, and links the shared workflow rules instead of copying them.
- `README.md` describes `fresh-fvsbc`, its place in the pipeline, and its status, and claims nothing the roadmap has not recorded.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 1: Scope and design

Parent issue: #5
Branch: `feature/p1-scope-design`
Status: complete

Goal: settle the repository's public footing, then state the question, the users, the scope, and the out-of-scope items, and record the first decisions as ADRs.

- [x] P1.1 Add the MIT licence and align the package metadata (#6)
- [x] P1.2 Write the problem statement and scope in `notes/` (#7)
- [x] P1.3 Record the first design decisions as ADRs in `notes/adr/` (#8)

Acceptance criteria:

- `LICENSE` is MIT, and the package metadata agrees with it.
- `notes/` states the problem, the users, the scope, and the out-of-scope items.
- Every ADR is accepted or superseded, and any new decision is recorded.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 2: Contracts and prototype

Parent issue: #10
Branch: `feature/p2-contracts-prototype`
Status: active

Goal: define the interfaces and the data contracts, then build the smallest prototype that exercises them.

- [x] P2.1 Define the interface and data contracts in `docs/` (#11)
- [ ] P2.2 Build a prototype that exercises the contracts on synthetic data (#12)
- [x] P2.3 Record the FVS source patch set and its oracle comparison (#13)
- [x] P2.4 Rename the project to `fresh-fvsbc` (#14)

Acceptance criteria:

- `docs/` states the interfaces and the data contracts: the tree-list input, the keyword set, the parsed outputs, and the provenance record.
- A prototype runs on synthetic data and exercises each contract, with checks that can fail.
- The build question in ADR 0001 is answered with evidence: either `bc` builds from the variant matrix, or the patch the FVS source submodule needs is recorded.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 3: Build

Parent issue: TBD
Branch: `feature/p3-build`
Status: planned

Goal: implement the agreed scope, one task at a time, on the phase branch.

- [ ] P3.1 Implement the first build task

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 4: Verify

Parent issue: TBD
Branch: `feature/p4-verify`
Status: planned

Goal: show that the build meets its acceptance criteria, and record the evidence in the changelog.

- [ ] P4.1 Run the acceptance checks and record the evidence

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 5: Release and deploy

Parent issue: TBD
Branch: `feature/p5-release`
Status: planned

Goal: tag a release, publish the docs, and verify the published artifacts from a clean checkout.

- [ ] P5.1 Write the release notes and the known-gaps list
- [ ] P5.2 Tag, publish, and verify from a clean checkout (maintainer approval required)

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 6: Operate and maintain

Parent issue: TBD
Branch: `feature/p6-operate`
Status: planned

Goal: keep the project current: triage incoming ideas, review on a cadence, and close out cleanly.

- [ ] P6.1 Set a review cadence and record the first review

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Detailed Next Steps Notes

1. `P2.3` records what `P2.2`'s build spike produced. **`FVSbc` builds, imports, and runs a 200-year projection.** The patch is now twelve items across nine modified files plus one new file, banked at `notes/reference/fvsbc-patchset.diff.gz` and listed in ADR 0004. Applying it to `ef5fa84` was checked to reproduce the working tree byte for byte. See `notes/reference/fvsbc-build-spike.md`.
2. **The merchantable cubic volume defect is fixed and confirmed against an official reference.** `canada/bc/vols.f` never set `MCFV`, which `base/gradd.f` uses to build `OMCCUR`. The fix reproduces all nine of the reference's nonzero merchantable-volume rows value for value. Four further hypotheses were disproved on the way, and they are recorded. See `notes/reference/fvsbc-smoke-run.md`.
3. **The numbers are now compared against the FVS project's own BC test data.** The first official case matches with the project's exact command and reports zero differing lines across all four stands; the second runs all fifteen stands and twelve of them match in every table. See `notes/reference/fvsbc-validation.md`, and item 8 for what the comparison does not establish.
4. `P2.2`'s prototype is planned on #12 and it stays in `P2.2`. It is bounded by the five `P2.1` contract pages, each of which ends with the items it assigns to `P2.2`: the field order BC reads and the `TREEFMT` injection hazard in `docs/reference/tree-list.rst`; `BECINFO` and the keyword validator in `keywords.rst`; the table list in `outputs.rst`; the variant list in `provenance.rst`; and the height units and the crown-ratio scale in `nemora-ingest.rst`. Four of those are settled by one successful run of a synthetic stand.
5. The patch set is banked in this repository at `notes/reference/fvsbc-patchset.diff.gz`. It is not pushed to `UBC-FRESH/PyFVS`; that is a fork-side change, it needs an approval, and ADR 0004 names it.
6. The seed omits task issue numbers from `templates/project/ROADMAP.md.tmpl`, while `docs/reference/workflow-model.rst` requires them. Reported as `UBC-FRESH/ubc-fresh-dev-workflow` issue #44. Until it is fixed, add the numbers by hand when a task's issue exists.
7. **`P2.3` satisfies Phase 2's third acceptance criterion**, which asks that "the patch the FVS source submodule needs is recorded". The patch is recorded; the fork itself is unmodified and unpushed, as #10's out-of-scope section requires. `P2.2`, the synthetic-data prototype with checks that can fail, is still open, and so is the phase.
8. **The oracle is a 2022 fixture and the project's own checker skips this variant**, so the comparison bounds rather than proves correctness. The `.sum.save` files carry `06-28-2022` in their `-999` headers, the source built here is `ef5fa84` of 2026-09-10, and the checker carries `#FVSbc -- Omit currently 20260226`. The residual is confined to three dense stands of the second case, and it is attributed, not proven, to upstream changes made after the fixture was written.
9. **Proposed adjacent work, not started: promote the comparison into the repository as a test that can fail.** Every comparison so far was an ad hoc script outside the repository, and three of them were buggy in ways that produced false findings. A test that runs the first official case and asserts zero differing lines would have caught them. It needs a task of its own.
10. **Disclosure: thirteen commits labelled `P2.2` delivered `P2.3`'s work**, and a fourteenth corrected the record they produced. `P2.2`'s deliverable is the synthetic-data prototype, so the label is wrong on those commits. They are not rewritten, on the rule in `docs/reference/phase-closeout.rst`. The correct task is recorded retroactively here and on #13.
11. `P2.4` (#14) is proposed, and `ADR 0005` is proposed with it. Three things carry a name that reads as `fvsbc`: this project's package, PyFVS's BC extension submodule, and the FVS variant that the FVS tree calls `FVSbc`. There is no import collision between the first two, which is worth stating because an earlier claim said there was; the problem is that three names and one spelling cannot be told apart in prose. The rename is 161 occurrences across 28 tracked files, of which ten are history and stay as written. **The repository rename is a public change and needs its own approval**, and the published Pages URL changes with it, so any outward link must move in the same change set.
    **Resolved on 2026-10-23: all six subtasks are done, the four acceptance criteria are met, and `#14` is closed.** `ADR 0005` is accepted. Two statements in this proposal turned out to be wrong about the environment and are corrected in the ADR and the changelog: the precedent it cited for the `Renamed by` line, and the claim that the workspace symlink would need repointing.
12. **The reference note filenames keep the old name, deliberately.** `notes/reference/fvsbc-build-spike.md`, `-smoke-run.md`, `-validation.md`, and `fvsbc-patchset.diff.gz` are cited by accepted ADR 0004, by the contract pages, and by these notes. `ADR 0005` says renaming them is its own step rather than a search and replace, and the step resolved to keeping them: renaming a file whose name an accepted ADR cites would strand that citation in a document that is not rewritten. Only the prose inside changed.
13. **Open, and the maintainer's to decide: `ADR 0004` is still `Status: proposed`.** Its task, `P2.3`, is closed, and the ADR satisfied `P2`'s third acceptance criterion by recording the banked patch set. The other three ADRs of its generation read `accepted`, so the status looks like an oversight rather than a deliberate deferral. Marking an ADR accepted is the maintainer's act and I will not do it silently, so it is recorded here.
14. **Open, and a settings change: this project's CI exercises one Python version where the workflow's own quality-gates page states two.** `.github/workflows/ci.yml` has a single `quality` job named `Quality gates`, and branch protection requires exactly that context. The workflow spec's `quality-gates.rst` states that the quality job runs on Python 3.11 **and** 3.12, and its example protection lists `"Quality gates, Python 3.11"` and `"Quality gates, Python 3.12"`. So every gate here has only ever run on the 3.12 interpreter, which is the one `.venv` provides. I noticed it while reading the required status checks during `P2.4` and said in that report that I would record it; this is the record, added a move later than it should have been. Changing CI or branch protection is a settings change and needs the maintainer's approval, so nothing has been changed.
15. **Open, from the first synthetic run, and each needs a decision before subtask 7 can close.** Recorded with its evidence in `notes/reference/synthetic-run.md`. **(a)** The output database holds `FVS_Cases` and `FVS_Error` only; `FVS_Summary_Metric`, `FVS_Compute`, and `FVS_TreeList_Metric` need a `DATABASE` output block, and PyFVS already occupies that block, so a key's own is refused as used in the wrong context. The summary is available in memory instead. Which route the reader takes — the database, or the in-memory frame plus the database for cases and errors — is a decision, not a detail. **(b)** `FVS_Error` holds warnings as well as errors, so the output contract's "assert `FVS_Error` is empty" has to become "holds no error", or the fixture needs a BC-valid forest code. **(c)** The height units and the crown-ratio scale are still unverified in both directions for the target side, and each needs a controlled run that varies one input and watches what changes; the first run could not settle either, because `SITECODE FD 100` dominates the height it computed.
    **Resolved on 2026-10-23.** **(a)** and **(b)** are decided and implemented: the reader takes the database for `FVS_Cases` and `FVS_Error`, takes the summary from PyFVS's in-memory frame, and fails a run on a row of severity `ERROR` rather than on a non-empty `FVS_Error`; the output contract says so at rules 1, 2, and 5, and its "Not verified" list is answered at three of four points. **(c)** remains open, and needs the two controlled runs.
    **Resolved in full on 2026-10-23.** **(c)** is settled too: the height units are metres on both sides, proved by a run that varied `live_ht` alone and moved the summary's `top_ht` by the metre-to-foot factor, and the crown-ratio field is a crown class 1 to 9 that FVS expands to a percent by `n*10-5`, which `base/intree.f` states in its own comment. Both contract pages carry them, and the runs are in `notes/reference/synthetic-run.md`. Nothing in this note is open.
