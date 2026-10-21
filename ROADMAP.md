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

1. `P2.2`'s build spike is done, and **`FVSbc` builds and imports** with a nine-line patch set across four files plus one new file. `fvs_step` exposes `fvs_init`, `fvs_grow`, and `fvs_end`. See `notes/reference/fvsbc-build-spike.md` and ADR 0004.
2. Nothing has been run. The module imports, which is not evidence that it computes correctly. The next move is a smoke run on a synthetic stand, which would also close the open questions in the tree-list, output, and `nemora` contracts.
3. The prototype half of `P2.2` is unblocked. Whether it lands in `P2.2` or moves to `P3` is a scope decision.
4. The patch set lives in the fork and is not pushed. Pushing it to `UBC-FRESH/PyFVS` needs an approval, and it is named in ADR 0004.
5. The seed omits task issue numbers from `templates/project/ROADMAP.md.tmpl`, while `docs/reference/workflow-model.rst` requires them. Reported as `UBC-FRESH/ubc-fresh-dev-workflow` issue #44. Until it is fixed, add the numbers by hand when a task's issue exists.
