Reviews
=======

The project's own review cadence. It exists because a backlog that nobody reads becomes a list of
apologies, and because a gate that stopped testing something looks exactly like a gate that passes.

The cadence is the maintainer's to hold. The agent records each review; the maintainer decides whether
the interval is right.

When
----

**Quarterly, on the first Monday of January, April, July and October.** That is the interval the
workflow's model log already assumes, and a quarter is long enough for a backlog to change and short
enough that a gap does not go unnoticed.

**The first review was the seed rather than a scheduled one**: it was held on 2026-10-25, at the end
of `P6.3` (#40), when the cadence was set, and it is off the schedule by design. The schedule starts
with the January 2027 row below.

A review that was not held is visible in the table below, because the row for its date has no review
against it. That is the whole reason the table is here: "quarterly" on its own is a sentence, not a
commitment.

Who
---

The maintainer holds the review and approves its record. The agent prepares it: it gathers the state,
checks each triage row's reopen condition, and writes the record. **The agent does not approve its own
review**, for the same reason it does not verify its own phase close-out.

What a review covers
--------------------

1. **The triage backlog**, `notes/triage.md`. Every disposition is re-read, and **any row whose reopen
   condition has been met is reopened**. A disposition changes only in a change set that names the
   review that changed it.
2. **The release.** What shipped, what the last phase changed, and whether the published artefacts still
   match the source at the tag.
3. **The model log's re-checks**, `docs/agents/roles-and-models.rst`. Each row's evidence is recorded
   against the work done since the last review, and a row that stays unproven says so.
4. **The gates.** The dashboard's six, the mutation harness's count, and the tests that only run where
   the extension is built. A gate that no longer exercises what it names is the failure this item is
   for.
5. **The open proposals**, including anything filed upstream, and whether any has been answered.

Where the records live
----------------------

One file per review, `notes/reviews/YYYY-MM-DD.md`, named for the date it was held. **A record is not
edited after the maintainer approves it**; a later review corrects an earlier one by saying so, which is
the rule this project applies to its approved reports. **Before approval it is a draft**, and a
Verifier's findings correct it, exactly as `P2`'s close-out report was revised before it was approved.
The record says when it was revised and why.

The schedule
------------

.. list-table::
   :header-rows: 1
   :widths: 45 45

   * - Due
     - Discharged by
   * - 2026-10-25, the first review, at ``P6.3`` (#40)
     - ``notes/reviews/2026-10-25.md``
   * - 2027-01-04
     - not yet due
   * - 2027-04-05
     - not yet due
   * - 2027-07-05
     - not yet due
   * - 2027-10-04
     - not yet due

A row that is past its date and still says "not yet due" is a missed review, and the next record says
which one was missed and why.

What a review does not do
-------------------------

- **It does not change the code.** A finding is a task proposal, not a patch.
- **It does not close a phase.** Phases close on their own close-out, with their own approval.
- **It does not re-verify a phase.** The Verifier does that, per close-out, and this review reads the
  results.
