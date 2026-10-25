# Phase 6 plan: Operate and maintain

Phase: P6 Operate and maintain
Parent issue: the issue this plan is committed with
Branch: `feature/p6-operate`
Roadmap: `ROADMAP.md`, section "Phase 6: Operate and maintain"
Predecessor: `P5` closed as `c528f22`, release `v0.1.0` at `ef11f94`

## Goal

Keep the project current: triage what is open, fix the one defect that can give a caller silently wrong
numbers, and set a review cadence with its first review recorded.

## The three tasks, and why this order

1. **`P6.1` Triage the twelve gaps.** Every item in `RELEASE_NOTES.md`'s known-gaps list becomes one of
   three things: **fix now**, **fix later** with a named phase, or **accepted** with the reason it will
   not be fixed. A gap that is nobody's decision is the state the project has been in since `P2`, and
   triage is what ends it. **This goes first because it decides what the rest of the phase is.**
2. **`P6.2` Make two runs in one process safe.** `run_case` is not re-entrant: a second run inherits the
   first one's Fortran state, so two runs in one process are not independent, and the directory
   isolation the module documents is not enough. **This is the only gap that can give a caller silently
   wrong numbers from a released package**, which is why it is a task and not a triage line.
3. **`P6.3` Set a review cadence and record the first review.** The roadmap's own goal, and the last
   thing: a cadence with nothing to review would be paperwork, and after `P6.1` there is a triaged
   backlog to review against.

## The mechanism for `P6.2` is not decided here

Two routes, and they change the public API's contract differently:

- **A guard** that refuses a second run in one process, with a message that says to use a subprocess.
  Cheap, honest, and it turns a silent wrong answer into a loud refusal. **It would break the current
  test suite**, which runs several projections in one process, so the tests would move to subprocesses.
- **A subprocess per run**, so the API keeps working and the isolation is real. The cost is that
  `FVS.summary` comes back across a process boundary, which is a serialization problem.

**I will bring that back as its own decision with the evidence from a spike**, because a guard changes
what a caller may do and a subprocess changes what the API returns.

## What else this phase's activation fixes

**The roadmap's "Detailed Next Steps Notes" section is stale by four phases.** It lists the CI quality
matrix, `ADR 0004`'s status, `FVS_Compute`'s reachability, the oracle comparison, and the workflow
revision as open. All five were closed between `P2` and `P4`, and `AGENTS.md` already pins the workflow
revision. The section is rewritten to point at the twelve gaps and the tasks that address them, and it
says the earlier list was stale rather than quietly deleting it.

## Out of scope

- **The block-keyword capability.** Triaged in `P6.1`; a model change with a research burden does not
  belong in a maintenance phase.
- **`YSM-SkyRanch`'s residual.** Understanding, not a defect, and it needs a research question of its
  own.
- **Any release.** `v0.1.0` is out; the next one follows a phase that changes the package.
- **Any settings change.** None is proposed.

## Risks

- **Triage that becomes a wish list.** The mitigation is that every item ends in one of three states,
  and "accepted" has to carry a reason a reader can disagree with.
- **A guard that breaks callers.** It changes the API's contract, which is why the mechanism comes back
  as a decision rather than being chosen here.
- **A cadence nobody keeps.** The first review is recorded in this phase; whether the second happens is
  the maintainer's to hold, and the plan says so rather than pretending a schedule enforces itself.
