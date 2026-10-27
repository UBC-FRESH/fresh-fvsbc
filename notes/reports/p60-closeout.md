# Phase close-out report: P60 Release 0.17.0

Phase: P60 Release 0.17.0
Parent issue: #256
Pull request: #258
Evidence head: `404c570`
Date: 2026-10-27
Status: merged, tagged and released.

## Recommendation

Nothing is waiting. **Settings changes: none.**

## 1. Acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.17.0` | the clean checkout install reports `0.17.0` | met |
| The recipes page is published and linked | in the tag, and in the toctree | met |
| The notes say what is checked, what is not, and why | `RELEASE_NOTES.md` at the tag | met |
| `python scripts/dashboard.py` exits zero | green on the pull request's head | met |

## 2. Verification from a clean checkout at the tag

A recipe from the page, run as written:

```text
clone: 404c570 v0.17.0
version: 0.17.0

$ fresh-fvsbc ... --block "FMIN|MORTREPT=1|FUELOUT=2|FUELREPT=2|POTFIRE=2|SIMFIRE=1,20,1,21,1,100,1" ...
tables: FVS_Cases, FVS_Consumption_Metric, FVS_Fuels_Metric, FVS_Mortality_Metric,
        FVS_PotFire_Cond_Metric, FVS_PotFire_Metric, FVS_Summary_Metric
```

And the trap the page warns about, which is why the page exists:

```text
$ fresh-fvsbc ... --block "DATABASE|...|MORTREDB|CUTLIDB" ...      # the options, no events
tables: FVS_Cases, FVS_Summary_Metric
```

Both options accepted, neither table written, and the run reports success.

## 3. What was published

```bash
git tag -a v0.17.0 404c570 -m "fresh-fvsbc 0.17.0"
git push origin v0.17.0
gh release create v0.17.0 --title "fresh-fvsbc 0.17.0" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.17.0>

## 4. What this does not verify

- `FVS_InvReference` is still the one exposed table no run of this package produces, with the writer
  compiled in and called.
- `FVS_Regen_SitePrep`'s allocation columns still differ from the standalone's, for a reason this
  package is not implicated in.

## 5. Why this release is worth taking

The recipes page is the only artifact from this stretch that a lab member will read **before** being
confused. Everything else — the oracle, the coverage, the attributions — is for whoever maintains the
package. A silent missing table is the most expensive failure mode this project has, because the run
succeeds.
