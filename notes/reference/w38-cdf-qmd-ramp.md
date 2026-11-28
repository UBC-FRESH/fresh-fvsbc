# W38: CDF BA>60 mortality ramp on QMD

Status: **shipped in wrapper 0.41.23 / engine 0.4.17.**

## 1. The term

For CDF, `BA > 60 m²/ha`:

```
RAMP = max(0, min(1, (50 - QMD)/25))
X = X * (1 - 0.5*RAMP)
```

QMD is computed in `morts.f` from metric BA and stems/ha. Small-QMD high-BA stands keep more
stems; large-QMD stands keep the donor response. This replaces the fixed 29–33 band, which changed
only four intervals.

## 2. Expanded clean CDF fold (31 test / 52 train)

| Build | Test BA MAE | Test TPH MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| `cdf-v3` | 2.489 | 201.406 | 2.032 | **164.062** |
| W38 ×0.5 | **2.460** | **201.342** | **2.015** | 164.099 |

Held-out BA and TPH both improve; train BA improves; train TPH changes by 0.04 TPH (0.02%).

## 3. Five-site high-BA leave-one-site-out

| Build | Mean BA MAE | Mean TPH MAE |
| --- | ---: | ---: |
| `cdf-v3` | 2.34 | 47.16 |
| W38 ×0.5 | **2.05** | **43.28** |

Both improve.

## 4. What it does not do

The ramp improves the aggregate fold, not the dense >100 m²/ha stand's specific TPH history; the
dense stand's QMD is 35–53, where the ramp is mild. The mixed-sign dense history remains.

## Reproduce

- Expanded fold: `probe_cdf_w38_50_expanded/` against `probe_cdf_base_expanded/`.
- LOOCV: `probe_cdf_w38_50_loocv_*/`.
- Patch: `notes/reference/calibration/w38-cdf-qmd-ramp.patch.gz`.
