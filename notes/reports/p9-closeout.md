# Phase close-out report: P9 The database block

Phase: P9 The database block
Parent issue: #50
Pull request: #54, `feature/p9-database-block` into `main`
Evidence head: `552965c`; CI run `40173093545` succeeds on it
Report commit: the commit that adds this report
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

1. Squash-merge #54 and delete the branch.
2. Close #50 with a comment citing the merge commit.

**Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The record says the tables are reachable, and what was wrong before | Triage rows 2 and 11, `RELEASE_NOTES.md` gaps 2 and 10, and a correction note on ADR 0009 | met |
| A set whose `DATABASE` block comes after the stand is refused | `KeywordOrderError`, two tests, and the mutation `keywords-accepts-a-late-database-block` | met |
| `FVS_Compute` and `FVS_Summary_Metric` are read from a real run through the reader | A run with the block first writes both; the reader returns them with `BIGVOL` and `Tph` | met |
| `fresh_fvsbc.cli` is on the API page | `docs/api/package.rst`; docs build green under `-W` | met |
| `python scripts/dashboard.py` exits zero | Green on `552965c`; CI `40173093545` succeeds | met |

## 2. Workflow compliance

- Parent #50 and children #51–#53 before the branch; branch named as the workflow names it.
- Branch from `main`: `6adc1e6`.
- Commit messages start with task IDs.
- Roadmap and changelog in step.
- Child issues closed with closeout evidence.

## 3. What fell out on the way

- **`read_table` lost an empty table's columns**, because it built the frame from records and a table
  with no rows has none. Fixed, with a test.
- **The contract's table list was missing `FVS_Summary_Metric`**, which the official case writes. The
  count is 33, not 32, and the page and its test say so.
- **The mutation harness caught a stale anchor** — `outputs-renames-the-columns`, moved by the
  empty-table fix — and reported `ERROR`, not a pass.

## 4. Decision

Approve recommendations 1 and 2.
