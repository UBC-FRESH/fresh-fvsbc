# Phase close-out report: P2 Contracts and prototype

Phase: P2 Contracts and prototype
Parent issue: #10
Pull request: #16, `feature/p2-contracts-prototype` into `main`
Evidence head: `fc5cef2`, the head that the gates in section 3 cover
Report commit: the commit that adds this revision of the report. Its CI run is posted on the pull request.
Date: 2026-10-23
Status: queued for approval. Not merged. **Revised** after a Verifier session checked every claim in the
first revision; its findings are attached to #15 and its corrections are in section 5.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #16, and delete the branch `feature/p2-contracts-prototype`.
2. Close parent issue #10 with a closeout comment that cites the merge commit.
3. Launch `P3`, after approving `P3`'s plan: create its parent issue, its branch, its child issues as
   sub-issues, and its roadmap subtask lines, then start its first task. **A plan first, because this
   phase's central failure was having none**: `session-protocol.rst` requires the plan to be written
   before anything is edited, and `workflow-model.rst` puts the plan of record in `ROADMAP.md` with the
   detail in `notes/`. Section 6 proposes the scope.

Settings changes, each with its exact command. Each one runs only after its own approval.

- **Recommended, not run: the CI quality matrix.** Three jobs — `quality`, `dashboard`, `pre-commit` —
  each run on Python 3.12 alone, where `quality-gates.rst` requires the quality job on **3.11 and
  3.12** and names four required contexts. **The change is two parts, and the second must not be run
  alone.** First, the workflow file changes **two things about the `quality` job**: its `name:` line
  becomes `Quality gates, Python ${{ matrix.python-version }}`, which is what the specification's own
  `ci.yml` uses, and it gains a `[3.11, 3.12]` matrix. **Both are required.** Adding a matrix to the
  current static `name: Quality gates` would produce contexts called `Quality gates (3.11)`, which no
  required check names, and the protection change would then demand checks that never report. **An
  earlier revision described only the matrix, and the second Verifier pass caught it.** Second, branch protection
  is set with the specification's own command, which **sets all four contexts with `PUT`**:

  ```bash
  gh api -X PUT repos/UBC-FRESH/fresh-fvsbc/branches/main/protection --input - <<'JSON'
  {
    "required_status_checks": {
      "strict": true,
      "contexts": [
        "Quality gates, Python 3.11",
        "Quality gates, Python 3.12",
        "Green dashboard summary",
        "Pre-commit parity"
      ]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": null,
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "required_linear_history": true
  }
  JSON
  ```

  **A warning worth keeping in the report.** The first revision of this report printed a `PATCH` that set
  two contexts. `PATCH` **replaces** `contexts`, so run as written it would have dropped the
  `Green dashboard summary` and `Pre-commit parity` required checks and installed a context
  (`Quality gates, Python 3.11`) that no job produced. The Verifier found it before approval. The command
  above is the specification's, and it sets the four contexts the specification names.

  The body is the specification's, **plus `required_linear_history: true`**, which `P1`'s close-out
  records as a deliberate addition stricter than the specification. A `PUT` replaces the whole body, so
  omitting it would silently relax a rule this project chose. **The first revision carried only the two
  `strict` fields**, which is not the specification's body; the second Verifier pass caught it. After
  running it, read the rule back with
  `gh api repos/UBC-FRESH/fresh-fvsbc/branches/main/protection --jq '{.required_status_checks, .required_linear_history}'`
  and confirm `required_linear_history` survived, which the agent has not tested and the report does not
  claim.

  **Default: approve the workflow change and hold the protection change until the matrix has run once**,
  so that the two new contexts exist before protection requires them.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| `docs/` states the interfaces and the data contracts: the tree-list input, the keyword set, the parsed outputs, and the provenance record | `tree-list.rst`, `keywords.rst` and `outputs.rst` each name the FVS commit they were read from, `ef5fa84`. `provenance.rst` does not, and says why: the contract is this project's own design and is not read from FVS. `nemora-ingest.rst` does not either, because it describes `nemora`'s output shape rather than an FVS format. **An earlier revision of this cell listed `nemora-ingest.rst` among the pages naming the commit, which is false; the second Verifier pass caught it** | met |
