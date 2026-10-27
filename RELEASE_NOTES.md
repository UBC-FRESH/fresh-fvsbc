# fresh-fvsbc 0.17.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.16.1

- **There is now a recipe for every table.** Naming a table's option in a `DATABASE` block is **never
  enough on its own**: the option is accepted whether or not the run does what the writer reports on,
  and the table is then simply absent — the projection succeeds, the database is written, and nothing
  says the table is missing. The new :doc:`reference/table-recipes` page gives the second thing each
  one needs. Some of them are not obvious:

  - a **removal** for the cut list and the after-treatment tree list;
  - a **fire** for mortality and for consumption;
  - **more than one plot** for the stand statistics, which are the distribution among sample points;
  - an **infection** through the damage columns for the four dwarf-mistletoe tables, and `NEWSPRED` for
    the fourth;
  - a **`PLANT` line carrying stems per acre** for the regeneration tables;
  - an **`RDIN` block with `RRINIT` and `RRDOUT`** for root disease. Earlier revisions of the docs
    recorded its required parameters as undetermined; they are those two, and both tables are written
    and match.

- **Twenty-seven of the thirty-one exposed tables are checked against a standalone `FVSbc`** built from
  the same source, and match it **value for value** — including every per-tree row. That is up from
  thirteen, and from four before this stretch.

- **One table is not checked, and the reason is on the record.** `FVS_Regen_SitePrep`'s `PcntNone`,
  `PcntMech` and `PcntBurn` are the site-preparation allocation across plots, drawn from a random
  distribution. They differ from the standalone's, and the difference is **not in this package**: both
  runs agree on every observable input, this package's run is deterministic across seeds, and the writer
  is a pass-through. What is left is a hypothesis about the two drivers' draw streams, and
  `notes/triage.md` says so rather than guessing.

## What changed since 0.16.0

- **The command prints the keyword set's warnings.** `0.16.0` added a warning about the fire-model
  block ordering, and **nothing printed it**: the run's result carries FVS's warnings from `FVS_Error`,
  and the validator's warnings had no route out of the run. The fix shipped and reached nobody who uses
  the command — which is how most people use it.

  ```text
  fresh-fvsbc: warning: an FMIN block that asks for FUELOUT or POTFIRE must precede INVYEAR: ...
  ```

  Found by verifying `0.16.0` from a clean checkout, running the case its own notes describe.

## What changed since 0.15.1

- **The fuels and potfire tables were silently not written, and now they are.** `FUELOUT` and
  `POTFIRE` set `IFLALB` and `IPFLMB` to the inventory year when they are read, and `fmdout.f` and
  `fmpofl.f` treat **any positive value as "suppress this report"**. An `FMIN` block read after
  `INVYEAR` therefore switched its own reports off: the run succeeded and `FVS_Fuels_Metric`,
  `FVS_PotFire_Metric` and `FVS_PotFire_Cond_Metric` were simply absent.

  **The official case never hits it** — its inventory year arrives from the input database, so the year
  is still zero when the block is read — which is why it has gone unnoticed upstream and would have hit
  every user of this package, which writes the year as a keyword.

  The validator now **warns**, naming both keywords. This is a change to what `validate_keywords`
  returns: a set that puts the block after `INVYEAR` now carries a warning where it carried none.

- **Thirteen exposed tables are checked against FVS's own writer**, up from nine:
  `FVS_Carbon_Metric`, `FVS_Consumption_Metric`, `FVS_Down_Wood_Cov_Metric`,
  `FVS_Down_Wood_Vol_Metric`, `FVS_Fuels_Metric`, `FVS_Hrv_Carbon`, `FVS_PotFire_Cond_Metric`,
  `FVS_PotFire_Metric`, `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric`, `FVS_StrClass_Metric`,
  `FVS_Summary_Metric` and `FVS_TreeList_Metric` all match a standalone `FVSbc` **value for value**.
  To use them, put the fire-model block before `INVYEAR`:

  ```console
  $ fresh-fvsbc population.json --directory run \
      --block "FMIN|FUELOUT=2|POTFIRE=2|CARBREPT=2" \
      --keyword INVYEAR=2020 ...
  ```

