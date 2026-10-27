# Phase close-out report: P54 The fire tables

Phase: P54 The fire tables
Parent issue: #232
Pull request: #234
Evidence head: `ce27ab2`
Date: 2026-10-27
Status: merged.

## Recommendation

Release `0.16.0`. The validator returns a new warning, so a caller who asserts an empty list sees a
change, and thirteen tables have a check where nine did.

## 1. What shipped

- **The validator warns** when an `FMIN` block asking for `FUELOUT` or `POTFIRE` follows `INVYEAR`.
- **The harness leaves the inventory year to the run's own keyword**, so the standalone reads the
  stand in the order the run does.
- **All four fire tables are checked** and agree with the standalone value for value.

## 2. The defect

`FUELOUT` and `POTFIRE` set `IFLALB` and `IPFLMB` to `IY(1)` when they are read. `fmdout.f` sets
`LPRINT = .FALSE.` when `IFLALB > 0`, and `fmpofl.f` returns when `IPFLMB > 0` — so **any positive
value means "suppress this report"**. Read after `INVYEAR`, the block switches its own reports off.

The run succeeds. `FVS_Fuels_Metric`, `FVS_PotFire_Metric` and `FVS_PotFire_Cond_Metric` are simply
absent, and nothing in the output says so.

**The official case never hits it**, because its inventory year arrives from the input database rather
than an `INVYEAR` keyword, so `IY(1)` is still zero when the block is read. That is why the defect has
gone unnoticed upstream, and why it would have hit every user of this package, which writes the year as
a keyword.

## 3. Evidence

The same keyword set, differing only in where the `FMIN` block sits:

```text
block after INVYEAR:   FVS_Cases, FVS_Consumption_Metric, FVS_Down_Wood_Cov_Metric,
                       FVS_Down_Wood_Vol_Metric, FVS_SnagDet_Metric, FVS_SnagSum_Metric,
                       FVS_Summary_Metric, FVS_TreeList_Metric

block before INVYEAR:  the same, plus FVS_Fuels_Metric, FVS_PotFire_Cond_Metric, FVS_PotFire_Metric
```

And the oracle on the second:

```text
10 of 11 comparable tables agree; 1 explained; 2 not comparable.
FVS_Consumption_Metric, FVS_Fuels_Metric, FVS_PotFire_Cond_Metric, FVS_PotFire_Metric: match
```

## 4. Acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| A block after `INVYEAR` warns, naming both keywords | `tests/test_keywords.py` | met |
| A block before `INVYEAR` writes all four fire tables | section 3 | met |
| The oracle agrees with all four, value for value | section 3 | met |
| `python scripts/dashboard.py` exits zero | green on `d471654` | met |

## 5. What this does not do

- **`FVS_BurnReport_Metric`** stays out. It is not exposed, and its gate needs an invalid inventory
  year.
- **`FVS_InvReference`** is still written by the standalone and never by this package's build.

## 6. What the phase cost

One wrong turn worth recording: I first concluded `DBSFUELS` was **unreachable**, from `IFLALB = 9999`
and the `LPRINT` gate. That was half right — it is unreachable *after `INVYEAR`* — and the official
case's own `.out` disproved the stronger claim. The counter-evidence was one `grep` away and I nearly
shipped the wrong conclusion.
