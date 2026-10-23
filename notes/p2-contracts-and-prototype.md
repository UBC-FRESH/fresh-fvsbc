# P2 plan: contracts and prototype

Phase: `P2`. Parent issue: `#10`. Branch: `feature/p2-contracts-prototype`.
Plan of record: `ROADMAP.md`, section "Phase 2: Contracts and prototype". This file is the focused plan
that the roadmap's task lines link to, which is the role `notes/README.md` gives to a plan in this
directory: detail too long for `ROADMAP.md`.

Written 2026-10-23, retroactively, in response to a workflow audit. See "Provenance of this plan" at the
end, which records that and what it cost.

## Phase acceptance criteria, and the evidence for each

The four criteria are quoted from `ROADMAP.md`, and each names the artefact that satisfies it.

| # | Criterion | Evidence | Status |
| --- | --- | --- | --- |
| 1 | `docs/` states the interfaces and the data contracts: the tree-list input, the keyword set, the parsed outputs, and the provenance record | `docs/reference/tree-list.rst`, `keywords.rst`, `outputs.rst`, `provenance.rst`, `nemora-ingest.rst`; each read from the FVS source at commit `ef5fa84` and each naming what it did not verify | met |
| 2 | A prototype runs on synthetic data and exercises each contract, with checks that can fail | `src/fresh_fvsbc/{treelist,keywords,nemora,outputs,provenance}.py`, each with its module in `tests/`; mutation evidence for every task, recorded in `CHANGE_LOG.md` | met |
| 3 | The build question in ADR 0001 is answered with evidence: either `bc` builds, or the patch the FVS source submodule needs is recorded | `notes/adr/0004-the-fvsbc-build-recipe.md`; `notes/reference/fvsbc-patchset.diff.gz`, twelve items across nine modified files and one new file | met |
| 4 | `python scripts/dashboard.py` exits zero on the head commit of the phase branch | every task records a green dashboard in `CHANGE_LOG.md`; re-run at close-out and quoted in `notes/reports/p2-closeout.md` | met at each commit; re-verified at close-out |

## P2.1 Define the interface and data contracts in `docs/` (#11)

**Goal.** Read the FVS-BC source and write the five contract pages that the prototype is then built
against, so that no interface is invented at a call site.

**Scope.** The tree-list input format and species codes; the keyword vocabulary, the BC site input, and
the `BECINFO` question; the output database, its tables, and the `FVS_Cases` columns; the provenance
record; and the `nemora` ingestion bridge.

**Out of scope.** Any implementation; any real inventory data; the build, which is ADR 0001's open
question and was answered under `P2.3`.

**Subtasks.** Eleven, all complete; the live list is in issue `#11`. They read `canada/bc/BC.trf`,
`canada/bc/bcspp.f`, `canada/bc/blkdat.f`, `base/keywds.f`, `canada/bc/initre.f`, `dbsqlite/` and
`canada/bc/BCPLOT.F77`, hand the `TREEFMT` conflict to `P2.2`, write the five pages, and add
`CODE_OF_CONDUCT.md` and `CITATION.cff`.

**Acceptance criteria.** `docs/` carries the five pages; each names the commit it was read from; each
separates what is verified from what is not.

**Verification.** `docs/reference/index.rst` links all five; `python -m sphinx -b html docs -W -q` exits
zero, which is the dashboard's docs gate.

**Artifacts.** The five contract pages, `CODE_OF_CONDUCT.md`, `CITATION.cff`.

**Risks.** A contract read from the wrong file. Realised twice, and both were caught by a second read:
`canada/bc/BC.trf` is an SVS asset rather than a tree-list format, and `canada/bc/bcspp.f` is neither
compiled nor called by the BC build. Both are disclosed in issue `#11`'s comments.

## P2.2 Build a prototype that exercises the contracts on synthetic data (#12)

**Goal.** The smallest prototype that exercises each of the five contracts on synthetic data, with
checks that can fail, and that answers the empirical questions the contracts left open.

**Scope.** A `nemora`-shaped population fixture built at runtime; the tree-list writer; the keyword-set
validator; the `nemora` adapter; the synthetic run and the output reader; the provenance record; the
package skeleton and the gate wiring.

**Out of scope.** The full BC layer and any release (P3 and P5); a real build in CI (P3); the patch set
and the oracle comparison, which are `P2.3`.

**Subtasks.** Twelve in the live body of issue `#12`; eleven are complete. The one that is not is the
last item below, and it is a recorded limitation rather than work in progress:

