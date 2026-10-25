# The 25 table candidates

`P24` classified all 44 tables by writer and call site. Fourteen are exposed. Of the remaining 30, **25
have a writer and a call site** — the candidates — five have a writer that nothing calls, and one has a
gate no valid input satisfies.

**Fifteen are wired as of `P32`** — `FVS_TreeList_Metric`, `FVS_CutList_Metric`,
`FVS_Down_Wood_Cov_Metric` and `FVS_Stats_Species_Metric` in `P27`, `FVS_StrClass_Metric` and
`FVS_ATRTList_Metric` in `P28`, `FVS_CanProfile` in `P30`, then `FVS_Stats_Stand`, `FVS_Mortality_Metric`,
`FVS_DM_Spp_Sum_Metric` and `FVS_DM_Stnd_Sum_Metric` in `P31`, then the other two dwarf-mistletoe tables
and the two root-disease summaries in `P32`. The reader went from fourteen tables to **twenty-nine**.

**Every estimate on this page that said "needs an infection state" or "needs a stand the fixture cannot
express" was wrong**, and `notes/reference/fixture-limits.md` records why: the three blockers were a
keyword field (`DESIGN` field 4), a keyword option (`MORTREPT`), and a damage code (30, not 21). **The
fixture was never the constraint.** They stay in place below, marked **wired**, because their estimates are the record of what they
cost and the evidence for the estimates on the rest.

This note exists so the remaining work can be planned rather than apologised for. It gives each candidate
what we actually know, why the table exists, and an estimate of the cost, the risk and the value of wiring
it in. **The estimates are mine, they are ranges, and they are not commitments.** Every one of them can
move once the table is tried, because the last three phases each found that the obvious trigger was the
wrong one.

## What "wired" means here

A table is wired when all four are true:

1. A run here writes it, and `tests/test_run.py` has a case that fails if it stops.
2. `read_table` returns it, so it is in `EXPOSED_TABLES`.
3. The output contract lists it and says what its rows mean.
4. The recipe is in `keywords.rst` or the reachability note, so a caller can reproduce the run.

A table that runs but is not tested is not wired, and output contract rule 3 keeps it out of the API.

**A self-check, so this note can be trusted or falsified**: it names exactly 25 tables, every one of them
in the 44 and none of them already exposed, and every routine, option and keyword it names was checked
against `tmp/pyfvs/fvs` before it was written down. A name that is not in the source is a claim nobody can
check, and three phases here have been spent correcting exactly that kind of claim.

## The cross-cutting risk: most of these have no oracle

The official dump is the only independent check, and it covers **four** tables — down wood volume, snag
detail, snag summary, and the summary itself. Everything else rests on "the run writes it and the columns
match the schema", which is a weaker claim: it proves the table exists, not that its numbers are right.

That matters more for some tables than others. A per-tree listing can be spot-checked against the tree
list the run consumed. A climate summary or a calibration statistic cannot be checked without a second
source. **Where a table's numbers cannot be checked, this note says so under Risk**, and that is a
property of the evidence, not of the work.

## The `DATABASE` option map

The options `dbsin.f` accepts, and the table each one asks for. This is the cheapest thing to try first
for any candidate: several are one option away.

| Option | Table |
| --- | --- |
| `TREELIDB` | `FVS_TreeList_Metric` |
| `CUTLIDB` | `FVS_CutList_Metric` |
| `ATRTLIDB` | `FVS_ATRTList_Metric` |
| `CLIMREDB` | `FVS_Climate_Metric` |
| `STRCLSDB` | `FVS_StrClass_Metric` |
| `MORTREDB` | `FVS_Mortality_Metric` |
| `DWDCVDB` | `FVS_Down_Wood_Cov_Metric` |
| `CALBSTDB` | `FVS_CalibStats` |
| `REGREPTS` | the `FVS_Regen_*` tables |
| `INVSTATS` | `FVS_Stats_*` |
| `MISRPTS` | the four `FVS_DM_*` tables |
| `RDSUM`, `RDDETAIL` | the three `FVS_RD_*` tables |
| `ECONRPTS` | the two economics tables — **no call site**, so the option writes nothing |

`FVS_CanProfile` is not in this list: its writer is reached from `fmpocr.f`, which the `CANFPROF` option
inside `FMIN` may gate. That is a guess to test, not a finding.

## Group A — per-tree and per-stand listings (6)

The package currently exposes **no per-tree output at all**. That is the largest hole in it: a caller who
wants to know what happened to individual trees has to parse a fixed-width report.

