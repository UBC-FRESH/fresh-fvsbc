# FVS-BC Roadmap

This roadmap is the plan of record and the issue tracker map for FVS-BC. Keep it in step with the GitHub issues, `CHANGE_LOG.md`, and `notes/`. `scripts/check_workflow.py` parses the phase headers, status lines, and checkboxes below, so keep their format.

Every phase starts as `planned` with `Parent issue: TBD`. Activate a phase only after its parent issue exists and the maintainer approves it.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap | #1 | `feature/p0-bootstrap` | complete |
| P1 Scope and design | #5 | `feature/p1-scope-design` | complete |
| P2 Contracts and prototype | #10 | `feature/p2-contracts-prototype` | complete |
| P3 Build | #17 | `feature/p3-build` | complete |
| P4 Verify | #25 | `feature/p4-verify` | complete |
| P5 Release and deploy | #31 | `feature/p5-release` | complete |
| P6 Operate and maintain | #37 | `feature/p6-operate` | complete |
| P7 Keyword blocks and gate hygiene | #43 | `feature/p7-blocks-and-gates` | complete |
| P8 Release 0.2.0 | #47 | `feature/p8-release-0-2-0` | complete |
| P9 The database block | #50 | `feature/p9-database-block` | complete |
| P10 Release 0.3.0 | #55 | `feature/p10-release-0-3-0` | complete |
| P11 The command's block form, and 0.3.1 | #58 | `feature/p11-block-form` | complete |
| P12 The table names | #62 | `feature/p12-table-names` | complete |
| P13 The tables the official case writes | #67 | `feature/p13-tables` | complete |
| P14 Release 0.4.0 | #71 | `feature/p14-release-0-4-0` | complete |
| P15 The conditional | #75 | `feature/p15-if-blocks` | complete |
| P16 Release 0.5.0 | #79 | `feature/p16-release-0-5-0` | complete |
| P17 The fuels and potfire tables | #82 | `feature/p17-extension-tables` | complete |
| P18 What the remaining tables need | #86 | `feature/p18-table-reachability` | complete |
| P19 Release 0.6.0 | #90 | `feature/p19-release-0-6-0` | complete |
| P20 The carbon tables | #95 | `feature/p20-carbon` | complete |
| P21 Release 0.7.0 | #99 | `feature/p21-release-0-7-0` | complete |
| P22 The consumption table | #103 | `feature/p22-consumption` | complete |
| P23 Release 0.8.0 | #107 | `feature/p23-release-0-8-0` | complete |
| P24 The sweep over the remaining tables | #111 | `feature/p24-sweep` | complete |
| P25 The notes describe the next release | #115 | `feature/p25-notes-for-the-next-release` | complete |
| P26 The damage-agent blocks | #119 | `feature/p26-dm-rd` | complete |
| P27 The cheap tables | #123 | `feature/p27-the-cheap-five` | complete |
| P28 StrClass and ATRTList | #127 | `feature/p28-strclass-atrtlist` | complete |
| P29 Release 0.9.0 | #131 | `feature/p29-release-0-9-0` | complete |
| P30 CanProfile and the fixture limits | #135 | `feature/p30-canprofile-fixture` | complete |
| P31 The three questions, answered | #139 | `feature/p31-three-questions` | complete |
| P32 The rest of the damage agents | #143 | `feature/p32-dm-rd-rest` | complete |
| P33 Release 0.10.0 | #147 | `feature/p33-release-0-10-0` | complete |
| P34 The regeneration tables | #151 | `feature/p34-regen` | complete |
| P35 Release 0.11.0 | #155 | `feature/p35-release-0-11-0` | complete |
| P36 Banking it for real use | #159 | `feature/p36-bank-for-deployment` | complete |
| P37 The web front end | #163 | `feature/p37-web-design` | complete |
| P38 The web surface, first cut | #167 | `feature/p38-web-first-cut` | complete |
| P39 A real BC case, and what it broke | #171 | `feature/p39-real-case` | complete |
| P40 Release 0.12.0 | #175 | `feature/p40-release-0-12-0` | complete |
| P41 The container deployment and the oracle harness | #181 | `feature/p41-container-and-oracle` | complete |
| P43 The proxy prefix | #186 | `feature/p43-proxy-prefix` | complete |
| P42 The THINQFA supplemental record | #179 | `feature/p42-thinqfa` | complete |
| P44 Release 0.13.0 | #192 | `feature/p44-release-0-13-0` | complete |
| P45 The tree handoff, mapped | #196 | `feature/p45-tree-handoff` | complete |
| P46 The DSNin tree handoff | #200 | `feature/p46-dsnin` | complete |
| P47 A quiet run | #204 | `feature/p47-quiet-run` | complete |
| P48 Release 0.14.0 | #208 | `feature/p48-release-0-14-0` | complete |
| P49 The oracle, attributed | #212 | `feature/p49-oracle-attributed` | complete |
| P50 The fire-model block | #216 | `feature/p50-fire-model-block` | complete |
| P51 Release 0.15.0 | #220 | `feature/p51-release-0-15-0` | complete |
| P52 A refusal is reported | #223 | `feature/p52-refusal-is-reported` | complete |
| P53 Release 0.15.1 | #228 | `feature/p53-release-0-15-1` | complete |
| P54 The fire tables | #232 | `feature/p54-fire-tables` | complete |

## Lifecycle Map

| Stage | Phases | Exit criteria |
| --- | --- | --- |
| Scope and design | P0, P1 | Goal, scope, and out-of-scope items recorded; decisions in ADRs, each accepted or deferred |
| Build | P2, P3 | Each task committed with its task ID; each commit leaves the dashboard green; docs updated in the same change set |
| Verify | P4 | The dashboard and CI pass on the head commit; each acceptance criterion has evidence in the close-out report |
| Release and deploy | P5 | Tag, release notes, and Pages live; a clean checkout verifies them; each release action approved on its own |
| Operate and maintain | P6 | Review cadence held; incoming ideas triaged; retirement decided and recorded as an ADR |
| Retire | P6 (procedure) | Archive notice, final changelog entry, and issues closed |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside the task's issue body. Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and its parent issue closes.

## Phase 0: Bootstrap

Parent issue: #1
Branch: `feature/p0-bootstrap`
Status: complete

Goal: adapt the contract to this project, and make the first pull request reviewable.

