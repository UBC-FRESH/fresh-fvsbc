# Phase close-out report: P53 Release 0.15.1

Phase: P53 Release 0.15.1
Parent issue: #228
Pull request: #230
Evidence head: `5ccc52e`
Date: 2026-10-27
Status: merged, tagged and released.

## Recommendation

Nothing is waiting. **Settings changes: none.**

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.15.1` | the clean checkout install reports `0.15.1` | met |
| The notes lead with the fix | `RELEASE_NOTES.md` at the tag | met |
| A clean checkout refuses both cases with a message and exit `2` | section 3 | met |
| `python scripts/dashboard.py` exits zero | green on the pull request's head | met |

## 2. What shipped

The one-line fix `P52` made: `KeywordOrderError` is an input error the command reports.

## 3. Verification from a clean checkout at the tag

```text
clone: 5ccc52e v0.15.1
version: 0.15.1

refusal 1: fresh-fvsbc: a DATABASE block must precede the stand setup; FVS refuses it later with
           'KEYWORD ENTERED IS USED IN WRONG CONTEXT'. The official case puts it first
           exit: 2
refusal 2: fresh-fvsbc: "SNAGOUT" is a fire-model keyword, and FVS reads it only between FMIN and
           its END; put it in the block's nested keywords
           exit: 2

good run:  warnings: 0, provenance recorded
```

**Both refusals are the verification**, and both were a traceback in `0.15.0`.

## 4. What was published

```bash
git tag -a v0.15.1 5ccc52e -m "fresh-fvsbc 0.15.1"
git push origin v0.15.1
gh release create v0.15.1 --title "fresh-fvsbc 0.15.1" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.15.1>

## 5. What this release does not verify

It is a patch. Everything `0.15.0` does not verify, `0.15.1` does not verify either: the fuel, potfire
and consumption tables need a fire rather than a keyword, and `FVS_InvReference` is still written by the
standalone and never by this package's build.

## 6. The lesson

The refusal was covered by the validator's tests and never by the command that delivers it. A check
whose finding cannot reach the user has not been checked. That is now a test per refusal, at the
command's boundary rather than the validator's.
