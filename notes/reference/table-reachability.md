# Which of the 44 tables a run here can actually write

Found while trying to expose more tables (`P17`, `P18`, `P20`, `P22`). **Fourteen are exposed; the rest
are not all reachable, and the reason differs by table.** This note records what was checked rather than
guessed.

## The tables an option reaches

`FVS_Fuels_Metric`, `FVS_PotFire_Metric` and `FVS_PotFire_Cond_Metric` need an **`FMIN` block** with
`FUELOUT`, `FUELREPT` and `POTFIRE` — they are options inside it, not keywords — and a `DATABASE` block
asking for `FuelsOut`, `FuelReDB` and `PotfirDB`. `FVS_Carbon_Metric` and `FVS_Hrv_Carbon` need
`CARBREPT` in the same block and `CARBREDB` in the `DATABASE` block. `FVS_Down_Wood_Vol_Metric` and the
two snag tables take the `DATABASE` options the official case already uses.

## Carbon: reachable, but only through `CARBREPT`

`FVS_Carbon_Metric` is created by `metric/dbsqlite/dbsfmcrpt.f`, and **`DBSFMCRPT` has one call site in
the whole source**: `fmcrbout.f:212`. That routine returns early on `IF (ICRPTB .EQ. 0) GOTO 900`, and
`ICRPTB` is set by the `FMIN` option **`CARBREPT`**. The `DATABASE` option `CARBREDB` alone is accepted
— the run's own report says `CARBREDB   CARBON REPORTS SENT TO SPECIFIED DATABASE.` — and writes
nothing, because the writer is never reached. `CALBSTAT` is a different thing entirely: it writes
calibration statistics to **unit 13**, a file.

So the recipe is two lines in two blocks, and no keyword at all:

```text
DATABASE
DSNOut
FVSOut.db
Summary
CARBREDB
ComputDB
END

FMIN
CARBREPT
END
```

That run writes **`FVS_Carbon_Metric`** (14 columns, from live above- and below-ground carbon through
down dead wood, forest floor and shrub/herb to the total and the carbon released by fire) and
**`FVS_Hrv_Carbon`** (9 columns: products, landfill, energy, emissions, merchantable carbon stored and
removed). Both are exposed.

Two properties a caller should know:

- `CARBREPT` alone is enough. `FUELOUT`, `FUELREPT` and `POTFIRE` are not needed for carbon.
- **The total can be NULL.** A period whose components FVS leaves undefined carries NULL in
  `Total_Stand_Carbon` and in `Standing_Dead`, and the reader returns `NaN` rather than inventing a
  zero. The first period of a run carries a real total — 13.6 tonnes of carbon per hectare on the
  synthetic stand — so a zero in that column is a value, and a NULL is the absence of one.

## Consumption: reachable, but only when something burns

`FVS_Consumption_Metric` is written by `DBSFMFUEL`, called from `fmfout.f:227` — inside the routine that
runs when a fire occurs. Neither the `DATABASE` option `BURNREDB` nor the `BURNREPT` option is enough on
its own, and the fuel options are needed as well or the routine never reaches the call.

A fire is an **activity**, not a keyword: `FMBURN` looks for activity 2506 with `OPFIND`, and the `FMIN`
option **`SIMFIRE`** is what schedules it. The recipe that works:

```text
DATABASE
DSNOut
FVSOut.db
Summary
FuelsOut
FuelReDB
BURNREDB
ComputDB
END

FMIN
FUELOUT            2
FUELREPT           2
BURNREPT
SIMFIRE            1
END
```

That run writes one consumption row: 22.569 tonnes per hectare consumed, 77.31 percent of the duff and
82.2 percent of the 7.6 cm plus fraction, with smoke production per size class. It is exposed.

## The burn report: a gate nothing can satisfy

`FVS_BurnReport_Metric` is written by `DBSFMBURN`, called from `fmfout.f:102` inside
`IF (IFMBRB .LT. 0 .AND. IFIRE .GE. 0)`. `IFMBRB` is assigned in exactly two places:

```text
fminit.f:853    IFMBRB = 9999            (initialisation)
fmin.f:228      IFMBRB = IY(1)           (the BURNREPT option)
```

`IY(1)` is the inventory year, so the gate needs a **negative** value that neither assignment produces.
It is satisfied by `INVYEAR -1` — verified, the table appears — but a stand inventoried in year -1 is
invalid input that shifts the whole calendar, so this is a dead branch rather than a recipe. The table is
**not exposed**, and `keywords.rst` says why.

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

The reader exposes **fourteen**. Of the remaining 30:

- some are reachable with a `DATABASE` option and a keyword the model already supports;
- carbon is reachable through `CARBREPT`, and consumption through `SIMFIRE`; all three tables are
  exposed;
- the burn report's gate cannot be satisfied by valid input;
- dwarf mistletoe and root disease have no writer.

**The gap is not "36 tables need a triggering case".** It is a mixture of three things, and the triage
should say which before anyone spends a phase on it.
