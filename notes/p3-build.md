# P3 plan: build

Phase: `P3`. Parent issue: `#17`. Branch: `feature/p3-build`.
Plan of record: `ROADMAP.md`, section "Phase 3: Build". This file is the focused plan the roadmap's task
lines link to, which is the role `notes/README.md` gives to a plan in this directory.

**Written before the work, which is the rule `P2` broke.** `P2`'s plan was written after both the work and
an audit of it, and the audit's first finding was that it did not exist. This one exists first, and
`session-protocol.rst` requires it before the first edit.

## Phase acceptance criteria, and the evidence each will need

| # | Criterion | Evidence that will satisfy it |
| --- | --- | --- |
| 1 | The CI quality job runs on Python 3.11 and 3.12, and branch protection requires all four contexts the workflow spec names | `gh pr checks` showing both contexts, and `gh api …/branches/main/protection --jq .required_status_checks.contexts` |
| 2 | The pinned fork's BC variant builds from a clean checkout in CI, not only in a developer's scratch clone | a CI job log that builds and imports `pyfvs.fvsbc`, on the phase's head |
| 3 | The standalone `FVSbc` executable builds from ADR 0004's recipe, and a run through it writes `FVS_Compute` and `FVS_Summary_Metric` | the executable's path and version output, and the two tables' row counts from a run |
| 4 | A mutation harness is committed, and reproduces a named mutation failing a named test | the command, its output, and a deliberate non-mutation control |
| 5 | The public API covers the five `P2.1` contracts, and one synthetic run through it returns outputs carrying provenance | a test that runs the whole chain and asserts each contract's artefact |
| 6 | The command-line entry point runs a case end to end | a recorded invocation, its exit status, and its outputs |
| 7 | `python scripts/dashboard.py` exits zero on both Python versions | the two CI jobs' logs, plus the local run |

## P3.1 The CI quality matrix, and a CI build of the variant

**Goal.** Close the limit on `P2`'s fourth acceptance criterion, and make the build reproducible outside a
developer's machine.

**Scope.** The `quality` job's `name:`, its `setup-python` input, and its matrix; a CI job that builds the
pinned fork's BC variant and imports it; and the branch-protection change that requires the four contexts,
run only after the matrix has produced them.

**Out of scope.** Any other CI change. Building every variant. Publishing anything.

**Subtasks.**

- [ ] Set the `quality` job's `name:` to `Quality gates, Python ${{ matrix.python-version }}` and its `setup-python` input to the matrix variable, and add a `[3.11, 3.12]` matrix.
- [ ] Add a job that applies ADR 0004's patch to the pinned fork, builds the BC variant, and imports `pyfvs.fvsbc`.
- [ ] After the matrix has run, set branch protection with the specification's four-context `PUT`, including this project's `required_linear_history`, and read the rule back.
- [ ] Record the change in the changelog with the reason, since a gate change requires one.

**Acceptance criteria.** Both quality contexts report on a pull request; the build job passes; protection
requires the four contexts and still requires linear history.

**Verification.** `gh pr checks <n>`; `gh api repos/UBC-FRESH/fresh-fvsbc/branches/main/protection --jq '{.required_status_checks.contexts, .required_linear_history}'`.

**Artifacts.** `.github/workflows/ci.yml`, the changelog entry, and the read-back quoted in the task's
closeout comment.

**Risks.** The build takes several minutes and needs `gfortran`, `meson`, `ninja` and `patchelf`; if the
runner lacks one, the job records the failure rather than being deleted. **The protection change must not
run before the matrix has produced the contexts**, or `main` would require checks that never report — the
exact command error a Verifier session caught in `P2`'s report.

## P3.2 The standalone `FVSbc` executable

**Goal.** Reach `FVS_Compute` and `FVS_Summary_Metric`, which PyFVS makes unreachable by occupying the
`DATABASE` output block. This is `P2.2`'s one deferred subtask.

**Scope.** Building the executable from the pinned fork with ADR 0004's recipe, recording its build and
invocation, and a run that writes the two tables.

