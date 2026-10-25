# Phase close-out report: P11 The command's block form, and 0.3.1

Phase: P11 The command's block form, and 0.3.1
Parent issue: #58
Pull request: #61, `feature/p11-block-form` into `main`
Evidence head: `d471766`; CI run `40175355821` succeeds on it
Report commit: the commit that adds this report
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

1. Squash-merge #61 and delete the branch.
2. Tag `v0.3.1` at the merge commit and push it.
3. `gh release create v0.3.1 --title "fresh-fvsbc 0.3.1" --notes-file RELEASE_NOTES.md`.
4. Verify from a clean checkout **through the command**, with a `--block` for the `DATABASE` block, and confirm `FVS_Compute` is written.
5. Check the published pages against the source at the tag.
6. Close #58.

**Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| `--block` writes a block, and the two options keep their order | Four parser and order tests | met |
| A run through the command with a `DATABASE` block first writes `FVS_Compute` | `test_a_run_through_the_command_writes_a_compute_table`, run in the build job | met |
| A `--block` for a keyword that takes no lines is refused | `test_a_block_for_a_keyword_that_takes_no_lines_exits_two` | met |
| The package reports `0.3.1` and a clean checkout installs it | version test; **the clean checkout is action 4** | pending by construction |
| `python scripts/dashboard.py` exits zero | Green on `d471766`; CI `40175355821` succeeds | met |

## 2. Workflow compliance

- Parent #58 and children #59–#60 before the branch; branch named as the workflow names it.
- Branch from `main`: `892f14d`.
- Commit messages start with task IDs; roadmap and changelog in step.
- **One deviation, caught and fixed in the phase**: the first draft of the two child issue bodies was a
  placeholder ("do the work, with its tests"), which is the slop the issue format exists to prevent.
  Both were rewritten with real scope and subtasks before any code.

## 3. Decision

Approve 1 to 6. One criterion is pending by construction and its output goes in the closeout comment on
#58.
