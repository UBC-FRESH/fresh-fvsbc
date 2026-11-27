# A negative result: CWH small-tree height rows do not ship

Status: **explored, reverted. The pooled BWBS/CWH fallback stays.**

## 1. What was tried

The small-tree height model in `regent.f` is driven by `ST_COEF` rows. CWH has no rows of its own; it
uses the pooled `BWBS/all CWH/all MH/all CDF/all` fallback that W5 fitted from BWBS data. W18 fitted
CWH rows instead.

The engine's form:

```
HTGRL = (CON + HT * H_m) / (1 + EXPMLT * exp(HCCFL*H_m/max(CCFL,36) + CCFSL*CCFS/max(CCFL,36)))
```

`HTGRL` is a five-year height increment in centimetres. `CCFL` and `CCFS` come from `ccfcal.f`, so the
script ports that routine (RD1/RD2/RD3, RDA/RDB, the PN coefficients, and the BC species order) and
reproduces the cumulative sums from `regent.f`: per-tree CCF, total CCF, the CCF of smaller trees, and
`CCFL = total - own`.

117,489 same-tree pairs below 10.16 cm with both heights, in CWH:

| Species | n | Free fit r² | EXPMLT = 1 r² | Residual SD (cm/5yr) |
| --- | ---: | ---: | ---: | ---: |
| AT | 3,081 | 0.380 | 0.246 | 103 |
| BG | 11,295 | 0.431 | 0.257 | 70 |
| CW | 24,876 | 0.268 | 0.182 | 58 |
| FD | 8,608 | 0.411 | 0.112 | 77 |
| HW | 62,510 | 0.371 | 0.217 | 77 |
| SE | 4,961 | 0.315 | 0.184 | 86 |

## 2. Why it does not ship

The free fit explains a fair share of the height variance, but its parameters land on their bounds
(CON above 500, EXPMLT at 20) — the form is not identified for these data. Constraining EXPMLT to the
banked rows' 1.0 gives well-behaved parameters but a weaker fit.

At stand level, with the shipped `BAIMULT 8` bundle, both variants are clearly worse:

| Build | Test BA bias | Test MAE | Train BA bias | Train MAE |
| --- | ---: | ---: | ---: | ---: |
| **Current (pooled fallback)** | **+0.15** | **4.01** | **−0.13** | **5.03** |
| W18 free (`EXPMLT` free) | +3.43 | 6.59 | +3.32 | 7.12 |
| W18 constrained (`EXPMLT = 1`) | +4.78 | 7.89 | +4.38 | 8.00 |

Without the bundle (`BAIMULT 1`) the current build scores −4.49 / 5.99; the small-tree variants score
−1.15 / 7.22 and +0.28 / 8.32. They move the bias but add more variance than they remove, and the
bundle interaction makes the shipped configuration substantially worse.

`regent.f` was reverted; the fold returns to +0.15 / 4.01 (verified after the revert).

## 3. What would change the answer

- Fit against the **engine's own** CCF per tree rather than a reimplementation: one run with the tree
  list and a debug dump would remove the porting risk.
- Fit the **diameter** response directly, since that is what the dataset measures and what the
  small-tree height model ultimately drives.
- Use a form with fewer correlated terms; `EXPMLT` and `HCCFL` trade off almost exactly at these
  densities.

Until one of those lands, CWH small trees keep the pooled fallback, and the CWH support reason keeps
saying "donor small tree".