**Out of scope.** Replacing the PyFVS route. The FFI stays the primary route; this is the route for the
tables it cannot reach.

**Subtasks.**

- [ ] Build `bin/FVSbc` from the patched fork, and record the command and its output.
- [ ] Run one case through it with a `DATABASE` output block, and confirm `FVS_Compute` and `FVS_Summary_Metric` are written.
- [ ] Record the recipe as an addition to ADR 0004 or as a new ADR, whichever the maintainer prefers; the default is a new ADR, since ADR 0004 is accepted.

**Acceptance criteria.** The executable exists, runs, and writes both tables; the recipe is recorded.

**Verification.** The executable's path and `--version`-equivalent output; `sqlite3 <db> ".tables"`; row
counts for both tables.

**Artifacts.** The recorded recipe, and `notes/reference/standalone-run.md`.

**Risks.** The standalone build is a different build path from the Python extension, and may need its own
patch. If it does, that is a finding for the ADR, not a workaround at a call site.

## P3.3 The mutation harness

**Goal.** Make the falsifiability evidence for every test reproducible from the repository, which removes
the limit on `P2`'s second acceptance criterion.

**Scope.** A committed tool that applies a named mutation, runs a named test, asserts the test fails, and
restores the file; a registry of mutations per module; and a control that asserts an unmutated run passes.

**Out of scope.** Coverage tooling. Property tests, which already exist.

**Subtasks.**

- [ ] Write the harness so that a mutation which does not apply is an error rather than a pass.
- [ ] Register the mutations already recorded in `CHANGE_LOG.md` for the five prototype modules.
- [ ] Run it in CI, or record why not.

**Acceptance criteria.** The harness reproduces a named mutation failing a named test, and a non-mutation
control passes; an anchor that does not match exits non-zero.

**Verification.** The harness's own tests, and one recorded run whose output names each mutation and its
test.

**Artifacts.** The harness, its tests, and a recorded run.

**Risks.** **The failure mode this harness exists to prevent is its own**: a mutation that silently does
not apply looks like a passing test. `P2` hit exactly that, twice. The harness's first test is therefore
that a bad anchor fails loudly.

## P3.4 The public API over the five contracts

**Goal.** A documented public surface over `treelist`, `keywords`, `nemora`, `outputs` and `provenance`,
with the open decisions below resolved.

**Scope.** The package's exported names and their docstrings; the resolution of the three open contract
questions below; and the API pages under `docs/api/`.

**Out of scope.** New capability. The modules exist and are tested; this task is the surface and the
decisions.

**Subtasks.**

- [ ] Export the five modules' public names from the package, with `__all__` and numpydoc docstrings.
- [ ] Resolve the record-versus-dataframe question, and record it in `outputs.rst`.
- [ ] Resolve the species-assignment question in `nemora-ingest.rst`.
- [ ] Resolve the `BECINFO` question in `keywords.rst`, which `P2.1` assigned to `P2.2` and `P2.2` did not discharge.
- [ ] Add the API pages, and extend `tests/test_api_docstrings.py` to cover the package.

**Acceptance criteria.** `import fresh_fvsbc` exposes the documented names; every public name has a
numpydoc docstring; the three contract questions are answered in the pages that asked them.

**Verification.** `python -c "import fresh_fvsbc; print(fresh_fvsbc.__all__)"`; the docs gate; the
extended docstring test.

**Artifacts.** `src/fresh_fvsbc/__init__.py`, `docs/api/`, and the three contract pages.

**Risks.** Widening the surface before it is needed. The default is to export what the contracts name and
nothing else.

## P3.5 Run orchestration

**Goal.** One function that assembles a keyword set, writes a tree list, drives FVS, reads the outputs
back, and returns them with their provenance.

**Scope.** The orchestration over the existing modules; the `DATABASE` output route the reader already
handles; and the error path that reports a failed run.

**Out of scope.** The standalone route, which is `P3.2`; any modelling decision.

**Subtasks.**

