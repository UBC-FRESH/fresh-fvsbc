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
     - ``P5.2`` review
   * - 2026-10-23
     - Verifier, for verification and close-out evidence review.
     - A separate session on the same model as the Implementer, reading only the committed artefacts.
     - **Unproven.** Named before its first run, so it has no results yet. The workflow's rule says the
       independence comes from the gates rather than from a different model, so a separate session is
       the smallest change that creates it. Its first run verifies ``P2``'s close-out report, and its
       findings are the evidence for or against this row.
     - ``P5.2`` review

A model that misses the bar for a family is replaced for that family, and the replacement is logged
with its reason. The workflow's seed project logs one further choice, ``claude-haiku-5-5`` as
Implementer and Verifier for its own Phase 3, on the evidence of its commits' gate results. This
project has not trialled a second model and does not claim one.

Re-checks
---------

**Every row is re-checked at this project's quarterly review**, whose cadence and records are in
:doc:`reviews` and ``notes/reviews/``, and a row is re-checked sooner when the provider or the model
changes. A re-check that keeps a choice adds a row with its new date and its evidence; a re-check that
changes one adds a row for the new choice. The first review, on 2026-10-25, recorded the evidence for
both rows below and changed neither. **An earlier revision of this paragraph named the seed workflow's
``P5.2``**, which is a task in that repository rather than this one's cadence.
