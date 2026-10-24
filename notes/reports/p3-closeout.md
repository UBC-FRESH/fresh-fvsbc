# Phase close-out report: P3 Build

Phase: P3 Build
Parent issue: #17
Pull request: #24, `feature/p3-build` into `main`, opened as a draft so the matrix could be verified
Evidence head: `ed03085`, the head that the gates in section 3 cover
Report commit: the commit that adds this revision of the report. Its CI run is posted on the pull request.
Date: 2026-10-24
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. **Amend the phase's third acceptance criterion**, which `P3.2` disproved rather than met. Replace
   this line in `ROADMAP.md`:

   ```text
   - The standalone executable writes `FVS_Compute` and `FVS_Summary_Metric`.
   ```

   with:

   ```text
   - **Withdrawn by `P3.2` (#19), which resolved it by explanation (ADR 0009):** `FVS_Compute` holds the
     caller's `COMPUTE` expressions rather than an output table, and this project defines none;
     `FVS_Summary_Metric` was available in memory all along. The standalone executable was built from
     upstream `main` and is proven and not adopted.
   ```

   **This is the maintainer's yardstick, not the agent's**, which is why it is proposed here rather than
   edited in this change set. Until it is approved, section 1 records the criterion as not met.
2. Mark pull request #24 ready for review: `gh pr ready 24`.
3. Squash-merge pull request #24, and delete the branch `feature/p3-build`:
   `gh pr merge 24 --squash --delete-branch`.
4. Close parent issue #17 with a closeout comment that cites the merge commit.
5. Launch `P4`, after approving its scope in section 6: create its parent issue, its branch
   `feature/p4-verify`, its child issues as sub-issues, and its roadmap subtask lines, then start its
   first task.