| Table | Writer, called from | Why it exists |
| --- | --- | --- |
| `FVS_TreeList_Metric` | `DBSTRLS`, `prtrls.f` | the per-tree listing — species, dbh, height, damage, volume, per cycle | | |
| `FVS_CutList_Metric` | `DBSCUTS`, `prtrls.f` | the trees removed, with the reason and the volume | | |
| `FVS_ATRTList_Metric` | `DBSATRTLS`, `prtrls.f` | the attribute list: the same trees with the full attribute set | | |
| `FVS_FIAVBC_TreeList` | `DBS_FIAVBC_TRLS`, `fvs.f` | a tree list in the shape the US Forest Service's FIA database expects | | |
| `FVS_FIAVBC_CutList` | `DBS_FIAVBC_CUTLST`, `cuts.f` | the same for removals | | |
| `FVS_FIAVBC_ATRTList` | `DBS_FIAVBC_ATRTLS`, `cuts.f` | the same for attributes | | |

The three `FIAVBC` tables are a different matter from the three `prtrls` ones: their names belong to the
**FIA reporting variant** of BC, not to plain `FVSbc`, so their call sites may sit behind a variant flag
that this build never sets. Test them last in this group, and expect them not to fire.

## Group B — fire effects and dead wood (3)

| Table | Writer, called from | Why it exists |
| --- | --- | --- |
| `FVS_Mortality_Metric` | `DBSFMMORT`, `fmfout.f` | mortality by agent and size, which the summary only totals | | |
| `FVS_Down_Wood_Cov_Metric` | `DBSFMDWCOV`, `fmdout.f` | down wood as **cover** rather than volume — the input coarse woody debris models want | | |
| `FVS_BurnReport_Metric` | `DBSFMBURN`, `fmfout.f` | the burn conditions of a fire: moisture by size class, wind, flame length | | |

`FVS_Mortality_Metric` and `FVS_Down_Wood_Cov_Metric` sit in the two routines the package already
triggers (`fmfout.f` for a fire, `fmdout.f` for the fuel output), so they are likely one option each.

## Group C — stand statistics and structure (5)

| Table | Writer, called from | Why it exists |
| --- | --- | --- |
| `FVS_Stats_Stand` | `DBSSTATS`, `stats.f` | stand-level statistics: quadratic mean diameter, basal area, volumes, by species and total | | |
| `FVS_Stats_Species_Metric` | `DBSSTATS`, `stats.f` | the same broken down by species | | |
| `FVS_StrClass_Metric` | `DBSSTRCLASS`, `sstage.f` | **structural stage** — the class BC uses for old-growth and habitat assessment | | |
| `FVS_Climate_Metric` | `DBSCLSUM`, `clauestb.f` | the climate the run used: temperature, precipitation, and the derived indices | | |
| `FVS_CanProfile` | `DBSFMCANPR`, `fmpocr.f` | the canopy profile by height layer — the vertical structure a fuel or wildlife model wants | | |

`FVS_StrClass_Metric` is the highest-value table in this group for BC work: structural stage is the
currency of old-growth and biodiversity assessment in this province, and nothing else in the package
carries it.

## Group D — regeneration (3)

| Table | Writer, called from | Why it exists |
| --- | --- | --- |
| `FVS_Regen_Tally_Metric` | `DBSTALLY`, `estab.f` | the regeneration tally: what established, by species and height class | | |
| `FVS_Regen_Sprouts_Metric` | `DBSSPRT`, `esuckr.f` | sprout regeneration, which is how many BC hardwoods regenerate | | |
| `FVS_Regen_SitePrep` | `DBSSITEPREP`, `estab.f` | the site preparation applied before planting | | |

These need an establishment model to be active, so the recipe is a keyword set that plants or allows
natural regeneration — more than an option, less than an infection state.

## Group E — damage agents (7)

| Table | Writer, called from | Why it exists |
| --- | --- | --- |
| `FVS_DM_Spp_Sum_Metric` | `DBSMIS1`, `misprt.f` | dwarf mistletoe summary by species | | |
| `FVS_DM_Stnd_Sum_Metric` | `DBSMIS1`, `misprt.f` | dwarf mistletoe summary for the stand | | |
| `FVS_DM_Sz_Sum_Metric` | `DBSMIS1`, `misprt.f` | dwarf mistletoe summary by size class | | |
| `FVS_DM_TreeList_Metric` | `DBSMIS1`, `misprt.f` | dwarf mistletoe per tree | | |
| `FVS_RD_Sum_Metric` | `DBSRD1`, `rdpr.f` | root disease summary | | |
| `FVS_RD_Det_Metric` | `DBSRD1`, `rdpr.f` | root disease detail by centre and species | | |
| `FVS_RD_Beetle_Metric` | `DBSRD1`, `rdpr.f` | the bark-beetle interaction with root disease | | |

**These are the ones the sweep re-opened, and they are the most expensive.** `P26` established that both
families are block keywords — `MISTOE` and `RDIN` — and that `MISTOE`'s block form is accepted by FVS and
echoes its sub-keywords. It also established that **a block alone writes no table**: the model needs an
infection state, meaning a mistletoe rating per tree and a root-disease centre, which the fixture
generator has no field for. So the work is not "find the option"; it is "give the bridge a way to express
an infected stand", and that is a change to the fixture contract as much as to the keyword set.

