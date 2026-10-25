# Phase close-out report: P29 Release 0.9.0

Phase: P29 Release 0.9.0
Parent issue: #131
Pull request: #133
Evidence head: `8913a5b`
Date: 2026-10-25
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.9.0` | the clean checkout install reports `0.9.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: six tables, the pattern, the three failure modes, nine gaps | met |
| A clean checkout reads a per-tree table and the structural stage | section 3 | met |
| The published documentation matches the source at the tag | twenty exposed on the published page | met |
| `python scripts/dashboard.py` exits zero | green on `820fc06`, the pull request's head | met |

## 2. What shipped

Six tables, taking the reader from fourteen to **twenty of 44**:

| Table | What it carries | Trigger |
| --- | --- | --- |
| `FVS_TreeList_Metric` | **the first per-tree output the package has had** | `TREELIDB` + `TREELIST` |
| `FVS_CutList_Metric` | the trees removed, same shape | `CUTLIDB` + `CUTLIST` + a removal |
| `FVS_StrClass_Metric` | the **structural stage** — the BC-specific one | `STRCLSDB` + `STRCLASS` |
| `FVS_ATRTList_Metric` | the after-treatment attribute list | `ATRTLIDB` + `ATRTLIST` + a **partial** removal |
| `FVS_Down_Wood_Cov_Metric` | down wood as cover | `DWDCVDB` + `DWDCVOUT` |
| `FVS_Stats_Species_Metric` | statistics by species | `INVSTATS` + `STATS` |

## 3. Verification from a clean checkout at the tag

```text
clone: 8913a5b v0.9.0
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
installed version: 0.9.0
exposed: 20 of 44
FVS_TreeList_Metric: 32 rows, 34 columns
FVS_CutList_Metric: 8 rows | CCum in tree: True | CCuM in cut: True
FVS_StrClass_Metric: 5 rows, 46 columns
FVS_ATRTList_Metric: 8 rows
summary: (3, 22)
```

A fresh venv, the variant built from the pinned source with `-Dfvsvariants=bc`, the package installed from
the tag clone, and one run with four requests and a partial removal reading all four tables.

The `CCum`/`CCuM` line is the interesting one: the check is not that the names match, but that they
**differ**, because that is what FVS does.

## 4. What was published

```bash
git tag -a v0.9.0 8913a5b -m "fresh-fvsbc 0.9.0"
git push origin v0.9.0
gh release create v0.9.0 --title "fresh-fvsbc 0.9.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.9.0>

## 5. What this release did not verify

- **None of the six new tables is checked against an independent source.** The official dump covers four
  tables and none of them is new here. The per-tree pair can be spot-checked against the tree list the run
  consumed, which is what the test does; the structural stage and the statistics cannot.
- **Two of the six attempted tables did not land.** `FVS_Mortality_Metric` needs a fire that kills trees
  and `FVS_Stats_Stand` needs a stand with more than one sample point. Both are recorded with what would
  close them, and neither was exposed.

## 6. Workflow compliance

Parent #131 and child #132 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40240044937` concluded `success` on `820fc06` before `gh pr merge 133`
ran.

One slip worth recording: in `P28` the roadmap briefly carried `#P28` placeholders, and the workflow
validator **failed the dashboard red** until the issues existed and the numbers were real. The gate caught
a real mistake, which is what it is for.

## 7. Decision

No approval is needed for anything outstanding. The next phase should be the fixture, not another table:
`FVS_Mortality_Metric`, `FVS_Stats_Stand`, the seven damage agents and every regeneration table all need a
stand the generator cannot express, so the fixture is what stands between this project and the other
twenty-four tables.
