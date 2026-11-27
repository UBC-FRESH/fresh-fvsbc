# SBSmc2 residual: a size-specific BL 10-20 cm term does not pass

Status: **negative result.** No change shipped; `sbs-v3-bl-ccf-mm185-2026-11-27` stays.

## 1. The target

After W22 (`MORTMULT 1.85`, BL CCFA −0.35) the SBSmc2 cell is **+1.5 m²/ha / −81 TPH**. The
next test was a train-only, size-specific BL 10–20 cm growth term, using the engine's `FIXDG`
keyword (species, multiplier, min/max DBH in cm) rather than another zone-wide multiplier.

`FIXDG` was temporarily added to the bundle whitelist, three SBS+recruitment bundles were
built with `FIXDG BL <g> 10 20`, and each was run through the held-out fold.

## 2. Results

| BL 10–20 multiplier | Fold | BA MAE | TPH bias | TPH MAE | Cell BA / TPH |
| --- | --- | ---: | ---: | ---: | ---: |
| shipped (none) | test | 5.91 | +20 | 644.3 | +1.5 / −81 |
| 0.90 | test | 5.94 | +20 | 644.7 | +1.6 / −78 |
| 0.80 | test | 5.94 | +21 | 644.7 | +1.5 / −74 |
| 0.70 | test | 5.94 | +22 | 644.6 | +1.4 / −67 |
| shipped | train | 4.94 | −36 | 396.9 | |
| 0.90 | train | 4.95 | −36 | 397.2 | |
| 0.80 | train | 4.94 | −35 | 397.6 | |
| 0.70 | train | 4.93 | −34 | 397.8 | |

The lever barely reaches the cell: even at 0.70 it removes 14 of the 81 TPH bias and 0.1 m²/ha
of BA, while the fold's BA and TPH MAE are flat or slightly worse. A size-specific growth
reduction is the right direction for the cell's BA/TPH pair, but the 10–20 cm BL component is
too small in the aggregate to move the fold, and the cell's TPH deficit is dominated by
mortality.

The `FIXDG` whitelist change was reverted; no bundle uses it.

## 3. What the residual is

The cell is train +4.4 BA / −170 TPH and test −3.8 / −321 (2 test intervals). Growth reduction
fixes the cell directions but worsens the held-out BA; mortality changes fix TPH but move BA the
other way. The two folds diverge, so no single size-specific term improves both. The remaining
+1.5/−81 is at the edge of what these levers can express.

## Reproduce

- `~/workspace/bwbs-work/probe_sbs_fixdg_{90,80,70}/` (144 rows each).
- Bundles `bundle_sbs_fixdg_{90,80,70}.json` (local).
