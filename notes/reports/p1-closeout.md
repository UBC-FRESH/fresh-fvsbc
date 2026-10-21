# Phase close-out report: P1 Scope and design

Phase: P1 Scope and design
Parent issue: #5
Pull request: #9, `feature/p1-scope-design` into `main`
Evidence head: `5953a40`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-21
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #9, and delete the branch `feature/p1-scope-design`. Then confirm that the squash commit's tree equals the approved head, as `phase-closeout.rst` requires.
2. Close parent issue #5 with a closeout comment that cites the merge commit. Child issues #6, #7, and #8 are already closed, each with a closeout comment.
3. Launch P2 (Contracts and prototype): create its branch, set the phase statuses in `ROADMAP.md`, create its child issues as sub-issues, and start `P2.1`.
4. After the merge, re-run `gh api repos/UBC-FRESH/fvsbc/license -q .license.spdx_id` and record that it returns `MIT`. The check reads the default branch, so it cannot pass before the merge.
5. Open an issue on `UBC-FRESH/ubc-fresh-dev-workflow` for the seed defect in deviation 6: `templates/project/ROADMAP.md.tmpl` omits the task issue numbers that `docs/reference/workflow-model.rst` requires. The RTFM protocol requires the gap to be reported.

Settings changes, each with its exact command. Each one runs only after its own approval.

- None. Branch protection on `main` was set during this phase, with the maintainer's approval. It requires
  `Quality gates`, `Green dashboard summary`, and `Pre-commit parity`, with `strict` enabled, linear
  history required, and force-pushes and deletions denied. Administrators are exempt.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| `LICENSE` is MIT, and the package metadata agrees with it | `a027f85`. `LICENSE` is 1070 bytes, sha `d3c9d40`. `pyproject.toml` sets `license = "MIT"`; `README.md` agrees | met, with the API check deferred to after the merge |
| `notes/` states the problem, the users, the scope, and the out-of-scope items | `e35b288`, `notes/scope.md`. Ten out-of-scope items, each with a reason | met |
| Every ADR is accepted or superseded, and any new decision is recorded | `9bff84e`. ADRs 0001, 0002, and 0003 are `accepted`. No ADR is left `proposed`; `0000-template.md` carries `proposed` because it is the template | met |
| `python scripts/dashboard.py` exits zero on the head commit | `9bff84e`, six gates green; CI run 39561248776 | met |

## 2. Workflow compliance

- Parent issue before the branch: parent issue #5 was created at 2026-10-21T07:19Z, before the branch `feature/p1-scope-design`. Met.
- Branch from `main`: merge-base `9c576f3`, the P0 squash merge. Met.
- Commit messages that start with task IDs: 3 of 4. `P1.1`, `P1.2`, and `P1.3` do. `P1 activate the scope and design phase` starts with the phase ID. See deviation 1.
- Gates for each commit: section 3.
- Roadmap and changelog in step: `e7cc81d` activated P1 and marked P0 complete; each task commit checked its own roadmap box and appended its own changelog entry. Met.
- Child issues closed with closeout evidence: #6, #7, and #8 are closed, each with a closeout comment that names its commit, its verification, and the pages it changed. See deviation 8.
- Approval gates: the Pages settings change was approved and executed during P0's close-out. Branch protection was approved and executed during this phase. No other settings were touched.

## 3. Gate evidence

| Commit | Gates | Result |
| --- | --- | --- |
| `e7cc81d` | local: `python scripts/check_workflow.py` | 0 errors, 3 warnings |
| `a027f85` | local: full dashboard, six gates | GREEN, exit 0 |
| `e35b288` | local: full dashboard, six gates | GREEN, exit 0 |
| `9bff84e` | local: full dashboard, six gates | GREEN, exit 0 |

The three warnings are `CODE_OF_CONDUCT.md` and `CITATION.cff`, which the seed reports as recommended but missing, plus `LICENSE` before `a027f85` added it. After `a027f85` the validator reports two warnings.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39562155577 | `5953a40` | success | `CI` on the pull request, on the corrections in deviations 5 to 12 |
| 39561405782 | `15f3ee2` | success | `CI` on the pull request, on the first version of this report |
| 39561248776 | `9bff84e` | success | `CI` on the pull request: Quality gates, Green dashboard summary, and Pre-commit parity all pass |
| 39561170450 | `e35b288` | success | `CI` on the pull request |
| 39560465154 | `a027f85` | success | `CI` on the pull request |

