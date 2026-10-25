# Which of the 44 tables a run here can actually write

The mechanical answer, for all 44. `P24` swept the source rather than guessing: each table's name is
looked for across `tmp/pyfvs/fvs` excluding the build directory, the `SUBROUTINE` in every file that
mentions it is the writer, and the writer's call sites are counted with `grep -rl "CALL <name>"` in
`bin/FVSbc_buildDir`.

**Counts, after `P27`: 18 exposed, 21 with a writer and a call site, 5 with a writer and no call site, and 0 without a writer.**

## The correction this sweep forced

`P18` recorded that the dwarf-mistletoe and root-disease writers **do not exist in this source**. That was
wrong, and the error was a bad grep: it searched for the symbols `DBSFMMRPT`, `DBSRDOUT` and `DBSRDDET`,
which are not the writers' names. The writers are **`DBSMIS1`**, called from `misprt.f`, and **`DBSRD1`**,
called from `rdpr.f`. Both have call sites, so both families are reachable in principle.

The lesson is the same one `P17` and `P20` taught: the answer was one directory away, and the negative
claim was the one that needed the most evidence.

## The table

| Table | Writer | Called from | Verdict |
| --- | --- | --- | --- |
| `FVS_ATRTList_Metric` | `DBSATRTLS` | prtrls.f | writer and call site |
| `FVS_BurnReport_Metric` | `DBSFMBURN` | fmfout.f | writer and call site |
| `FVS_CalibStats` | `DBSCALIB` | dgdriv.f,regent.f | writer and call site |
| `FVS_CanProfile` | `DBSFMCANPR` | fmpocr.f | writer and call site |
| `FVS_Carbon_Metric` | `DBSFMCRPT` | fmcrbout.f | exposed |
| `FVS_Cases` | `DBSCASE` | dbs_fiavbc_atrtls.f,dbs_fiavbc_cutlst.f,dbs_fiavbc_trls.f,dbsatrtls.f,dbscalib.f,dbsclsum.f,dbscmpu.f,dbscuts.f,dbserror.f,dbsfmburn.f,dbsfmcanpr.f,dbsfmcrpt.f,dbsfmdsnag.f,dbsfmdwcov.f,dbsfmdwvol.f,dbsfmfuel.f,dbsfmhrpt.f,dbsfmmort.f,dbsfmpf.f,dbsfmpfc.f,dbsfmssnag.f,dbsfuels.f,dbsingrow.f,dbsmis.f,dbsplothab.f,dbsprssql.f,dbsrd.f,dbsreference.f,dbssiteprep.f,dbssprt.f,dbsstats.f,dbsstrclass.f,dbssumry.f,dbstally.f,dbstrls.f | exposed |
| `FVS_Climate_Metric` | `DBSCLSUM` | clauestb.f | writer and call site |
| `FVS_Compute` | `DBSCMPU` | oplist.f | exposed |
| `FVS_Consumption_Metric` | `DBSFMFUEL` | fmfout.f | exposed |
| `FVS_CutList_Metric` | `DBSCUTS` | prtrls.f | exposed |
| `FVS_DM_Spp_Sum_Metric` | `DBSMIS1` | misprt.f | writer and call site |
| `FVS_DM_Stnd_Sum_Metric` | `DBSMIS1` | misprt.f | writer and call site |
| `FVS_DM_Sz_Sum_Metric` | `DBSMIS1` | misprt.f | writer and call site |
| `FVS_DM_TreeList_Metric` | `DBSMIS1` | misprt.f | writer and call site |
| `FVS_Down_Wood_Cov_Metric` | `DBSFMDWCOV` | fmdout.f | exposed |
| `FVS_Down_Wood_Vol_Metric` | `DBSFMDWVOL` | fmdout.f | exposed |
| `FVS_EconHarvestValue_Metric` | `DBSECHARV` | — | writer, no call site |
| `FVS_EconSummary_Metric` | `DBSECSUM` | — | writer, no call site |
| `FVS_Error` | `DBSERROR` | errgro.f | exposed |
| `FVS_FIAVBC_ATRTList` | `DBS_FIAVBC_ATRTLS` | cuts.f | writer and call site |
| `FVS_FIAVBC_CutList` | `DBS_FIAVBC_CUTLST` | cuts.f | writer and call site |
| `FVS_FIAVBC_Summary` | `DBSCARBBIOSUMRY` | — | writer, no call site |
| `FVS_FIAVBC_TreeList` | `DBS_FIAVBC_TRLS` | fvs.f | writer and call site |
| `FVS_Fuels_Metric` | `DBSFUELS` | fmdout.f | exposed |
| `FVS_Hrv_Carbon` | `DBSFMHRPT` | fmchrvout.f | exposed |
| `FVS_InvReference` | `DBSREFERENCE` | fvs.f | exposed |
| `FVS_Mortality_Metric` | `DBSFMMORT` | fmfout.f | writer and call site |
| `FVS_PotFire_Cond_Metric` | `DBSFMPFC` | fmpofl.f | exposed |
| `FVS_PotFire_Metric` | `DBSFMPF` | fmpofl.f | exposed |
| `FVS_RD_Beetle_Metric` | `DBSRD1` | rdpr.f | writer and call site |
| `FVS_RD_Det_Metric` | `DBSRD1` | rdpr.f | writer and call site |
| `FVS_RD_Sum_Metric` | `DBSRD1` | rdpr.f | writer and call site |
| `FVS_Regen_HabType` | `DBSPLOTHAB` | — | writer, no call site |
| `FVS_Regen_Ingrow_Metric` | `DBSINGROW` | — | writer, no call site |
| `FVS_Regen_SitePrep` | `DBSSITEPREP` | estab.f | writer and call site |
| `FVS_Regen_Sprouts_Metric` | `DBSSPRT` | esuckr.f | writer and call site |
| `FVS_Regen_Tally_Metric` | `DBSTALLY` | estab.f | writer and call site |
| `FVS_SnagDet_Metric` | `DBSFMDSNAG` | fmsout.f | exposed |
| `FVS_SnagSum_Metric` | `DBSFMSSNAG` | fmssum.f | exposed |
| `FVS_Stats_Species_Metric` | `DBSSTATS` | stats.f | exposed |
| `FVS_Stats_Stand` | `DBSSTATS` | stats.f | writer and call site |
| `FVS_StrClass_Metric` | `DBSSTRCLASS` | sstage.f | writer and call site |
| `FVS_Summary_Metric` | `DBSSUMRY` | disply.f,sumout.f | exposed |
| `FVS_TreeList_Metric` | `DBSTRLS` | prtrls.f | exposed |