| A prototype runs on synthetic data and exercises each contract, with checks that can fail | `src/fresh_fvsbc/{treelist,keywords,nemora,outputs,provenance}.py` with fifteen test modules, pytest green; a real BC run on a tree list this project wrote, in `notes/reference/synthetic-run.md` | **met with a stated limit.** Falsifiability is evidenced by mutations applied **by hand in the session** and recorded in `CHANGE_LOG.md`; **no committed harness reproduces them**, so a reader cannot re-run the check. Section 5 records it, and section 6 proposes the fix |
| The build question in ADR 0001 is answered with evidence: either `bc` builds, or the patch the FVS source submodule needs is recorded | `notes/adr/0004-the-fvsbc-build-recipe.md` numbers twelve items; `notes/reference/fvsbc-patchset.diff.gz` touches ten files, nine modified and one new | **met with a stated limit.** The committed diff can be inspected, but the round trip that reproduces the working tree cannot be re-run here, because the base commit `ef5fa84` is in a fork that is not this repository. Verified once, in a scratch clone, and not verifiable from the record |
| `python scripts/dashboard.py` exits zero on the head commit of the phase branch | green on `fc5cef2`; six gates; CI run `40035213071` succeeds on that exact head | **met on 3.12 only.** The specification requires the quality job on 3.11 and 3.12. Stated as a limit, with the settings change above as the fix |

## 2. Workflow compliance

- **Parent issue before the branch.** `#10` was created 2026-10-21T07:39:56Z; the branch's first commit
  `a4ad4ea` is 2026-10-21T07:41:05Z. **The first revision of this report quoted the activation comment's
  timestamp here, and the Verifier caught it.**
- **Branch from `main`.** Merge-base `cbcadf3`, the head of `main` at `P1`'s close-out.
- **Commit messages that start with a task ID.** 40 of the 41 commits on the branch since `main`. The
  one that does not starts with the phase ID, and it is the phase activation.
- **Gates for each commit.** Section 3.
- **Roadmap and changelog in step.** Both changed in the same change set as the work they record for
  every task whose change set touched them. **No mechanical test exists for "same change set"**, so this
  is a claim about the record rather than a verified fact. Two exceptions are disclosed in section 5.
- **Child issues closed with closeout evidence.** `#11` names `b426635`, `#13` names `84b5ec7`, and `#14`
  names its per-move commits. `#12` and `#15` remain open, and section 5 now records why for each.
- **Approval gates.** The repository rename in `P2.4` was approved before it ran. Pages was approved and
  executed in `P0`'s close-out, and branch protection in `P1`'s. The approval dialogues themselves are
  not committed, so the reports are the record. **This phase published outside the repository**: it filed
  `ubc-fresh-dev-workflow#45` and `#46`, and the `P2.4` rename republished the project's public URL and its Pages
  path. **The first revision claimed the opposite, and the Verifier caught it.** Both were approved
  actions.

## 3. Gate evidence

- **On the evidence head `fc5cef2`:** all six dashboard gates green, reproduced by the Verifier, and CI
  run `40035213071` succeeds on that exact head.
- **Per commit:** every commit's changelog entry records the dashboard result for its change set.
  **Those records are the implementer's claims, not independent evidence**, and this report does not
  present them as evidence. Criterion 2 in section 1 is marked as met with the stated limit that follows
  from this: the falsifiability evidence is not reproducible from the repository.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| `40035213071` | `fc5cef2` | success | `pull_request`, on the evidence head |