## Group F — calibration (1)

| Table | Writer, called from | Why it exists |
| --- | --- | --- |
| `FVS_CalibStats` | `DBSCALIB`, `dgdriv.f`, `initre.f`, `regent.f` | the calibration statistics FVS computes when it is calibrated against measured plots | | |

Niche: it is only meaningful for a calibrated run, and this package does not calibrate.

## The estimate table

Effort is the work to wire one table, assuming the trigger is found on the first or second attempt.
**S** is the proven option pattern — half a day. **M** needs a keyword or a block the model does not have
— one to two days. **L** needs an inventory state or a modelling setup — open-ended.

| Table | Effort | Risk | Value | Status |
| --- | --- | --- | --- | --- |
| `FVS_TreeList_Metric` | S | low — checkable against the tree list the run consumed | **high** — no per-tree output exists at all | **wired in `P27`** |
| `FVS_CutList_Metric` | S | low — same check | **high** — removals are the question most runs ask | **wired in `P27`** |
| `FVS_ATRTList_Metric` | S | medium — wide, and the attribute meanings are undocumented here | medium | **wired in `P28`** |
| `FVS_Mortality_Metric` | S | low | **high** — mortality by agent is the forest-health question | **wired in `P31`** |
| `FVS_Down_Wood_Cov_Metric` | S | low | medium — CWD models | **wired in `P27`** |
| `FVS_Stats_Stand` | S | medium — no oracle; checkable only for internal consistency | **high** — the numbers most reports quote | **wired in `P31`** |
| `FVS_Stats_Species_Metric` | S | medium — same | medium | **wired in `P27`** |
| `FVS_StrClass_Metric` | S | medium — the class boundaries are a model choice, not a fact | **high** for BC old-growth work | **wired in `P28`** |
| `FVS_Climate_Metric` | S | **high** — no way to check the indices without a second source | medium | |
| `FVS_CanProfile` | S | low — `CANFPROF` was the guess and it worked | medium | **wired in `P30`** |
| `FVS_Regen_Tally_Metric` | M | medium — needs an establishment model active | **high** for BC silviculture | |
| `FVS_Regen_Sprouts_Metric` | M | medium | medium | |
| `FVS_Regen_SitePrep` | M | medium | low | |
| `FVS_CalibStats` | S | **high** — meaningless without calibration | low | |
| `FVS_FIAVBC_*` (3) | M | **high** — probably behind a variant flag this build never sets | medium, to FIA users only | |
| `FVS_DM_*` (4) | S | low — damage code 30 and a severity | **high** in BC | **all four wired** |
| `FVS_RD_*` (3) | S | low — `RRINIT` and `RRDOUT` inside the block | **high** in BC | **two of three wired in `P32`** |
| `FVS_BurnReport_Metric` | — | **cannot be wired** — the gate needs an invalid input | none | |

## A proposed order

Cheapest first, and each step leaves the dashboard green:

1. **Done in `P27`** — `FVS_TreeList_Metric`, `FVS_CutList_Metric`, `FVS_Down_Wood_Cov_Metric`, and
   `FVS_Stats_Species_Metric`, which came along with the statistics option. Four tables, and the
   per-tree hole is closed. **Two from this step resisted**: `FVS_Mortality_Metric` needs a fire that
   kills trees, and `FVS_Stats_Stand` needs a stand with more than one sample point.
2. **Done in `P28`** — `FVS_StrClass_Metric` and `FVS_ATRTList_Metric`. The attribute list needed
   more than the note predicted: it is the *after-treatment* listing, so it needs a removal that leaves
   trees, and a removal that takes everything creates the table and inserts nothing.
3. **`FVS_CanProfile` done in `P30`**, and it took an hour rather than the day the `M` estimate gave:
   the guess was right. **The `FVS_Regen_*` three** remain, and they need an establishment model active.
4. **`FVS_Stats_Species_Metric`, `FVS_Climate_Metric`, `FVS_CalibStats`** — the low-value tail.
5. **The damage agents (7)** — a phase of its own, and it needs a fixture change first, so it should be
   planned as two: the bridge expresses an infected stand, then the tables follow.
6. **The `FIAVBC` three** — last, and only if a caller asks, because they may not be reachable at all.

That would take the reader from fourteen tables to **39 of 44**: everything except the five with no call
site, which no amount of work can write.

## What would change these estimates

- **A second oracle.** If a newer official dump carries any of these tables, the risk column collapses
  and the value column rises, because the numbers become checkable. The 2022 fixture carries four.
- **A caller.** Every accepted gap in `notes/triage.md` reopens on a caller's need, and a caller turns a
  `low` value into a `high` one without changing the effort.
- **The trigger turning out to be an option.** The `S` estimate assumes it is. Three of the last four
  tables needed something else, so treat `S` as the optimistic case.
