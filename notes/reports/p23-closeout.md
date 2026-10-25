# Phase close-out report: P23 Release 0.8.0

Phase: P23 Release 0.8.0
Parent issue: #107
Pull request: #109
Evidence head: `a919f11`
Date: 2026-10-25
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.8.0` | the clean checkout install reports `0.8.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: consumption, the fire event, the dead gate, nine gaps | met |
| A clean checkout reads a consumption row with a non-zero total | section 3 | met |
| The published documentation matches the source at the tag | fourteen exposed on the published page | met |
| `python scripts/dashboard.py` exits zero | green on `734ec0a`, the pull request's head | met |

## 2. What shipped

- **`FVS_Consumption_Metric`**, so the reader exposes **fourteen of 44**.
- **The trigger is a fire event, not an option.** A fire in FVS is an *activity*: `FMBURN` looks for
  2506 with `OPFIND`, and the `FMIN` option `SIMFIRE` schedules it. `DBSFMFUEL` is called from inside the
  routine that runs when something burns, so `BURNREDB` alone writes nothing.
- **A dead gate is recorded rather than papered over.** `FVS_BurnReport_Metric` is written only inside
  `IF (IFMBRB .LT. 0)`, and `IFMBRB` is assigned `9999` at initialisation and the inventory year by
  `BURNREPT`. `INVYEAR -1` satisfies the gate and the table appears — but a stand inventoried in year -1
  is invalid input that shifts the whole simulation, so the table is **not** exposed.

## 3. Verification from a clean checkout at the tag

```text
clone: a919f11 v0.8.0
pyfvs at: e95172b
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
installed version: 0.8.0
exposed: 14 of 44
FVS_Consumption_Metric: 1 rows, 19 columns
Total_Consumption: 22.569 t/ha
Percent_Consumption_Duff: 77.31
summary: (3, 22)
```

A fresh venv, the variant built from the pinned source with `-Dfvsvariants=bc`, the package installed from
the tag clone, and one run with `SIMFIRE` in an `FMIN` block reading the consumption row.

## 4. What was published

```bash
git tag -a v0.8.0 a919f11 -m "fresh-fvsbc 0.8.0"
git push origin v0.8.0
gh release create v0.8.0 --title "fresh-fvsbc 0.8.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.8.0>

## 5. What this release did not verify

- **The consumption numbers are not checked against a reference**, for the same reason the carbon numbers
  are not: the 2022 oracle fixture carries no consumption section. 22.569 t/ha is FVS's own output read
  back.
- **The `INVYEAR -1` path was tested and rejected.** It is recorded in the reachability note as evidence
  for the dead-gate claim, not as a recipe a caller should use.

## 6. Workflow compliance

Parent #107 and child #108 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40227838918` concluded `success` on `734ec0a` before `gh pr merge 109`
ran.

## 7. Decision

No approval is needed for anything outstanding. The next phase is the sweep: classify each of the
remaining 30 tables by its writer's existence and call site, so the table question closes with a record
rather than an open invitation.