- [x] Run the build spike, and record the command, its output, and its exit status.
- [x] Record the build outcome, and write the build-recipe ADR if the spike is conclusive.
- [x] Write a synthetic stem population shaped like `nemora` output, as a fixture built at runtime in `tests/`.
- [x] Write the tree-list writer, with a test that asserts the exact column positions and tests that reject an unresolvable species code.
- [x] Write the keyword-set validator: reject an unknown keyword by name, warn on `xSALVAGE`, and carry a hash.
- [x] Answer the `TREEFMT` hazard: whether PyFVS injects its own format for a BC run, and whether it misaligns a list.
- [x] Run the synthetic stand through the `DATABASE` path.
- [x] Write the output reader for `FVS_Cases` and `FVS_Error`, and report a run as failed when it holds a row of severity `ERROR`.
- [ ] Read `FVS_Compute` and `FVS_Summary_Metric`. **Not reachable through PyFVS**, which occupies the `DATABASE` output block; see "Proposals" below.
- [x] Write the `nemora` adapter: require `species` and `tree_age`, and reject a crown ratio the one-digit field cannot represent.
- [x] Record provenance for the run, including the case id and run datetime from `FVS_Cases`.
- [x] Create the package skeleton and extend the gates to cover it.

**Acceptance criteria.** The prototype exercises each contract on synthetic data; its checks can fail;
`python scripts/dashboard.py` exits zero.

**Verification.** `python scripts/dashboard.py`. Each module's mutation evidence is in the changelog
entry for its task: four mutations for the keyword validator, four for the adapter, four for the output
reader and four for the provenance record, each one shown to fail the test it targets before the change
is kept.

**Artifacts.** `src/fresh_fvsbc/{treelist,keywords,nemora,outputs,provenance}.py`, their test modules,
`tests/nemora_fixtures.py`, and `notes/reference/synthetic-run.md`.

**Risks, and how each resolved.**

- *A hand-written BC tree list is misread.* Resolved: BC's `TREFMT` opens `I4,T1,I7`, and `T1` returns
  the cursor to column 1, so `tree_num` is read from columns 1 to 7 and shares its first four with
  `plot_id`. The record is therefore 69 columns, not the 73 that the declared widths sum to, and the
  writer refuses a tree number needing more than columns 5 to 7. Proved with `gfortran`, with
  `base/intree.f`, and by decoding `FVSso/sot03.tre`.
- *A test that needs the built extension is skipped silently.* Resolved: the extension check is recorded,
  and the reader and adapter reach neither `pyfvs` nor `pandas`, so the suite needs neither.
- *A test that cannot fail.* Realised once, and caught by the mutation check: the rule that only a
  message's leading tokens carry the severity was unobservable, since first-match-wins is identical to
  scanning the whole message. The limit was removed and the test rewritten.

## P2.3 Record the FVS source patch set and its oracle comparison (#13)

**Goal.** Record the twelve-item patch the BC variant needs, and compare the built variant's numbers
against the FVS project's own BC test data, with the limits of that comparison stated.

**Scope.** The patch set, banked; ADR 0004; the two official cases; the residual; the mislabelled-commit
disclosure.

**Out of scope.** Pushing the patch to `UBC-FRESH/PyFVS`, which is a fork-side change needing its own
approval; any change to the FVS Fortran in this repository.

**Subtasks.** Three, all complete; the live list is in issue `#13`.

**Acceptance criteria.** The patch is banked and reproduces the working tree; the comparison is recorded
with its limits; the mislabelled commits are disclosed.

**Verification.** Applying the patch to `ef5fa84` reproduces the working tree byte for byte; the first
official case matches under the FVS project's own command with zero differing lines across 164 rows and
four stands.

**Artifacts.** `notes/adr/0004-the-fvsbc-build-recipe.md`, `notes/reference/fvsbc-patchset.diff.gz`,
`notes/reference/fvsbc-build-spike.md`, `notes/reference/fvsbc-validation.md`.

**Risks.** The oracle is a 2022 fixture and the FVS project's own checker skips this variant, so the
comparison bounds rather than proves correctness. Stated in the contract and in the roadmap.

## P2.4 Rename the project to `fresh-fvsbc` (#14)

**Goal.** Stop this wrapper sharing a name with PyFVS's BC extension module and with the FVS variant
itself.

**Scope.** The repository, the distribution, the import name, the published URLs, the living documents,
one `Renamed by` line in ADRs 0001 to 0004, and the local directory.

**Out of scope.** The FVS variant, which stays `bc`, and the PyFVS build flag, which stays
`-Dfvsvariants=bc`; the historical record, which keeps the old name; the reference note filenames, which
accepted ADR 0004 cites.

**Subtasks.** Six, all complete; the live list is in issue `#14`. `ADR 0005` carries the decision.

