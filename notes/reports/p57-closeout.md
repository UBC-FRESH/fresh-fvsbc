# Phase close-out report: P57 Release 0.16.1

Phase: P57 Release 0.16.1
Parent issue: #244
Pull request: #246
Evidence head: `516334b`
Date: 2026-10-27
Status: merged, tagged and released.

## Recommendation

Nothing is waiting. **Settings changes: none.**

## 1. Acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The package reports `0.16.1` | the clean checkout install reports `0.16.1` | met |
| The notes lead with the delivery | `RELEASE_NOTES.md` at the tag | met |
| A clean checkout prints the warning on standard error | section 2 | met |
| `python scripts/dashboard.py` exits zero | green on the pull request's head | met |

## 2. Verification from a clean checkout at the tag

```text
clone: 516334b v0.16.1
version: 0.16.1

$ fresh-fvsbc ... --keyword INVYEAR=2020 --block "FMIN|FUELOUT=2|POTFIRE=2"
fresh-fvsbc: warning: an FMIN block that asks for FUELOUT or POTFIRE must precede INVYEAR: both
capture the inventory year when they are read, and FVS treats a positive value as 'suppress this
report', so the fuels and potfire tables would be silently not written

$ fresh-fvsbc ... --block "FMIN|FUELOUT=2|FUELREPT=2|POTFIRE=2|SIMFIRE=1,20,1,21,1,100,1" ...
tables: FVS_Consumption_Metric, FVS_Fuels_Metric, FVS_PotFire_Cond_Metric, FVS_PotFire_Metric
```

**The first block is the release.** `0.16.0` printed nothing there.

## 3. What was published

```bash
git tag -a v0.16.1 516334b -m "fresh-fvsbc 0.16.1"
git push origin v0.16.1
gh release create v0.16.1 --title "fresh-fvsbc 0.16.1" --notes-file RELEASE_NOTES.md
```

Release: <https://github.com/UBC-FRESH/fresh-fvsbc/releases/tag/v0.16.1>

## 4. What this does not verify

A patch. Everything `0.16.0` leaves open, this leaves open: `FVS_InvReference` and
`FVS_BurnReport_Metric`.
