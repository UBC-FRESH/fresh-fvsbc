# What each exposed table needs, and which have a check

Thirty-one tables are exposed. This page gives the keyword set that makes each one **appear**, and
whether `scripts/oracle_compare.py` has compared it against a standalone `FVSbc`. It is the recipe
book for the oracle: a table with no check needs a case here, and the case is usually two keywords.

`P49` made the comparison trustworthy, `P50` gave the fire-model block a writer, and `P54` found that
three tables were silently absent. **Twenty-eight of the thirty-one have now been produced and
compared.**

## The result

| Verdict | Tables |
| --- | --- |
| **Match** | `FVS_ATRTList_Metric`, `FVS_CanProfile`, `FVS_Carbon_Metric`, `FVS_Compute`, `FVS_Consumption_Metric`, `FVS_CutList_Metric`, `FVS_DM_Spp_Sum_Metric`, `FVS_DM_Stnd_Sum_Metric`, `FVS_DM_Sz_Sum_Metric`, `FVS_DM_TreeList_Metric`, `FVS_Down_Wood_Cov_Metric`, `FVS_Down_Wood_Vol_Metric`, `FVS_Fuels_Metric`, `FVS_Hrv_Carbon`, `FVS_Mortality_Metric`, `FVS_PotFire_Cond_Metric`, `FVS_PotFire_Metric`, `FVS_RD_Det_Metric`, `FVS_RD_Sum_Metric`, `FVS_Regen_Tally_Metric`, `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric`, `FVS_Stats_Species_Metric`, `FVS_Stats_Stand`, `FVS_StrClass_Metric`, `FVS_Summary_Metric`, `FVS_TreeList_Metric` |
| **Differs, and the difference is open** | `FVS_Regen_SitePrep` |
| **Explained** | `FVS_Cases` (`SamplingWt`, see the module) |
| **Not comparable** | `FVS_Error`, `FVS_InvReference` |

## The recipes

A table appears when its `DATABASE` option is named **and** the run does what the writer reports on.
The option alone is accepted and writes nothing, which is the trap that costs the most time.

### Always

- `Summary` and `ComputDB` are cheap and give `FVS_Summary_Metric` and `FVS_Compute`.
- `TREELIDB` **and** a `TREELIST` keyword give `FVS_TreeList_Metric`.
- `STRCLSDB` **and** `STRCLASS` give `FVS_StrClass_Metric`.

### The fire-model block

Put `FMIN` **before `INVYEAR`** — `FUELOUT` and `POTFIRE` capture the inventory year, and FVS reads a
positive value as "suppress" (`P54`).

| Table | `DATABASE` option | Also needs |
| --- | --- | --- |
| `FVS_Fuels_Metric` | `FuelsOut` | `FUELOUT` |
| `FVS_PotFire_Metric`, `FVS_PotFire_Cond_Metric` | `PotfirDB` | `POTFIRE` |
| `FVS_Consumption_Metric` | `FuelReDB` | `FUELREPT` |
| `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric` | `SnagOuDB`, `SnagSuDB` | `SNAGOUT`, `SNAGSUM` |
| `FVS_Down_Wood_Vol_Metric`, `FVS_Down_Wood_Cov_Metric` | `DWDVLDB`, `DWDCVDB` | `DWDVLOUT`, `DWDCVOUT` |
| `FVS_Carbon_Metric`, `FVS_Hrv_Carbon` | `CarbReDB` | `CARBREPT` |
| `FVS_Mortality_Metric` | `MORTREDB` | `MORTREPT` **and a fire** — the writer is called from `fmburn.f` |
| `FVS_CanProfile` | — | `CANFPROF` |

`SIMFIRE=1,20,1,21,1,100,1` schedules a fire at cycle 1. Without one, the fire tables report the
initial state and the mortality table never appears.

### The event tables

| Table | `DATABASE` option | Also needs |
| --- | --- | --- |
| `FVS_CutList_Metric` | `CUTLIDB` | `CUTLIST` **and a removal** — `THINBBA=1,2` on this fixture cuts |
| `FVS_ATRTList_Metric` | `ATRTLIDB` | `ATRTLIST` **and a removal** — the writer is called from `cuts.f` |
| `FVS_Stats_Species_Metric` | `INVSTATS` | `STATS` |
| `FVS_Stats_Stand` | `INVSTATS` | `STATS` **and `DESIGN`'s fourth field above 1** — it is the distribution among sample points |

### The blocks

`RDIN`, `MISTOE` and `ESTAB` are blocks of **keywords**, written by the shared writer and checked
against `rdinie.f`, `misin.f` and `esin.f`.

| Table | Block | `DATABASE` option |
| --- | --- | --- |
| `FVS_RD_Det_Metric`, `FVS_RD_Sum_Metric` | `RDIN` with `RRINIT` and `RRDOUT` | `RDDETAIL`, `RDSUM` |
| `FVS_DM_*` (four) | `MISTOE` with `MISTPINF`, `MISTPRT`, `NEWSPRED` | `MISRPTS` |
| `FVS_Regen_Tally_Metric`, `FVS_Regen_SitePrep` | `ESTAB` with a `PLANT` line carrying stems per acre | `REGREPTS` |

**The four dwarf-mistletoe tables also need an infection.** The rating enters through the damage
columns — code `30` with the Hawksworth rating as the severity — and `NEWSPRED` is what makes the tree
list appear. Without it three of the four are written and the fourth is not.

## The open difference

`FVS_Regen_SitePrep` **differs**, and the difference is in the model rather than in the writer: the
`.out` prints `PCT: 74 20 6` for this package's run and `PCT: 100 0 0` for the standalone's, in the same
`SITE PREP SUMMARY` block.

**`P59` ruled out every observable input**: both runs have one plot, 4,146 tree rows, the same aspect,
slope, elevation and basal area, and this package's run is deterministic across seeds. What is left is
`estab.f`'s site-prep selection, which fills `SUMPRE` from draws out of the pre-generated uniform array
`WK6`; the likeliest cause is that the two drivers consume different numbers of draws before it runs.
That is a hypothesis — the draws were not compared.

The three columns that move are integers describing a random allocation, and every other table in the
same run matches. `notes/triage.md` carries the evidence and what would reopen it.

## What this cost, and what it taught

Every table needed two things, and the second was never the obvious one: a *removal* for the cut and
ATRT lists, a *fire* for mortality, *more than one plot* for the stand statistics, an *infection* for the
mistletoe tables, and a `PLANT` line with stems per acre for the regeneration ones. The option alone is
always accepted, and the table is always simply absent.
