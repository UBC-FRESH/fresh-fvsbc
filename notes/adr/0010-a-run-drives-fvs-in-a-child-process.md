# ADR 0010: a run drives FVS in a child process

Status: accepted on 2026-10-25, by the maintainer, on the spike recorded below.
Supersedes: nothing. Refines the working-directory caveat in `src/fresh_fvsbc/run.py`.
Issues: #39, under `P6` (#37).

## Context

`run_case` drives one projection through PyFVS's step API in the caller's process. Two things follow,
and both are wrong for a released package:

1. **FVS keeps its state in the process, not in the working directory.** A case run after another
   projection produces different numbers, even in a fresh directory. `P4.2` found this when the oracle
   comparison failed in CI on 104 of 164 rows, and the same failure reproduces on any machine.
2. **A run changes the process's working directory** for the duration of the projection, so two threads
   that run at once interfere.

## The measurement

The spike for `P6.2`, run on 2026-10-25 in the build environment:

| Measurement | Result |
| --- | --- |
| Two runs of the **same** case in one process | identical, 0 differing cells |
| The official case after a synthetic one, one process | **104 differing rows** |
| The official case alone, or in a child process | 0 |
| A subprocess per run, synthetic case | 0.50 s against 0.12 s in-process, a constant **+0.38 s** |
| A subprocess per run, official case | 1.03 s drive, so **+37 percent** |
| Tests a guard would break today | none, one real drive per process |

**The bug is not "any second run".** It is a run inheriting a *different* case's state. That is worse
than a second-run rule would suggest, because a guard cannot tell the two apart.

## Decision

**A run drives FVS in a child process.** `run_case` spawns `python -m fresh_fvsbc._child`, which changes
into the run's directory, drives the projection, and writes the summary and the build's variant list
beside the outputs. The parent reads them and never changes its own working directory.

The alternative was a **guard** that refuses a second run in one process. It was rejected because it
converts a defect into a refusal: a caller who runs ten stands would write ten subprocess calls
themselves, which is the same work this decision does for them, and worse. The guard also refuses the
second of two concurrent callers rather than serving both.

A third option, in-process first and a child afterwards, was rejected because the behaviour would depend
on call order and the first run would still not be thread-safe. That hidden statefulness is worse than
either simple option.

## Consequences

- **Two runs in one process are independent, and a run is thread-safe**, because the parent shares
  nothing between them and never changes directory.
- **Each run costs about 0.38 s more**, a constant: interpreter start and imports. On the official case
  that is 37 percent, and on the synthetic case it is four times a small number.
- **The summary crosses the boundary as a file.** The child writes `summary.csv` from `FVS.summary`, and
  the parent reads it. The output contract's substance holds — the summary is still FVS's own frame
  rather than a re-derivation — and the file is inspectable.
- **A new failure mode**: a child that dies without writing its summary. The parent checks for the files
  and raises `RunError` with the child's output, rather than returning a partial result.
- **`ExtensionUnavailableError` keeps its meaning**: the child exits with a distinct code when PyFVS is
  not importable, and the parent re-raises the same type rather than wrapping it in a generic error.
- **The run directory gains two files**, `summary.csv` and `variants.json`, and the documentation that
  lists what a run writes is corrected with this change.

## What this does not decide

- **Block keywords.** A separate gap, triaged to a proposed `P7`.
- **Where a caller's population and keyword set come from.** Unchanged.