## What changed since 0.15.0

- **A refused keyword set is reported, not raised.** `validate_keywords` raises `KeywordOrderError` for
  a `DATABASE` block after the stand setup — the exact mistake the check exists to catch — and the
  command did not list it among its input errors, so Python printed a **traceback over the message**.
  It has been that way since the order check was added, and every release before this one has it. The
  same applied to a fire-model keyword written outside its `FMIN` block.

  ```text
  fresh-fvsbc: a DATABASE block must precede the stand setup; FVS refuses it later with
  'KEYWORD ENTERED IS USED IN WRONG CONTEXT'. The official case puts it first
  ```

  Found by verifying `0.15.0` from a clean checkout, running the refusal the release notes describe.

## What changed since 0.14.0

- **`FMIN` holds keywords, not raw lines.** This is a **breaking change** for anyone who built the
  fire-model block with `lines=`. A raw line let the caller space FVS's ten-column fields by hand,
  and a mis-spaced field is **not refused — it is read as a different number**:
  `SNAGCLAS  0.0   10.0  20.0  40.0` reaches FVS as class 2 `20.0` and class 3 `0.0`, with no error.
  The block now takes `Keyword` values and the shared writer spaces them, the body is checked against
  `fmin.f`'s own **fifty-five** keywords, a fire-model keyword outside the block is refused because
  FVS would ignore it, and `FUELMODL` and `DEFULMOD` take their one supplemental record. From the
  shell: `--block "FMIN|SNAGOUT=1|SNAGSUM=2|CARBREPT=2"`.
- **Nine tables are now checked against FVS's own writer.** The oracle comparison is attributed — the
  `0 of 5` was never source drift — and it reports what it can prove:
  `FVS_Carbon_Metric`, `FVS_Down_Wood_Cov_Metric`, `FVS_Down_Wood_Vol_Metric`, `FVS_Hrv_Carbon`,
  `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric`, `FVS_StrClass_Metric`, `FVS_Summary_Metric` and
  `FVS_TreeList_Metric` all match a standalone `FVSbc` **value for value**, including all 3,996
  per-tree rows. Before this release, four tables had a check.
- **The comparison reports what it cannot compare, and why.** It counts matches, explained differences
  and out-of-reach tables apart, so a table only one side writes is never read as agreement. Two are
  out of reach and named: `FVS_Error` is written only when FVS logs something, and `FVS_InvReference`
  is written by the standalone on every run and never by this package's build, for a cause that is not
  established.

## What changed since 0.13.0

- **A run that logs nothing is no longer reported as failed.** FVS writes `FVS_Error` **only when it has
  something to log**, and the reader treated an absent table as a failure to read — on the premise, stated
  in the output contract, that the extension writes it on every run. **That premise was false.** A
  999-tree single-plot case raised no warning, wrote no such table, and the package reported a perfectly
  good run as failed. `read_errors` now answers an absent table with an empty frame of its columns, so
  silence reads as a clean run.
- **The oracle harness reads a run's trees.** The standalone `FVSbc` now gets them through a
  `DATABASE ... DSNin ... TreeSQL` input database built from the run's own tree list and keywords: **999
  trees load and it writes 3,996 per-tree rows**. The inline `TREEDATA` route is dead — its field 1 is a
  file reference number, `2` for an external file and `15` for inline records, and neither placement works.
- **The comparison runs, and it is not yet an oracle.** It reports **0 of 5 tables agreeing** and the
  differences are **unattributed**: the two builds come from different source revisions — the pin
  `e95172b`/`ef5fa847` against upstream `28fda8ed`, because the pin's standalone will not build (ADR 0008)
  — and that alone can move numbers. `notes/triage.md` says so rather than presenting a tool that runs as
  a check that passes.

## What changed since 0.12.0

