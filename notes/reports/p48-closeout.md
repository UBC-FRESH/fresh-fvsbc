# Phase close-out report: P48 Release 0.14.0

Phase: P48 Release 0.14.0
Parent issue: #208
Pull request: #210
Evidence head: `b0c7e77`
Date: 2026-10-27
Status: merged, tagged and released. This report records what was carried out and what the verification
returned.

## Recommendation

Nothing is waiting. The roadmap flip goes to `main` in its own pull request, after its run is green.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.14.0` | the clean checkout install reports `0.14.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: the quiet-run fix, the handoff, eleven gaps | met |
| A clean checkout runs a quiet stand and does not report it as failed | section 3 | met |
| The published documentation matches the source at the tag | `outputs` page states the new rule | met |
| `python scripts/dashboard.py` exits zero | green on `4e82e56`, the pull request's head | met |

## 2. What shipped

- **A run that logs nothing is no longer reported as failed.** `FVS_Error` is written only when FVS has
  something to log; the reader treated an absent table as a failure to read, on a premise stated in the
  contract that a 999-tree single-plot case disproved.
- **The oracle harness reads a run's trees** through a `DSNin` input database: 999 trees, 3,996 per-tree
  rows.
- **The comparison is stated as a tool, not an oracle**: 0 of 5 tables agree and the differences are
  unattributed.

## 3. Verification from a clean checkout at the tag

```text
clone: b0c7e77 v0.14.0
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
version: 0.14.0
Requires: pandas
ran bc in runs/quiet
summary: 3 rows, 22 columns
warnings: 0
tables: ['FVS_Cases', 'FVS_TreeList_Metric', 'FVS_Summary_Metric']
FVS_Error present: False
```

**That last line is the release.** The same case on `0.13.0` raised
`the run failed: 'FVS_Error' is not in the database`; it now completes with `warnings: 0`. The
verification is the failing case, not a case that always passed.

## 4. What was published

```bash
git tag -a v0.14.0 b0c7e77 -m "fresh-fvsbc 0.14.0"
git push origin v0.14.0
gh release create v0.14.0 --title "fresh-fvsbc 0.14.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.14.0>

## 5. What this release does not verify

- **The oracle comparison still agrees on nothing.** 0 of 5 tables, unattributed. The two builds are
  different source revisions — the pin `e95172b`/`ef5fa847` against upstream `28fda8ed` — and that alone
  moves numbers. No table outside the four with a dump oracle is checked by this release either.
- **The web surface was not re-verified here.** It is unchanged since `0.13.0`'s verification, which covered
  the proxy prefix and a served run; this release touched the reader and the harness only.

## 6. How the bug was found

Not by a test. By chasing a warning the oracle harness printed — `PLOT COUNT= 1` against `DESIGN`'s five —
which turned out to be **my inconsistent test case**, and then, once the case was consistent, the run failed
for a reason that had nothing to do with the plot count.

That is the third time in this project that a real defect surfaced from running something against real data
rather than from a test I wrote, and the first time it was a defect that would have hit a user on their
first quiet stand.

## 7. Workflow compliance

Parent #208 and child #209 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `success` on `4e82e56` before `gh pr merge 210` ran.

## 8. Decision

No approval is needed for anything outstanding. The next piece with real value is **testing whether a
standalone can be built from the pin**, which is the only way to attribute the oracle comparison's
differences. ADR 0007 says it will not build; confirming or refuting that with the patch sets decides
whether the oracle is finishable or should end with a reason.
