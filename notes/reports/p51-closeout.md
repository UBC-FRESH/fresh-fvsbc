# Phase close-out report: P51 Release 0.15.0

Phase: P51 Release 0.15.0
Parent issue: #220
Pull request: #222
Evidence head: `a2e6996`
Date: 2026-10-27
Status: merged, tagged and released. This report records what was carried out and what the
verification returned.

## Recommendation

Nothing is waiting. `P52` is merged on top of it, and it fixes a crash the verification found; that
fix wants a **`0.15.1`** patch release, which is the next report's business.

**Settings changes: none.** The tag and the release are named in section 4 with their exact commands.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.15.0` | the clean checkout install reports `0.15.0` | met |
| The notes lead with the breaking change | `RELEASE_NOTES.md` at the tag | met |
| A clean checkout builds an `FMIN` block from keywords and the tables appear | section 3 | met |
| The published documentation matches the source at the tag | `keywords` page describes the block | met |
| `python scripts/dashboard.py` exits zero | green on `d672dff`, the pull request's head | met |

## 2. What shipped

- **`FMIN` holds keywords, not raw lines.** A breaking change, and the reason is that the old form
  could produce a run FVS accepted that meant something else: `SNAGCLAS  0.0   10.0  20.0  40.0`
  reaches FVS as class 2 `20.0` and class 3 `0.0`, with no error.
- **Nine tables are checked against FVS's own writer**, up from four.

## 3. Verification from a clean checkout at the tag

```text
clone: a2e6996 v0.15.0
version: 0.15.0
ran bc: summary 3 rows, warnings 0
tables: FVS_Carbon_Metric 2, FVS_Cases 1, FVS_Down_Wood_Cov_Metric 2,
        FVS_Down_Wood_Vol_Metric 2, FVS_Hrv_Carbon 2, FVS_SnagDet_Metric 2,
        FVS_SnagSum_Metric 2, FVS_Summary_Metric 3, FVS_TreeList_Metric 3996
SNAGCLAS  CLASS 1= 0.0; CLASS 2= 10.0; CLASS 3= 20.0; CLASS 4= 40.0
```

**The last line is the release.** The same values written as a raw line read back as `CLASS 2= 20.0`,
`CLASS 3= 0.0`, `CLASS 4= 2537.5`.

The old form is refused, and so is a fire-model keyword outside the block:

```text
fresh-fvsbc: "FUELOUT            2" is not a fire-model keyword. An FMIN block holds only the
keywords fmin.f reads, and 55 are known
```

## 4. What was published

```bash
git tag -a v0.15.0 a2e6996 -m "fresh-fvsbc 0.15.0"
git push origin v0.15.0
gh release create v0.15.0 --title "fresh-fvsbc 0.15.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.15.0>

## 5. What this release does not verify

- **`FVS_Fuels_Metric`, `FVS_PotFire_Metric` and `FVS_Consumption_Metric` are still unchecked.** They
  need a fire to occur, not a keyword to be set, and the oracle has not been given one.
- **`FVS_InvReference`** is still written by the standalone and never by this package's build, for a
  cause that is not established.
- **The web surface was not re-verified here.** It is unchanged since `0.13.0`'s verification.

## 6. What the verification found

The refusal of a fire-model keyword outside its block **raised a Python traceback** instead of
reporting the message, and so did the older `DATABASE`-after-the-stand refusal. The validator caught
both and the command did not deliver them. That is `P52`, merged as `6074a66`, and it is why `0.15.0`
is not the version anyone should install.

## 7. Workflow compliance

Parent #220 and child #221 before the branch; the commit starts with its task ID; the roadmap and the
changelog in step. **The merge waited for the run**: `success` on `d672dff` before `gh pr merge 222`.

One lapse, recorded rather than hidden: a later branch marked this phase complete in the tracker
**before** its closeout, and the workflow validator caught it. The row was put back.

## 8. Decision

Release `0.15.1` with `P52`'s fix. A released version that prints a traceback where it has a message
is a defect worth a patch, and the patch is one line.