- [ ] Write the orchestration over `keywords`, `treelist`, `nemora`, `outputs` and `provenance`.
- [ ] Return the outputs with the provenance record, and fail a run that holds an error.
- [ ] Test it end to end on the synthetic population, skipping when the built extension is absent and recording the skip.

**Acceptance criteria.** One call runs a synthetic stand and returns its tables with provenance; a run
with an error row raises.

**Verification.** The end-to-end test, and the recorded skip when the extension is absent.

**Artifacts.** The orchestration module and its tests.

**Risks.** The extension is not in CI until `P3.1`; the test skips rather than fails, and the skip is
recorded, not silent.

## P3.6 The command-line entry point

**Goal.** Run a case from a shell, with the same guarantees as the API.

**Scope.** One command, its arguments, its exit codes, and its output paths.

**Out of scope.** A configuration language, and any interactive mode.

**Subtasks.**

- [ ] Write the command over the orchestration.
- [ ] Test its exit codes for success, a failed run, and bad input.
- [ ] Document it in the README and in `docs/`.

**Acceptance criteria.** The command runs a case end to end, and exits non-zero on a failed run.

**Verification.** A recorded invocation with its exit status and its outputs.

**Artifacts.** The command module, its tests, and its documentation.

**Risks.** A command that duplicates the API's logic. It calls the orchestration and adds no modelling.

## Task order, and one deviation from it

`P3.3`, the mutation harness, was run **before** `P3.2`, the standalone executable, which is not the
numbered order. The reason: the harness is the tool every remaining task's tests will be checked with,
and `P2` produced both a vacuous test and a mutation that never applied. Building it first means `P3.2`
and `P3.4` to `P3.6` are verified with it rather than retro-fitted. The maintainer approved the reorder.

## Open decisions, as recommendations with defaults

1. **Records or a dataframe from the reader.** `outputs.rst` says a dataframe; `pandas` is not a
   dependency. **Default: add `pandas` and return a dataframe**, because the contract says so, the sibling
   projects are pandas-based, and `P2`'s records were a narrowing that the report had to disclose. The
   alternative — keeping records and amending the contract — is cheaper and was `P2`'s choice; it should be
   reversed deliberately or kept deliberately, not left ambiguous.
2. **Where species comes from.** `nemora-ingest.rst` asks whether a caller will ever have species, or
   whether the project needs a species-assignment step. **Default: keep requiring it from the caller**, and
   record that a species-assignment step is out of scope until a caller asks for one.
3. **`BECINFO` and the BEC value.** `keywords.rst` asks how a caller supplies a BEC value and whether
   `BECINFO` is live, and assigned it to `P2.2`, which did not discharge it. **Default: read
   `canada/bc/becset.f` and `canada/bc/initre.f` again and record the answer either way**, because an
   unanswered contract item is worse than a "no".

## Carried from `P2`, and where each lands

| Carried item | Landed in |
| --- | --- |
| The one open `P2.2` subtask: reading `FVS_Compute` and `FVS_Summary_Metric` | `P3.2` |
| The CI quality matrix, and the limit on `P2`'s fourth criterion | `P3.1` |
| The missing mutation harness, and the limit on `P2`'s second criterion | `P3.3` |
| The `BECINFO` question, assigned to `P2.2` and not discharged | `P3.4` |
| The record-versus-dataframe question | `P3.4` |

## Phase risks

- **The build is the expensive part.** Two tasks depend on a compiled variant, and the CI job that proves
  it may be slow. If the runner cannot build it, the phase records that as a limit rather than pretending
  otherwise.
- **The plan can drift from the issues.** `P2`'s changelog and issue body disagreed about subtask numbers.
  The rule for this phase: the issue body is the live checklist, this file is the depth, and the roadmap
  mirrors the checklist.
- **The agent's self-reports are the weak point.** `P2` published a false citation, a vacuous test and a
  claim about a harness that did not exist, and two of those were found by a Verifier session rather than
  by the agent. The Verifier role continues, its rows stay `Unproven` until it has evidence, and every
  closeout claim cites a commit, a command, or a run.
