Agent roles and models
======================

This page records **this project's** roles and the model chosen for each, and the log of those
choices. The roles, and the rule for choosing a model, are the workflow's own, at
``docs/agents/roles-and-models.rst`` in `UBC-FRESH/ubc-fresh-dev-workflow
<https://github.com/UBC-FRESH/ubc-fresh-dev-workflow>`__. This page does not restate them, it applies
them.

The roles, in one line each
---------------------------

- **Planner** drafts the phase, its tasks and subtasks, the issue bodies, and the ADRs. The plan of
  record is ``ROADMAP.md``, and the detail is the focused plan under ``notes/``.
- **Implementer** makes one bounded change at a time, with its tests in the same change set, and
  commits it with its task ID.
- **Verifier** runs the gates, reproduces a red result, and checks each claim in a close-out report
  against its evidence.
- **Maintainer** approves each gate, and each action that changes a setting, publishes, or touches
  private data.

The verifier is separate from the implementer
---------------------------------------------

The workflow states the rule and its reason: *a verifier is separate from the implementer, even when
one model runs both, because one model in two roles is still one reviewer; the independent check
comes from the gates, which are mechanical, and from the evidence rules.*

This project applies it as follows.

- **The independent check is the gates.** ``python scripts/dashboard.py`` runs six of them, and
  ``scripts/check_workflow.py`` a seventh. A claim in a report is not evidence on its own.
- **The Verifier is a separate session.** It reads only the committed artefacts — the diff, the issue
  body and its comments, the plan, the report — and not the working session's memory. It publishes its
  findings as a comment on the task issue, and each finding names a commit, a command, or a run.
- **The Verifier does not resolve its own findings.** A finding is closed by evidence, not by the
  implementer's assertion.

The model log
-------------

One row per choice. A row is dated, names its role and task families, states its model and its
evidence, and says how strong that evidence is. A changed choice adds a row; an old row is not edited.

.. list-table::
   :header-rows: 1
   :widths: 11 25 22 32 10

   * - Date
     - Role and task families
     - Model choice
     - Evidence
     - Re-check
   * - 2026-10-23
     - Planner and Implementer, for planning, implementation, and documentation.
     - ``deepseek v4.1 flash``, through OpenCode's gateway.
     - **Unproven, and the evidence runs against it.** The choice was in place while ``P2`` was planned
       and built, and a workflow audit then found the plan of record missing, the roadmap's subtask
       level never written, and several self-reports unreliable. An audit is evidence against this row,
       not for it. No comparison was run, and one session in all three of Planner, Implementer and
       Verifier is one reviewer by the workflow's own rule.
     - ``2026-10-25`` review
   * - 2026-10-23
     - Verifier, for verification and close-out evidence review.
     - A separate session on the same model as the Implementer, reading only the committed artefacts.
     - **Unproven.** Named before its first run, so it has no results yet. The workflow's rule says the
       independence comes from the gates rather than from a different model, so a separate session is
       the smallest change that creates it. Its first run verifies ``P2``'s close-out report, and its
       findings are the evidence for or against this row.
     - ``2026-10-25`` review
   * - 2026-10-25
     - Planner and Implementer, re-check at the first quarterly review.
     - Unchanged.
     - **Still unproven, and the evidence is mixed.** A plan was written before the code in ``P3``,
       ``P4``, ``P5`` and ``P6``, and per-task plan comments were posted from ``P3.5`` on, but
       ``P3.1`` to ``P3.4`` carry none. The plan of record went stale twice: ``P3``'s roadmap notes
       were four phases out of date and were found in ``P6``, and ``P4.4``'s premise was false when
       the task opened. A conclusion in an approved report was wrong. **The Verifier caught the
       conclusion and the release metadata; it did not catch the stale roadmap or ``P4.4``'s false
       premise.**
     - ``2027-01-04``
   * - 2026-10-25
     - Verifier, re-check at the first quarterly review.
     - Unchanged, a separate session on the same model.
     - **Supported, with a stated limit.** Six artefacts across fifteen passes, findings in the tens,
       and **one conclusion changed**: ``P3``'s third acceptance criterion was reported as "not met,
       and a false requirement" and is met. It also caught a release that would have shipped ``0.0.0``
       metadata under a ``0.1.0`` tag, an ADR whose own cost figures did not reproduce, and a triage
       row whose reopen condition fired on the normal case. **The limit**: it missed ``P3``'s claim
       that nothing asserted every name in ``__all__`` resolves, which had been false since ``P2``; it
       checks claims about the work and not every file the work cites.
     - ``2027-01-04``

**An old row's choice and its evidence are not edited.** A pointer may be corrected when it names
something that no longer exists, and the correction is recorded in the review that made it: the two
2026-10-23 rows' Re-check cells named the seed workflow's ``P5.2``, and the 2026-10-25 review corrected
them to this project's review dates.

A model that misses the bar for a family is replaced for that family, and the replacement is logged
with its reason. The workflow's seed project logs one further choice, ``claude-haiku-5-5`` as
Implementer and Verifier for its own Phase 3, on the evidence of its commits' gate results. This
project has not trialled a second model and does not claim one.

Re-checks
---------

**Every row is re-checked at this project's quarterly review**, whose cadence and records are in
:doc:`reviews` and ``notes/reviews/``, and a row is re-checked sooner when the provider or the model
changes. A re-check that keeps a choice adds a row with its new date and its evidence; a re-check that
changes one adds a row for the new choice. **The first review, on 2026-10-25, added the two rows at
the end of the table above**, which is that rule applied. **An earlier revision of this paragraph named the seed workflow's
``P5.2``**, which is a task in that repository rather than this one's cadence.
