# Phase close-out report: P2 Contracts and prototype

Phase: P2 Contracts and prototype
Parent issue: #10
Pull request: #16, `feature/p2-contracts-prototype` into `main`
Evidence head: `fc5cef2`, the head that the gates in section 3 cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-23
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #16, and delete the branch `feature/p2-contracts-prototype`.
2. Close parent issue #10 with a closeout comment that cites the merge commit.
3. Launch `P3`, **after approving `P3`'s plan**: create its parent issue, its branch, its child issues
   as sub-issues, and its roadmap subtask lines, then start its first task. `P3` is `planned` with a
   placeholder task and no plan, and `workflow-model.rst` requires a plan before a phase is activated,
   so the plan is `P3`'s first deliverable and not the agent's unilateral choice. Section 6 states the
   proposed scope and the recommended default for each open choice.

Settings changes, each with its exact command. Each one runs only after its own approval.

- **Recommended, not run: the CI quality matrix.** `.github/workflows/ci.yml` runs one `quality` job on
  Python 3.12, where `docs/reference/quality-gates.rst` requires 3.11 and 3.12 and names the contexts
  `Quality gates, Python 3.11` and `Quality gates, Python 3.12`. The change is two edits: the workflow
  file's matrix, and the required checks, which is a branch-protection change:
  `gh api -X PATCH repos/UBC-FRESH/fresh-fvsbc/branches/main/protection/required_status_checks -f 'contexts[]=Quality gates, Python 3.11' -f 'contexts[]=Quality gates, Python 3.12'`.
  **Default: approve it**, because the phase's own fourth acceptance criterion has never been checked on
  the 3.11 interpreter the specification requires.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| `docs/` states the interfaces and the data contracts: the tree-list input, the keyword set, the parsed outputs, and the provenance record | `docs/reference/{tree-list,keywords,outputs,provenance,nemora-ingest}.rst`, each naming the FVS commit it was read from | met |
| A prototype runs on synthetic data and exercises each contract, with checks that can fail | `src/fresh_fvsbc/{treelist,keywords,nemora,outputs,provenance}.py` with their test modules; mutation evidence per task in `CHANGE_LOG.md`; a real BC run on a tree list this project wrote, in `notes/reference/synthetic-run.md` | met |
| The build question in ADR 0001 is answered with evidence: either `bc` builds, or the patch the FVS source submodule needs is recorded | `notes/adr/0004-the-fvsbc-build-recipe.md`; `notes/reference/fvsbc-patchset.diff.gz`, twelve items, verified to reproduce the working tree from `ef5fa84` | met |
| `python scripts/dashboard.py` exits zero on the head commit of the phase branch | green on `fc5cef2`; six gates | **met on 3.12 only.** The specification requires the quality job on 3.11 and 3.12, and this project's CI runs one interpreter. Stated as a limit, and the fix is the approved settings change above |

## 2. Workflow compliance

- **Parent issue before the branch.** `#10` was created 2026-10-21T07:41Z; the branch's first commit is
  `a4ad4ea` of the same day, "P2 activate the contracts and prototype phase".
- **Branch from `main`.** Merge-base `cbcadf3`, the head of `main` at `P1`'s close-out.
- **Commit messages that start with a task ID.** 40 of the 41 commits on the branch since `main`. The
  one that does not starts with the phase ID, and it is the phase activation.
- **Gates for each commit.** Section 3.
- **Roadmap and changelog in step.** Both changed in the same change set as the work they record, for
  every task. Two exceptions, both disclosed in section 5: the roadmap's subtask level and the focused
  plan were written after the work, and the roadmap's detail had grown past what the roadmap should
  carry before it was moved to `notes/p2-contracts-and-prototype.md`.
- **Child issues closed with closeout evidence.** `#11`, `#13` and `#14`, each with a closeout comment
  naming its commits. `#12` and `#15` remain open, and section 5 records why.
- **Approval gates.** The repository rename in `P2.4` was approved before it ran. Pages was approved and
  executed in `P0`'s close-out, and branch protection in `P1`'s. No other setting was touched in this
  phase. Nothing in this phase published outside the repository.

## 3. Gate evidence

- **On the evidence head `fc5cef2`:** all six dashboard gates are green — lint, format, strict types,
  tests with the coverage gate, the workflow validator, and the docs build with warnings as errors.
- **Per commit:** every commit's changelog entry records the dashboard result for its change set.
  **Those records are the implementer's claims, not independent evidence**, and this report does not
  present them as evidence. The independent checks for this phase are the CI run on pull request #16
  and the Verifier's run, which `P2.5`'s last subtask requires and which reads only the committed
  artefacts.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| none before this pull request | — | — | CI triggers on a pull request to `main` and on a push to `main`, so no phase branch has ever had a run. The runs that follow pull request #16 are this phase's CI evidence, and they are posted on it |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| **A whole task's work ran with no child issue.** Thirteen commits labelled `P2.2` delivered `P2.3`'s work, and `#13` was created after it; twenty-four commits carry the `P2.2` label | The build spike was treated as an unplanned investigation rather than as a task, so the scaffold rule in `AGENTS.md` was not applied | The commits are not rewritten. `CHANGE_LOG.md` and `notes/p2-contracts-and-prototype.md` disclose it, `#13` was created retroactively, and the rule is now applied: no commit before its child issue exists |
