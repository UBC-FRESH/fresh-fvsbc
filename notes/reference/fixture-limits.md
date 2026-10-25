# The three questions, answered from the source

`P30` closed by calling three FVS behaviours unknown and recommending an investigation phase. That was
wrong: **all three are readable in the source, and two of them are a keyword field each.** This note records
the answers, the lines they come from, and what they unblock.

The version of this file written earlier the same day said the fixture was the binding constraint. It was
not. The constraint was **three keyword fields and one damage code**.

## 1. How FVS counts sample points: `DESIGN` field 4

`initre.f:798`, in the `DESIGN` handler:

```text
IF ( LNOTBK(4) ) IPTINV = IFIX( ARRAY(4) )
```

`IPTINV` is the inventory point count. `initre.f:330` defaults it to `IPTKNT`, the number of points counted
in the tree list, and `stats.f:147` then says:

```text
IF(IPTINV.GT.1) GO TO 50
C  1 POINT.  PRINT ERROR MESSAGE AND GO WRITE SPECIES STATS TO DATABASE.
```

Every run in this project passed `DESIGN 0 1 999 1 ...` — field 4 is **1**. Five plots in the tree list
made no difference, because the field overrode the count.

**With `DESIGN 0 1 999 5 0 5 1`, `FVS_Stats_Stand` is written.** The fixture never needed to change: the
adapter already maps one plot per stand.

## 2. What makes the mortality table appear: `MORTREPT`

`fmfout.f:294` gates the whole section:

```text
IF (IFMMRB .LT. 0 .AND. IFIRE .GE. 0) THEN
```

`fmin.f:1372`, the `MORTREPT` option (number 28):

```text
IFMMRB = -1
IFMMRE = -1
```

and its echo says it plainly: *"THE TREE MORTALITY REPORT WILL BE WRITTEN WHEN A FIRE OCCURS."*

This project passed `MORTREDB` — the `DATABASE` option — and never `MORTREPT`. **With `MORTREPT` and
`SIMFIRE`, `FVS_Mortality_Metric` is written**, on the three-tree fixture, with no fire that kills anything
special.

Note the contrast with the burn report, whose gate is the same shape: `BURNREPT` sets `IFMBRB = IY(1)`,
which is **not** negative, so that one really is dead. The mortality option sets `-1`, so that one works.
The two looked identical from the outside and are not.

## 3. How a mistletoe rating enters: damage codes 30 to 34

`misdam.f:63-80`:

```text
IMIST(ITREE)=0
IF(.NOT.MISFLG) GO TO 9000
DO 100 J=1,5,2
   IF(ICODES(J).EQ.30.OR.ICODES(J).EQ.31.OR.ICODES(J).EQ.32.
  &   OR.ICODES(J).EQ.33.OR.ICODES(J).EQ.34) THEN
      IMIST(ITREE)=ICODES(J+1)
```

The damage code pair is (code, severity), codes **30 to 34** are dwarf mistletoe, and **the severity is the
Hawksworth rating**, clamped to 0 to 6. `MISFLG` is `.TRUE.` from `misin0.f:86`, before any keyword is read.

The earlier attempt used **code 21** and got `NUMBER OF RECORDS WITH MISTLETOE 0`. With **code 30 and
severity 3**, the run reports eight infected records and writes `FVS_DM_Spp_Sum_Metric` and
`FVS_DM_Stnd_Sum_Metric`.

The adapter still hardcodes `damage1..3` to zero. That is a real gap — but it is an **adapter** gap of one
parameter, not an inventory-state problem, and the route is now known.

## What this says about the method

Three questions that `P30` called unknown were answered by reading three files. The mistake was not the
reading; it was treating "I ran an experiment and it did not work" as evidence about the software rather
than about the experiment. A negative experiment constrains what I tried, not what FVS does.

**The rule this project should keep**: before calling a behaviour unknown, grep for the variable that gates
it and read the assignment. `IFMMRB`, `IPTINV` and `IMIST` each had a single obvious assignment.

## What is still open

- **`FVS_DM_Sz_Sum_Metric` and `FVS_DM_TreeList_Metric`**: all five `DBSMIS*` routines are called from
  `misprt.f`, and two tables appear while these two do not. Their gates (`IDM3`, `IDM6`) are set to 1 by
  `MISRPTS`, so something else — probably a per-cycle flag — decides. One more read.
- **The root-disease tables**: `RDIN`'s field list is in `rdin.f` (date, method, two spread rates, the
  Monte Carlo count, and a disease type 1 to 4), and the required parameter that was refused was not
  identified. Also one more read.
- **The regeneration tables**: they need an establishment model active, which is a keyword set, not a
  fixture.
