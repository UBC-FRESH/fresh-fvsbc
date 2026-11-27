# W21: CWH small-tree density in both diameter and mortality

Status: **shipped in 0.41.2 on engine 0.4.12.** Tier stays C (unsigned).

## 1. Why

The W20 diameter-only density term improved BA on both CWH folds but raised TPH: slower small
trees mean less competition, so more stems survive. The direct pairs show that mortality also
rises with density, and the engine had no such term.

Data (CWH, same-tree pairs):

| Stand CCF | Small-tree DG (cm/yr) | Small-tree mortality (per yr) |
| --- | ---: | ---: |
| < 100 | 0.484 | 0.7% |
| 100–150 | 0.296 | 2.3% |
| 150–200 | 0.199 | 3.3% |
| 200–250 | 0.146 | 3.6% |
| 250–300 | 0.102 | 4.3% |
| 300–400 | 0.081 | 5.5% |

The height-derived engine model is density-neutral in diameter (0.155–0.186 cm/yr across CCF
166–655) and carries no CCF term in mortality.

## 2. The term

Reference CCF 166, the density at which the engine and the pairs agree:

```
diameter:  DGK = DGK * EXP(-0.45 * (CCF/100 - 1.66))            ! regent.f
mortality: X   = X   * EXP( 0.45 * MIN(CCF/100 - 1.66, 1.8))    ! morts.f, DBH < 10 cm
```

The mortality exponent is capped at CCF 346, where the observed mortality flattens. The 0.45
slope is the fitted diameter slope; the raw mortality slope is 0.64, so the mortality term is
deliberately conservative (the model's BAL/SQRTBA/RELDBH terms already carry some density).

Both terms are CWH-only and `LV2ATV = .FALSE.` (V3).

## 3. Fold evidence

CWH fold, 398 intervals, 108 held out, recruitment, five-year cycles, `BAIMULT 8`:

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| **shipped 0.41.1** | test | +0.158 | 4.000 | +199.8 | 273.0 |
| W20 diameter only | test | −0.304 | 3.804 | +227.5 | 297.8 |
| **W21 joint** | **test** | **−0.712** | **3.778** | **+144.3** | **234.9** |
| **shipped 0.41.1** | train | −0.108 | 5.030 | +139.3 | 357.3 |
| W20 diameter only | train | −0.301 | 4.976 | +147.8 | 364.1 |
| **W21 joint** | **train** | **−0.491** | **4.983** | **+108.1** | **337.2** |

Both BA and TPH improve on both folds. The held-out TPH MAE falls 38 stems (14%) and BA MAE
falls 0.22 m²/ha; the BA bias moves from +0.16 to −0.71, still inside the fold's spread.

## 4. What remains

- The CWH fold is unsigned (tier C). The term is fitted on aggregated pairs, not a formal
  likelihood.
- CW large-tree height remains the donor; the W11 form limitation stands.
- The term is specific to CWH small trees; other zones are untouched.

## 5. Build

Patch `w21-cwh-small-joint.patch.gz`, applied after `w18-sbs-bl-dg.patch.gz`. The full W2–W18 +
W21 chain was verified from a clean pinned tree. Engine `0.4.12`, wrapper `0.41.2`.