## The candidates, one by one

`notes/reference/table-candidates.md` takes the 25 candidates and gives each one what we know, why it
exists, and an estimate of the cost, the risk and the value of wiring it in, with a proposed order.

## What a call site does and does not mean

A call site means the writer runs **when its module runs**. It does not mean a keyword set can make that
module run: the fuels, potfire, carbon and consumption tables each needed a specific trigger found by
experiment, and two of those triggers were options inside `FMIN` rather than keywords. So the 25 tables in
"writer and call site" are **candidates**, not promises, and each needs a case before it is exposed.

Three things are settled:

- **Five tables cannot be written by this build.** `FVS_EconHarvestValue_Metric`, `FVS_EconSummary_Metric`,
  `FVS_FIAVBC_Summary`, `FVS_Regen_HabType` and `FVS_Regen_Ingrow_Metric` have writers with **no call
  site**, so the routine exists and nothing invokes it. Exposing them would expose a table that is always empty.
- **`FVS_BurnReport_Metric` has a call site and a gate no valid input satisfies.** It is written inside
  `IF (IFMBRB .LT. 0)`, and `IFMBRB` is assigned `9999` at initialisation and the inventory year by
  `BURNREPT`. `INVYEAR -1` makes the table appear, which is how the dead branch was confirmed, but a stand
  inventoried in year -1 is invalid input that shifts the whole simulation.
