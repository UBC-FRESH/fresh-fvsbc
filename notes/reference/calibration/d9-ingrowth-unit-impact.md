# D9.26 ingrowth evidence after the TPH unit fix

Date: 2026-11-07
Issue: #458
Cause: D9.24

FVS-BC metric reads `NATURAL` stems as trees per hectare. The pre-fix wrapper pre-converted to
trees per acre, delivering 2.471x too few trees. This re-runs the three main ingrowth candidates.

## Results

| Candidate | Old result | Corrected result | Verdict |
| --- | --- | --- | --- |
| IDFdk pilot, test | BA -6.0%, TPH -8.7% | BA -5.6%, TPH **+8.6%** | Test still passes; train TPH +37.4% overshoot |
| IDFdk pilot, train | BA -0.3%, TPH +9.0% | BA -0.3%, TPH **+37.4%** | Train no longer passes |
| 100 Mile candidate | BA +8.4%, TPH -13.1% | BA **+13.0%**, TPH +10.5% | **Retracted**; 0/6 sites pass |
| SBPSmk mature, in-sample | BA -2.8%, TPH -5.8% (old) | BA -4.2%, TPH -0.8%; 25/25 sites | In-sample still passes; temporal/nested not re-run |

The 100 Mile candidate is not valid under the corrected unit. The IDFdk test holdout still passes,
but the training overshoot means the pilot is not a clean bundle. The SBPSmk mature in-sample
result survives; its nested/temporal evidence still needs a full rerun.

## Consequences

- Do not use pre-D9.24 ingrowth evidence for any claim.
- The 100 Mile candidate is retracted; no bundle.
- The IDFdk bundle and binned bundle are **pilot/stale**, not validated.
- The SBPSmk mature bundle remains post-hoc; its in-sample result is updated, but its temporal and
  nested evidence must be re-run before any stronger claim.
- The ICHmw2 and CWH candidates have no ingrowth and are unaffected.

## Next

Re-fit the 100 Mile and IDFdk recruitment rates or use a recruitment model that includes density,
seed source, and site effects. Do not simply scale the old rates.
