# Phase close-out report: P35 Release 0.11.0

Phase: P35 Release 0.11.0
Parent issue: #155
Pull request: #157
Evidence head: `6b730e5`
Date: 2026-10-26
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.11.0` | the clean checkout install reports `0.11.0` | met |
| The notes say what changed and what is settled | `RELEASE_NOTES.md` at the tag: two tables, `ESTAB`, the classification | met |
| A clean checkout reads both regeneration tables | section 3 | met |
| The published documentation matches the source at the tag | thirty-one exposed on the published page | met |
| `python scripts/dashboard.py` exits zero | green on `370cc71`, the pull request's head | met |

## 2. What shipped

`FVS_Regen_Tally_Metric` and `FVS_Regen_SitePrep`, from an `ESTAB` block. The reader exposes **thirty-one
of 44**.

**`ESTAB` is a block, and its `NATURAL` line needs the stems per acre.** `esin.f` reports error 4 and drops
the whole keyword set when that field is zero, which is why a bare `ESTAB` was refused in every earlier
attempt.

## 3. Verification from a clean checkout at the tag

```text
clone: 6b730e5 v0.11.0
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
installed version: 0.11.0
exposed: 31 of 44
FVS_Regen_Tally_Metric: 2 rows, 14 columns
FVS_Regen_SitePrep: 1 rows, 8 columns
summary: (3, 22)
```

A fresh venv, the variant built from the pinned source with `-Dfvsvariants=bc`, the package installed from
the tag clone, and one run with an `ESTAB` block reading both tables.

## 4. What was published

```bash
git tag -a v0.11.0 6b730e5 -m "fresh-fvsbc 0.11.0"
git push origin v0.11.0
gh release create v0.11.0 --title "fresh-fvsbc 0.11.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.11.0>

## 5. What this release settles

The table work is finished, and the record says why rather than leaving an invitation open:

| Group | Count | Reason |
| --- | --- | --- |
| Exposed and tested | 31 | — |
| Needs something this project does not have | 6 | external climate attribute file; the FIA variant; a calibrated run; a bark-beetle specification; the sprout model |
| Gate no valid input satisfies | 1 | `FVS_BurnReport_Metric` |
| No writer call site | 5 | cannot be written by any amount of work |

`FVS_CalibStats` is the one deliberate refusal: the option works, the table appears on every run, and it is
always empty.

## 6. What this release did not verify

- **Neither regeneration table is checked against an independent source.** The official dump covers four
  tables and neither is one of them.
- **The two tables rest on one synthetic `ESTAB` line** — 200 stems per acre of a single species at date 1.
  A different establishment prescription would give different rows.

## 7. Workflow compliance

Parent #155 and child #156 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40251146625` concluded `success` on `370cc71` before `gh pr merge 157`
ran.

## 8. Decision

No approval is needed for anything outstanding. The remaining thirteen tables are classified, and six of
the eight candidates would need a project this one is not — a climate data format, or a different variant.