**Acceptance criteria.** The dashboard exits zero with the new names; no tracked code imports the old
name; every published URL resolves; the historical files are unchanged.

**Verification.** `git grep -nE "(^|[^A-Za-z_-])fvsbc" -- src tests` returns nothing; both published URLs
answer 200; the P0 and P1 reports are untouched in the task's diff.

**Artifacts.** The renamed package and documents, `notes/adr/0005-rename-the-project-to-fresh-fvsbc.md`.

**Risks.** The published Pages path is not redirected after a rename. Resolved in the same change set,
and the old path's 404 is the expected result.

## P2.5 Repair the plan of record after the workflow audit (#15)

**Goal.** Put the phase's plan, its roadmap grammar, and its published artefacts into the state the
workflow spec requires, before any further code is written.

**Scope.** The roadmap's subtask level and the link to this plan; parent issue `#10`'s child checklist
and scope; `README.md`'s status paragraph; the closed task issues' `Status:` and `Completion metadata:`;
the roadmap detail moved into this file; the workflow revision pinned in `AGENTS.md`; and the P2.3
incident recorded as a deviation.

**Out of scope.** Any change to CI or to branch protection, which is a settings change and needs the
maintainer's approval; any change to `P3`'s activation; the acceptance status of ADR 0004, which is the
maintainer's act.

**Subtasks.**

- [ ] Add the indented subtask level to `ROADMAP.md` for `P2.1` to `P2.4`, and link this plan from each task line.
- [ ] Reconcile parent issue `#10`: its child checklist and its scope, with a scope-change comment naming what changed and why.
- [ ] Correct `README.md`'s status paragraph, which claims that no variant has been built.
- [ ] Correct the closed task issues' `Status:` and `Completion metadata:`.
- [ ] Move the multi-paragraph roadmap notes into this file, leaving the roadmap carrying status and ordering.
- [ ] Pin the workflow revision in `AGENTS.md`, and file the missing agent pages upstream.
- [ ] Record the `P2.3` incident, thirteen commits with no child issue, as a deviation in the close-out report with its cause and remedy.

**Acceptance criteria.** `ROADMAP.md` carries the subtask level and links this plan; `#10` lists all five
children by number and ID; `README.md`'s status agrees with the roadmap; every closed task issue carries
a `Status:` value the templates define and a filled `Completion metadata:`; the dashboard exits zero.

**Verification.**

```bash
grep -nE '^\s{2,}- \[' ROADMAP.md
gh api repos/UBC-FRESH/fresh-fvsbc/issues/10/sub_issues --jq 'length'
gh issue view 10 -R UBC-FRESH/fresh-fvsbc --json body --jq .body | grep -c '^- \['
grep -c "does not build" README.md
python scripts/check_workflow.py
python scripts/dashboard.py
```

**Artifacts.** `ROADMAP.md`, `README.md`, `AGENTS.md`, this file, the issue bodies and comments, and
`notes/reports/p2-closeout.md`.

**Risks.** The roadmap's "Detailed Next Steps Notes" section may be required by the validator; the
dashboard is run before the commit that moves it. The maintainer may prefer a different `P3` shape, so
`P3` is left `planned` with its parent issue uncreated.

## Proposals for the maintainer, not tasks

Each is a recommendation with a default, as `phase-closeout.rst` requires, and each needs a decision
before the work it describes is started.

1. **The two unreachable output tables.** `FVS_Compute` and `FVS_Summary_Metric` cannot be read through
   PyFVS, because PyFVS occupies the `DATABASE` output block and exposes no way to configure it.
   **Recommendation: accept the limit for now, and open a separate task in `P3` to build the standalone
   `FVSbc` executable**, which does accept the block, if a caller needs either table. The default is to
   do nothing in `P2`, because the summary is available in memory and as a fixed-width report.
2. **The CI quality matrix.** `.github/workflows/ci.yml` runs one `quality` job on Python 3.12, where
   `quality-gates.rst` requires 3.11 and 3.12 with the contexts `Quality gates, Python 3.11` and
   `Quality gates, Python 3.12`. **Recommendation: approve the change and name it in the close-out
   report**; the exact commands are `gh api` edits to the workflow file and the branch-protection
   contexts. The default is to leave it, since it is a settings change.
3. **ADR 0004.** It is still `Status: proposed` although its task is closed and the phase's third
   acceptance criterion rests on it, its `Context` says the fourth patch item blocks the import while a
   later paragraph says the module imports, and its `Issues:` field names `#12` where the roadmap assigns
   it to `P2.3`. **Recommendation: the maintainer accepts it, and its `Context` and `Issues:` field are
   corrected in one commit with the correction disclosed**, as was done for ADR 0005.
