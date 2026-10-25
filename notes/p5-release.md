# Phase 5 plan: Release and deploy

Phase: P5 Release and deploy
Parent issue: the issue this plan is committed with
Branch: `feature/p5-release`
Roadmap: `ROADMAP.md`, section "Phase 5: Release and deploy"
Predecessor: `P4` closed as `446c25f`, report in `notes/reports/p4-closeout.md`

## Goal

Tag a release, publish the docs, and verify the published artifacts from a clean checkout.

## What a release means for this project

`fresh-fvsbc` wraps a pinned build of one FVS variant. A release therefore has to say, in its own text,
**which build it wraps** — the fork commit, the FVS source submodule, and the variant list — because a
result produced with it is only reproducible against those. That is the provenance contract's argument,
and a release note that omits it would be the one place the project's own discipline lapses.

## Scope

1. **`P5.1` The release notes and the known-gaps list.** What the release is, what it wraps, what is
   verified and how, and **what is not** — including the four items `P4` carried forward. The gaps are
   the part a reader needs most and the part a release is most tempted to soften.
2. **`P5.2` Tag, publish, and verify from a clean checkout.** A tag, the release with its notes, the
   published documentation, and an install from a clean environment that runs the command. **Each of
   those is a separate action with its own approval**, named with its exact command, as `AGENTS.md`
   requires.

## What is not in scope

- **Any code change.** If the release reveals a defect, it is a finding and a task, not a patch made
  under a tag.
- **`run_case`'s non-re-entrancy.** It is the largest open item and it belongs in a phase that can
  change the public API, not in a release.
- **Block keywords.** Same reason.
- **A wheel on PyPI.** The roadmap's goal says tag, publish the docs, and verify; a distribution to an
  index is a separate decision with an external account attached, and it is not implied here.

## The order, and why

`P5.1` first: the notes are what the tag points at, and writing them is the last chance to find that
something claimed as working is not. `P5.2` second, and it stops at each approval gate.

## Risks

- **A release that claims more than the record supports.** `P2`'s report and `P3`'s both published
  claims that were wrong, and `P4` caught one of them. The known-gaps list is the mitigation, and the
  Verifier reads it before the tag.
- **Publishing is irreversible in practice.** A tag can be deleted and a release can be edited, but a
  reader may have taken a copy. Every publishing action is named, approved, and read back.
- **The published docs are generated from the source and can drift.** `P5.2` verifies the published
  pages against the source rather than trusting the deploy job.

## Acceptance criteria, proposed

- The release notes name the build the release wraps: the PyFVS fork commit, the FVS source submodule,
  and the variant list.
- The known-gaps list names every open item the `P2`, `P3` and `P4` reports carry, each with the reason
  it is open.
- A clean checkout installs the release and runs `python -m fresh_fvsbc --help` and one case.
- The published documentation matches the source at the tag, checked page by page for the pages that
  changed in the last phase.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Open proposals, not tasks

- **`run_case`'s non-re-entrancy**, which needs a decision about the public API: a guard that refuses a
  second run in one process, a subprocess per run, or a documented restriction.
- **`YSM-SkyRanch`'s three stands**, unexplained since `P2.3`.
- **`scripts/check_workflow.py` and the POSIX temporary path**, which needs its own evidence because a
  new pattern can false-positive on legitimate prose.
