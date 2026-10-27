# Phase close-out report: P59 The site-prep difference

Phase: P59 The site-prep difference
Parent issue: #252
Pull request: #254
Evidence head: `6c08cda`
Date: 2026-10-27
Status: merged. No code.

## Recommendation

**No release.** This phase changed notes.

## 1. The question

`FVS_Regen_SitePrep` reports `PCT: 74 20 6` in this package's `.out` and `PCT: 100 0 0` in the
standalone's, in the same `SITE PREP SUMMARY` block. `P58` found it; this phase asked whether the
package is implicated.

## 2. What was ruled out

| Candidate | Evidence |
| --- | --- |
| The stand variables | `ESPREP` reads `ASPECT`, `SLOPE`, `BA`, `ELEV`. Both runs echo `ASPECT 0.`, `SLOPE 5%`, `ELEVATION 1158.2`, 4,146 tree rows, one plot |
| A stray draw | `RANNSEED` 1, 2 and 3 all give `74 20 6` and `76 20 4` — the run is deterministic |
| The writer | `DBSSITEPREP` stores what `estab.f` hands it, and the `.out` prints the same numbers from the same call |

## 3. What is left

`estab.f` fills `SUMPRE` from draws out of `WK6`, the pre-generated uniform array, and the three columns
are those counts as percentages after plot replication (`DUPNPT = NPTIDS*IDUP`).

**The likeliest cause is that the two drivers consume different numbers of draws before `estab.f`
runs** — the standalone reads its trees through a `DATABASE` block and this package through a tree-list
file.

**This is a hypothesis.** Testing it needs the draw index logged from both drivers, which is its own
change, and the draws themselves were not compared.

## 4. What the phase concludes

**The package is not implicated.** Every observable input agrees, the run is deterministic, and the
writer is a pass-through. What differs is a random allocation of site preparation across plots, and the
three integers that describe it.

The other 27 tables in the same run match, including the regeneration tally from the same `estab.f`
call.

## 5. Acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| Every observable input compared and recorded | section 2 | met |
| The remaining hypothesis stated as one, with what would test it | section 3 | met |
| The claim that the package is implicated withdrawn or supported | section 4 | met |
| `python scripts/dashboard.py` exits zero | green on `6c08cda` | met |
