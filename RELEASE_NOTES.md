# fresh-fvsbc 0.2.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.1.0

- **A run drives FVS in a child process** (ADR 0010). In `0.1.0`, a second run in one process inherited
  the first one's Fortran state: the official case differed from the oracle on **104 of 164 rows** after
  another case had run. It is now **0**, and a run no longer changes the caller's working directory, so
  two runs are independent and a run is thread-safe. Cost: about 0.4 s per run.
- **`COMMENT`, `COMPUTE` and `DATABASE` can be written.** The keyword model holds lines and the writer
  supplies the `END`. FVS's own report echoes a `COMPUTE` block as `DEFINE THE FOLLOWING`, so it is read
  rather than ignored.
- **The validator catches a POSIX temporary directory** in a tracked file, and not a placeholder, a
  repository-relative path, or a generic temp file.

The API changed in three places, which is why this is a minor bump: `Keyword` gained `lines`,
`BLOCK_KEYWORDS` split into `LINES_KEYWORDS` and `NESTED_KEYWORDS`, and `run_case` drives a child.

## The build this release wraps

Read from `src/fresh_fvsbc/provenance.py` and from the built extension:

| | |
| --- | --- |
| PyFVS fork | `UBC-FRESH/PyFVS` at **`e95172b`** |
| FVS source submodule | **`ef5fa847`** |
| Variant list | **`BC`**, status `OK` |

The patch sets are banked in `notes/reference/` and are **not pushed to the fork**; ADR 0004 is the
recipe.

## What is verified

- The variant builds from a clean clone at the pin, both patch sets apply, and `list_variants()` reports
  `BC` as `OK`. **The build is not byte-reproducible** across machines.
- The suite passes where the extension is built; the two skips are the tests that the extension is
  *absent*, and they invert in an environment without it.
- The build agrees with FVS's own oracle on the first official case: zero differing lines across 164
  rows. **The oracle is a 2022 fixture** (`FS2022.4`), and the comparison covers one of the two official
  cases.
- The command runs a case end to end and exits `0`; `1` and `2` are tested with a faked drive and in a
  subprocess, not by a real failing run.
- The dashboard passes on Python 3.11 and 3.12 in CI.
- The mutation harness catches all **26** mutations in its set. The set is the author's choice.

## Known gaps

Eleven, each with the reason it is open. `notes/triage.md` gives each a disposition and what would
reopen it.

1. **`IF` blocks are refused, not written.** `IF` wraps keywords ended by `ENDIF`, which needs a nested
   model; `COMMENT`, `COMPUTE` and `DATABASE` are supported.
2. **`FVS_Compute` is still not written.** It needs a `DATABASE` block asking for `ComputDB`, and PyFVS
   occupies that block. The expression can be defined; the table cannot be read.
3. **The second official case, `YSM-SkyRanch`, differs** on three stands, 328 of 375 rows identical,
   unexplained since `P2.3`.
4. **The oracle is a 2022 fixture, and the FVS project's own checker skips this variant.** Agreement is
   evidence, not proof.
5. **The residual on three dense stands** is attributed, not proven, to upstream changes.
6. **`run.py`'s drive body is covered only where the extension is built**: 87 percent in the quality
   job, 96 in the build environment, 98 overall.
7. **A parameter passed to the command cannot contain a comma.**
8. **At `-O0` the variant writes no database at all**, so the optimiser is not optional.
9. **The package needs a separately built extension.** Installing it does not build FVS.
10. **The reader exposes two of the database's 32 tables.**
11. **The `nemora` adapter requires `species` and `tree_age`**, and species assignment is out of scope.

## What is not in this release

A PyPI distribution, the standalone `FVSbc` (proven and not adopted, ADR 0008 and ADR 0009), any variant
other than BC, and real inventory data.