- **`THINQFA` is usable.** The keyword reads **one supplemental record** whose first column names the units
  of its residual-density target — `0` basal area per acre, `1` trees per acre, `2` stand density index —
  and the wrapper could not write it. The command now takes it after a semicolon:
  `--keyword THINQFA=1,0,24,0,1.4,2,100;1`. **A set without the record is refused rather than written**,
  because FVS would read the next keyword as the units record and the run would be wrong without saying so.
  The source is what settles it: `cuts.f` reads `PRMS(1..6)` from the six fields after the year, which
  leaves `QFATAR = INT(PRMS(7))` for that record.
- **The service works behind the JupyterHub proxy.** The dev container is **pre-authenticated** — JupyterHub
  authenticates the browser and forwards a local port under
  `/jupyterhub32/user/<name>/codeserver/proxy/<port>/` — so the service must bind off loopback and answer
  **under the prefix**. A middleware strips the prefix when the request carries it, which is what JupyterHub
  does, and leaves a request that does not alone. Verified live on `0.0.0.0`: both forms 200, the assets
  200, the container's own address 200. **Two wrong answers preceded it**: FastAPI's deprecated `root_path`
  answered both forms, and uvicorn's `root_path` answered neither.
- **`scripts/oracle_compare.py`**, a first cut at checking a run against the standalone `FVSbc`. It renders a
  standalone-runnable keyword file from a run directory, runs the binary and compares every exposed table.
  **The tree handoff is unfinished**: the standalone reads inline `TREEDATA` records as keywords and writes
  1001 `FVS_Error` rows, where the official case feeds trees through a `DATABASE ... DSNin ... TreeSQL`
  block. The triage records it.

## What changed since 0.11.0

- **There is a browser surface.** `pip install 'fresh-fvsbc[web]'` then `fresh-fvsbc web --runs DIR`. It is
  **a reader over the artefacts a run already wrote** — `run.key`, `run.tre`, `FVSOut.db`, `run.sum`,
  `summary.csv`, `provenance.json`, `variants.json` — and it starts a run by invoking the CLI in a
  subprocess, never by importing the Fortran extension. FastAPI behind an optional extra, a **vanilla ES
  module shell with no build step**, and four validated **skins** (`analyst`, `carbon`, `reviewer`,
  `tables`) whose unknown panels and actions are refused by name.
- **The surface marks which tables are verified.** `ORACLE_TABLES` is now a fact in `outputs.py`: four of
  the 31 exposed tables are checked against FVS's own database dump and 27 are not. `GET /api/oracle`
  reports the counts, every table record carries `oracle`, and the front end says so above the rows. A
  number whose provenance is unchecked must not look like one whose provenance is checked.
- **A real BC case ran through it, and broke four things.** The 2022 workshop bundle's own
  `FVS-BC.Stand.Structure.Data.db` — one stand, 1540 trees, site index FD 15, inventory year 2020 — found:
  **one plot holds at most 999 trees** (BC's record shares columns 1 to 4 between the plot and the tree
  number), so a larger stand is now refused **by name with the reason**; a **failed child was reported as
  running forever**, and is now reported `failed` with its log at `GET /api/runs/{id}/log`; a run that died
  before writing `run.key` was **invisible**, and a directory holding the service's log is now discovered;
  and the start request **grouped blocks after keywords**, which the `DATABASE`-first rule refuses — the
  list is now one ordered sequence.
- **A 999-tree subset of that real stand writes 7 tables through the surface**, including 3,996 per-tree
  rows, with the oracle flag marking one of the seven as verified and six as not.

## What changed since 0.10.0

- **Two more tables, so the reader exposes thirty-one of 44.** `FVS_Regen_Tally_Metric` and
  `FVS_Regen_SitePrep`, from an `ESTAB` block.
- **`ESTAB` is a block, and its `NATURAL` line needs the stems per acre.** `esin.f` reports error 4 and
  drops the **whole keyword set** when that field is zero — which is why a bare `ESTAB` was refused in every
  earlier attempt.
- **`FVS_CalibStats` is deliberately not exposed.** `CALBSTDB` creates the table on every run and it carries
  **nothing** unless the run is calibrated. A table that is always empty does not belong in the public API,
  and `keywords.rst` says so.
