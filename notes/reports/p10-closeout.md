# Phase close-out report: P10 Release 0.3.0

Phase: P10 Release 0.3.0
Parent issue: #55
Pull request: #57, `feature/p10-release-0-3-0` into `main`
Evidence head: `96ff2b7`; CI run on it
Report commit: the commit that adds this report
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

1. Squash-merge #57 and delete the branch.
2. Tag `v0.3.0` at the merge commit and push it.
3. `gh release create v0.3.0 --title "fresh-fvsbc 0.3.0" --notes-file RELEASE_NOTES.md`.
4. Verify from a clean checkout: fresh venv, the pinned variant built there, the package installed, `--help` and one case.
5. Check the published pages against the source at the tag.
6. Close #55.

**Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.3.0` | `pyproject.toml`, `__init__.py`, and the version test | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md`: four tables, the position rule, ten gaps, the current coverage figures | met |
| A clean checkout installs the release and runs one case | **pending**, action 4 | pending by construction |
| The published documentation matches the source at the tag | **pending**, action 5 | pending by construction |
| `python scripts/dashboard.py` exits zero on the head | Green on `96ff2b7` | met |

## 2. Workflow compliance

- Parent #55 and child #56 before the branch; branch named as the workflow names it.
- Branch from `main`: `58046ff`.
- Commit messages start with task IDs.
- Roadmap and changelog in step.
- One deviation: the first notes draft carried the previous release's coverage figures (87 and 98) where the current ones are 84 and 97; corrected before the commit.

## 3. Decision

Approve 1 to 6. Two criteria are pending by construction and their output goes in the closeout comment on #55.
