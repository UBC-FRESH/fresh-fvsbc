# fresh-fvsbc 0.9.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.8.0

- **Two more tables, and one of them is the BC-specific one.** `FVS_StrClass_Metric` carries the
  **structural stage** — the class BC uses for old-growth and habitat assessment — and
  `FVS_ATRTList_Metric` the after-treatment attribute list. The reader exposes **twenty of 44**.
- **The attribute list is the sharpest case yet of a table that needs more than a request.** Its writer
  returns unless it is called from `cuts.f`, so it is written only after a cutting operation, and a
  removal that takes everything creates the table and inserts **nothing**. A partial removal — a residual
  of zero with half the selected trees taken — is what produces rows.

- **Four more tables are readable, and they close the per-tree hole.** `FVS_TreeList_Metric`,
  `FVS_CutList_Metric`, `FVS_Down_Wood_Cov_Metric` and `FVS_Stats_Species_Metric` join the fourteen, so
  the reader exposes **eighteen**. Before this release the package had **no per-tree output at all**: a
  caller who wanted to know what happened to individual trees had to parse a fixed-width report.
- **An option alone is not enough, and that is now the pattern rather than the exception.** `TREELIDB`
  without a `TREELIST` request writes nothing, `CUTLIDB` without a `CUTLIST` request and an actual removal
  writes nothing, and `INVSTATS` without `STATS` writes nothing. The `DATABASE` block names the table; a
  second keyword asks FVS to produce the rows.
- **FVS spells one column differently in the two per-tree tables**: `CCum` in the tree list and `CCuM` in
  the cut list. The reader does not rename it, and the output contract says so.
- **Two of the five attempted tables resisted, and the reasons are recorded**: `FVS_Mortality_Metric` needs
  a fire that kills trees, and `FVS_Stats_Stand` needs a stand with more than one sample point.

- **The table gap is corrected, and the correction is the sweep's.** `notes/reference/table-reachability.md`
  now classifies all 44 tables mechanically: **fourteen exposed, 25 with a writer and a call site, five
  with a writer that nothing calls, none without a writer.** The five this build cannot write are
  `FVS_EconHarvestValue_Metric`, `FVS_EconSummary_Metric`, `FVS_FIAVBC_Summary`, `FVS_Regen_HabType` and
  `FVS_Regen_Ingrow_Metric`.
- **An earlier note was wrong.** `0.8.0`'s gap list said the dwarf-mistletoe and root-disease writers do
  not exist in this source. They do — `DBSMIS1`, called from `misprt.f`, and `DBSRD1`, called from
  `rdpr.f` — and the grep that "proved" otherwise searched for symbol names that are not in the source.
  **The published `0.8.0` release body keeps the original text**, because a release body is immutable;
  this file is the working copy for `0.9.0` and says what is true now.

## What changed since 0.7.0

- **The consumption table is readable.** `FVS_Consumption_Metric` joins the thirteen, so the reader
  exposes **fourteen**.
- **It needs a fire, not an option.** A fire in FVS is an *activity*, not a keyword: `FMBURN` looks for
  activity 2506 with `OPFIND`, and the `FMIN` option `SIMFIRE` schedules it. `DBSFMFUEL` is called from
  inside the routine that runs when something burns, so the `DATABASE` option `BURNREDB` alone writes
  nothing. One run reports 22.569 tonnes per hectare consumed and 77.31 percent of the duff.
- **The burn report beside it cannot be exposed.** `FVS_BurnReport_Metric` is written only inside
  `IF (IFMBRB .LT. 0)`, and `IFMBRB` is assigned `9999` at initialisation and the inventory year by
  `BURNREPT` — never negative unless `INVYEAR` is given an invalid negative year, which shifts the whole
  simulation. That is a dead branch in this source, and the pages say so.

## What changed since 0.6.0

- **Two carbon tables are readable.** `FVS_Carbon_Metric` and `FVS_Hrv_Carbon` join the eleven, so the
  reader exposes **thirteen**.