- **The table work is finished, and the record says why.** `notes/reference/table-reachability.md` classifies
  all 44 with a verdict each: thirty-one exposed, and thirteen that are not, of which eight are candidates
  and five have no call site at all. Of the eight, six are blocked by something this project does not have —
  an external climate attribute file, the FIA variant, a calibrated run, a bark-beetle specification, or the
  sprout model — and one has a gate no valid input can satisfy.

## What changed since 0.9.0

- **Two more tables, so the reader exposes thirty-one of 44.** `FVS_Regen_Tally_Metric` and
  `FVS_Regen_SitePrep`, from an `ESTAB` block.
- **`ESTAB` is a block, and its `NATURAL` line needs the stems per acre.** `esin.f` refuses the line —
  and the whole keyword set with it — when that field is zero, which is why a bare `ESTAB` was refused in
  every earlier attempt.
- **`FVS_CalibStats` is deliberately not exposed.** The table is created on every run and carries **nothing**
  unless the run is calibrated, and this package does not calibrate. Exposing it would put an always-empty
  table in the public API.

- **Eight more tables are readable, and the reader exposes twenty-nine of 44.** In order: `FVS_Stats_Stand`,
  `FVS_Mortality_Metric`, the four dwarf-mistletoe tables, two of the three root-disease tables, and
  `FVS_CanProfile`.
- **Four behaviours this project had called unknown were each one line of the source.** `P30` ran
  experiments, they did not fire, and it recorded a conclusion about FVS. That was wrong, and the
  correction is the substance of this release:
  - **`DESIGN`'s fourth field is the inventory point count** (`initre.f:798`). Every run here passed `1`,
    which is why `FVS_Stats_Stand` — the distribution among sample points — could never be computed.
  - **`MORTREPT` sets `IFMMRB = -1`** (`fmin.f:1372`), which is what `fmfout.f:294` gates on. `MORTREDB`
    alone writes nothing. The burn report's `BURNREPT` sets its equivalent to the inventory year, which the
    same gate rejects — two options that look identical and behave oppositely.
  - **Damage codes 30 to 34 are the mistletoe rating** (`misdam.f:76`), with the severity as the Hawksworth
    rating. Code 21, an earlier guess, registers as no mistletoe at all.
  - **`MISTPRT` and `NEWSPRED` gate the last two DM tables** (`misprt.f` calls `DBSMIS3` inside
    `IF (PRTMIS)` and `DBSMIS5`/`DBSMIS6` inside `IF (NEWMOD)`), and **`RDIN` refuses the whole set**
    without `RRTINV` or `RRMAN`.
- **`RDIN` is a block**, and it joins the five the model already writes, so a caller can express root
  disease.
- **The fixture was never the constraint.** The adapter already maps one plot per stand, and the tree list
  carries five plot ids when given five stands. Nothing was added to the fixture, because nothing was shown
  to be missing.

## What changed since 0.8.0

- **Four more tables, so the reader exposes twenty-nine of 44.** `FVS_DM_Sz_Sum_Metric`,
  `FVS_DM_TreeList_Metric`, `FVS_RD_Sum_Metric` and `FVS_RD_Det_Metric`. **All four dwarf-mistletoe tables
  and two of the three root-disease tables are now readable.**
- **The two DM tables that stayed away were behind two sub-keywords of the `MISTOE` block.** `misprt.f`
  calls `DBSMIS3` inside `IF (PRTMIS)` and `DBSMIS5`/`DBSMIS6` inside `IF (NEWMOD)`; `MISTPRT` sets the
  first and `NEWSPRED` the second.
- **`RDIN` is a block, and it refuses the whole set without an initialization.** `rdin.f` reports
  "NEITHER TREELIST OR MANUAL INITIALIZATION SPECIFIED" at the block's `END` unless `RRTINV` or `RRMAN` was
  seen; `RRINIT` sets `RRMAN`, and `RRDOUT` adds the detail table.

- **Four more tables, and three questions answered by reading the source instead of guessing.**
  `FVS_Stats_Stand`, `FVS_Mortality_Metric`, `FVS_DM_Spp_Sum_Metric` and `FVS_DM_Stnd_Sum_Metric` join the
  twenty-one, so the reader exposes **twenty-five of 44**.
