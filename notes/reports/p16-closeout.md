# Phase close-out report: P16 Release 0.5.0

Phase: P16 Release 0.5.0
Parent issue: #79
Pull request: #81
Evidence head: `bd79d4c`
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

1. Squash-merge #81 and delete the branch, **after its run is green**.
2. Tag `v0.5.0` at the merge commit and push it.
3. `gh release create v0.5.0 --title "fresh-fvsbc 0.5.0" --notes-file RELEASE_NOTES.md`.
4. Verify from a clean checkout: fresh venv, the pinned variant, the package installed, and a run with an `IF` block whose report carries the condition.
5. Check the published pages against the source at the tag.
6. Close #79.

**Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.5.0` | the version test | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md`: the conditional, nine gaps | met |
| A clean checkout installs it and runs a case with an `IF` block | **pending**, action 4 | pending by construction |
| The published documentation matches the source at the tag | **pending**, action 5 | pending by construction |
| `python scripts/dashboard.py` exits zero | green on `bd79d4c` | met |

## 2. Workflow compliance

Parent #79 and child #80 before the branch; branch named as the workflow names it; commit messages start
with task IDs; roadmap and changelog in step.

**The merge waits for the run.** The previous close-out merged a roadmap pull request before its checks
reported, on an account that can bypass protection; the recommendation above says to wait, and the agent
will.

## 3. Decision

Approve 1 to 6.