- **The trigger was an option, not a keyword.** `CARBREPT` inside an `FMIN` block is what sets `ICRPTB`
  and lets `fmcrbout.f` reach `DBSFMCRPT`, the carbon writer's only call site. The `DATABASE` option
  `CARBREDB` alone is accepted and writes nothing, which is why the previous release recorded carbon as
  unreachable.
- **A carbon total can be NULL.** `Total_Stand_Carbon` is NULL in a period where one of its components
  is undefined, and the reader returns `NaN` rather than inventing a zero — a zero there is a value, and
  a NULL is the absence of one.

## What changed since 0.5.0

- **Three more tables are readable.** `FVS_Fuels_Metric`, `FVS_PotFire_Metric` and
  `FVS_PotFire_Cond_Metric` join the eight, so the reader exposes **eleven**.
- **`FMIN` is the fourth line block.** `POTFIRE`, `FUELOUT` and `FUELREPT` are **options inside it, not
  keywords**, which is why the model could not express them: with `FMIN` written and a `DATABASE` block
  asking for `FuelsOut`, `FuelReDB` and `PotfirDB`, one run writes all three tables.
- **A record of which of the rest can be written at all**, in `notes/reference/table-reachability.md`.
  It found that carbon's writer has one call site in the fire-carbon report path and the `DATABASE`
  option alone does not reach it, and that the dwarf-mistletoe and root-disease writers **do not exist
  in this source**.

## What changed since 0.4.0

- **`IF` blocks can be written.** A caller can put keywords behind a condition — a thinning schedule, an
  establishment rule, anything FVS reads conditionally:
  `Keyword("IF", (), ("MOD(AGE,60) EQ 0",), (Keyword("THINBBA", ("0", "0.0")),))` renders as the
  condition, `THEN`, the body and `ENDIF`, with an optional `ELSE`.
- **The body is validated**, so an unknown keyword inside a conditional is refused like one outside it.
- **`ALSOTRY` is not modelled**, because no fixture here uses it.

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
- The exposed tables the official dump carries hold its row counts, and a `DATABASE` block placed first
  makes them written.
- A run with `CARBREPT` writes both carbon tables, and the first period carries a non-zero total — 13.6
  tonnes of carbon per hectare on the synthetic stand.
- A run with `SIMFIRE` writes one consumption row, and it carries a non-zero consumption — 22.569 tonnes
  per hectare on the same stand.
- The command runs a case end to end and exits `0`; `1` and `2` are tested with a faked drive and in a
  subprocess, not by a real failing run.
- The dashboard passes on Python 3.11 and 3.12 in CI.
- The mutation harness catches all **27** mutations in its set. The set is the author's choice.

## Known gaps

Nine, each with the reason it is open. `notes/triage.md` gives each a disposition and what would reopen
it.

1. **The reader exposes twenty of 44 tables.** The other 24 are classified in
   `notes/reference/table-reachability.md`: 19 have a writer and a call site and are candidates, five have
   a writer that nothing calls, and the burn report's gate cannot be satisfied by valid input. A call site
   is not a promise; each candidate needs its own case, and `notes/reference/table-candidates.md` gives
   each one a cost, a risk and a value.
2. **The second official case, `YSM-SkyRanch`, differs** on three stands, 328 of 375 rows identical,
   unexplained since `P2.3`.
3. **The oracle is a 2022 fixture, and the FVS project's own checker skips this variant.** Agreement is
   evidence, not proof.
4. **The residual on three dense stands** is attributed, not proven, to upstream changes.
5. **`run.py`'s drive body is covered only where the extension is built**: 84 percent in the quality
   job, which has no extension, and the gate is met at 97 percent overall because the build job covers
   the rest.
6. **A parameter passed to the command cannot contain a comma.**
7. **At `-O0` the variant writes no database at all**, so the optimiser is not optional.
8. **The package needs a separately built extension.** Installing it does not build FVS.
9. **The `nemora` adapter requires `species` and `tree_age`**, and species assignment is out of scope.

## What is not in this release

A PyPI distribution, the standalone `FVSbc` (proven and not adopted, ADR 0008 and ADR 0009), any variant
other than BC, and real inventory data.
