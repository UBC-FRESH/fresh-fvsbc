# Phase close-out report: P19 Release 0.6.0

Phase: P19 Release 0.6.0
Parent issue: #90
Pull request: #92
Evidence head: `7d1d405`
Date: 2026-10-25
Status: merged, tagged and released. This report records what was carried out and what the verification
found.

## Recommendation

Nothing is waiting. The release is published; this report, the roadmap flip and the documentation
correction below go to `main` in one pull request.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.6.0` | the clean checkout install reports `0.6.0` | met |
| The notes say what changed and what remains | `RELEASE_NOTES.md` at the tag: three tables, `FMIN`, the reachability record, nine gaps | met |
| A clean checkout installs it and runs a case reading a new table | section 3 | met |
| The published documentation matches the source at the tag | eleven exposed on the published page; **one stale section found and corrected after the tag**, section 5 | met with a caveat |
| `python scripts/dashboard.py` exits zero | green on `0344bd4`, the pull request's head | met |

## 2. What shipped

- **Three tables**: `FVS_Fuels_Metric`, `FVS_PotFire_Metric`, `FVS_PotFire_Cond_Metric`. The reader
  exposes **eleven of 44**.
- **`FMIN` as the fourth line block**, which is how `FUELOUT`, `FUELREPT` and `POTFIRE` are expressed —
  they are options inside it, not keywords, which is why the official case's own `POTFIRE 2` produced
  nothing through this route before.
- **`notes/reference/table-reachability.md`**, which says which of the rest can be written at all.

## 3. Verification from a clean checkout at the tag

```text
clone: 7d1d405 v0.6.0
pyfvs at: e95172b
list_variants: {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
installed version: 0.6.0
exposed: 11 of 44
FVS_Fuels_Metric: 2 rows, 22 columns
FVS_PotFire_Metric: 2 rows, 29 columns
FVS_PotFire_Cond_Metric: 2 rows, 12 columns
summary: (3, 22)
```

A fresh venv, the variant built from the pinned source with `-Dfvsvariants=bc`, the package installed from
the tag clone, and one run with an `FMIN` block reading all three new tables. Two build details are worth
recording because they cost time: the venv needs `meson`, `ninja` and `patchelf` **on `PATH`**, and a
detached copy of the source makes `setuptools_scm` produce an invalid version, so the build pins
`SETUPTOOLS_SCM_PRETEND_VERSION`.

## 4. What was published

```bash
git tag -a v0.6.0 7d1d405 -m "fresh-fvsbc 0.6.0"
git push origin v0.6.0
gh release create v0.6.0 --title "fresh-fvsbc 0.6.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.6.0>

## 5. What the verification found

The published output contract page **contradicted itself**: rule 1 said the database held `FVS_Cases` and
`FVS_Error` and no more, and that PyFVS exposed no way to ask for a named table, while rule 4 on the same
page listed eleven exposed tables. The "Not verified" section was worse — it still said nine of those
eleven were not exposed, and that `FVS_Compute` was outside the reader's surface.

Both claims predate this release and both are now false. The correction is in this pull request. **The tag
carries the older text**; the published pages follow `main`, so a reader sees the correction, and the next
release carries it in its own tree.

This is the second time in three phases that a test or a page asserted a premise the code had outgrown.
Both were found by running the thing rather than by reading it.

## 6. Workflow compliance

Parent #90 and child #91 before the branch; the branch named as the workflow names it; the commit starts
with its task ID; the roadmap and the changelog in step.

**The merge waited for the run.** `40221829392` concluded `success` on `0344bd4` before `gh pr merge 92`
ran, and the merge was read back to confirm it. The account can bypass branch protection, and this phase
did not.

## 7. Decision

No approval is needed for anything still outstanding. The next phase is a choice between tracing the
fire-carbon report path and leaving the tables with no writer unexposed, and it is presented as a
decision rather than started.