- [x] P0.1 Adapt `AGENTS.md` and `README.md` to this project (#2)
- [x] P0.2 Confirm the validator and the docs build pass (#3)

Acceptance criteria:

- `AGENTS.md` states the project-specific rules, and links the shared workflow rules instead of copying them.
- `README.md` describes `fresh-fvsbc`, its place in the pipeline, and its status, and claims nothing the roadmap has not recorded.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 1: Scope and design

Parent issue: #5
Branch: `feature/p1-scope-design`
Status: complete

Goal: settle the repository's public footing, then state the question, the users, the scope, and the out-of-scope items, and record the first decisions as ADRs.

- [x] P1.1 Add the MIT licence and align the package metadata (#6)
- [x] P1.2 Write the problem statement and scope in `notes/` (#7)
- [x] P1.3 Record the first design decisions as ADRs in `notes/adr/` (#8)

Acceptance criteria:

- `LICENSE` is MIT, and the package metadata agrees with it.
- `notes/` states the problem, the users, the scope, and the out-of-scope items.
- Every ADR is accepted or superseded, and any new decision is recorded.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 2: Contracts and prototype

Parent issue: #10
Branch: `feature/p2-contracts-prototype`
Status: complete

Goal: define the interfaces and the data contracts, then build the smallest prototype that exercises them.

The detail for this phase is the focused plan `notes/p2-contracts-and-prototype.md`, which carries each
task's sections, the phase criteria and their evidence, the deviations, and the open proposals.

- [x] P2.1 Define the interface and data contracts in `docs/` (#11)
  - [x] Read `canada/bc/BC.trf`, and establish that it is an SVS asset rather than a tree-list format.
  - [x] Read `canada/bc/bcspp.f`, and establish that the BC build does not compile it and never calls it.
  - [x] Read `canada/bc/blkdat.f`, and record its `TREFMT` tree-record format and its `JSP` species list.
  - [x] Read `base/keywds.f` and `canada/bc/initre.f`, and record the keyword vocabulary and the BC site input.
  - [x] Read `dbsqlite/` and `canada/bc/BCPLOT.F77`, and record the output tables and the BEC structure.
  - [x] Record the format conflict between the BC variant default and PyFVS's injected `TREEFMT`, and hand the resolution to `P2.2`.
  - [x] Write the tree-list input contract.
  - [x] Write the keyword-set contract.
  - [x] Write the output contract and the provenance record.
  - [x] Write the `nemora` ingestion contract.
  - [x] Add `CODE_OF_CONDUCT.md` and `CITATION.cff`.
- [x] P2.2 Build a prototype that exercises the contracts on synthetic data (#12) — its one open subtask was **transferred to `P3.2` (#19)** and **discharged there** (ADR 0009): reading `FVS_Compute` and `FVS_Summary_Metric`, which PyFVS makes unreachable
  - [x] Run the build spike, and record the command, its output, and its exit status.
  - [x] Record the build outcome, and write the build-recipe ADR if the spike is conclusive.
  - [x] Write a synthetic stem population shaped like `nemora` output, as a fixture built at runtime in `tests/`.
  - [x] Write the tree-list writer, with a test that asserts the exact column positions and tests that reject an unresolvable species code.
  - [x] Write the keyword-set validator: reject an unknown keyword by name, warn on `xSALVAGE`, and carry a hash.
  - [x] Answer the `TREEFMT` hazard: whether PyFVS injects its own format for a BC run, and whether it misaligns a list.
  - [x] Run the synthetic stand through the `DATABASE` path.
  - [x] Write the output reader for `FVS_Cases` and `FVS_Error`, and fail a run that holds a row of severity `ERROR`.
  - [x] Read `FVS_Compute` and `FVS_Summary_Metric`. **Transferred to `P3.2` (#19)**, which builds the standalone executable that reaches them; PyFVS makes them unreachable by occupying the `DATABASE` output block.
  - [x] Write the `nemora` adapter: require `species` and `tree_age`, and reject a crown ratio the one-digit field cannot represent.
  - [x] Record provenance for the run, including the case id and run datetime from `FVS_Cases`.
  - [x] Create the package skeleton and extend the gates to cover it.
- [x] P2.3 Record the FVS source patch set and its oracle comparison (#13)
  - [x] Bank the patch set and record the recipe in ADR 0004.
  - [x] Compare the build against the official BC test data and record the results with their limits.
  - [x] Disclose the mislabelled commits in the changelog and on this issue.
- [x] P2.4 Rename the project to `fresh-fvsbc` (#14)
  - [x] Rename the GitHub repository. Public; approved and run on 2026-10-23.
  - [x] Update the published URLs in `pyproject.toml` and `CITATION.cff`.
  - [x] Rename the package directory, the distribution name, and the gate configuration.
  - [x] Rename the living documents, and add the variant-versus-package wording rule.
  - [x] Add the `Renamed by ADR 0005` line to ADRs 0001 to 0004.
  - [x] Rename the local directory.
- [x] P2.5 Repair the plan of record after the workflow audit (#15)
  - [x] Add the indented subtask level to this roadmap for `P2.1` to `P2.4`, and link the plan from each task line.
  - [x] Reconcile parent issue `#10`: its child checklist and its scope, with a scope-change comment.
  - [x] Correct `README.md`'s status paragraph, which claims that no variant has been built.
  - [x] Correct the closed task issues' `Status:` and `Completion metadata:`.
  - [x] Move the multi-paragraph roadmap notes into the focused plan.
  - [x] Pin the workflow revision in `AGENTS.md`, and file the missing agent pages upstream.
  - [x] Record the `P2.3` incident, thirteen commits with no child issue, in the close-out report.
  - [x] Record this project's roles and open the model log at `docs/agents/roles-and-models.rst`.
  - [x] Have a separate Verifier session check every claim in the close-out report against its evidence.

Acceptance criteria:

- `docs/` states the interfaces and the data contracts: the tree-list input, the keyword set, the parsed outputs, and the provenance record.
- A prototype runs on synthetic data and exercises each contract, with checks that can fail.
- The build question in ADR 0001 is answered with evidence: either `bc` builds from the variant matrix, or the patch the FVS source submodule needs is recorded.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 3: Build

Parent issue: #17
Branch: `feature/p3-build`
Status: complete

Goal: implement the agreed scope of the BC layer on top of the validated prototype: make the build
reproducible in CI, reach the two output tables PyFVS cannot, make the falsifiability evidence
reproducible, and give the package a public API, a run orchestration, and a command-line entry point.

The detail for this phase is the focused plan `notes/p3-build.md`, written before the work began.

- [x] P3.1 The CI quality matrix, and a CI build of the variant (#18)
  - [x] Set the `quality` job's `name:` to `Quality gates, Python ${{ matrix.python-version }}` and its `setup-python` input to the matrix variable, and add a `[3.11, 3.12]` matrix.
  - [x] Add a job that applies ADR 0004's patch to the pinned fork, builds the BC variant, and imports `pyfvs.fvsbc`.
  - [x] After the matrix has run, set branch protection with the specification's four-context `PUT`, including `required_linear_history`, and read the rule back.
  - [x] Record the gate change in the changelog with its reason.
- [x] P3.2 Build the standalone `FVSbc` executable (#19) — **proven and not adopted**; `FVS_Compute` holds `COMPUTE` expressions and the summary was already available in memory (ADR 0009)
  - [x] Build `bin/FVSbc` from the patched fork, and record the command and its output.
  - [x] Run one case through it with a `DATABASE` output block, and confirm `FVS_Compute` and `FVS_Summary_Metric` are written.
  - [x] Record the recipe as a new ADR.
- [x] P3.3 Commit the mutation harness (#20)
  - [x] Write the harness so that a mutation which does not apply is an error rather than a pass.
  - [x] Register the mutations already recorded for the five prototype modules.
  - [x] Run it in CI, or record why not.
- [x] P3.4 The public API over the five contracts, and three open decisions (#21)
  - [x] Export the five modules' public names, with `__all__` and numpydoc docstrings.
  - [x] Resolve the record-versus-dataframe question in `outputs.rst`.
  - [x] Resolve the species-assignment question in `nemora-ingest.rst`.
  - [x] Resolve the `BECINFO` question in `keywords.rst`.
  - [x] Add the API pages, and extend `tests/test_api_docstrings.py` to cover the package.
- [x] P3.5 Run orchestration (#22)
  - [x] Write the orchestration over the five prototype modules.
  - [x] Return the outputs with the provenance record, and fail a run that holds an error.
  - [x] Test it end to end, skipping when the built extension is absent and recording the skip.
- [x] P3.6 The command-line entry point (#23)
  - [x] Write the command over the orchestration.
  - [x] Test its exit codes for success, a failed run, and bad input.
  - [x] Document it in the README and in `docs/`.

Acceptance criteria:

- The quality job runs on Python 3.11 and 3.12, and protection requires all four contexts the workflow spec names.
- The pinned fork's BC variant builds from a clean checkout in CI.
- The standalone executable writes `FVS_Compute` and `FVS_Summary_Metric`.
- The mutation harness reproduces a named mutation failing a named test.
- One synthetic run through the public API returns outputs carrying provenance.
- The command-line entry point runs a case end to end.
- `python scripts/dashboard.py` exits zero on both Python versions.

## Phase 4: Verify

Parent issue: #25
Branch: `feature/p4-verify`
Status: complete

Goal: show that the build meets its acceptance criteria, and record the evidence in the changelog.

The detail for this phase is the focused plan `notes/p4-verify.md`, which carries each task's sections,
the phase criteria, the order and its reason, and the open proposals.

- [x] P4.1 The acceptance checks, from a clean checkout (#26)
  - [x] Build the variant from the pin in a clean checkout, and record the command, the exit status, and the import.
  - [x] Run the full suite there, and record the count and the skips with their reasons.
  - [x] Run the command on the synthetic population, and record the exit status and the outputs.
  - [x] Record each of `P3`'s seven criteria with the evidence that produces it.
- [x] P4.2 Promote the oracle comparison into a repository test (#27)
  - [x] Establish where the official case data comes from, and whether it may be committed, with its licence.
  - [x] Write the comparison as a repository test, skipping with a recorded reason when the data or the build is absent.
  - [x] Record the result, including the stands and rows it covers and the columns it does not.
- [x] P4.3 Make the dashboard's 3.11 evidence literal (#28) — both interpreters in the existing job, chosen by the maintainer, so no protection change
  - [x] Choose between running the script under both interpreters in the existing job and renaming the context with protection changed in the same approved move.
  - [x] Write the change and the protection change, with its exact command, as a proposal.
  - [x] After approval, run it and read the protection back.
- [x] P4.4 Close the `__all__` gap (#29) — **its premise was false**: the assertion exists since `6e99a41`, so the task became proving it can fail
  - [x] Add a mutation the harness catches, so the existing assertion's falsifiability is reproducible.
  - [x] Assert that `__all__` holds no duplicate, which nothing else checks.

Acceptance criteria:

- Each of `P3`'s seven acceptance criteria has evidence recorded in the changelog, with the command or run id that produces it.
- The oracle comparison runs from the repository against the committed or fetched case data, and its result is recorded.
- `python scripts/dashboard.py` exits zero on 3.11 and 3.12 in CI, with the protection contexts still matching the four the workflow spec names.
- Every name in the package's `__all__` resolves, asserted by a test.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 5: Release and deploy

Parent issue: #31
Branch: `feature/p5-release`
Status: complete

Goal: tag a release, publish the docs, and verify the published artifacts from a clean checkout.

The detail for this phase is the focused plan `notes/p5-release.md`, which carries each task's sections,
the phase criteria, the order and its reason, and the open proposals.

- [x] P5.1 The release notes and the known-gaps list (#32)
  - [x] Record the build the release wraps: the PyFVS fork commit, the FVS source submodule, and the variant list, read from the pins rather than quoted.
  - [x] Write what the release is and what it does, in the README's terms rather than new ones.
  - [x] Write the known-gaps list from the `P2`, `P3` and `P4` reports, each item with the reason it is open.
  - [x] State what is verified and how, citing the commands and run ids rather than asserting.
- [x] P5.2 Tag, publish, and verify from a clean checkout (#33) — tagged `v0.1.0` at `ef11f94`, released, and verified
  - [x] Propose the tag name and the release body, and wait for approval before creating either.
  - [x] Propose the documentation publication and what it changes, and wait for approval.
  - [x] After approval, run each action and read it back.
  - [x] Verify from a clean checkout: install the release, run `python -m fresh_fvsbc --help`, and run one case.
  - [x] Check the published pages against the source at the tag.

Acceptance criteria:

- The release notes name the build the release wraps: the PyFVS fork commit, the FVS source submodule, and the variant list.
- The known-gaps list names every open item the `P2`, `P3` and `P4` reports carry, each with the reason it is open.
- A clean checkout installs the release and runs `python -m fresh_fvsbc --help` and one case.
- The published documentation matches the source at the tag, checked page by page for the pages that changed in the last phase.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 6: Operate and maintain

Parent issue: #37
Branch: `feature/p6-operate`
Status: complete

Goal: keep the project current: triage incoming ideas, review on a cadence, and close out cleanly.

The detail for this phase is the focused plan `notes/p6-operate.md`, which carries each task's sections,
the phase criteria, the order and its reason, and the open proposals.

- [x] P6.1 Triage the twelve known gaps (#38)
  - [x] Read the twelve gaps and, for each, the report that carries it.
  - [x] Assign each a disposition: fix now, fix later with a named phase, or accepted with a reason.
  - [x] Record the table where a reader looks, and say what the disposition costs.
  - [x] Propose a phase for anything marked fix-later that no phase covers.
- [x] P6.2 Make two runs in one process safe (#39)
  - [x] Spike both mechanisms and record what each costs: a guard that refuses a second run, and a subprocess per run.
  - [x] Bring the choice back as a decision with the evidence, before changing the API.
  - [x] Implement the chosen mechanism, with the docstrings and docs corrected to match.
  - [x] Add the test that shows the second run cannot silently disagree, and a mutation the harness catches.
- [x] P6.3 Set the review cadence and record the first review (#40) — **built, then reverted at the maintainer's direction**: a quarterly cadence, a due-date table and per-review records were 202 lines and five commits to schedule a review of a twelve-item list where nine items are "won't fix". The rule is one line, above.
  - [x] State the cadence, what it covers, and who holds it.
  - [x] Record the first review: the triaged backlog, the release's state, and the model log's re-checks.
  - [x] Say where the next review is recorded, so that a missed one is visible rather than silent.

Acceptance criteria:

- Every item in `RELEASE_NOTES.md`'s known-gaps list carries a disposition: fix now, fix later with a named phase, or accepted with a reason.
- Two runs in one process cannot silently disagree; the mechanism is recorded and tested.
- A review cadence is stated, and the first review is recorded against the triaged backlog.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 7: Keyword blocks and gate hygiene

Parent issue: #43
Branch: `feature/p7-blocks-and-gates`
Status: complete

Goal: write the keyword blocks that were refused, and close the gate gap that let machine-specific
paths into a tracked file.

- [x] P7.1 Write the line blocks (#44)
  - [x] The model holds lines, and the writer supplies the ``END``, because a block without one swallows the rest of the file.
  - [x] ``COMMENT``, ``COMPUTE`` and ``DATABASE`` are accepted; ``IF`` is still refused by name, because it wraps keywords rather than lines.
  - [x] Demonstrated end to end: FVS's own report echoes a ``COMPUTE`` block as ``DEFINE THE FOLLOWING``.
- [x] P7.2 Catch a POSIX temporary path (#45)
  - [x] A pattern in ``scripts/check_workflow.py``, with the evidence that it does not false-positive on legitimate prose.
  - [x] A test that a machine-specific path in a tracked file is found, and one that a placeholder is not.

Acceptance criteria:

- The line blocks are written and FVS reads them, and ``IF`` is refused with a message that says why.
- A POSIX temporary path in a tracked file fails the validator, and a placeholder or a repository-relative path does not.
- ``python scripts/dashboard.py`` exits zero on the head commit of the phase branch.

## Phase 8: Release 0.2.0

Parent issue: #47
Branch: `feature/p8-release-0-2-0`
Status: complete

Goal: release `0.2.0`, because `main` carries a correctness fix for a defect that is in `v0.1.0`.

- [x] P8.1 Version and notes for 0.2.0 (#48)
  - [x] Bump `pyproject.toml` and `__init__.py` to `0.2.0`, together, because a test asserts they agree.
  - [x] Rewrite `RELEASE_NOTES.md` for 0.2.0: what changed since 0.1.0, the pins, and the gaps that remain with their limits.
  - [x] Name the gaps that closed, and narrow the block-keyword gap to `IF`.

Acceptance criteria:

- The package reports `0.2.0`, the notes name the build it wraps and the gaps that remain, and a clean checkout installs the release and runs one case.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit of the phase branch.

## Phase 9: The database block

Parent issue: #50
Branch: `feature/p9-database-block`
Status: complete

Goal: correct a conclusion in the record that is wrong — `FVS_Compute` is reachable — then make the
`DATABASE` block first-class and expose the two tables it unlocks.

- [x] P9.1 Correct the record on `FVS_Compute` (#51)
  - [x] Correct the triage's row: the constraint is the block's **position**, not PyFVS's ownership.
  - [x] Correct `RELEASE_NOTES.md`'s gap, which says the table cannot be read.
  - [x] Add a correction note to ADR 0009 rather than rewriting it.
- [x] P9.2 Make the `DATABASE` block first-class (#52)
  - [x] A rule in the orchestration: the block must precede the stand setup, and a set that puts it later is refused.
  - [x] Expose `FVS_Compute` and `FVS_Summary_Metric` in the reader, which rule 3 permits once they are tested.
  - [x] A test that a run with the block first writes both tables, and one that a late block is refused.
  - [x] Correct `outputs.rst` and `keywords.rst`.
- [x] P9.3 Put the command on the API page (#53)
  - [x] Add the `automodule` entry for `fresh_fvsbc.cli`.

Acceptance criteria:

- The record says the tables are reachable, and says what was wrong before.
- A set whose `DATABASE` block comes after the stand is refused with a message that says to put it first.
- `FVS_Compute` and `FVS_Summary_Metric` are read from a real run through the public reader.
- `fresh_fvsbc.cli` appears on the API page.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 10: Release 0.3.0

Parent issue: #55
Branch: `feature/p10-release-0-3-0`
Status: complete

Goal: release `0.3.0`, because `main` carries four exposed tables instead of two and a corrected record.

- [x] P10.1 Version and notes for 0.3.0 (#56)
  - [x] Bump `pyproject.toml` and `__init__.py` to `0.3.0`, together.
  - [x] Rewrite `RELEASE_NOTES.md`: what changed since 0.2.0, the pins, and the gaps that remain.
  - [x] Drop the `FVS_Compute` gap, which is a documented requirement now, and name the 29 tables that still need tests.

Acceptance criteria:

- The package reports `0.3.0`, the notes say what changed and what remains, and a clean checkout installs the release and runs one case.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 11: The command's block form, and 0.3.1

Parent issue: #58
Branch: `feature/p11-block-form`
Status: complete

Goal: let the command write a keyword block, so a shell user can reach the tables `0.3.0` exposes, then
release `0.3.1`.

- [x] P11.1 The command's block form (#59)
  - [x] A `--block NAME=FIELDS|LINE|LINE` option.
  - [x] One ordered destination shared with `--keyword`.
  - [x] Refuse a `--block` for a keyword that takes no lines.
  - [x] A test that a run through the command with a `DATABASE` block first writes `FVS_Compute`.
  - [x] Document the syntax.
- [x] P11.2 Version and notes for 0.3.1 (#60)
  - [x] Bump the version in two files.
  - [x] Rewrite the notes.
  - [x] Record the closed gap in the triage.

Acceptance criteria:

- `--block` writes a block, and the two options keep their relative order.
- A run through the command with a `DATABASE` block first writes `FVS_Compute`.
- The package reports `0.3.1` and a clean checkout installs it.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 12: The table names

Parent issue: #62
Branch: `feature/p12-table-names`
Status: complete

Goal: the contract's table list is the base schema's and BC builds the metric one, so twenty-four names
are wrong for this variant. Record it, then correct it from the schema.

- [x] P12.1 Record that the list names the wrong schema (#63)
  - [x] Read the schema the variant actually builds.
  - [x] Record the evidence in `notes/reference/table-names.md`.
- [x] P12.2 Correct the list from the metric schema (#64)
  - [x] Read the metric schema in full, including the dynamic statement.
  - [x] Correct the list, the page and the tests.
  - [x] Confirm the official case's database names only tables in the corrected list.

Acceptance criteria:

- The evidence is recorded, with the file that shows it.
- The list, the page and the tests name the metric schema's tables, and every exposed table is in the list.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 13: The tables the official case writes

Parent issue: #67
Branch: `feature/p13-tables`
Status: complete

Goal: expose the four tables the official case writes that the reader did not, and check them against
FVS's own database dump.

- [x] P13.1 Expose the four tables and check them against the dump (#68)
  - [x] Expose `FVS_Down_Wood_Vol_Metric`, `FVS_InvReference`, `FVS_SnagDet_Metric` and `FVS_SnagSum_Metric`.
  - [x] Parse the dump's per-table CSV sections, mapping the two names it writes differently.
  - [x] A test that every exposed table the dump carries holds the dump's row count.
  - [x] Correct the contract page's exposed list.

Acceptance criteria:

- The reader exposes eight tables, and each of the four the dump carries holds the dump's row count.
- `FVS_InvReference` is exposed, and its exposure says why the dump cannot check it.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 14: Release 0.4.0

Parent issue: #71
Branch: `feature/p14-release-0-4-0`
Status: complete

Goal: release `0.4.0`, because `main` carries eight exposed tables instead of four and a table list that
names what the build creates.

- [x] P14.1 Version and notes for 0.4.0 (#72)
  - [x] Bump the version in two files.
  - [x] Rewrite the notes.
  - [x] Narrow the table gap to the 36 the official case does not write.

Acceptance criteria:

- The package reports `0.4.0`, the notes say what changed and what remains, and a clean checkout installs it and reads two of the new tables.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 15: The conditional

Parent issue: #75
Branch: `feature/p15-if-blocks`
Status: complete

Goal: write `IF` blocks, the last keyword form the model could not express.

- [x] P15.1 Write the conditional (#76)
  - [x] The model holds `nested` and `otherwise` beside `lines`, and only `IF` may carry them.
  - [x] The writer emits the official case's form, and the `ELSE` branch.
  - [x] The validator recurses into a conditional's body.
  - [x] A run with an `IF` block succeeds and FVS's report carries the condition.
  - [x] Correct `docs/reference/keywords.rst`.

Acceptance criteria:

- An `IF` block renders the official case's form, and an `ELSE` branch renders too.
- An unknown keyword inside a conditional is refused like one outside it.
- A run with an `IF` block succeeds, and FVS's report carries the condition.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 16: Release 0.5.0

Parent issue: #79
Branch: `feature/p16-release-0-5-0`
Status: complete

Goal: release `0.5.0`, because `main` carries `IF` blocks and nobody can use them from a release.

- [x] P16.1 Version and notes for 0.5.0 (#80)
  - [x] Bump the version in two files.
  - [x] Rewrite the notes.
  - [x] Drop the `IF` gap.

Acceptance criteria:

- The package reports `0.5.0`, the notes say what changed and what remains, and a clean checkout installs it and runs a case with an `IF` block.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 17: The fuels and potfire tables

Parent issue: #82
Branch: `feature/p17-extension-tables`
Status: complete

Goal: reach the tables that need an extension, starting with the three one `FMIN` block unlocks.

- [x] P17.1 Write `FMIN` and expose the three tables (#83)
  - [x] `FMIN` joins the line blocks.
  - [x] Expose `FVS_Fuels_Metric`, `FVS_PotFire_Metric` and `FVS_PotFire_Cond_Metric`.
  - [x] A run with an `FMIN` block writes all three, and the reader returns them.
  - [x] Correct the two contract pages.

Acceptance criteria:

- `FMIN` renders as a line block, and a run with it writes the three tables.
- The reader exposes eleven tables, and the three are non-empty with their identity column.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 18: What the remaining tables need

Parent issue: #86
Branch: `feature/p18-table-reachability`
Status: complete

Goal: record which of the 44 tables a run here can write, and why the rest cannot.

- [x] P18.1 Record which tables a run can write (#87)
  - [x] The four reachable with an option, and which option.
  - [x] Carbon: the writer's single call site, the accepted option, and the file `CALBSTAT` writes to.
  - [x] Dwarf mistletoe and root disease: the absence of a writer.
  - [x] The triage entry.

Acceptance criteria:

- Each verdict names the evidence: a call site, an option the run's report echoes, or the absence of a writer.
- The triage says the gap is a mixture rather than 36 recipes.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 19: Release 0.6.0

Parent issue: #90
Branch: `feature/p19-release-0-6-0`
Status: complete

Goal: release `0.6.0`, because `main` carries three more tables and a record of which of the rest can be
written at all.

- [x] P19.1 Version and notes for 0.6.0 (#91)
  - [x] Bump the version in two files.
  - [x] Rewrite the notes.
  - [x] Replace the table gap with what the reachability record says.

Acceptance criteria:

- The package reports `0.6.0`, the notes say what changed and what remains, and a clean checkout installs it and reads one of the new tables.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 20: The carbon tables

Parent issue: #95
Branch: `feature/p20-carbon`
Status: complete

Goal: expose the two carbon tables, because the writer they need is one option away and no keyword
reaches it.

- [x] P20.1 Write `CARBREPT` and expose the carbon tables (#96)
  - [x] Expose `FVS_Carbon_Metric` and `FVS_Hrv_Carbon`.
  - [x] A run with `CARBREPT` in an `FMIN` block writes both, and the first period carries a non-zero total.
  - [x] Document the NULL that FVS writes into `Total_Stand_Carbon` when a component is undefined.
  - [x] Correct the contract pages, the reachability record, and the module docstring.

Acceptance criteria:

- A run with `CARBREPT` in an `FMIN` block writes both carbon tables, with a non-zero total in the first period.
- The reader exposes thirteen tables, and the NULL that FVS writes is documented rather than hidden.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 21: Release 0.7.0

Parent issue: #99
Branch: `feature/p21-release-0-7-0`
Status: complete

Goal: release `0.7.0`, because `main` carries the two carbon tables and the trigger that reaches them.

- [x] P21.1 Version and notes for 0.7.0 (#100)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.6.0".
  - [x] Replace the table gap with thirteen exposed.
  - [x] Add the carbon run to what is verified.

Acceptance criteria:

- The package reports `0.7.0`, and the notes say what changed and what remains.
- A clean checkout installs it and reads a carbon table with a non-zero total.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 22: The consumption table

Parent issue: #103
Branch: `feature/p22-consumption`
Status: complete

Goal: expose the consumption table, which needs a fire event rather than an option — and record why the
burn report beside it cannot be exposed at all.

- [x] P22.1 Write `SIMFIRE` and expose the consumption table (#104)
  - [x] Expose `FVS_Consumption_Metric`.
  - [x] A run with `SIMFIRE` and the fuel options writes one row with non-zero consumption.
  - [x] Record why the burn report cannot be exposed.
  - [x] Correct the contract pages, the reachability record, and the triage.

Acceptance criteria:

- A run with `SIMFIRE` writes one consumption row with non-zero consumption.
- The reader exposes fourteen tables.
- The burn report's dead gate is recorded with the two assignments that prove it.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 23: Release 0.8.0

Parent issue: #107
Branch: `feature/p23-release-0-8-0`
Status: complete

Goal: release `0.8.0`, because `main` carries the consumption table and the record of why the burn report
cannot be exposed.

- [x] P23.1 Version and notes for 0.8.0 (#108)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.7.0".
  - [x] Replace the table gap with fourteen exposed.
  - [x] Add the consumption run to what is verified.

Acceptance criteria:

- The package reports `0.8.0`, and the notes say what changed and what remains.
- A clean checkout installs it and reads a consumption row with a non-zero total.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 24: The sweep over the remaining tables

Parent issue: #111
Branch: `feature/p24-sweep`
Status: complete

Goal: classify all 44 tables mechanically, so the table question closes with a record instead of an open
invitation — and correct the claim the sweep disproves.

- [x] P24.1 Sweep the 44 tables and correct the record (#112)
  - [x] Sweep all 44: writer by source mention, call sites by `grep -rl "CALL <name>"`.
  - [x] Rewrite the reachability note as the definitive classification.
  - [x] Correct the "no writer" claim in every live document.
  - [x] Record the correction in the changelog.

Acceptance criteria:

- Every one of the 44 tables has a verdict, and each is reproducible with the commands the note names.
- The wrong "no writer" claim is corrected in every live document.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 25: The notes describe the next release

Parent issue: #115
Branch: `feature/p25-notes-for-the-next-release`
Status: complete

Goal: stop `RELEASE_NOTES.md` on `main` from claiming to be the published `0.8.0` body.

- [x] P25.1 Retitle the notes for the next release and carry the correction (#116)
  - [x] Move the title to `0.9.0`.
  - [x] Add "What changed since 0.8.0" with the sweep's correction.
  - [x] Leave every earlier section exactly as it was published.

Acceptance criteria:

- `RELEASE_NOTES.md` on `main` no longer claims to describe `0.8.0`.
- The correction is the first entry of the next release's section.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 26: The damage-agent blocks

Parent issue: #119
Branch: `feature/p26-dm-rd`
Status: complete

Goal: take the dwarf-mistletoe and root-disease tables the sweep re-opened, and find out whether the block
keywords that start them are enough.

- [x] P26.1 The damage-agent blocks, and what they do not reach (#120)
  - [x] `MISTOE` joins the line blocks.
  - [x] A run with a `MISTOE` block is accepted and echoes its sub-keyword.
  - [x] Record what was tried and what would close the gap.
  - [x] Write `notes/reference/table-candidates.md`.

Acceptance criteria:

- A run with a `MISTOE` block is accepted, and the report echoes its sub-keyword.
- The reachability note says what was tried, what FVS said, and what would close the gap.
- `notes/reference/table-candidates.md` covers all 25 candidates with an estimate each.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 27: The cheap tables

Parent issue: #123
Branch: `feature/p27-the-cheap-five`
Status: complete

Goal: take the five tables the candidate note called cheapest, close the per-tree hole, and record the two
that resist.

- [x] P27.1 The four tables, and the two that resisted (#124)
  - [x] Expose `FVS_TreeList_Metric`, `FVS_CutList_Metric`, `FVS_Down_Wood_Cov_Metric` and `FVS_Stats_Species_Metric`.
  - [x] A run with `TREELIDB`, `CUTLIDB`, `DWDCVDB`, `INVSTATS` and the matching requests writes all four.
  - [x] Record why `FVS_Mortality_Metric` and `FVS_Stats_Stand` did not appear.
  - [x] Update the contract pages, the reachability note and the candidate note.

Acceptance criteria:

- A run writes all four tables, and the reader exposes eighteen.
- The per-tree test asserts the identity columns and the `CCum`/`CCuM` difference.
- The two that resisted are recorded with what would close them.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 28: StrClass and ATRTList

Parent issue: #127
Branch: `feature/p28-strclass-atrtlist`
Status: complete

Goal: take the two tables the candidate note put second, one of which is the BC-specific one.

- [x] P28.1 The structural stage and the attribute list (#128)
  - [x] Expose `FVS_StrClass_Metric` and `FVS_ATRTList_Metric`.
  - [x] A run writes both, and the attribute list needs a partial removal.
  - [x] Update the contract pages, the reachability note and the candidate note.

Acceptance criteria:

- A run writes both tables, and the reader exposes twenty.
- The test records that a removal taking everything creates the attribute table and inserts nothing.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 29: Release 0.9.0

Parent issue: #131
Branch: `feature/p29-release-0-9-0`
Status: complete

Goal: release `0.9.0`, because `main` carries six more tables — including the first per-tree output the
package has had, and the BC-specific structural stage.

- [x] P29.1 Version and notes for 0.9.0 (#132)
  - [x] Bump the version in two files.
  - [x] Reorder "What changed since 0.8.0" into one account, with the six tables and the correct counts.
  - [x] Add the per-tree and stage runs to what is verified.
  - [x] Check that no bullet still says eighteen or fourteen exposed.

Acceptance criteria:

- The package reports `0.9.0`, and the notes say what changed and what remains.
- A clean checkout installs it and reads a per-tree table and the structural stage.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 30: CanProfile and the fixture limits

Parent issue: #135
Branch: `feature/p30-canprofile-fixture`
Status: complete

Goal: test the claim that the fixture is the binding constraint, and take whatever table does not need it.

- [x] P30.1 The canopy profile, and what the fixture cannot reach (#136)
  - [x] Expose `FVS_CanProfile`.
  - [x] Test the fixture claim: more plots, a bigger stand under a fire, and an infected stand.
  - [x] Record the three results with their evidence, and withdraw the claim they disprove.

Acceptance criteria:

- A run with `CANFPROF` writes the canopy profile, and the reader exposes twenty-one.
- The fixture claim is tested, not repeated, and the note says what each experiment returned.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 31: The three questions, answered

Parent issue: #139
Branch: `feature/p31-three-questions`
Status: complete

Goal: answer the three questions `P30` called unknown by reading the source, and take the four tables they
unblock.

- [x] P31.1 The three questions, answered, and the four tables (#140)
  - [x] Expose `FVS_Stats_Stand`, `FVS_Mortality_Metric` and the two dwarf-mistletoe summaries.
  - [x] A run with `DESIGN` field 4 above 1, `MORTREPT` and a fire, and damage code 30 writes them.
  - [x] Replace the note that called the fixture the constraint with the three answers.
  - [x] Update the contract pages, the reachability note and the candidate note.

Acceptance criteria:

- A run writes all four tables, and the reader exposes twenty-five.
- Each answer names the file and line it comes from.
- The note that called the fixture the constraint is replaced by the answers.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 32: The rest of the damage agents

Parent issue: #143
Branch: `feature/p32-dm-rd-rest`
Status: complete

Goal: finish the dwarf-mistletoe family and take the two root-disease tables that are reachable, by reading
the gates first.

- [x] P32.1 The rest of the damage agents (#144)
  - [x] `RDIN` joins the line blocks.
  - [x] Expose the two remaining dwarf-mistletoe tables and the two root-disease tables.
  - [x] A run with `MISTPRT`/`NEWSPRED`, and one with `RRINIT`/`RRDOUT`, writes all four.
  - [x] Update the contract pages, the reachability note and the candidate note.

Acceptance criteria:

- A run writes all four tables, and the reader exposes twenty-nine.
- Each recipe names the flag it sets and the line it is set on.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 33: Release 0.10.0

Parent issue: #147
Branch: `feature/p33-release-0-10-0`
Status: complete

Goal: release `0.10.0`, because `main` carries eight more tables and the correction of a method that had
been treating source-readable behaviour as unknown.

- [x] P33.1 Version and notes for 0.10.0 (#148)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.9.0": the eight tables, and the four answers with their lines.
  - [x] Replace the table gap with twenty-nine exposed and the ten named candidates.
  - [x] Add the four new runs to what is verified.

Acceptance criteria:

- The package reports `0.10.0`, and the notes say what changed and what remains.
- A clean checkout installs it and reads a statistics table, a mortality table, a damage-agent table and a root-disease table.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 34: The regeneration tables

Parent issue: #151
Branch: `feature/p34-regen`
Status: complete

Goal: take the regeneration tables, and settle the tables that cannot be taken at all.

- [x] P34.1 The regeneration tables, and the ones that stay out (#152)
  - [x] `ESTAB` joins the line blocks.
  - [x] Expose `FVS_Regen_Tally_Metric` and `FVS_Regen_SitePrep`.
  - [x] Record why the other tables stay out.
  - [x] Update the contract pages, the reachability note and the candidate note.

Acceptance criteria:

- A run with an `ESTAB` block writes both tables, and the reader exposes thirty-one.
- Each table that stays out has a recorded reason, not a guess.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 35: Release 0.11.0

Parent issue: #155
Branch: `feature/p35-release-0-11-0`
Status: complete

Goal: release `0.11.0`, because `main` carries the regeneration tables and the classification that closes
the table work.

- [x] P35.1 Version and notes for 0.11.0 (#156)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.10.0".
  - [x] Say that the table work is finished and why the rest is not effort.
  - [x] Add the regeneration run to what is verified.

Acceptance criteria:

- The package reports `0.11.0`, and the notes say what changed and what is settled.
- A clean checkout installs it and reads both regeneration tables.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 36: Banking it for real use

Parent issue: #159
Branch: `feature/p36-bank-for-deployment`
Status: complete

Goal: bank the project in the state a lab member can deploy it from, and record what real use should watch
for.

- [x] P36.1 The deployment note, and the stray artefact (#160)
  - [x] Write `notes/reference/deployment-readiness.md`.
  - [x] Remove the tracked `pyfvs.log` and ignore `*.log`.
  - [x] Point the README at the note.

Acceptance criteria:

- `notes/reference/deployment-readiness.md` carries the recipe, the gotchas, and what to watch.
- No build artefact is tracked, and `*.log` is ignored.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 37: The web front end

Parent issue: #163
Branch: `feature/p37-web-design`
Status: complete

Goal: give `fresh-fvsbc` a browser surface over the artefacts a run already writes, on the same front-end
architecture as ws4 and fhops — and record what FVS Online is, since that is the prior art.

- [x] P37.1 The web front end design note (#164)
  - [x] The artefact contract.
  - [x] The service surface, including the oracle flag per table.
  - [x] The skins, checked against a registry.
  - [x] The stack decisions and the tests.
  - [x] The prior-art record.

Acceptance criteria:

- The note names the artefact contract, the service surface, the skins, the stack decisions and the tests.
- The prior art is recorded from the workshop bundle, with the source location it points to.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 38: The web surface, first cut

Parent issue: #167
Branch: `feature/p38-web-first-cut`
Status: complete

Goal: build the surface the design note specifies — the artefact readers, the skin loader, the FastAPI
service, the static shell, and the contract tests.

- [x] P38.1 The readers, the skins, the service and the shell (#168)
  - [x] `web/runs.py`: discovery and the artefact readers, with no web dependency.
  - [x] `web/skins.py` and the four manifests, with unknown names refused.
  - [x] `web/app.py`: the endpoints, the oracle flag, SSE and the local-only bind refusal.
  - [x] `web/static/`: the shell, with no build step.
  - [x] `fresh-fvsbc web` dispatched before the run parser, and the `web` extra with package data.

Acceptance criteria:

- `fresh-fvsbc web --runs DIR` serves a real run directory, and every endpoint returns what the files hold.
- An unexposed table, a missing table and a missing run are each refused by name.
- The oracle flag is asserted against `EXPOSED_TABLES` and `ORACLE_TABLES`.
- The core install is unchanged: `pip install fresh-fvsbc` still pulls pandas only.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 39: A real BC case, and what it broke

Parent issue: #171
Branch: `feature/p39-real-case`
Status: complete

Goal: run a real BC case from the 2022 workshop bundle through the web surface, and fix what it breaks.

- [x] P39.1 A real BC case, and the four defects it found (#172)
  - [x] Refuse a stand above 999 trees per plot by name, with the reason.
  - [x] Report a failed child as `failed`, and serve its log.
  - [x] Discover a run the service started even when the child died before writing `run.key`.
  - [x] Take one ordered keyword list, so a `DATABASE` block can precede the stand setup.
  - [x] Record the limit in the tree-list contract, the triage and the deployment note.

Acceptance criteria:

- A real 999-tree BC stand runs through the web surface and writes 7 tables, including 3996 per-tree rows.
- The 1540-tree stand is refused by name, is visible as `failed`, and its log explains why.
- A run started through the API can ask for output tables, in the order the contract requires.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 40: Release 0.12.0

Parent issue: #175
Branch: `feature/p40-release-0-12-0`
Status: complete

Goal: release `0.12.0`, because `main` carries a whole new surface, verified against a real BC stand.

- [x] P40.1 Version and notes for 0.12.0 (#176)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.11.0".
  - [x] Add the 999-tree limit and the missing authentication to the known gaps, and renumber.
  - [x] Add the surface's verification to what is verified.

Acceptance criteria:

- The package reports `0.12.0`, and the notes say what changed and what remains.
- A clean checkout installs the web extra, serves a run, and reads its tables through the API.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 41: The container deployment and the oracle harness

Parent issue: #181
Branch: `feature/p41-container-and-oracle`
Status: complete

Goal: record the deployment the dev container actually has, and make a first cut of the oracle harness.

- [x] P41.1 The container deployment, recorded (#182)
  - [x] The reference page and the deployment note give the proxied command.
  - [x] The refusal message names the proxy rather than only the risk.
  - [x] A test asserts the service answers with and without its root path.
- [x] P41.2 The oracle harness, first cut (#183)
  - [x] `scripts/oracle_compare.py` renders, runs and compares.
  - [x] Tests cover the rendering, the comparison and the exit paths without the binary.
  - [x] The triage records the tree handoff the harness still needs.

Acceptance criteria:

- The reference page and the deployment note give the exact proxied command, and the refusal names it.
- A test asserts the service answers with and without its root path.
- `scripts/oracle_compare.py` renders, runs and compares, with tests that do not need the binary.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 42: The THINQFA supplemental record

Parent issue: #179
Branch: `feature/p42-thinqfa`
Status: complete

Goal: make `THINQFA` usable. The keyword reads a second record that selects the residual-density units, and
the wrapper could not write it.

- [x] P42.1 Add the THINQFA supplemental record (#180)
  - [x] `SUPPLEMENTAL_KEYWORDS` and a `supplemental` tuple on `Keyword`.
  - [x] Exactly one record, first character `0`, `1` or `2`; refused when missing or on another keyword.
  - [x] Rendered immediately after the keyword, with no `END`.
  - [x] `--keyword THINQFA=...;0` through the CLI, which the web API inherits.

Acceptance criteria:

- A `THINQFA` set renders its units record, and a set without one is refused by name.
- The record reaches FVS through the CLI and therefore through the API.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 43: The proxy prefix

Parent issue: #186
Branch: `feature/p43-proxy-prefix`
Status: complete

Goal: make the service work behind the JupyterHub proxy without depending on whether it strips the prefix.

- [x] P43.1 Handle the proxy prefix in the service (#187)
  - [x] A middleware strips a configured prefix when the request carries it.
  - [x] The test asserts both forms.

Acceptance criteria:

- `/api/runs` and `<prefix>/api/runs` both answer 200, as do the assets.
- No deprecation warning on start.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 44: Release 0.13.0

Parent issue: #192
Branch: `feature/p44-release-0-13-0`
Status: complete

Goal: release `0.13.0`, because `main` carries three things a deployment needs: `THINQFA`, the JupyterHub
proxy fix, and the oracle harness first cut.

- [x] P44.1 Version and notes for 0.13.0 (#193)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.12.0".
  - [x] Restate the authentication gap as the deployment assumption it is.
  - [x] Add the proxied verification to what is verified.

Acceptance criteria:

- The package reports `0.13.0`, and the notes say what changed and what remains.
- A clean checkout serves a run at `/api/runs` and under a prefix.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 45: The tree handoff, mapped

Parent issue: #196
Branch: `feature/p45-tree-handoff`
Status: complete

Goal: find the mechanism by which the standalone reads tree records, and record it.

- [x] P45.1 Map the tree handoff and record it (#197)
  - [x] `TREEDATA`'s field 1 and what each value means.
  - [x] The two routes tried and how each failed, with FVS's own messages.
  - [x] The route that is known to work, named.

Acceptance criteria:

- The triage states each mechanism, each failure, and FVS's own message for it.
- The harness warns, in its own docstring, that its tree handoff is unfinished.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 46: The DSNin tree handoff

Parent issue: #200
Branch: `feature/p46-dsnin`
Status: complete

Goal: make the standalone read a run's trees, so the oracle harness can compare at all.

- [x] P46.1 Read the trees through a DSNin input database (#201)
  - [x] An input database with `FVS_TreeInit` and `FVS_StandInit`.
  - [x] A `DSNin` block in place of the inline records.
  - [x] The exit-code fix: a logged error is not a fatal one.

Acceptance criteria:

- The standalone reads every tree and writes the per-tree table.
- The harness compares without treating a logged error as fatal.
- The triage records that the differences are not yet attributed.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 47: A quiet run

Parent issue: #204
Branch: `feature/p47-quiet-run`
Status: complete

Goal: stop reporting a run as failed when FVS simply had nothing to log.

- [x] P47.1 A run that logs nothing is not a failed run (#205)
  - [x] `read_errors` answers an absent `FVS_Error` with an empty frame.
  - [x] `ERROR_COLUMNS` names its columns.
  - [x] The contract page stops claiming the table is written on every run.

Acceptance criteria:

- A database without `FVS_Error` reads as no errors, with the table's columns.
- The contract page says why, and names the case that disproved the old claim.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 48: Release 0.14.0

Parent issue: #208
Branch: `feature/p48-release-0-14-0`
Status: complete

Goal: release `0.14.0`, because `main` carries a fix that mattered to a user-facing failure.

- [x] P48.1 Version and notes for 0.14.0 (#209)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.13.0", leading with the quiet-run fix.
  - [x] Say that the oracle comparison runs and is not yet an oracle.

Acceptance criteria:

- The package reports `0.14.0`, and the notes say what changed and what remains.
- A clean checkout runs a quiet stand and does not report it as failed.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 49: The oracle, attributed

Parent issue: #212
Branch: `feature/p49-oracle-attributed`
Status: complete

Goal: finish the standalone comparison so it is an oracle — it reports what agrees, explains what it
can, and fails on anything it cannot.

- [x] P49.1 The comparison says what it means (#213)
  - [x] The output `DATABASE` block opens before the input block.
  - [x] `tree_num` is read with the blanks ignored, as Fortran reads it.
  - [x] Run-identity columns are not compared.
  - [x] An unexplained difference fails, and a stale explanation is reported.

Acceptance criteria:

- A run's `FVS_Summary_Metric` and `FVS_TreeList_Metric` match the standalone's value for value.
- The run-identity columns cannot make a table differ.
- An unexplained difference fails the comparison, and an explanation that stops applying is reported.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 50: The fire-model block

Parent issue: #216
Branch: `feature/p50-fire-model-block`
Status: complete

Goal: make `FMIN` a validated block of keywords, so the snag, down-wood, fuel, potfire and carbon
tables can be asked for without hand-spacing FVS's fields.

- [x] P50.1 `FMIN` holds keywords (#217)
  - [x] The block moves from raw lines to keywords, rendered by the shared writer.
  - [x] The body is checked against `fmin.f`'s fifty-five keywords.
  - [x] A fire-model keyword outside the block is refused.
  - [x] `--block "FMIN|SNAGOUT=1|..."` parses each entry as a keyword.

Acceptance criteria:

- The block renders each parameter in FVS's ten-column field.
- A name outside `fmin.f`'s table is refused, and so is a fire-model keyword outside the block.
- `--block "FMIN|SNAGOUT=1|SNAGSUM=2"` builds the block.
- The snag, down-wood and carbon tables are written, and the oracle agrees with them.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 51: Release 0.15.0

Parent issue: #220
Branch: `feature/p51-release-0-15-0`
Status: complete

Goal: release `0.15.0`, because `main` carries a breaking change to the fire-model block and nine
tables now have a check where four did.

- [x] P51.1 Version and notes for 0.15.0 (#221)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.14.0", leading with the breaking change.
  - [x] Say which nine tables are checked and which two are out of reach.

Acceptance criteria:

- The package reports `0.15.0`, and the notes lead with the breaking change.
- A clean checkout builds an `FMIN` block from keywords and the snag, down-wood and carbon tables appear.
- The published documentation matches the source at the tag.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 52: A refusal is reported

Parent issue: #223
Branch: `feature/p52-refusal-is-reported`
Status: complete

Goal: report a refused keyword set instead of raising through the command line.

- [x] P52.1 A refused set is a reported error (#224)
  - [x] `KeywordOrderError` joins the input errors the command reports.
  - [x] A test for each order refusal.

Acceptance criteria:

- A `DATABASE` block after the stand exits `2` with the validator's message.
- A fire-model keyword outside its block does the same.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 53: Release 0.15.1

Parent issue: #228
Branch: `feature/p53-release-0-15-1`
Status: complete

Goal: release `0.15.1`, because `0.15.0` is published with a defect in it.

- [x] P53.1 Version and notes for 0.15.1 (#229)
  - [x] Bump the version in two files.
  - [x] Add "What changed since 0.15.0", leading with the fix.
  - [x] Verify both refusals from a clean checkout: a message and exit `2`.

Acceptance criteria:

- The package reports `0.15.1`, and the notes lead with the fix.
- A clean checkout refuses both cases with a message and exit `2`.
- `python scripts/dashboard.py` exits zero on the head commit.

## Phase 54: The fire tables

Parent issue: #232
Branch: `feature/p54-fire-tables`
Status: complete

Goal: give the oracle a fire, and make the four fire tables reachable and checked.

- [x] P54.1 The fire tables are reachable and checked (#233)
  - [x] The validator warns when `FUELOUT` or `POTFIRE` is read after `INVYEAR`.
  - [x] The harness leaves the inventory year to the run's own keyword.
  - [x] The four fire tables are checked against the standalone.

Acceptance criteria:

- A block that asks for `FUELOUT` or `POTFIRE` after `INVYEAR` warns, naming both keywords.
- A block before `INVYEAR` writes all four fire tables.
- The oracle agrees with all four, value for value.
- `python scripts/dashboard.py` exits zero on the head commit.

## Open decisions and where the detail lives

The detail for each phase lives in its focused plan under `notes/`; the evidence lives in
`notes/reports/`. What stays here is the ordering and the open decisions.

- **The current open items are the twelve known gaps in `RELEASE_NOTES.md`**, and **`notes/triage.md`
  gives each a disposition** — fix now, fix later with a phase, or accepted with the reason and what
  would reopen it. It is the backlog the review cadence reviews against. **Two rows are proposed for a
  `P7`** — the block keywords and the validator's temporary-path pattern — and its scope is the
  maintainer's to set rather than the table's to assume.
- **`run_case`'s non-re-entrancy and the thread-safety limit** are `P6.2`, and the mechanism is a
  decision rather than an assumption.
- **The triage is reviewed at each phase close-out**, in the phase's own report, and a disposition
  changes only in a change set that names the review that changed it.

**Every earlier open decision is closed, and an earlier revision of this section listed five of them as
open for four phases.** The CI quality matrix was done in `P3.1` (#18); `ADR 0004` was accepted on
2026-10-23; `FVS_Compute` and `FVS_Summary_Metric` were resolved by explanation in `P3.2` (#19) with
ADR 0009; the oracle comparison was promoted into a repository test in `P4.2` (#27); and `AGENTS.md`
pins the workflow revision. The list is kept here as history rather than deleted, because a stale plan
of record is a defect this project has now found twice.
