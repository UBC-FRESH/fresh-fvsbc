# W28: SBSmc2 stem-shape mortality

Status: **shipped in 0.41.6 on engine 0.4.14.** Tier stays C (unsigned).

## 1. Why

After `sbsmc2-v3` (0.41.5) the full subzone was still **+9.1 m²/ha BA / −908 TPH**: too much
basal area on too few stems. Saving small stems alone raised BA; thinning large stems alone lost
TPH. The shape that fixes both is two-sided: **save small stems, thin large ones**.

## 2. The term

In `morts.f`, SBSmc2 only, V3:

```
DBH < 10 cm   X = X * 0.5      ! small stems survive
DBH >= 20 cm  X = X * 2.5      ! large stems thin
```

Coupled with the `sbsmc2-v3` bundle (`BAIMULT 0.3` + recruitment v1).

## 3. Evidence

Full-subzone fold (249 intervals, 126 sites, 42 held out):

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.41.5 | test | +9.1 | 12.52 | −908 | 1,212 |
| **W28** | **test** | **+6.9** | **11.61** | **−729** | **1,081** |
| 0.41.5 | train | +2.6 | 7.66 | −215 | 566 |
| **W28** | **train** | **+0.4** | **7.13** | **−183** | **545** |

All four MAE figures and all four biases improve. The subzone is still +6.9/−729; the remaining
deficit is ingress (stems entering the smallest class), not survival of existing small stems.

## 4. Build and scope

Patch `w28-sbsmc2-stem-shape.patch.gz`, after `w22-sbs-bl-density.patch.gz`. The term is scoped to
`SBSmc2` only; other SBS subzones are untouched. Engine 0.4.14, wrapper 0.41.6.

## Reproduce

- Full-subzone fold: `~/workspace/bwbs-work/probe_sbsmc2_w28d/` (205 rows).
- Bundle: `notes/reference/calibration/sbsmc2-v3-bundle.json`.