- **`DESIGN`'s fourth field is the inventory point count.** Every run here passed `1`, so `FVS_Stats_Stand`
  — the distribution among sample points — could not be computed and said so. With `5` it is written. The
  fixture never needed to change; the adapter already maps one plot per stand.
- **`MORTREPT` is what makes the mortality table appear**, because `fmin.f` sets `IFMMRB = -1` for it and
  `fmfout.f` gates the section on `IF (IFMMRB .LT. 0 .AND. IFIRE .GE. 0)`. `MORTREDB` alone is accepted and
  writes nothing. The burn report's `BURNREPT` sets its equivalent to the inventory year, which is why that
  one really is dead — two options that look identical and behave oppositely.
- **A mistletoe rating enters through the damage columns**: `misdam.f` maps damage codes **30 to 34** onto
  the Hawksworth rating, with the severity as the rating. Code 21, an earlier guess, registers as no
  mistletoe at all.
- **The previous release's "the fixture is the binding constraint" was wrong**, and
  `notes/reference/fixture-limits.md` now records the three answers with the lines they come from.

- **One more table, and a claim withdrawn.** `FVS_CanProfile` joins the twenty — the canopy fuels profile by
  height layer, which is the vertical structure a fuel or wildlife model wants — so the reader exposes
  **twenty-one of 44**. Its trigger, `CANFPROF` inside `FMIN`, was a guess in the candidate note and the
  guess was right.
- **"The fixture is the binding constraint" was tested and is mostly wrong.** Three experiments, in
  `notes/reference/fixture-limits.md`: the fixture **already** produces five plots (the tree list carries
  plot ids 1 to 5), yet FVS reports `DISTRIBUTION OF ATTRIBUTES AMONG SAMPLE POINTS CANNOT BE COMPUTED WITH
  ONE SAMPLE POINT`; a five-plot population with **200 trees** under a 100 percent burn still writes no
  mortality table; and `damage1 = 21` does not register as dwarf mistletoe at all. **Nothing was added to
  the fixture**, because nothing was shown to be missing.

- **Six more tables are readable, and the reader exposes twenty of 44.** Two of them close the biggest
  hole the package had: `FVS_TreeList_Metric` and `FVS_CutList_Metric` are its **first per-tree output
  ever** — one row per tree per period, with the FVS, PLANTS and FIA species codes, so a result can be
  joined to anything else. The other four are `FVS_Down_Wood_Cov_Metric`, `FVS_Stats_Species_Metric`,
  `FVS_StrClass_Metric` and `FVS_ATRTList_Metric`.
- **`FVS_StrClass_Metric` carries the structural stage** — the class British Columbia uses for old-growth
  and habitat assessment, and nothing else in the package carried it.
- **An option alone is not enough, and that is now the rule rather than the exception.** The `DATABASE`
  block names the table; a second keyword asks FVS to produce the rows. `TREELIDB` needs `TREELIST`,
  `CUTLIDB` needs `CUTLIST`, `INVSTATS` needs `STATS`, `DWDCVDB` needs `DWDCVOUT`, `STRCLSDB` needs
  `STRCLASS`, `ATRTLIDB` needs `ATRTLIST`. Without the second keyword the option is accepted and writes
  nothing.
- **The attribute list has three failure modes, and all three were hit.** Its writer returns unless it is
  called from `cuts.f`, so it is written only after a cutting operation. A residual above the stand's
  basal area cancels the thinning and writes no table; a removal that takes everything creates the table
  and inserts **nothing**; a **partial** removal — residual zero with half the selected trees taken — is
  what produces rows.
- **FVS spells one column differently in the two per-tree tables**: `CCum` in the tree list and `CCuM` in
  the cut list. The reader does not rename it, and the output contract says so.
- **Two of the six attempted tables resisted, and the reasons are recorded**: `FVS_Mortality_Metric` needs
  a fire that kills trees, and `FVS_Stats_Stand` is the distribution of attributes among sample points and
  the fixture has one.
