# Phase close-out report: P40 Release 0.12.0

Phase: P40 Release 0.12.0
Parent issue: #175
Pull request: #177
Evidence head: `472dcd2`
Date: 2026-10-27
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.12.0` | the clean checkout install reports `0.12.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: the surface, the oracle flag, the real case, eleven gaps | met |
| A clean checkout installs the web extra, serves a run, and reads its tables | section 3 | met |
| The published documentation matches the source at the tag | a `web` page in the reference toctree | met |
| `python scripts/dashboard.py` exits zero | green on `d7426e3`, the pull request's head | met |

## 2. What shipped

A browser surface, and the flag that makes it trustworthy.

- **`fresh-fvsbc web --runs DIR`** — FastAPI behind an optional extra, a vanilla ES module shell with no
  build step, and four validated skin manifests.
- **`ORACLE_TABLES`** — four of the 31 exposed tables are checked against FVS's own dump and 27 are not; the
  API reports it and the front end says so above the rows.
- **Four fixes a real BC case found** — the 999-tree refusal by name, `failed` runs visible with their log,
  discovery of a run that died before writing `run.key`, and one ordered keyword list so a `DATABASE` block
  can precede the stand setup.

## 3. Verification from a clean checkout at the tag

```text
clone: 472dcd2 v0.12.0
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
version: 0.12.0
web extra present: fastapi 0.162.0
Requires: pandas                       <- the core install is unchanged
ran bc in runs/fir20: summary 3 rows, 22 columns, 1 warning
/api/oracle: {"exposed":31,"oracle":4,...}
/api/runs:   [{"id":"fir20","state":"complete","tables":5}]
FVS_TreeList_Metric   3996 rows  oracle=False
FVS_StrClass_Metric      5 rows  oracle=False
FVS_Summary_Metric       3 rows  oracle=True
/api/runs/fir20/tables/FVS_CalibStats -> 404, "'FVS_CalibStats' is not an exposed table; this reader exposes 31"
```

The run is the 2022 workshop bundle's own stand, 999 trees of the 1540 it carries, site index FD 15,
inventory year 2020. **The release verification now has two paths**: the CLI, and the service reading a run
that checkout produced.

## 4. What was published

```bash
git tag -a v0.12.0 472dcd2 -m "fresh-fvsbc 0.12.0"
git push origin v0.12.0
gh release create v0.12.0 --title "fresh-fvsbc 0.12.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.12.0>

## 5. What this release does not verify

- **The surface's browser behaviour.** The API is covered by 60 tests, the shell is served, and the panels
  were exercised by hand — but no browser automation runs, so the compare panel and the chart are checked
  by eye only.
- **Concurrency.** Two runs started at once through the API are untested. The service tracks processes in a
  dict and the CLI is re-entrant by ADR 0010, but nothing asserts the combination.
- **The `POST /api/runs` path on a machine where the extension is missing** reports a failed run rather than
  a clear "the extension is not built" at the surface. The CLI's own message is in the run's log.

## 6. The two new gaps, and why they are gaps

1. **One plot holds at most 999 trees.** BC's tree record shares columns 1 to 4 between the plot and the
   tree number, so the writer has three digits. The 2022 workshop's own case carries 1540 trees in one plot.
   Subdividing a stand changes what the statistics mean, so it is a modelling decision.
2. **The surface has no authentication.** It binds `127.0.0.1` and refuses anything else without
   `--allow-remote`. That refusal is the security decision until there is an auth story.

## 7. Workflow compliance

Parent #175 and child #176 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40455540247` concluded `success` on `d7426e3` before `gh pr merge 177`
ran.

## 8. Decision

No approval is needed for anything outstanding. The next phase with real value is the **oracle harness**: the
standalone FVSbc binary is buildable and proven (ADR 0008, ADR 0009), and using it as a comparison tool would
let any run's numbers be checked against FVS's own output — the one thing standing between "the reader
returned this" and "this is right", for 27 tables.