The pull request reports `mergeable_state: clean`, with all three required checks passing under the new branch protection.

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| 1. P1's task order differs from the seeded order, and the seeded tasks were renamed | The maintainer asked for the licence during P0's close-out, so the licence became `P1.1` and the problem statement and ADRs shifted to `P1.2` and `P1.3` | Recorded in `e7cc81d`. The P0 close-out report still refers to accepting the ADRs as "`P1.2`"; the actual task is `P1.3`. The report is evidence of what was approved and is not rewritten |
| 2. ADR 0001 was edited rather than superseded | Its "Consequences" named the follow-on decisions as unwritten, but ADR 0002 and ADR 0003 existed. An accepted ADR is never rewritten, so the fix had to land before acceptance | Corrected in `9bff84e`, in the same commit that accepted it |
| 3. The licence acceptance criterion cannot be checked before the merge | `gh api repos/UBC-FRESH/fvsbc/license` reads the default branch, so it returns 404 while `LICENSE` lives on the phase branch | Requested in the Recommendation, step 4. The file is confirmed present on the branch, sha `d3c9d40` |
| 4. `pyproject.toml` gained a `[project]` table without a `[build-system]`, and the version is `0.0.0` | The task is licence and metadata alignment. A build backend and a real version are packaging work | Recorded here and in the pull request. Deferred to the packaging phase |
| 5. Pull request titles and bodies did not follow `git-conventions.rst` | The page was not read before the pull requests were opened. Its title form is `P<n> <phase name> (#<parent>)`, and its body starts with `Part of #<parent>` | Corrected on #4 and #9 in `5953a40`'s change set. The REST API was used, because `gh pr edit` fails with a Projects-classic GraphQL deprecation error |
| 6. Roadmap task lines omitted the issue numbers, and P1's status was `active` rather than `pr-open` | `workflow-model.rst` requires `P<n>.<m> <task name> (#<issue>)`, and defines `pr-open` as "every task is done, the pull request is open, and the report is queued". The seed template `templates/project/ROADMAP.md.tmpl` omits the numbers, and the template was followed instead of the reference page | Corrected in `5953a40`. The template defect is reported to `UBC-FRESH/ubc-fresh-dev-workflow`, per the RTFM protocol |
| 7. Issue body files were not run through `check_workflow.py --files` before posting | `issue-standard.rst` requires it. The flag exists and works | Applied to every body posted after the correction, with the command and its exit status recorded |
| 8. Child issues #6, #7, and #8 were left open when the phase was queued | `guides/first-project.rst` closes each child when its task completes, and `github-mapping.rst` says a child closes after its closeout comment is posted. The parent closes after the merge | Closed with closeout comments naming each commit, its verification, and the pages it changed |
| 9. The local branch `feature/p0-bootstrap` survived P0's merge | `phase-closeout.rst` deletes the branch locally and on its remote. The remote deletion succeeded; the local one was missed | Deleted locally with `git branch -d`, which succeeded because the branch still tracked its remote |
| 10. The repository was created `--public` immediately | `guides/first-project.rst` creates it `--private`, and switches to `--public` after the maintainer has reviewed it. The command was proposed before the spec was read. The maintainer approved the command as proposed | Not reversible without a settings change. `fvsbc` stays public. Disclosed here |
| 11. Branch protection included `required_linear_history` | The command in `quality-gates.rst` does not name it. It was added as a sensible default for a squash-merge workflow | Disclosed. It is stricter than the spec, not looser |
| 12. The P0 report's red `Docs` gate was never refreshed to name the commit that fixed it | `phase-closeout.rst` says a red gate is a deviation until the report names the commit that fixed it. The gate was fixed after the P0 merge, and the P0 report had already been approved | P0 is merged and its report is closed evidence. Recorded here instead |

Deviations 5 to 9 share one cause: the spec pages that govern them were not read before the work. A full
read of `docs/` followed, and these are its findings.

## 6. Next phase

P2 (Contracts and prototype). Goal: define the interfaces and data contracts, then build the smallest prototype that exercises them.

Tasks:

- `P2.1` Define the interface and data contracts in `docs/`.
- `P2.2` Build a prototype that exercises the contracts on synthetic data.

Recommended defaults for the open choices, each with its reason:

- **Make the build spike the first act of `P2.2`.** ADR 0001 records one central uncertainty: whether adding `bc` to the PyFVS variant matrix is sufficient, or the FVS source submodule needs a patch. Every later phase depends on the answer, and it is the cheapest risk to retire.
- **Write the build-recipe ADR only after the spike.** The P1.3 scope excluded it deliberately. An ADR written before the evidence would rest on expectation.
- **Define the tree-list contract against `BC.trf` and the species table, not against a guess.** Both are readable in the pinned fork without a build, so `P2.1` can be specific before `P2.2` runs.
- **Record the two remaining validator warnings in P2.1.** `CODE_OF_CONDUCT.md` and `CITATION.cff` are still missing, and the seed expects both.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
