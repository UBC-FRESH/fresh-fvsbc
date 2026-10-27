# Phase close-out report: P44 Release 0.13.0

Phase: P44 Release 0.13.0
Parent issue: #192
Pull request: #194
Evidence head: `c5ec25f`
Date: 2026-10-27
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.13.0` | the clean checkout install reports `0.13.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: `THINQFA`, the proxy fix, the harness, eleven gaps | met |
| A clean checkout serves a run at `/api/runs` and under a prefix | section 3 | met |
| The published documentation matches the source at the tag | `keywords` and `web` pages carry both changes | met |
| `python scripts/dashboard.py` exits zero | green on `9f2fdb8`, the pull request's head | met |

## 2. What shipped

- **`THINQFA`'s supplemental record**, which the wrapper could not write at all. A set without it is refused
  rather than written, because FVS would read the next keyword as the units record.
- **The JupyterHub proxy fix.** `v0.12.0` answered a prefixed path by accident, through a deprecated FastAPI
  parameter, and the obvious correction broke it entirely.
- **`scripts/oracle_compare.py`**, a first cut at checking a run against the standalone `FVSbc`.

## 3. Verification from a clean checkout at the tag

```text
clone: c5ec25f v0.13.0
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
version: 0.13.0
Requires: pandas                      <- the core install is unchanged
ran bc in runs/fir20: summary 3 rows, 22 columns
THINQFA   1         0         24        0         1.4       2         100
1
/api/runs                                              -> 200
/jupyterhub32/user/gep/codeserver/proxy/9998/api/runs  -> 200
/jupyterhub32/user/gep/codeserver/proxy/9998/          -> 200
/jupyterhub32/user/gep/codeserver/proxy/9998/app.js    -> 200
```

**The `THINQFA` record was confirmed by FVS itself**, not only by the writer. Its activity schedule reads:

```text
BASE     THINQFA   2020       0.0000     9.4488     0.0000     1.4000     0.7874   100.0000     1.0000
```

The last two values are the target `100` and the **units code `1`** — the supplemental record, parsed and
used. The activity is then `DELETED OR CANCELED` because the target exceeds the stand's stocking, which is
FVS's own decision and not a parsing failure.

## 4. What was published

```bash
git tag -a v0.13.0 c5ec25f -m "fresh-fvsbc 0.13.0"
git push origin v0.13.0
gh release create v0.13.0 --title "fresh-fvsbc 0.13.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.13.0>

## 5. What this release does not verify

- **The oracle harness is unfinished.** It renders, runs and compares, but the standalone reads inline
  `TREEDATA` records as keywords and writes 1001 `FVS_Error` rows. The official case feeds trees through a
  `DATABASE ... DSNin ... TreeSQL` block, and that is the route to finish it. No table's numbers are
  cross-checked by this release.
- **`THINQFA` is verified as parsed, not as applied.** The activity was cancelled by stocking in the test
  case, so the thinning it describes never ran.
- **The web surface still has no authentication of its own.** The container's proxy supplies it, which is
  the deployment assumption the notes now state.

## 6. Workflow compliance

Parent #192 and child #193 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40464899927` concluded `success` on `9f2fdb8` before `gh pr merge 194`
ran.

## 7. Decision

No approval is needed for anything outstanding. The next piece with real value is finishing the oracle
harness's tree handoff, which is the only remaining route to a check for the 27 unverified tables.
