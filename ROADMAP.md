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

- `AGENTS.md` states the fvsbc-specific rules, and links the shared workflow rules instead of copying them.
- `README.md` describes `fvsbc`, its place in the pipeline, and its status, and claims nothing the roadmap has not recorded.
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
