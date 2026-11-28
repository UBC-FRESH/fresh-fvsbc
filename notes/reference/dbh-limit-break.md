# The DBH-limit break: why the SBS subzone folds over-predicted TPH

Status: **root cause found and fixed in the tooling; the affected bundles are refit in 0.41.17.**

## 1. The defect

Early PSP visits tally only trees above a large DBH limit; later visits tally from 2 cm. The
byvisit table carries the limit as `DBH_LIMIT_TAG`:

| Site | Visit | Year | `DBH_LIMIT_TAG` | Tree DBH min |
| --- | ---: | ---: | ---: | ---: |
| 4045242 | 1 | 1976 | 9.1 | 9.1 |
| 4045242 | 2 | 1986 | 2.0 | 2.8 |
| 4045242 | 3 | 1996 | 2.0 | — |

`4045242|1|1976|1986` is therefore read as 2,646 → 15,233 TPH and 28 → 74 m²/ha, even though the
start visit never tallied the small stems. Across the calibration intervals, **2,797 of 17,151
(16%)** change `DBH_LIMIT_TAG` between the two visits; in the SBS subzones every change is the
same 9.1 → 2.0 step:

| Subzone | Intervals | Limit change |
| --- | ---: | ---: |
| SBSmk1 | 327 | 106 |
| SBSmw | 343 | 101 |
| SBSwk2 | 233 | 68 |
| SBSdw1 | 84 | 9 |
| SBSmc2 | 249 | 40 |
| SBSmc | 121 | 0 |

## 2. The tool fix

`scripts/run_calibration_probe.py --stable-dbh-limit` drops intervals whose two visits tally
different limits. It is off by default so old runs reproduce; every calibration from here should
use it. A future harmonization could keep the intervals by summarizing both visits at the larger
limit, but dropping is the conservative choice.

## 3. Clean-fold results

The engine alone (no subzone bundle) on the stable-DBH-limit folds:

| Subzone | Test BA MAE / TPH MAE | Train BA MAE / TPH MAE |
| --- | ---: | ---: |
| SBSmk1 | 5.143 / 381.4 | 4.810 / 430.2 |
| SBSmw | 4.880 / 239.0 | 4.062 / 139.4 |
| SBSwk2 | 3.778 / 244.5 | 4.182 / 441.3 |
| SBSdw1 | 6.717 / 221.8 | 7.808 / 215.5 |
| SBSmc2 | 7.294 / 676.9 | 7.746 / 495.1 |
| SBSmc | 1.930 / 71.2 | 2.541 / 69.1 |

The old subzone bundles were fit on folds that included the break. On the clean folds they fail:

| Bundle | Test BA MAE / TPH MAE | Train BA MAE / TPH MAE |
| --- | ---: | ---: |
| `sbsmk1-v3` (old) | 5.550 / 426.6 | 5.360 / 500.4 |
| `sbsmw-v3` (old) | 4.880 / 257.0 | 4.085 / 188.4 |
| `sbswk2-v3` (old) | 3.820 / 336.7 | 4.484 / 502.2 |
| `sbsdw1-v3` (old) | 3.703 / 219.6 | 6.414 / 216.8 |
| `sbsmc2-v3` (old) | 7.004 / 686.3 | 7.454 / 467.6 |

`SBSmk1` is the clearest case: the old bundle makes both clean folds worse, so it is withdrawn.

## 4. Clean refits

Columns are BA MAE / TPH MAE.

| Bundle | Contents | Test base → clean | Train base → clean |
| --- | --- | --- | --- |
| `sbsmw-v3` | `BAIMULT 0.95` | 4.880/239.0 → **4.774/231.2** | 4.062/139.4 → **4.000/139.1** |
| `sbswk2-v3` | `BAIMULT 2.0`, `MORTMULT 1.2` | 3.778/244.5 → **3.774/221.5** | 4.182/441.3 → **4.005/372.7** |
| `sbsdw1-v3` | `MORTMULT 1.25` | 6.717/221.8 → **4.243/210.6** | 7.808/215.5 → **6.794/210.6** |
| `sbsmc2-v3` | `BAIMULT 0.3`, `MORTMULT 1.15` | 7.294/676.9 → **6.248/655.0** | 7.746/495.1 → **6.754/467.6** |

All four measures improve for each bundle. Recruitment is dropped everywhere: once the limit break
is removed, it either does nothing or adds variance. `SBSmk1` has no clean candidate that improves
BA and TPH in both folds (the best growth/mortality pairs trade 0.01–0.02 m²/ha of BA MAE for a
TPH gain), so it ships no bundle.

## 5. What else this touches

The break is not SBS-specific: 2,797 intervals span CWH, ICH, MS, IDF and every other zone. The
zone-level bundles (`cwh-v3`, `mh-v3`, `ms-v3`, `sbs-v3`, …) were calibrated before the flag
existed and need rechecking on stable folds. That recheck is the next step; it is not assumed safe
by this change.

## Reproduce

- Clean folds: `~/workspace/bwbs-work/probe_*_stable_*`.
- Tool: `scripts/run_calibration_probe.py --stable-dbh-limit`.
