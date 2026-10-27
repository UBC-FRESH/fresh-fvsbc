# Phase close-out report: P55 Release 0.16.0

Phase: P55 Release 0.16.0
Parent issue: #236
Pull request: #238
Evidence head: `eab4dbb`
Date: 2026-10-27
Status: merged, tagged and released.

## Recommendation

**Release `0.16.1`.** `0.16.0`'s headline fix — the fire-model ordering warning — **does not reach
anyone using the command**, which `P56` fixed. Settings changes: none.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.16.0` | the clean checkout install reports `0.16.0` | met |
| The notes lead with the defect | `RELEASE_NOTES.md` at the tag | met |
| A clean checkout writes all four fire tables | `ce27ab2`'s verification, section 3 | met |
| The oracle agrees with all four | same | met |
| `python scripts/dashboard.py` exits zero | green on the pull request's head | met |

## 2. What shipped

- The validator warns when an `FMIN` block asking for `FUELOUT` or `POTFIRE` follows `INVYEAR`.
- Thirteen exposed tables are checked, up from nine, including all four fire tables.

## 3. The verification, and what it caught

The clean checkout reports `0.16.0` and the tables are right. Then the case the notes describe was run:

```text
$ fresh-fvsbc population.json --keyword INVYEAR=2020 --block "FMIN|FUELOUT=2|POTFIRE=2" ...
warnings: 0
```

**No warning.** The validator computed it and nothing printed it: `RunResult.warnings` is FVS's
`FVS_Error` rows, and the validator's warnings had no route out of `run_population`. So the release's
headline fix reached nobody using the command.

That is `P56`, merged as `cd33b2f`. With it:

```text
fresh-fvsbc: warning: an FMIN block that asks for FUELOUT or POTFIRE must precede INVYEAR: ...
```

## 4. What was published

```bash
git tag -a v0.16.0 eab4dbb -m "fresh-fvsbc 0.16.0"
git push origin v0.16.0
gh release create v0.16.0 --title "fresh-fvsbc 0.16.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.16.0>

## 5. What this does not verify

- `FVS_InvReference` and `FVS_BurnReport_Metric` remain out, for the reasons the notes give.
- The web surface is unchanged since `0.13.0`'s verification.

## 6. The pattern worth naming

**Twice now, a release has shipped a fix that did not reach the user**: `P52`'s refusal printed as a
traceback, and now a warning nobody printed. Both were found by running the released version's own
documented case from a clean checkout, and neither by the unit tests. The verification step is doing
the work the tests are not, and it is the step that keeps paying.