| `40035298416` | `fc83cd9` | success | `pull_request`, the first report commit |
| `40036088709` | `0b6542d` | success | `pull_request`, the revised report, the head the Verifier's second pass covers |
| none before #16 | — | — | A phase branch gets runs **while its pull request is open**, which is why `feature/p0-bootstrap` and `feature/p1-scope-design` have runs and this branch had none until #16 opened. The first revision said no phase branch had ever had a run, which the run list contradicts |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| **The first revision of this report overstated.** It asserted a mutation harness that exists nowhere in the repository or its history, printed a branch-protection command that would have dropped two required checks, repeated the false citation in section 6, and carried four wrong numbers | The same class of failure the report itself documents: a plausible claim asserted more strongly than the evidence, written by the same session that had just been criticised for it | Found by the Verifier session before approval, and corrected in this revision. Its findings are attached to #15, and its verdict is cited in the header. It is the process catching the implementer, which is what the row records rather than a claim about its value |
| **A whole task's work ran with no child issue.** Thirteen commits labelled `P2.2` delivered `P2.3`'s work, and `#13` was created after it; twenty-four commits carry the `P2.2` label | The build spike was treated as an unplanned investigation rather than as a task, so the scaffold rule in `AGENTS.md` was not applied | The commits are not rewritten. `CHANGE_LOG.md` and the plan disclose it, `#13` was created retroactively, and the rule is now applied: no commit before its child issue exists |
| **The roadmap carried no subtask level, and no focused plan existed in `notes/`** | The third level of the three-level structure was never written down, and the detail went into the issue body and fifteen prose items in the roadmap | `notes/p2-contracts-and-prototype.md` written, and the roadmap's `P2` block carries the subtask level: 39 lines when it was added at `c0ba0c9`, **41 at the evidence head**. The first revision gave only the stale figure |
| **`README.md` claimed no variant had been built** while the roadmap and the changelog recorded that it did, violating `P0`'s own acceptance criterion | Nothing updated the front door when the build succeeded | Corrected at `c0ba0c9`. The stale sentence stood for **31 commits**, not the "six" the first revision claimed — the Verifier could not reproduce that number and neither can this revision |
| **Parent issue `#10`'s child checklist listed two of its four children**, its scope named two tasks, and no scope-change comment existed | `P2.3` and `P2.4` were added without reconciling the parent body | One body edit and one scope-change comment (`c0ba0c9`), now listing five children and five tasks |
| **Closed task issues carried a stale `Status:` and an unfilled `Completion metadata:`**, and `#12`'s status used a value no template defines | The closeout comment was posted but the body was not updated | Corrected by issue edits, which are **not commits** and so leave no commit record; the previous values are not checkable from the repository |
| **`#12` and `#15` remain open at the close-out.** `#12`'s one open subtask is deferred, not unfinished; `#15`'s last subtask is the Verifier run | `#12`'s open item is a limitation with a known remedy in `P3`; `#15`'s is the verification the phase's own process requires | Section 6 carries `#12`'s item into `P3`; `#15` closes after this report is approved |
| **Four claims published on 2026-10-21 were wrong**, and three were retracted only in conversation | Ad hoc comparison scripts outside the repository, never checked against a known-good case | Retracted in the files. The standing proposal is to promote the comparison into a repository test that can fail |
| **A false citation was published in an accepted ADR, and the accepted ADR was then edited** | `ADR 0005` claimed a precedent that does not exist here, and its body was corrected after acceptance | Corrected and disclosed, but **the correction should have been a new ADR**, since `notes/README.md` says an accepted ADR is superseded rather than rewritten. The rule was applied for the rest of the phase — until section 6 of this report broke it again in a smaller way, which the Verifier also caught |
| **A test that could not fail** | The output reader limited a severity search to a message's leading tokens, which is unobservable because first-match-wins gives the same answer | The limit was removed and the test rewritten (`dcb9e12`) |
| **No mutation harness is committed**, so the falsifiability evidence cannot be re-run by a reader | The mutations were applied by hand in the session; the harness was an ad hoc shell step, and the first revision's claim that it "now asserts its anchor is unique" describes a change that was never made | **Corrected here rather than papered over.** Section 6 proposes committing the harness as a `P3` task |
| **The `P2.3` validation limits are absent from the first revision of this report** | They are in the plan and the changelog but were not carried into the report, so a reader of the report alone would not see them | Added: the oracle is a 2022 fixture; the FVS project's own checker skips this variant; the residual on three dense stands of the second case is attributed, not proven, to upstream changes; the patch set is **banked, not pushed**; and at `-O0` the built variant processes no stand at all, a robustness limit whose cause is not established |
| **`ADR 0004` is still `Status: proposed`**, its `Context` contradicts a later paragraph, and its `Issues:` names `#12` where the roadmap assigns it to `P2.3` | The status was never brought to `accepted` after `P2.3` closed | **Not the agent's act.** The plan's proposal 3 recommends the maintainer accepts it and that its `Context` and `Issues:` are corrected together |
| **The CI quality matrix runs on one Python version** where the specification requires two, and the seed's own CI template does too | The seeded `ci.yml` was never changed, and branch protection matches it | **Not run.** Named with the corrected command in the Recommendation; the criterion is marked as met with the limit; and the seed defect is filed upstream as `ubc-fresh-dev-workflow#46` |
| **The project had no roles page and no model log, and no reviewer was ever named** | Neither the agent nor the workflow audit named the gap until the maintainer asked who the reviewers were | `docs/agents/roles-and-models.rst` added (`bc793cb`), both rows marked `Unproven`, and this Verifier run is the first evidence for the Verifier row |
| **The workflow revision was unpinned** | `AGENTS.md` named the workflow with no path, URL, or revision | Pinned to `93b5cd9` of 2026-10-13 (`fc5cef2`), and the seed's template defect filed as `ubc-fresh-dev-workflow#45` |
| **The seed's roadmap template omits task issue numbers** where `workflow-model.rst` requires them | A defect in the seed | Reported upstream as `ubc-fresh-dev-workflow#44`, during `P1` |

