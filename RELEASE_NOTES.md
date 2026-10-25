# fresh-fvsbc 0.1.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

This is a **pre-1.0 release with known gaps**, listed below. The list is not a formality: the
capability this package does not have is a keyword block, and the limit it does not state is that a run
is not re-entrant. The public API can change.

## The build this release wraps

A result produced with this package is reproducible only against the build it wraps, so the release
names it. These values are read from `src/fresh_fvsbc/provenance.py` and from the built extension, not
quoted from memory:

| | |
| --- | --- |
| PyFVS fork | `UBC-FRESH/PyFVS` at **`e95172b`** |
| FVS source submodule | **`ef5fa847`** |
| Variant list | **`BC`**, status `OK` |
| Variant library | `pyfvs.fvsbc` |

The patch sets that make the build work are in this repository under `notes/reference/`: the
PyFVS-repository patch and the FVS-source patch. **They are banked here, not pushed to the fork**, so a
rebuild applies them to a clean checkout as ADR 0004 records.

## What is verified, and how

Each claim below names the command or the CI run that produces it. Where a check has a limit, the limit
is in the same sentence.

- **The variant builds from a clean checkout.** A fresh clone at `e95172b`, both patch sets applied with
  `git apply --check` first, `-Dfvsvariants=bc`, exit 0, `list_variants()` reporting `BC` as `OK`
  (`P4.1`, commit `cf64bec`). **It shows the recipe is not specific to one working tree; it does not
  show the build is byte-reproducible**, and the machine that ran it differs from CI's.
- **The test suite passes**: 378 passed, 2 skipped, coverage 98 percent on the release branch. **The
  two skips are the tests that need the built extension** — the end-to-end run and the oracle
  comparison — because this environment has none. In the clean environment where the extension is
  built, those two run and the two tests that the extension is *absent* skip instead. Neither skips
  silently.
- **One synthetic run through the public API returns outputs carrying provenance**, with one
  `FVS_Cases` row, a summary of 5 rows and 22 columns, and `provenance.json` beside the outputs
  (`notes/reference/synthetic-run.md`). **That the outputs reproduce is shown; that they are right is
  not**, and correctness rests on the oracle comparison below.
- **The command runs a case end to end and exits 0** (`notes/reference/synthetic-run.md`). It exits 1
  for a failed run and 2 for bad input; **both are tested with a faked drive and in a subprocess, not
  by a real failing run**.
- **The build agrees with FVS's own oracle on the first official case**: zero differing lines across
  164 rows and four stands, `FVS_Compute` at 160 rows, on the development machine **and** on CI's
  runner. **The oracle is a 2022 fixture** (`FS2022.4`, revision `20221118`), the comparison covers one
  of the two official cases, and it runs in a child process because FVS keeps its state in the process.
  See gaps 3 and 4.
- **The dashboard passes on Python 3.11 and 3.12**, in CI, with both records green (`P4.3`, run
  `40131167200`), and the branch protection still requires the four contexts with linear history.
- **The mutation harness catches all 24 mutations in its set** (`python scripts/mutation_check.py`).
  **It shows every mutation in the set is caught; the set is the author's choice.**

## Known gaps

Each is open for a stated reason, and each says where it is recorded. **Every one is triaged in
`notes/triage.md`**, which says which are being fixed, which are proposed for a later phase, and which are
accepted with the reason and what would reopen them.

1. **`run_case` is not re-entrant in a process, and a run is not thread-safe.** A second run inherits
   the first one's Fortran state, so two runs in one process are not independent, and the directory
   isolation the module documents is not enough. A run also changes the process's working directory for
   the projection and restores it afterwards, so two threads that run at once will interfere. A guard,
   a subprocess per run, or a documented restriction are the routes, and the choice changes the public
   API's contract. **The largest open item.** Recorded in `notes/reference/p4-acceptance.md`,
   `notes/reports/p4-closeout.md`, and `docs/reference/outputs.rst`.
2. **Block keywords are refused, not written.** `COMMENT`, `COMPUTE`, `IF` and `DATABASE` take a block
   of records ended by `END`, and the keyword model has no room for one, so the validator refuses them
   by name rather than producing a file that cannot work. **A run that needs `COMPUTE` cannot be
   expressed**, and `FVS_Compute` is exactly that table. A capability, not a fix.
3. **The second official case, `YSM-SkyRanch`, still differs**: 328 of 375 rows identical, three stands
   differing by small amounts, unexplained since `P2.3`. The oracle comparison covers the case that
   passes and says so.
4. **The oracle is a 2022 fixture, and the FVS project's own checker skips this variant**, carrying
   `#FVSbc -- Omit currently 20260226`. So agreement with it is evidence, not proof.
5. **The residual on three dense stands** of the second case is attributed, not proven, to upstream
   changes.
6. **`scripts/check_workflow.py` does not catch a POSIX temporary path** in a tracked file, though it
   catches a home-directory path. Four such paths were in a tracked note until `P3`'s close-out.
7. **`run.py`'s drive body is covered only where the extension is built**: the quality job reports that
   file at 87 percent and the build environment at 96, while the gate is met at 98 percent overall.
8. **A parameter passed to the command cannot contain a comma**, because the comma separates the
   fields. The API has no such limit.
9. **At `-O0` the variant writes no database at all**, so the optimiser is not optional. Recorded in
   ADR 0008 for the standalone and in `P4`'s report for the extension.
10. **The package needs a separately built extension.** Installing it does not build FVS; the variant
    comes from the pinned fork and the patch sets, by ADR 0004's recipe.
11. **The reader exposes two of the database's 32 tables.** `FVS_Cases` and `FVS_Error` are the ones
    the project has tested, and output contract rule 3 keeps an untested table out of the public API
    even when a run writes it. The summary comes from the run in memory instead.
12. **The `nemora` adapter requires `species` and `tree_age` from the caller**, because `nemora` emits
    neither, and it fails rather than defaulting. **Species assignment is out of scope** until a
    caller asks: `nemora` has no species machinery, so assigning one is a modelling question with a
    research burden of its own.

## What is not in this release

- **A distribution on PyPI.** Publishing to an index is a separate decision with an external account
  attached.
- **The standalone `FVSbc` executable.** It builds from upstream `main` and is **proven and not
  adopted** (ADR 0008, ADR 0009), so no CI job and no contract surface depend on it.
- **Any variant other than BC.** This package wraps `FVSbc` and only `FVSbc`; the other variants are
  PyFVS's concern.
- **Real inventory data.** The fixtures are synthetic, and BC inventory data is treated as restricted
  until its licence is proven open.

## Documentation

The contracts are the pages under `docs/reference/`: the tree-list input, the keyword set, the outputs,
the provenance record, and the `nemora` ingestion. The command and its exit codes are in `docs/usage.rst`.
The phase reports under `notes/reports/` carry the evidence for every claim above.
