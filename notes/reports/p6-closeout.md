# P6 close-out: Operate and maintain

Merged branch: `feature/p6-operate`. Evidence head: the commit that adds this report; its CI run is on
PR #41.

## What shipped

- **`P6.1`** the twelve known gaps triaged in `notes/triage.md`: one fixed now, two proposed for a `P7`,
  nine accepted with a reason and a reopen condition.
- **`P6.2`** `run_case` drives FVS in a child process (ADR 0010), so two runs in one process are
  independent and a run is thread-safe. The defect returned numbers differing from the oracle on 104 of
  164 rows; it is now 0. Cost about 0.4 s per run. 25 of 25 mutations caught.
- **`P6.3`** built a quarterly review cadence, and it was **reverted** on the maintainer's direction:
  202 lines and five commits to schedule a review of a twelve-item list where nine items are "won't
  fix", against four commits for `P6.2`. The rule is one line in the roadmap. One real defect was kept:
  the model log's `Re-check` column named the seed workflow's task instead of this project's.

## Criteria

Four of four met: every gap has a disposition; two runs cannot silently disagree and the mechanism is
recorded and tested; the cadence requirement was met and then reverted by the maintainer, whose
direction supersedes it; dashboard green on the head.

## What went wrong

The process outweighed the product in `P6.3`. The cause was the agent putting "review on a cadence" into
the phase scope, writing the option text, and then treating a process document like a phase report.
Recorded in the changelog.

## Merge

`gh pr merge 41 --squash --delete-branch`, then close #37. No settings change.