## 6. Next phase

**`P3` Build.** Its goal, from `ROADMAP.md`, is to implement the agreed scope, one task at a time. It is
`planned` with a placeholder task and a placeholder criterion, and no plan.

**Recommended default for each open choice, with its reason.**

1. **Write `P3`'s plan before doing any of its work.** Reason: `session-protocol.rst` requires the plan to
   be written before anything is edited, and this phase's central failure was having none. **The first
   revision attributed that requirement to `workflow-model.rst`, which does not state it; the Verifier
   caught the false citation.**
2. **Proposed scope.** The BC layer proper: the public API over the five prototype modules; the run
   orchestration that assembles a keyword set, writes a tree list, drives FVS, and returns outputs with
   provenance; the command-line entry point; and the build wiring that makes the pinned fork's BC variant
   reproducible from a clean checkout. Reason: `notes/scope.md` and ADRs 0001 to 0003 bound it. **The
   prototype is validated on synthetic data**; what was validated against the FVS project's own BC test
   data is the **built variant**, under `P2.3`, and the first revision conflated the two.
3. **Carry `P2.2`'s open subtask into `P3` as a task**: building the standalone `FVSbc` executable, which
   is the only route to `FVS_Compute` and `FVS_Summary_Metric`. Reason: a limitation with a known remedy,
   and out of `P2`'s scope.
4. **Commit the mutation harness** so a reader can re-run the falsifiability check that criterion 2 now
   reports as a limit. Reason: the evidence exists only as changelog prose.
5. **Promote the oracle comparison into a repository test that can fail.** Reason: every comparison so far
   was an ad hoc script outside the repository, and three were buggy in ways that produced published
   false findings.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.

## Verification before approval

`P2.5`'s last subtask required a **separate Verifier session** to check every claim in this report against
its evidence, reading only the committed artefacts. It did, on the first revision: 45 claims checked, 28
supported, 13 unsupported, 2 unverifiable, and eight omissions, and its verdict was **do not approve as
written**. This revision makes the corrections it named. Its findings are attached to #15 rather than summarised here, and they
are **evidence for the Verifier row of the model log**, which that page still marks `Unproven`. One run
by the same model is not proof that the role works, and the report does not claim it is.
