# D6.3 small-tree output path

Status: the fitted growth is normal; the explosion is in the DBH/output state, not the DG equation
Date: 2026-11-03
Issue: #341
Build: local `fresh-fvsbc-pyfvs 0.4.0` with temporary debug writes, reverted after the run

## 1. The growth model is not producing 421

A one-tree `PL` input at 5 tree-list units, `SBPSmc/01`, one 11-year cycle. Temporary writes in
`dgf.f` and `dgdriv.f` record the fitted terms and the tripling result.

`DGF` reports every fitted coefficient at zero for this stand:

```text
D6DGF   4.99999   0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.45  0.0
```

The tripling path reports normal increments:

```text
D6TRIP   1.9075   0.1913   -0.0268   0.2394   -0.2918   1.6569   0.3842   0.4891   0.3007
```

The first value is inside-bark DBH, and the last three are `DG` for the original, upper, and lower
triple. They are fractions of a unit, not 421.

## 2. The output state is not

`FVS_TreeList_Metric` and `FVS_Summary_Metric` for the same run report:

| Quantity | Value |
| --- | ---: |
| Final DBH | 439.50 |
| DG | 421.03 |
| Final height | 304.50 |
| HtG | 299.50 |
| Summary BA | 14 |
| Summary QMD | 439.50 |
| Summary top height | 304.50 |

The final tree list has three rows for the one tree, with the same exploded DBH and different TPH.
The tripling `DG` values above do not produce that DBH.

## 3. What this means

D6.2's threshold is real, but the cause is not the fitted small-tree diameter equation. The model
returns a normal increment; something after it writes an exploded DBH into the tree and summary
arrays. The candidates are:

- the tripling or `DBH` update path;
- a scratch array reused as DBH for small trees;
- the tree-list writer reading a different field;
- the height-growth model copying a bad `DG` into `Ht`.

The height threshold at DBH 8–10 and the diameter threshold below 8 are both consistent with the
same bad state being used by two consumers.

## 4. Next instrument

Instrument `DBH`, `DG`, and `HT` immediately before and after the tripling and `DGBND` calls, and at
the start of the output write, for the same one-tree case. Compare the original record with the two
triples. That will name the write that turns a 0.38 increment into 439.

No parameter is changed. The debug writes are not committed; the source is restored after the run.

## 5. Limits

- One tree, one stand, one 11-year cycle.
- The debug build is local, not a released wheel.
- The tree-list units and metric summary units are distinct; the table above keeps them separate.
