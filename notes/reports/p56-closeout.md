# Phase close-out report: P56 Warnings are delivered

Phase: P56 Warnings are delivered
Parent issue: #239
Pull request: #241
Evidence head: `cd33b2f`
Date: 2026-10-27
Status: merged.

## Recommendation

Release `0.16.1`. `0.16.0` computes its headline warning and drops it.

## 1. What shipped

The command prints every warning the keyword set carries, to standard error, before the run.

## 2. What it fixes

`RunResult.warnings` is FVS's `FVS_Error` rows. The validator's warnings are a different thing, and
nothing carried them out of `run_population` — so `0.16.0`'s fire-model ordering warning was computed,
returned to nobody, and discarded.

## 3. Acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| A set that carries a warning prints it | `tests/test_command.py`, and the clean checkout | met |
| A set that carries none prints nothing | the same tests | met |
| `python scripts/dashboard.py` exits zero | green on `cd33b2f` | met |

## 4. What it does not do

No warning changed. The one `0.16.0` added is right; only its delivery was missing.
