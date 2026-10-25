# Which of the 44 tables a run here can actually write

Found while trying to expose more tables (`P17`, `P18`). **Eleven are exposed; the rest are not all
reachable, and the reason differs by table.** This note records what was checked rather than guessed.

## The four that are reachable with an option

`FVS_Fuels_Metric`, `FVS_PotFire_Metric` and `FVS_PotFire_Cond_Metric` need an **`FMIN` block** with
`FUELOUT`, `FUELREPT` and `POTFIRE` — they are options inside it, not keywords — and a `DATABASE` block
asking for `FuelsOut`, `FuelReDB` and `PotfirDB`. `FVS_Down_Wood_Vol_Metric` and the two snag tables take
the `DATABASE` options the official case already uses.

## Carbon: the writer exists, and one option does not reach it

`FVS_Carbon_Metric` is created by `metric/dbsqlite/dbsfmcrpt.f`, and **`DBSFMCRPT` has one call site in
the whole source**: `fmcrbout.f:212`, inside the fire-carbon report path. The `DATABASE` option
`CARBREDB` is accepted — the run's own report says `CARBREDB   CARBON REPORTS SENT TO SPECIFIED
DATABASE.` — and **no table appears**. `CALBSTAT` is accepted too, and writes its statistics to **unit
13**, a file, not the database. So carbon needs the fire-carbon report path, not an option alone, and it
was not found in the time this note took.

## Dwarf mistletoe and root disease: no writer at all

```text
DBSFMMRPT   references in the source: 0
DBSRDOUT    references in the source: 0
DBSRDDET    references in the source: 0
```

The `FVS_DM_*_Metric` and `FVS_RD_*` tables are in the schema and **no routine writes them** in this
source. They are not a recipe to find; they are unreachable by construction, and exposing them would
expose a table that is always empty.

## What that means for the gap

The reader exposes eleven. Of the remaining 33:

- some are reachable with a `DATABASE` option and a keyword the model already supports;
- carbon needs the fire-carbon report path;
- dwarf mistletoe and root disease have no writer.

**The gap is not "36 tables need a triggering case".** It is a mixture of three things, and the triage
should say which before anyone spends a phase on it.
