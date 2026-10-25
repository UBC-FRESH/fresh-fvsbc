# Phase close-out report: P14 Release 0.4.0

Phase: P14 Release 0.4.0
Parent issue: #71
Pull request: #73
Evidence head: `72b9a88`
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

1. Squash-merge #73 and delete the branch.
2. Tag `v0.4.0` at the merge commit and push it.
3. `gh release create v0.4.0 --title "fresh-fvsbc 0.4.0" --notes-file RELEASE_NOTES.md`.
4. Verify from a clean checkout: fresh venv, the pinned variant, the package installed, and a run that reads two of the new tables.
5. Check the published pages against the source at the tag.
6. Close #71.

**Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.4.0` | the version test | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md`: eight tables, the 44-name correction, ten gaps | met |
| A clean checkout installs it and reads two of the new tables | **pending**, action 4 | pending by construction |
| The published documentation matches the source at the tag | **pending**, action 5 | pending by construction |
| `python scripts/dashboard.py` exits zero | green on `72b9a88` | met |

## 2. Workflow compliance

Parent #71 and child #72 before the branch; branch named as the workflow names it; commit messages start
with task IDs; roadmap and changelog in step.

**Two slips earlier in the session are recorded rather than repeated**: `P13`'s branch and issues were
created in the wrong order, and `P12`'s roadmap flip went to `main` directly instead of through a pull
request. Both are in the changelog.

## 3. Decision

Approve 1 to 6.