**Settings changes: none.** The one settings change this phase made was branch protection, in `P3.1`
(#18), approved before it ran and read back here:

```json
{"contexts":["Green dashboard summary","Pre-commit parity","Quality gates, Python 3.11","Quality gates, Python 3.12"],"linear":true}
```

No tag, release, external account, or visibility change is proposed. Two external issues were filed
before this phase, in `P2`, and remain open: `ubc-fresh-dev-workflow` #44, #45 and #46.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The quality job runs on Python 3.11 and 3.12, and protection requires all four contexts the workflow spec names | `.github/workflows/ci.yml` runs the quality job on a `python-version` matrix of `3.11` and `3.12`; the protection read-back above lists the four contexts and `required_linear_history: true`; run `40111537678` on the evidence head reports "Quality gates, Python 3.11" and "Quality gates, Python 3.12" both successful | met |
| The pinned fork's BC variant builds from a clean checkout in CI | The `build-variant` job clones `UBC-FRESH/PyFVS` at `e95172b`, initialises its FVS source submodule, applies both banked patch sets with `git apply --check` first, builds with `-Dfvsvariants=bc`, and imports `pyfvs.fvsbc`. Run `40073616342` succeeds, and its log shows the import step | met |
| The standalone executable writes `FVS_Compute` and `FVS_Summary_Metric` | `P3.2` (#19) closed **resolved by explanation**: `FVS_Compute` is the `COMPUTE`-expression table, and the official case's 160 rows are 4 stands x 40 periods x 3 expressions, none of which this project defines; `FVS_Summary_Metric` returns 21 rows through `FVS.summary` by both routes. The executable was built from upstream `main` and is proven and not adopted (ADR 0008, ADR 0009) | **not met, and the criterion is a false requirement.** Recommendation 1 withdraws it. `docs/reference/outputs.rst` records the answer on the contract page |
| The mutation harness reproduces a named mutation failing a named test | `scripts/mutation_check.py` carries 23 mutations; `23 of 23 mutations caught` on the evidence head. An anchor that does not match exits non-zero and says so, which happened twice in this phase and is recorded in section 5 | met |
| One synthetic run through the public API returns outputs carrying provenance | `tests/test_run.py::test_a_synthetic_stand_runs_end_to_end` passes in the build job, the only job with the extension: run `40073616342`, `26 passed, 1 skipped`; `notes/reference/synthetic-run.md` records the run, and `notes/reference/synthetic-run.md`'s later section records the same path through the command | met |
| The command-line entry point runs a case end to end | `notes/reference/synthetic-run.md` records the invocation, exit status `0`, the printed report, and the seven files it wrote. `src/fresh_fvsbc/cli.py` is at 100 percent coverage | met |
| `python scripts/dashboard.py` exits zero on both Python versions | Green on the evidence head, locally. In CI the dashboard **script** runs in the `dashboard` job on 3.12 only; on 3.11 the six gates it wraps run individually in the quality job and pass | **met in substance, not in letter.** The gates pass on both versions; the script is run on one. Section 6 proposes the protection-safe fix, which cannot be made here without renaming a required context |

## 2. Workflow compliance

- **Parent issue before the branch.** `#17` was created 2026-10-23T23:29:26Z; the branch's first commit
  `cfb6b1d` is 2026-10-23T23:30:20Z.
- **Plan before the work.** `notes/p3-build.md` was written and committed in `cfb6b1d`, the activation
  commit, and each child issue's plan comment was posted before that task's first code commit.
- **Branch from `main`.** Merge-base `6e99a41`, the squash-merge of `P2`.
- **Commit messages that start with a task ID.** 21 of the 22 commits on the branch. The one that does
  not is `ed03085`, which closes `P2.2` (#12) and starts with a verb. It is disclosed in section 5.
- **Gates for each commit.** Section 3.
- **Roadmap and changelog in step.** Each task's change set carries its roadmap tick and its changelog
  entry. **No mechanical test exists for "same change set"**, so this is a claim about the record
  rather than a verified fact.
- **Child issues closed with closeout evidence.** `#18` through `#23` each carry a closeout comment
  naming the commit, the CI run, and the verification. `#12` was closed in this phase, late; section 5
  records it.
- **Approval gates.** The branch-protection change in `P3.1` was approved before it ran. The `P3.3`
  before `P3.2` reorder was approved. No other settings change, publication, or private data was
  touched. The approval dialogues are not committed, so the reports and the issues are the record.

## 3. Gate evidence

- **On the evidence head `ed03085`:** all six dashboard gates green, run locally in this session, and
  CI run `40111537678` succeeds on that exact head.
- **Per commit:** every commit's changelog entry records the dashboard result for its change set.
  **Those records are the implementer's claims, not independent evidence**, and this report does not
  present them as evidence.
- **The mutation harness** runs inside the quality job, so a stale anchor fails CI rather than being
  found by hand. It caught two in this phase, both in section 5.

## 4. CI evidence

**Twenty runs on the branch: seventeen success, one failure, two cancelled.** Every run is a
`pull_request` run, because CI runs on pull requests and pushes to `main` only; #24 was opened as a
draft early so the matrix could be verified against a real pull request rather than in the abstract.

The one failure is the first run of the build job, and it is the most useful row in the table:

- `40040321924` on `594eab6`, **failure**, in `Build the BC variant` with `error:
  metadata-generation-failed`. The recipe needed the PyFVS-repository patch set, which had never been
  banked; `2e55f10` banked it, and the job passed from `67edefb` on. **This is the failure that made
  the job honest**: the recipe in ADR 0004 named two patch sets and the repository carried one.
- `40040548859` on `2e55f10` and `40040604602` on `86e29e8`, **cancelled** within a minute of starting.
  Both commits were superseded by `67edefb` within seconds of each other. The workflow declares no
  `concurrency` block, so the cancellation was not the workflow's doing, and **the record does not say
  who cancelled them.** They are counted as neither evidence nor failure.

| Run ID | Head commit | Conclusion | Task |
| --- | --- | --- | --- |
| `40111537678` | `ed03085` | success | the evidence head |
| `40073789906` | `b6e789d` | success | `P3.6` roadmap |
| `40073616342` | `4a7a9ed` | success | `P3.6`, the build job runs the end-to-end test |
| `40072653313` | `e863b5d` | success | `P3.5` roadmap |
| `40072469117` | `b6f0bc1` | success | `P3.5`, the first end-to-end run in CI |
| `40070672108` | `5af11f3` | success | `P3.4` roadmap |
| `40070640710` | `2a9b024` | success | `P3.4` part two |
| `40069315166` | `ba19998` | success | `P3.4` part one |
| `40068086642` | `3dec72e` | success | `P3.4`'s `BECINFO` answer |
| `40067779962` | `ae2d909` | success | `P3.2` closeout |
| `40067725235` | `984d490` | success | `P3.2` resolution |
| `40066238799` | `fdbdc29` | success | `P3.2` banked standalone |
| `40043915379` | `66634d8` | success | `P3.2` first record |
| `40043248691` | `2b1964d` | success | `P3.3` mutation harness |
| `40042127787` | `5c3c0ba` | success | `P3.1` closeout |
| `40040787779` | `13dd18a` | success | `P3.1` subtasks |
| `40040638048` | `67edefb` | success | `P3.1`, the build job's first green run |
| `40040604602` | `86e29e8` | cancelled | superseded within seconds |
| `40040548859` | `2e55f10` | cancelled | superseded within seconds |
| `40040321924` | `594eab6` | failure | the build job, `metadata-generation-failed` |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| **A phase acceptance criterion was a false requirement.** "The standalone executable writes `FVS_Compute` and `FVS_Summary_Metric`" cannot be met, because `FVS_Compute` is the `COMPUTE`-expression table and the summary was reachable in memory all along | The criterion was written from the output contract's table list, before the tables' contents were known | `P3.2` (#19) resolved it by explanation and ADR 0009 records the decision. The criterion is not edited in this change set, because the yardstick is the maintainer's; recommendation 1 carries the exact amendment |
| **`P3.3` ran before `P3.2`**, which is not the numbered order | The harness is the tool every remaining task's tests are checked with, and `P2` produced both a vacuous test and a mutation that never applied | Maintainer-approved before it ran, recorded in `notes/p3-build.md`'s task-order section, and the order paid for itself: the harness caught two stale anchors and one mis-pointed mutation later in the phase |
| **`render_keyword` was wrong for every keyword**, and the keyword contract had no record of the layout. It wrote each parameter on its own line; `base/keyrdr.f` reads `KEYWRD=RECORD(1:8)` and `KARD(I)=RECORD(J:J+9)`, so parameters are ten-column fields of the same record. An eleven-keyword set produced 26 `FVS01 ERROR: INVALID KEYWORD WAS SPECIFIED` rows | The module's tests asserted the shape it produced rather than the shape FVS reads, and nothing had ever fed a real key file | Found by the first run through the orchestration in `P3.5`, fixed in `b6f0bc1`, disclosed in the changelog, and `docs/reference/keywords.rst` now records the layout with the Fortran cited. **The defect dates from `P2` and was not introduced here** |
| **`pandas` became the project's first runtime dependency**, withdrawing `P2`'s narrowing of the output contract's rule 2 to records | `P2` narrowed the rule because the project declared no dependencies; `nemora` already depends on `pandas`, so the narrowing saved nobody anything and cost a disclosed deviation | `P3.4` restored the rule, added `pandas>=2.0` and `pandas-stubs`, and `docs/reference/outputs.rst` records that the narrowing is withdrawn |
| **The tree-list handoff is a reading of keyword contract rule 4**, which allows one exception, "the tree-record format". The run writes `TREEFMT` **and** `TREEDATA` | Without `TREEDATA` FVS never opens the tree file, so the format and the instruction to use it cannot be separated | Recorded on `docs/reference/keywords.rst` in the same change set rather than left to be inferred, because a rule read generously should say so |
| **A gate was strengthened mid-phase.** The `build-variant` job built and imported the extension but never ran the tests, so the end-to-end test skipped in every job and was never converted into a gate | The job was written in `P3.1` before there was an end-to-end test to run in it | `P3.6` added the test step in `4a7a9ed`; run `40073616342` shows `26 passed, 1 skipped` |
| **`P2.2` (#12) stayed open four days past its discharge**, so the roadmap said `complete` while the issue was open, and its body still said `Status: active` | The `P2` close-out carried its one open subtask into `P3` deliberately, and `P3.2` discharged it without closing the issue | Closed in `ed03085` with a comment that names the gap rather than glossing it, its completion metadata filled, and the roadmap's `P2.2` line amended to say "and discharged there". **This commit is also the one whose message does not start with a task ID** |
| **The mutation harness caught two stale anchors and one mis-pointed mutation.** `outputs-treats-every-row-as-an-error` lost its anchor when the reader began returning dataframes; `keywords-accepts-any-name` lost its when the validator gained `SPECIAL_KEYWORDS`; and a new `run-hashes-the-set-the-caller-wrote` mutation was pointed at a test that did not exercise it | The anchors are exact text, and three modules were rewritten in this phase | Each was reported as `ERROR … the anchor occurs 0 times` or `MISSED` rather than as a pass, and each was fixed in the change set that broke it. The registry is 23 of 23 |

## 6. Next phase

`P4` is the roadmap's stub: "show that the build meets its acceptance criteria, and record the evidence
in the changelog", with one task and a placeholder criterion. Proposed scope, as recommendations with
defaults:

1. **`P4.1`, the acceptance checks, run from a clean checkout.** Build the variant from the pin, run the
   suite, run the command, and record the run ids and the outputs. This is the phase's substance and it
   needs no new code.
2. **Promote the oracle comparison into a repository test.** `P2.3` compared the build against the
   official BC test data and recorded the result in `notes/reference/fvsbc-validation.md`; the
   comparison is not reproducible from the repository. This is the oldest open proposal in the project,
   it is carried in `CHANGE_LOG.md`, and `P4` is where it belongs.
3. **Make the dashboard's 3.11 evidence literal.** The criterion in section 1 is met in substance and not
   in letter. The protection-safe fix is to keep the job's name and run the script under both
   interpreters inside it, or to rename the context and change protection in the same approved move.
   **Either way it touches a required context, so it needs its own approval** — which is why it is not in
   this change set.
4. **Close the `__all__` gap.** `P3.4` noted that nothing asserts every name in the package's `__all__`
   resolves; it was checked by hand once. A one-line test closes it.

Not in `P4`, and named so it is not lost:

- **Block keywords are refused, not written** (`COMMENT`, `COMPUTE`, `IF`, `DATABASE`). A run that needs
  `COMPUTE` cannot be expressed through this package. That is a capability with a research burden, not a
  fix, and it is the largest known gap in the public surface.
- **`run.py`'s drive body is covered only where the extension is built**, so the quality job reports that
  file at 87 percent. The build job covers it, and the gate is met at 98 percent overall.

## 7. Decision

Approve recommendations 1 to 5, or amend them. The phase's six tasks are complete and its branch is
green; one of its seven acceptance criteria is a false requirement and one is met in substance rather
than in letter, and both are stated above rather than left to be found.

## Verification before approval

- `python scripts/dashboard.py` on `ed03085`: six gates green.
- CI run `40111537678` on `ed03085`: five jobs successful, including the build job's end-to-end test.
- `gh api repos/UBC-FRESH/fresh-fvsbc/branches/main/protection`: the read-back quoted in the header.
- `python scripts/mutation_check.py`: `23 of 23 mutations caught`.
- `gh issue list --state open`: `#17` alone, before this report was written.
