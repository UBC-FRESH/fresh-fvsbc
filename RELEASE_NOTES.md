# fresh-fvsbc 0.3.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.2.0

- **The reader exposes four tables, not two.** `FVS_Compute` and `FVS_Summary_Metric` join
  `FVS_Cases` and `FVS_Error`, so a `COMPUTE` expression's output and the summary are readable as
  typed columns rather than as a fixed-width report.
- **A `DATABASE` block must precede the stand setup**, and the validator now refuses a set that puts it
  later, with the FVS error the rule avoids. **This corrects `P3.2`**, which concluded that PyFVS owned
  the block and the tables were therefore unreachable. The constraint was always position.
- **`read_table` keeps an empty table's columns**, which it lost before, because it built the frame from
  records and a table with no rows has none.
- **The contract's table list is 33, not 32.** It was missing `FVS_Summary_Metric`, which the official
  case writes.
- `fresh_fvsbc.cli` is on the published API page.

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
- A run with a `DATABASE` block first writes `FVS_Compute` and `FVS_Summary_Metric`, and the reader
  returns them.
- The command runs a case end to end and exits `0`; `1` and `2` are tested with a faked drive and in a
  subprocess, not by a real failing run.
- The dashboard passes on Python 3.11 and 3.12 in CI.
- The mutation harness catches all **27** mutations in its set. The set is the author's choice.

## Known gaps

Ten, each with the reason it is open. `notes/triage.md` gives each a disposition and what would reopen
it.

1. **`IF` blocks are refused, not written.** `IF` wraps keywords ended by `ENDIF`, which needs a nested
   model; `COMMENT`, `COMPUTE` and `DATABASE` are supported.
2. **The reader exposes four of the database's 33 tables.** The other 29 are reachable by the same
   `DATABASE` block and each needs its own test before output contract rule 3 allows exposing it.
3. **The second official case, `YSM-SkyRanch`, differs** on three stands, 328 of 375 rows identical,
   unexplained since `P2.3`.
4. **The oracle is a 2022 fixture, and the FVS project's own checker skips this variant.** Agreement is
   evidence, not proof.
5. **The residual on three dense stands** is attributed, not proven, to upstream changes.
6. **`run.py`'s drive body is covered only where the extension is built**: 84 percent in the quality
   job, which has no extension, and the gate is met at 97 percent overall because the build job covers
   the rest.
7. **A parameter passed to the command cannot contain a comma.**
8. **At `-O0` the variant writes no database at all**, so the optimiser is not optional.
9. **The package needs a separately built extension.** Installing it does not build FVS.
10. **The `nemora` adapter requires `species` and `tree_age`**, and species assignment is out of scope.

## What is not in this release

A PyPI distribution, the standalone `FVSbc` (proven and not adopted, ADR 0008 and ADR 0009), any variant
other than BC, and real inventory data.
