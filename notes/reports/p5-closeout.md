# Phase close-out report: P5 Release and deploy

Phase: P5 Release and deploy
Parent issue: #31
Pull request: #34, `feature/p5-release` into `main`, opened as a draft when the phase was activated
Evidence head: `2251fca`, the head that the gates in section 3 cover. **The branch carried 5 commits and
5 CI runs at that head.**
Report commit: the commit that adds this revision of the report. Its CI run is posted on the pull request.
Date: 2026-10-25
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

**The maintainer approved the tag, the release and the verification on 2026-10-25.** They run after the
merge, because a tag points at a commit on `main`, so they are carried out as part of this close-out
rather than asked for again.

1. Squash-merge pull request #34, and delete the branch `feature/p5-release`:
   `gh pr merge 34 --squash --delete-branch`.
2. Tag the merge commit, and push the tag:
   `git tag -a v0.1.0 -m "fresh-fvsbc 0.1.0, wrapping FVSbc at e95172b" <merge-sha>` then
   `git push origin v0.1.0`.
3. Create the release from the notes the Verifier read:
   `gh release create v0.1.0 --title "fresh-fvsbc 0.1.0" --notes-file RELEASE_NOTES.md`.
4. **Verify from a clean checkout**: a fresh virtual environment, the tagged package installed, a build
   of the pinned variant, `python -m fresh_fvsbc --help`, and one case.
5. Verify the published documentation against the source at the tag. **The publication needs no command**:
   `.github/workflows/docs.yml` deploys Pages on push to `main`, so the merge publishes it.
6. Close parent issue #31 with a closeout comment that cites the merge and the tag.
7. Launch `P6`, after approving its scope in section 6.

**Settings changes: none.** No branch protection, repository setting, or account changed in this phase.
The Pages deployment is the one that `P0` approved and that runs on every push to `main`.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The release notes name the build the release wraps: the PyFVS fork commit, the FVS source submodule, and the variant list | `RELEASE_NOTES.md`, commit `af13358`: the fork at `e95172b`, the FVS source at `ef5fa847`, and `BC` at status `OK`, **read from `src/fresh_fvsbc/provenance.py` and from the built extension rather than quoted** | met |
| The known-gaps list names every open item the `P2`, `P3` and `P4` reports carry, each with the reason it is open | `RELEASE_NOTES.md` lists **twelve**, assembled by grepping the three reports and reconciled by the Verifier's reverse check, which added three the implementer had missed: a run is not thread-safe, the reader exposes two of 32 tables, and the adapter requires `species` and `tree_age` | met, with the reverse check as the evidence that it is complete |
| A clean checkout installs the release and runs `python -m fresh_fvsbc --help` and one case | **Run on 2026-10-25 against the branch head `2251fca`, which is the tree the tag will carry** (a squash-merge changes the commit, not the tree). A clean `git clone` at that head, a fresh virtual environment, the pinned variant built there, the package installed, and: `fresh_fvsbc.__version__` is `0.1.0`, `python -m fresh_fvsbc --help` exits 0, and one case exits 0 with a summary of 5 rows and 22 columns and a provenance record carrying `0.1.0`, `e95172b` and `ef5fa847` | met |
| The published documentation matches the source at the tag, checked page by page for the pages that changed in the last phase | **Not yet run.** It is action 5, and the pages that changed are `usage.rst` (added in `P3.6`) and the reference pages corrected in `P3` and `P4` | **pending** |
| `python scripts/dashboard.py` exits zero on the head commit of the phase branch | Green on `2251fca`, locally, and CI run `40140012732` succeeds on that exact head | met |

**Four met, one pending by construction.** The fifth is the published-documentation check, which cannot
run before the merge because Pages deploys on push to `main`. **Its output is recorded in the closeout
comment on #31, and if it fails that is a finding and the phase's status is corrected rather than the
check softened.**

## 2. Workflow compliance

- **Parent issue before the branch.** `#31` was created before `feature/p5-release` was cut from
  `446c25f`, and the plan `notes/p5-release.md` was committed in `54887dd`, the activation commit,
  before any task's code.
- **A plan before each task.** `#32` and `#33` carry plan comments; `P5.2`'s records the approved
  commands and the order they must run in.
- **Branch from `main`.** `446c25f`, the squash-merge of `P4`.
- **Commit messages that start with a task ID.** All five commits at the evidence head.
- **Gates for each commit.** Section 3.
- **Roadmap and changelog in step.** Each task's change set carries its roadmap tick and its changelog
  entry.
