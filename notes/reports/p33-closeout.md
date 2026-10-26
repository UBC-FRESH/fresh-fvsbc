# Phase close-out report: P33 Release 0.10.0

Phase: P33 Release 0.10.0
Parent issue: #147
Pull request: #149
Evidence head: `a6f0011`
Date: 2026-10-26
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.10.0` | the clean checkout install reports `0.10.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: eight tables, four answers with lines, nine gaps | met |
| A clean checkout reads a statistics, mortality, damage-agent and root-disease table | section 3 | met |
| The published documentation matches the source at the tag | twenty-nine exposed on the published page | met |
| `python scripts/dashboard.py` exits zero | green on `a35e7cd`, the pull request's head | met |

## 2. What shipped

Eight tables, taking the reader from twenty-one to **twenty-nine of 44**:

| Table | What it carries | Trigger |
| --- | --- | --- |
| `FVS_Stats_Stand` | the distribution of attributes among sample points | `DESIGN`'s fourth field above 1 |
| `FVS_Mortality_Metric` | mortality by species and size class | `MORTREPT` + a fire |
| `FVS_DM_Spp_Sum_Metric`, `FVS_DM_Stnd_Sum_Metric` | dwarf mistletoe by species and stand | `MISRPTS`, damage code 30, an `MISTOE` block |
| `FVS_DM_Sz_Sum_Metric` | dwarf mistletoe by size class | the same, plus `MISTPRT` |
| `FVS_DM_TreeList_Metric` | dwarf mistletoe per tree | the same, plus `NEWSPRED` |
| `FVS_RD_Sum_Metric`, `FVS_RD_Det_Metric` | root disease by centre and species | an `RDIN` block with `RRINIT`, and `RRDOUT` |
| `FVS_CanProfile` | canopy fuels by height layer | `CANFPROF` inside `FMIN` |

## 3. Verification from a clean checkout at the tag

```text
clone: a6f0011 v0.10.0
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
installed version: 0.10.0
exposed: 29 of 44
FVS_Stats_Stand: 4 rows, 13 columns
FVS_Mortality_Metric: 2 rows, 22 columns
FVS_DM_Sz_Sum_Metric: 15 rows, 14 columns
FVS_DM_TreeList_Metric: 260 rows, 48 columns
FVS_RD_Sum_Metric: 6 rows, 20 columns
FVS_RD_Det_Metric: 3 rows, 24 columns
summary: (3, 22)
```

A fresh venv, the variant built from the pinned source with `-Dfvsvariants=bc`, the package installed from
the tag clone, and **one run** that carries an infected five-plot stand, an `RDIN` block and a fire, reading
all six of the tables new in this release. That single run is the evidence that the triggers compose: they
are not alternatives.

## 4. What was published

```bash
git tag -a v0.10.0 a6f0011 -m "fresh-fvsbc 0.10.0"
git push origin v0.10.0
gh release create v0.10.0 --title "fresh-fvsbc 0.10.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.10.0>

## 5. What this release corrects, and how it happened

The substance of this release is not the eight tables. It is that **four behaviours this project had
recorded as unknown were each one line of the source**, and `P30` had written a recommendation — a fixture
phase — on the strength of three experiments that did not fire.

| Recorded as unknown | Answer | Line |
| --- | --- | --- |
| how FVS counts sample points | `DESIGN`'s fourth field sets `IPTINV` | `initre.f:798` |
| what makes the mortality table appear | `MORTREPT` sets `IFMMRB = -1` | `fmin.f:1372`, gate at `fmfout.f:294` |
| how a mistletoe rating enters | damage codes 30 to 34, severity is the rating | `misdam.f:76` |
| why two DM tables stayed away | `MISTPRT`/`NEWSPRED` gate `DBSMIS3`/`5`/`6` | `misprt.f` |

The failure was methodological: a negative experiment constrains what was tried, not what the software does.
The rule is now in `notes/reference/fixture-limits.md` — before calling a behaviour unknown, grep for the
variable that gates it and read the assignment.

## 6. What this release did not verify

- **None of the eight new tables is checked against an independent source.** The official dump covers four
  tables and none of them is new here. `FVS_Stats_Stand` and `FVS_Mortality_Metric` are checkable for
  internal consistency only.
- **Three of the four dwarf-mistletoe tables and both root-disease tables rest on one infected fixture
  stand.** The values are FVS's own output read back, and a different stand would give different ones.

## 7. Workflow compliance

Parent #147 and child #148 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40247551761` concluded `success` on `a35e7cd` before `gh pr merge 149`
ran.

## 8. Decision

No approval is needed for anything outstanding. Ten candidates remain, each with a named gate in
`notes/reference/table-reachability.md`; five tables have no call site and cannot be written by any amount
of work.