| **The roadmap carried no subtask level, and no focused plan existed in `notes/`** | The third level of the three-level structure was never written down, and the detail went into the issue body and into fifteen prose items in the roadmap instead | `notes/p2-contracts-and-prototype.md` written, and the roadmap's `P2` block carries 39 indented subtask lines (`c0ba0c9`) |
| **`README.md` claimed no variant had been built** for two days and six commits after the variant built, contradicting the roadmap and violating `P0`'s own acceptance criterion | Nothing updated the front door when the build succeeded, and the `P2.4` rename substituted the new name into the stale sentence | Corrected (`c0ba0c9`); the README now points at ADR 0004, the patch set, and the validation note |
| **Parent issue `#10`'s child checklist listed two of its four children**, its scope named two tasks, and no scope-change comment existed | `P2.3` and `P2.4` were added without reconciling the parent body | One body edit and one scope-change comment (`c0ba0c9`), now listing five children and five tasks |
| **Closed task issues carry a stale `Status:` and an unfilled `Completion metadata:`** — `#11` reads `active` and `#14` reads `planned`, both closed | The closeout comment was posted but the body was not updated, and `#12`'s status used a value no template defines | Corrected in this change set, with the commit, the verification, and pull request #16 |
| **Four claims published on 2026-10-21 were wrong**, and three were retracted only in conversation | They came from ad hoc comparison scripts outside the repository, never checked against a known-good case; three failed on `'INF'` parsed as a float or on a column misalignment | Retracted in the files. The standing proposal is to promote the comparison into a repository test that can fail |
| **A false citation was published in an accepted ADR, and the accepted ADR was then edited** | `ADR 0005` claimed a precedent that does not exist in this repository, and its body was corrected after acceptance | Corrected and disclosed, but **the correction should have been a new ADR**, since `notes/README.md` says an accepted ADR is superseded rather than rewritten. The agent applied that rule for the rest of the phase |
| **A test that could not fail** | The output reader limited a severity search to a message's leading tokens, which is unobservable because first-match-wins gives the same answer | The limit was removed and the test rewritten (`dcb9e12`) |
| **The mutation harness can report a pass for a mutation that never applied** | A `ruff format` run moved the anchor the mutation targeted | The harness now asserts its anchor is unique, and the mutation is redone when it is not (`dcb9e12`, `f1a974f`) |
| **`ADR 0004` is still `Status: proposed`**, its `Context` contradicts a later paragraph, and its `Issues:` field names `#12` where the roadmap assigns it to `P2.3` | The status was never brought to `accepted` after `P2.3` closed | **Not the agent's act.** Recorded in `ROADMAP.md` and in the plan's proposal 3, with a recommended default |
| **The CI quality matrix runs one Python version** where the specification requires two | The seeded `ci.yml` was never changed, and branch protection matches it | **Not run.** Recorded with its exact command in the Recommendation, and the criterion above is marked as met with that limit |
| **The project had no roles page and no model log, and no reviewer was ever named** | Neither the agent nor the workflow audit named the gap until the maintainer asked who the reviewers were | `docs/agents/roles-and-models.rst` added (`bc793cb`), with both log rows marked `Unproven` |
| **The workflow revision was unpinned** | `AGENTS.md` named the workflow with no path, URL, or revision | Pinned to `93b5cd9` of 2026-10-13 (`fc5cef2`), and the seed's template defect filed upstream as `ubc-fresh-dev-workflow#45` |
| **The seed's roadmap template omits task issue numbers** where `workflow-model.rst` requires them | A defect in the seed | Reported upstream as `ubc-fresh-dev-workflow#44` |

## 6. Next phase

**`P3` Build.** Its goal, from `ROADMAP.md`, is to implement the agreed scope, one task at a time. It is
`planned` with a placeholder task and a placeholder criterion, and no plan.

**Recommended default for each open choice, with its reason.**

1. **Write `P3`'s plan before activating it.** Reason: `workflow-model.rst` requires a plan before a
   phase is activated, and this phase's central failure was having none.
2. **Proposed scope.** The BC layer proper: the public API over the five prototype modules; the run
   orchestration that assembles a keyword set, writes a tree list, drives FVS, and returns outputs with
   provenance; the command-line entry point; and the build wiring that makes the pinned fork's BC
   variant reproducible from a clean checkout. Reason: `notes/scope.md` and ADRs 0001 to 0003 bound it,
   and the prototype is validated against the FVS project's own data.
3. **Recommended: carry `P2.2`'s one open subtask into `P3` as a task** — building the standalone
   `FVSbc` executable, which is the only route to `FVS_Compute` and `FVS_Summary_Metric`. Reason: it is
   a limitation with a known remedy, not unfinished work, and it is out of `P2`'s scope.
4. **Recommended: promote the oracle comparison into a repository test that can fail.** Reason: every
   comparison so far was an ad hoc script outside the repository, and three were buggy in ways that
   produced published false findings.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.

## Verification before approval

`P2.5`'s last subtask requires a **separate Verifier session** to check every claim in this report
against its evidence, reading only the committed artefacts, and to post its findings on `#15`. The
report is not ready for approval until those findings are attached to it.