- **Approval gates.** The three publishing actions were **presented with their exact commands, their
  cost, and a recommendation before being asked for**, and approved on 2026-10-25. `P5.1`'s release
  notes were read by the Verifier **before** the tag, which is what the task's plan required.
- **Nothing was published before approval.** No tag, release, or deployment ran in this phase before
  the maintainer's decision.

## 3. Gate evidence

- **On the evidence head `2251fca`:** all six dashboard gates green, run locally, and CI run
  `40140012732` succeeds on that exact head.
- **Per commit:** every commit's changelog entry records the dashboard result for its change set.
  **Those records are the implementer's claims, not independent evidence.**

## 4. CI evidence

**Five runs, five successes.**

| Run ID | Head commit | Conclusion | Task |
| --- | --- | --- | --- |
| `40140012732` | `2251fca` | success | `P5.1` roadmap |
| `40139858444` | `2649dc7` | success | `P5.1` skip description |
| `40139529988` | `9c87f98` | success | `P5.1` Verifier corrections |
| `40139111249` | `af13358` | success | `P5.1` release notes |
| `40137705237` | `54887dd` | success | the activation commit |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| **The release would have shipped wrong metadata.** The notes named `0.1.0` while `pyproject.toml` and `__init__.py` said `0.0.0`, and the plan had deferred the version bump to `P5.2` | The plan treated the version as a tagging concern, when a tag must point at a commit whose own metadata agrees with it | Both files now say `0.1.0` in `9c87f98`, the version test passes, and the plan's error is recorded in the changelog rather than quietly fixed. Found by the Verifier |
| **The notes overstated the oracle twice.** They said the comparison was "exact on the toolchain that produced the oracle", which was wrong both ways: the oracle is a **2022 `FS2022.4` fixture**, and after `P4.2`'s child-process fix the comparison passes on the development machine **and** on CI's runner | The claim was carried over from `P4`'s earlier, incorrect explanation of the CI failure | Rewritten in `9c87f98`, and gap 4 now states the fixture's age and that the FVS project's own checker skips this variant |
| **Three gaps were missing from the list**, and it claimed to be complete | The list was assembled from the reports' headlines; the reverse check found what the headlines omitted | A run is not thread-safe, the reader exposes two of 32 tables, and the adapter requires `species` and `tree_age`. "Listed in full" is gone, and the list has twelve items |
| **The README said `P2` was active** at the start of this phase, four phases after it closed | The status section was not updated when the phase changed | Corrected in `af13358`, and it now links the release notes. A release must not ship a README that contradicts the roadmap |
| **Two verification limits were missing from the notes**: the command's exit codes 1 and 2 are tested with a faked drive and in a subprocess, and the synthetic run is shown to reproduce rather than to be right | Written from the changelog rather than from `notes/reference/p4-acceptance.md`, which carries the limits | Both are stated in the same sentence as the claim they qualify |
| **The implementer described the skips backwards** in the last Verifier pass: on this branch the two skips are the tests that need the extension, not the tests that the extension is absent | The two environments' skip sets were conflated | Corrected in `2649dc7` and checked against `pytest -rs` in both environments |

## 6. Next phase

`P6` is "Operate and maintain", and this report can say what it inherits. **Two items outrank the rest
because they are about the public API rather than about a test:**

1. **`run_case` is not re-entrant in a process, and a run is not thread-safe.** Two runs in one process
   are not independent, and a run changes the process's working directory. A guard, a subprocess per
   run, or a documented restriction are the routes, and the choice changes the public API's contract.
2. **Block keywords are refused, not written.** A run that needs `COMPUTE` cannot be expressed.

The rest, as the release notes carry them: `YSM-SkyRanch`'s three stands, the validator's missing
POSIX-temporary-path pattern, `run.py`'s coverage split, the reader's two-of-32 tables, the adapter's
required fields, the command's comma limit, `-O0` writing no database, and the package needing a
separately built extension.

## 7. Decision

Approve recommendations 1 to 7, or amend them. **Two of the phase's five criteria are pending by
construction**, and the phase is not complete until their output is recorded; the report will be
amended with that output rather than the phase closed on a promise.

## Verification before approval

- `python scripts/dashboard.py` on `2251fca`: six gates green.
- CI run `40140012732` on `2251fca`: five jobs successful.
- `python scripts/mutation_check.py`: `24 of 24 mutations caught`.
- The release notes read by the Verifier twice, eight findings then one, all closed.