4. **`P3`'s shape.** `P3` is `planned` with a placeholder task and a placeholder criterion.
   **Recommendation: before `P3` is activated, its parent issue, its child issues, its roadmap subtask
   lines and its focused plan are written in that order**, and the maintainer approves the plan before
   the first commit. `session-protocol.rst` requires the plan to be written before anything is edited,
   and `workflow-model.rst` puts the plan of record in `ROADMAP.md` with the detail under `notes/`. An
   earlier version of this proposal attributed the requirement to `workflow-model.rst` alone, which
   does not state it; a Verifier session caught the false citation.

## Deviations and disclosures

Relocated from `ROADMAP.md`'s "Detailed Next Steps Notes", where the detail had grown past what the
roadmap should carry. Each names what happened and what it cost.

- **A whole task's work ran with no child issue, no roadmap entry and no plan.** Thirteen commits
  between 2026-10-21 and 2026-10-23 are labelled `P2.2` but delivered `P2.3`'s work — the patch set and
  the oracle comparison — and issue `#13` was created after the work was done. `AGENTS.md` states the
  scaffold rule in one line: create the parent issue, the branch, and the roadmap entry before the work.
  The commits are not rewritten, and `CHANGE_LOG.md` discloses the mislabelling. The cause is that the
  agent treated the build spike as an unplanned investigation rather than as a task, and the remedy is
  now a rule the agent applies: no commit before its child issue exists.
- **Four claims published on 2026-10-21 were wrong, and three were retracted only in conversation.**
  The cause is recorded: they came from ad hoc comparison scripts outside the repository that were never
  checked against a known-good case, and three failed on `'INF'` parsed as a float or on a column
  misalignment. The remedy is the standing proposal to promote the comparison into a repository test
  that can fail, which would have caught all three.
- **A false citation was published in an accepted ADR.** `ADR 0005` claimed the `Renamed by` form
  followed this repository's `ADR 0004`'s own `Refined by` line, and no such line exists here; the
  precedent is the seed's. The body was corrected and the correction is disclosed. **It should not have
  been edited after acceptance**: `notes/README.md` says an accepted ADR is superseded rather than
  rewritten, and approval in conversation is not the exception the rule does not have.
- **A test that was checking nothing.** The output reader's severity rule limited the search to a
  message's leading tokens, and a mutation that removed the limit changed no result, which proved the
  rule was unobservable. The limit was removed and the test rewritten.
- **A validation claim was published before its own correction.** The merchantable-volume defect was
  initially attributed to a cause that a later commit disproved; the corrected cause is that
  `canada/bc/vols.f` never set `MCFV`, which `base/gradd.f` uses to build `OMCCUR`.
- **The oracle comparison bounds correctness rather than proving it.** The `.sum.save` fixtures carry
  `06-28-2022`, the source built here is `ef5fa84` of 2026-09-10, and the FVS project's own checker
  carries `#FVSbc -- Omit currently 20260226`. The residual is confined to three dense stands of the
  second case, and it is attributed, not proven, to upstream changes after the fixture was written.
- **The tree-number field carries a composite.** Because `plot_id` and `tree_num` share columns 1 to 4,
  FVS reads the tree number as the plot id's digits followed by the tree number's. It stays unique
  within a plot, which is what FVS requires. Only a run confirms BC reads our record as intended, and
  one did read it: `notes/reference/synthetic-run.md`.
- **The patch set is banked, not pushed.** Pushing it to `UBC-FRESH/PyFVS` is a fork-side change needing
  its own approval, and ADR 0004 names it.
- **The reference note filenames keep the old project name, deliberately.** Accepted `ADR 0004` and the
  contract pages cite them, and renaming a file whose name an accepted ADR cites would strand the
  citation in a document that is not rewritten.
- **The roadmap template in the seed omits task issue numbers** where `workflow-model.rst` requires
  them; reported upstream as `UBC-FRESH/ubc-fresh-dev-workflow` issue `#44`.

## Provenance of this plan

This plan was written on 2026-10-23, **after** both the work it governs and a workflow audit. It should
have existed from 2026-10-21, before the first `P2.2` commit, in the form that `notes/README.md` names:
a focused plan, too long for the roadmap, linked from its roadmap task and kept current while the task is
active. Its absence is the failure the audit's first finding records, and it is the reason the roadmap
has no subtask level: the third level of the mandated three-level structure was never written down.

The audit that prompted it is summarised in `notes/reports/p2-closeout.md`, and its eleven corrective
actions are discharged across `P2.5` and the proposals above.