- **No table in the 44 is writerless.** Every one has a routine that creates it, which is why the earlier
  note's "no writer" verdicts were all wrong.

## The recipes found so far

Each of these was found by running, not by reading:

| Tables | Trigger |
| --- | --- |
| `FVS_Down_Wood_Vol_Metric`, `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric` | the `DATABASE` options the official case already uses |
| `FVS_Fuels_Metric`, `FVS_PotFire_Metric`, `FVS_PotFire_Cond_Metric` | `FUELOUT`, `FUELREPT`, `POTFIRE` inside `FMIN` |
| `FVS_Carbon_Metric`, `FVS_Hrv_Carbon` | `CARBREPT` inside `FMIN` |
| `FVS_Consumption_Metric` | `SIMFIRE` inside `FMIN` — a fire event, not an option |
| `FVS_TreeList_Metric`, `FVS_CutList_Metric` | `TREELIDB`/`CUTLIDB` plus a `TREELIST`/`CUTLIST` request, and for the cut list an actual removal |
| `FVS_Stats_Species_Metric` | `INVSTATS` plus `STATS` |
| `FVS_Down_Wood_Cov_Metric` | `DWDCVDB` plus `DWDCVOUT` inside `FMIN` |
| `FVS_BurnReport_Metric` | **none**: the gate needs an invalid input |
| `FVS_DM_*_Metric` (4) | **not found**: `MISTOE` is a block and its sub-keywords are accepted, but the tables need an infection state |
| `FVS_RD_*_Metric` (3) | **not found**: `RDIN` starts the block, and its required parameters were not determined |

## Two that resisted, and why

- **`FVS_Stats_Stand`** did not appear even with `INVSTATS` and `STATS`, while
  `FVS_Stats_Species_Metric` did. Its writer, `dbsstats.f`, describes it as the *distribution of stand
  attributes among sample points*, and the fixture stand carries a single point. **What would close it**:
  a multi-point stand, which the fixture generator does not produce.
- **`FVS_Mortality_Metric`** did not appear even with `MORTREDB` accepted — the report echoes `FFE
  MORTALITY INFO SENT TO SPECIFIED DATABASE` — and a `SIMFIRE` fire. The writer returns early on
  `IF(IMORTF.EQ.0)`, and the option sets `IMORTF=1`, so the call itself is not reached; most likely the
  three-tree fixture loses nothing to the fire. **What would close it**: a fire that kills trees, which
  needs a stand the FFE mortality model will act on.

## Dwarf mistletoe and root disease: blocks, and a state we do not have

Both families have writers with call sites (`DBSMIS1` from `misprt.f`, `DBSRD1` from `rdpr.f`), and both
writers are called unconditionally. What gates them is the module being *on*, and what makes it produce
rows is the stand carrying an **infection**.

What was tried, and what happened:

- **`MISRPTS`, `RDSUM` and `RDDETAIL` alone** — the three `DATABASE` options — write no tables at all.
- **`MISTOE` as a plain keyword** — refused, because it swallowed the following records. It is a block,
  terminated by `END`, and its sub-keywords (`MISTPINF`, `MISTGMOD`, `DMAUTO`, …) are read by `MISIN`.
  It is now a line block in the model, and a run with a `MISTPINF` line is accepted and echoed:
  `Date/Cycle= 0; Species= PW (1); Proportion to Infect= 0.50`.
- **That run still writes no dwarf-mistletoe table.** `MISFLG` is set to `.FALSE.` in `misin.f` and is
  turned on elsewhere, so a block alone does not enable the model, and an infected proportion at date 0
  does not by itself produce the statistics the tables carry.
- **`RDIN` with `0 1`** — refused with `FVS04 ERROR: A REQUIRED PARAMETER IS MISSING OR A PARAMETER IS
  INCORRECT`. Its field layout is in `rdin.f`, but which field is required was not determined, so `RDIN`
  is **not** modelled and the root-disease tables stay unexposed.

**What would close these**: a stand with a mistletoe rating per tree and a root-disease centre, which is
an inventory question rather than a keyword question. The fixture generator has no such field.
