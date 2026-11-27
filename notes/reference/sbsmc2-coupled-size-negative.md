# SBSmc2 coupled size-specific patch: tested, not shipped

Status: **negative result.** The shipped SBS bundle stays `sbs-v3-bl-ccf-mm185-2026-11-27`.

## 1. What was tried

FIXDG alone (BL 10–20 cm growth) was already a negative. This test coupled growth and
mortality for the same size class using the engine's two size-specific keywords:

```
FIXDG   BL <g> 10 20          ! diameter growth multiplier
FIXMORT BL <m> 10 20 3        ! type 3 = multiply the model mortality rate
```

with the shipped SBS parameters (`MORTMULT 1.85`, BL CCFA −0.35) and recruitment. Four growth
multipliers (0.6–0.9) × three mortality multipliers (0.9/1.0/1.1), page through the probe.
As before, `FIXDG` was temporarily added to the bundle whitelist and reverted.

## 2. Results

| g / m | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE | Cell BA / TPH |
| --- | ---: | ---: | ---: | ---: | ---: |
| shipped | **5.91** | **644.3** | **4.94** | **396.9** | +1.5 / −81 |
| 0.7 / 1.0 | 5.94 | 644.6 | 4.93 | 397.8 | +2.9 / −34 |
| 0.7 / 0.9 | 5.94 | 644.6 | 4.94 | 398.0 | +3.1 / −26 |
| 0.6 / 1.0 | 5.94 | 644.9 | 4.95 | 395.4 | +3.2 / −60 |
| 0.9 / 1.0 | 5.94 | 644.7 | 4.95 | 397.2 | +3.2 / −46 |

The held-out fold does not improve: BA MAE 5.91 → 5.94 and TPH 644.3 → 644.6 in every cell.
The SBSmc2 cell's TPH improves (to −26 at 0.7/0.9), but its BA rises from +1.5 to +3.1.

There is also a confound: `FIXMORT` at m = 1.0 is not neutral. It changes the mortality path
and raises cell BA (the coupling is not a clean growth + mortality product). A clean version
would need a new `morts.f` size-specific term rather than the generic keyword.

## 3. Why it cannot pass

The cell's two folds point in opposite directions: train +4.4 BA / −170 TPH, test −3.8 / −321.
Growth reduction fixes the train cell but worsens the held-out cell BA; the held-out aggregate
BA is also under (−0.5), so any growth reduction moves it the wrong way. A single size-specific
growth term cannot improve both folds, and the mortality keyword does not cleanly isolate the
size class.

## 4. What remains

The residual +1.5/−81 is at the edge of these levers. A clean attempt needs:

- a size-specific mortality term written directly in `morts.f` (not FIXMORT), and
- enough held-out SBSmc2 intervals to break the 2-test/8-train split dependence.

Until then the SBS bundle is unchanged.

## Reproduce

- `~/workspace/bwbs-work/probe_bl_{60,70,80,90}_{90,100,110}/` (144 rows each).
- Bundles `bundle_bl_<g>_<m>.json` (local).
