# fresh-fvsbc 0.4.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.3.1

- **The reader exposes eight tables, not four.** `FVS_Down_Wood_Vol_Metric`, `FVS_InvReference`,
  `FVS_SnagDet_Metric` and `FVS_SnagSum_Metric` join `FVS_Cases`, `FVS_Compute`, `FVS_Error` and
  `FVS_Summary_Metric`.
- **Four of them are checked against FVS's own database dump**, which turned out to be CSV with a header
  per table: 160 rows of down wood volume, 848 of snag detail, 160 of snag summary, against the same
  run's rendering. `FVS_InvReference` postdates the 2022 fixture and rests on the schema instead; the
  page says which is which.
- **The table list is corrected: 44 tables, not 33.** The old list was the *base* schema's, and this
  variant builds the *metric* one, so **twenty-four of its names were tables a run here never writes**.
  The list is derived from the schema's four layers with the most specific module winning, and the check
  is the official case's own database: seven tables, all of them in the list.

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
- Four exposed tables hold the dump's row counts, and a `DATABASE` block placed first makes them written.
- The command runs a case end to end and exits `0`; `1` and `2` are tested with a faked drive and in a
  subprocess, not by a real failing run.
- The dashboard passes on Python 3.11 and 3.12 in CI.
- The mutation harness catches all **27** mutations in its set. The set is the author's choice.

## Known gaps

Ten, each with the reason it is open. `notes/triage.md` gives each a disposition and what would reopen
it.

1. **`IF` blocks are refused, not written.** `IF` wraps keywords ended by `ENDIF`, which needs a nested
   model; `COMMENT`, `COMPUTE` and `DATABASE` are supported.
2. **The reader exposes eight of 44 tables.** The other 36 need a case that triggers each one before
   output contract rule 3 allows exposing it.
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
