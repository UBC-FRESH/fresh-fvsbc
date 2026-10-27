# Phase close-out report: P52 A refusal is reported

Phase: P52 A refusal is reported
Parent issue: #223
Pull request: #225
Evidence head: `6074a66`
Date: 2026-10-27
Status: merged.

## Recommendation

Release `0.15.1`. `0.15.0` is published with this defect in it.

## 1. What shipped

`KeywordOrderError` joins the input errors the command reports. A refused keyword set now reaches the
user as the validator's message rather than as a traceback:

```text
fresh-fvsbc: a DATABASE block must precede the stand setup; FVS refuses it later with
'KEYWORD ENTERED IS USED IN WRONG CONTEXT'. The official case puts it first
```

## 2. What it fixes

The validator raises `KeywordOrderError` for a `DATABASE` block after the stand — the mistake the
check exists to catch — and the command's `_INPUT_ERRORS` did not list it. So the check fired and
Python printed the traceback **over** the message. Every release since the order check was added has
this defect.

## 3. How it was found

Verifying `0.15.0` from a clean checkout, by running the refusal the release notes describe. The
refusal was there; the delivery was not.

## 4. Acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| A `DATABASE` block after the stand exits `2` with the message | the clean-checkout run, and `tests/test_command.py` | met |
| A fire-model keyword outside its block does the same | same | met |
| `python scripts/dashboard.py` exits zero | green on `6074a66` | met |

## 5. What it does not verify

Nothing else changed. The messages themselves were already right.
