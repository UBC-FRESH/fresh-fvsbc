# Phase close-out report: P0 Bootstrap

Phase: P0 Bootstrap
Parent issue: #1
Pull request: #4, `feature/p0-bootstrap` into `main`
Evidence head: `657390c`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-21
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #4, and delete the branch `feature/p0-bootstrap`.
2. Close parent issue #1 with a closeout comment that cites the merge commit.
3. Launch P1 (Scope and design): create its branch, set the phase statuses in `ROADMAP.md`, create its child issues as sub-issues, and start `P1.1`.

Settings changes, each with its exact command. Each one runs only after its own approval.

- Enable GitHub Pages with the GitHub Actions build type, so the `Docs` workflow stops failing on `main`:

  ```bash
  gh api -X POST repos/UBC-FRESH/fvsbc/pages -f build_type=workflow
  ```

  Cause and evidence: section 5, deviation 1.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| `AGENTS.md` states the fvsbc-specific rules, and links the shared workflow rules instead of copying them | `d21d571`. The "Project-specific rules" section holds six rules, each with its reason. The shared rules are unchanged from the seed | met |
| `README.md` describes `fvsbc`, its place in the pipeline, and its status, and claims nothing the roadmap has not recorded | `d21d571`. `README.md` states that `fvsbc` does not build `FVSbc` yet, matching `ROADMAP.md`, where P0 is active and P1 to P6 are planned | met |
| `python scripts/dashboard.py` exits zero on the head commit | `657390c`, six gates green; CI run 39559038099 | met |

## 2. Workflow compliance

- Parent issue before the branch: parent issue #1 was created at 2026-10-21T06:56:29Z. The branch `feature/p0-bootstrap` was created after it. Met.
- Branch from `main`: merge-base `9be3d7a`. Met.
- Commit messages that start with task IDs: 2 of 3. `P0.1` and `P0.2` do. `P0 activate the bootstrap phase` starts with the phase ID. See deviation 3.
- Gates for each commit: section 3.
- Roadmap and changelog in step: `14e3c71` activated P0 in `ROADMAP.md`. `657390c` checked P0.1 and P0.2, filled in the acceptance criteria, and recorded the dashboard result in `CHANGE_LOG.md`. Met.
- Child issues closed with closeout evidence: #2 and #3 are still open. They close with this phase.
- Approval gates: repository creation was approved by the maintainer. Label creation, the issues, and the branch were covered by the same instruction to continue. Enabling Pages is requested above and has not been run.

## 3. Gate evidence

| Commit | Gates | Result |
| --- | --- | --- |
| `9be3d7a` | local: `python scripts/check_workflow.py` | 0 errors, 3 warnings |
| `14e3c71` | local: `python scripts/check_workflow.py` | 0 errors, 3 warnings |
| `d21d571` | local: `python scripts/check_workflow.py` | 0 errors, 3 warnings |
| `657390c` | local: full dashboard, all six gates | GREEN, exit 0 |

The three warnings are `LICENSE`, `CODE_OF_CONDUCT.md`, and `CITATION.cff`, which the seed reports as recommended but missing.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39559038099 | `657390c` | success | `CI` on the pull request: Pre-commit parity, Quality gates, and Green dashboard summary all pass |
| 39558508047 | `9be3d7a` | success | `CI` on `main` |
| 39558507848 | `9be3d7a` | failure | `Docs` on `main`. The build job passes; the deploy job fails. See deviation 1 |
| 39558436633 | `3f0552b` | success | `CI` on `main` |
| 39558436657 | `3f0552b` | failure | `Docs` on `main`. Same cause as deviation 1 |

The `Docs` workflow triggers on push to `main` only, so the pull request does not run it. The pull request is green.

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| 1. The `Docs` workflow fails on every push to `main` | GitHub Pages is not enabled for `UBC-FRESH/fvsbc`. `gh api repos/UBC-FRESH/fvsbc/pages` returns 404. The `build` job passes; `actions/deploy-pages` fails with `Failed to create deployment (status: 404)`. The seed repository has Pages enabled with `build_type: workflow` | Requested in the Recommendation. Not run, because enabling Pages is a settings change and needs the maintainer's approval |
| 2. ADRs 0001, 0002, and 0003 were committed directly to `main` before P0 was activated | The repository did not exist when the decisions were made, and no parent issue existed to attach them to | Accepted as pre-phase work. The seed's own first commit carries no task ID for the same reason |
| 3. The commit `P0 activate the bootstrap phase` starts with a phase ID, not a task ID | Activating a phase is not itself a roadmap task | Recorded here. No history rewrite |
| 4. ADR 0002 was edited in place rather than superseded | It was factually wrong about `nemora`, and it was still `proposed` | The seed permits rewriting a proposed ADR. Corrected in `3f0552b` |
| 5. The `phase` and `task` labels did not exist | The seed ships the issue templates but not the labels those templates declare | Created with `gh label create`. Recorded in `CHANGE_LOG.md` |

## 6. Next phase

P1 (Scope and design). Goal: state the question, the users, the scope, and the out-of-scope items, and record the first decisions as ADRs.

Tasks:

- `P1.1` Write the problem statement and scope in `notes/`.
- `P1.2` Record the first design decisions as ADRs in `notes/adr/`.

Recommended defaults for the open choices, each with its reason:

- **Accept ADRs 0001 to 0003 as part of `P1.2`.** They are `proposed`, and nothing has contradicted them. Accepting them closes the design loop without new work.
- **Defer the build-recipe ADR until a spike attempts the build.** Whether adding `bc` to the PyFVS variant matrix is sufficient, or the FVS source submodule needs a patch, is currently unknown. ADR 0001 records it as unverified. An ADR written before the spike would rest on expectation rather than evidence.
- **Settle the licence in `P1.1`.** The repository is public and has no licence, so by default it grants no rights to use it. This blocks a release and should not wait for P5.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
