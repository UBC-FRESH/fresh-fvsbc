# Phase close-out report: P8 Release 0.2.0

Phase: P8 Release 0.2.0
Parent issue: #47
Pull request: #49, `feature/p8-release-0-2-0` into `main`
Evidence head: `a5c1c27`, the head the gates and CI run `40171777297` cover
Report commit: the commit that adds this report
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

1. Squash-merge #49 and delete the branch.
2. Tag `v0.2.0` at the merge commit and push it.
3. `gh release create v0.2.0 --title "fresh-fvsbc 0.2.0" --notes-file RELEASE_NOTES.md`.
4. Verify from a clean checkout: fresh venv, the pinned variant built there, the package installed, `--help` and one case.
5. Check the published pages against the source at the tag.
6. Close #47.

**Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.2.0` | `pyproject.toml`, `__init__.py`, and `test_package_version_matches_pyproject` | met |
| The notes name the build and the gaps that remain | `RELEASE_NOTES.md`: the three pins read from the code, eleven gaps, and the limits beside the claims | met |
| A clean checkout installs the release and runs one case | **pending**, action 4; it cannot run before the tag | pending by construction |
| The published documentation matches the source at the tag | **pending**, action 5 | pending by construction |
| `python scripts/dashboard.py` exits zero on the head | Green on `a5c1c27`; CI `40171777297` succeeds | met |

## 2. Workflow compliance

- Parent issue #47 and child #48 created before the branch; the branch is named as the workflow names it.
- Branch from `main`: `cacd899`.
- Commit messages start with task IDs.
- Roadmap and changelog in step.
- One deviation: the first notes draft merged two gaps into one to make the count ten; it is eleven, and the notes now say so.

## 3. Decision

Approve 1 to 6. Two criteria are pending by construction and their output goes in the closeout comment on #47.