- **The table classification is mechanical now, and it corrected an earlier note.** A sweep finds each
  table's writer by source mention and counts its call sites: **twenty exposed, 19 with a writer and a
  call site, five with a writer that nothing calls, and none without a writer.** It also showed that
  `0.8.0`'s gap list was wrong to say the dwarf-mistletoe and root-disease writers do not exist — they do,
  as `DBSMIS1` (called from `misprt.f`) and `DBSRD1` (called from `rdpr.f`), and the grep that "proved"
  otherwise searched for names that are not in the source. **The published `0.8.0` body keeps the original
  text**, because a release body is immutable.
- **`notes/reference/table-candidates.md` gives every remaining candidate a cost, a risk and a value**,
  with a proposed order. It is the plan for the other 24 tables, and it is written so it can be checked.

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
- A run with `DESIGN`'s fourth field above one writes `FVS_Stats_Stand`; one with `MORTREPT` and a fire
  writes `FVS_Mortality_Metric`; an infected stand writes all four dwarf-mistletoe tables; and an `RDIN`
  block with `RRINIT` writes the root-disease summary and, with `RRDOUT`, the detail.
- A run with a `TREELIST` request writes the per-tree tables, and the cut list carries the same identity
  columns as the tree list; a run with `STRCLASS` writes the structural stage; a run with `ATRTLIST` and a
  **partial** removal writes the attribute list, and one with no removal writes it empty.
- The command runs a case end to end and exits `0`; `1` and `2` are tested with a faked drive and in a
  subprocess, not by a real failing run.
- The dashboard passes on Python 3.11 and 3.12 in CI.
- The mutation harness catches all **27** mutations in its set. The set is the author's choice.

## Known gaps

Eleven, each with the reason it is open. `notes/triage.md` gives each a disposition and what would reopen
it.

1. **The reader exposes thirty-one of 44 tables.** The other 13 are classified in
   `notes/reference/table-reachability.md` with a verdict each: eight are candidates, five have a writer that
   nothing calls, and the burn report's gate cannot be satisfied by valid input. **Of the eight candidates,
   six are blocked by something this project does not have** — an external climate attribute file, the FIA
   variant, a calibrated run, a bark-beetle specification, the sprout model — and none is blocked by effort.
2. **One plot holds at most 999 trees.** BC's tree record shares columns 1 to 4 between the plot and the
   tree number, so the writer has three digits. A stand of 1540 trees — which the 2022 workshop's own case
   carries in one plot — is refused by name. Subdividing a stand into plots changes what the statistics
   mean, so it is a modelling decision and not a repair.
3. **The web surface has no authentication of its own, by design.** The dev container supplies it: the
   JupyterHub port proxy authenticates the browser, so the service is deployed with
   `--host 0.0.0.0 --allow-remote --root-path <proxy prefix>` and the proxy is what guards it. The service
   still refuses a non-loopback bind without `--allow-remote`, and its message says why. **This is a
   deployment assumption, not a defect** — reopened if the service is ever bound where no proxy fronts it.
4. **The second official case, `YSM-SkyRanch`, differs** on three stands, 328 of 375 rows identical,
   unexplained since `P2.3`.
5. **The oracle is a 2022 fixture, and the FVS project's own checker skips this variant.** Agreement is
   evidence, not proof.
6. **The residual on three dense stands** is attributed, not proven, to upstream changes.
7. **`run.py`'s drive body is covered only where the extension is built**: 84 percent in the quality
   job, which has no extension, and the gate is met at 97 percent overall because the build job covers
   the rest.
8. **A parameter passed to the command cannot contain a comma.**
9. **At `-O0` the variant writes no database at all**, so the optimiser is not optional.
10. **The package needs a separately built extension.** Installing it does not build FVS.
11. **The `nemora` adapter requires `species` and `tree_age`**, and species assignment is out of scope.

## What is not in this release

A PyPI distribution, the standalone `FVSbc` (proven and not adopted, ADR 0008 and ADR 0009), any variant
other than BC, and real inventory data.
