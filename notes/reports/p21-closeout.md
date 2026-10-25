# Phase close-out report: P21 Release 0.7.0

Phase: P21 Release 0.7.0
Parent issue: #99
Pull request: #101
Evidence head: `56b42c7`
Date: 2026-10-25
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.7.0` | the clean checkout install reports `0.7.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: two carbon tables, the trigger, the NULL, nine gaps | met |
| A clean checkout reads a carbon table with a non-zero total | section 3 | met |
| The published documentation matches the source at the tag | thirteen exposed on the published page | met |
| `python scripts/dashboard.py` exits zero | green on `0a06d9f`, the pull request's head | met |

## 2. What shipped

- **Two carbon tables**: `FVS_Carbon_Metric` and `FVS_Hrv_Carbon`. The reader exposes **thirteen of 44**.
- **The trigger is an option, not a keyword.** `CARBREPT` inside an `FMIN` block sets `ICRPTB`, which is
  what lets `fmcrbout.f` reach `DBSFMCRPT`, the carbon writer's only call site. The `DATABASE` option
  `CARBREDB` alone is accepted and writes nothing — the reason the previous release called carbon
  unreachable.
- **A NULL is documented, not hidden.** `Total_Stand_Carbon` is NULL in a period whose components FVS
  leaves undefined, and the reader returns `NaN` rather than inventing a zero.

## 3. Verification from a clean checkout at the tag

```text
clone: 56b42c7 v0.7.0
pyfvs at: e95172b | patchelf: patchelf 0.19.1
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
installed version: 0.7.0
exposed: 13 of 44
FVS_Carbon_Metric: 2 rows, 14 columns
FVS_Hrv_Carbon: 2 rows, 9 columns
Total_Stand_Carbon year 0: 13.606 tC/ha
NULL periods: 1 of 2
summary: (3, 22)
```

A fresh venv, the variant built from the pinned source with `-Dfvsvariants=bc`, the package installed from
the tag clone, and one run with `CARBREPT` in an `FMIN` block reading both tables.

**The NULL count is the interesting number**: one of two periods carries no total, and the run reports it
as `NaN` rather than zero. That is the behaviour the pages now describe, and this run is the evidence for
the description.

## 4. What was published

```bash
git tag -a v0.7.0 56b42c7 -m "fresh-fvsbc 0.7.0"
git push origin v0.7.0
gh release create v0.7.0 --title "fresh-fvsbc 0.7.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.7.0>

## 5. What this release did not verify

- **The carbon numbers are not checked against an independent source.** The oracle fixture is a 2022 dump
  that carries no carbon section, so the row counts and the 13.606 tC/ha are FVS's own output read back,
  not agreement with a reference. That is a weaker claim than the fuels and snag tables have, and the
  notes should not be read as saying otherwise.
- **The burn report and consumption tables remain unwritten.** `BURNREPT` with every fuel option on wrote
  neither: `DBSFMFUEL` is called from `fmfout.f:227`, inside the routine that runs when something burns.
  So those tables need a fire event, not an option.

## 6. Workflow compliance

Parent #99 and child #100 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40224681153` concluded `success` on `0a06d9f` before `gh pr merge 101`
ran.

## 7. Decision

No approval is needed for anything outstanding. The next spike is the burn path, and its question is
narrow: whether a fire event can be expressed in a keyword set this project can build.
