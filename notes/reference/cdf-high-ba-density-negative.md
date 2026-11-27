# CDF dense-stand residual: no density term, and the growth/mortality frontier

Status: **negative result.** No change shipped; `cdf-v3` and engine 0.4.11 stay as they are.

## 1. The hypothesis

The dense stand `4002349|1|2008|2024` is 33 m²/ha short at BA 112 → 153. The proposed
explanation was a missing density/high-BA growth term, to be fitted on CDF training
intervals and validated on the held-out fold.

## 2. What the data say

CDF FD growth pairs, 3,713 total (1,387 on the 13 training sites). Stand density
(`RELDEN`, from the ported CCF) ranges 23–326 ppm; training tops out at BA 80.8 while the
dense stand starts at 112.5.

The row's residual `ln(10*growth) - row_log` is **flat across density**:

| Training RELDEN bin | Intervals | Mean RELDEN | Mean residual |
| --- | ---: | ---: | ---: |
| 0–100 | 7 | 61 | 2.25 |
| 100–150 | 14 | 121 | 1.86 |
| 150–200 | 6 | 167 | 2.16 |
| 200–250 | 5 | 239 | 2.20 |
| 250–350 | 11 | 278 | 2.15 |

The interval-level slope is **+0.028 per 100 CCF** — flat. (A pair-level slope of −0.307 is
a composition artifact: denser intervals carry more suppressed trees.) The dense stand's
intervals sit at residuals 1.9–2.4, squarely inside the training band. There is no
density-specific growth signal to fit.

## 3. The real defect behind the level

The W10 fit script uses `y = ln(growth)` with growth in **cm/yr**, but the V3 engine applies
the row as a **10-year** diameter increment (`GRADD`, `FINT/YR`, `YR=10`). The FD CDF row is
therefore ~8× low at *every* density; `BAIMULT 8` (≈2.83× diameter growth) only partly masks
it. A W19 patch adding `ln(10)` to the FD constant was built and tested.

## 4. Period correction plus retuning

With W19 (FD row ×10), sweeping FD's BAIMULT and MORTMULT, train-selected:

| FD BAI / MORT | Test BA bias / MAE | Test TPH bias / MAE | Train BA MAE | Train TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| **shipped (row as-is, 8 / 0.5)** | **−3.12 / 3.46** | **−8.8 / 66.80** | **4.41** | **191.10** |
| 2.83 / 0.5 | +7.82 / 10.72 | −23.6 / 70.61 | 10.48 | 179.88 |
| 1.5 / 0.5 | +0.82 / 5.22 | −14.6 / 68.24 | 6.41 | 185.88 |
| 1.2 / 0.35 | +0.13 / 4.53 | −8.8 / 66.80 | 5.77 | 190.24 |
| 1.2 / 0.25 | +0.69 / 4.84 | −6.61 / 66.36 | 5.91 | 192.10 |
| 0.9 / 0.5 | −2.31 / 3.46 | −9.86 / 67.36 | 4.77 | 189.88 |

No setting improves both held-out BA and TPH. The best TPH settings cost 1.1–1.4 m²/ha of
BA MAE; the best BA settings worsen TPH. The shipped bundle sits on the frontier.

The dense stand itself shows the trade: correcting growth raises BA but self-thinning takes
more stems.

| Setting | Dense BA | Dense TPH |
| --- | ---: | ---: |
| shipped | 117 | 370 |
| FD 1.2 / MORT 0.25 | 126 | 375 |
| FD 1.5 / MORT 0.25 | 130 | 373 |
| measured | **153** | **518** |

`BAMAX` 140/170/200 did not separate in this harness (identical fold rows), so it was not a
usable lever here.

## 5. Conclusion

- The residual is **not** a missing density response; the FD row's density slope is already
  flat-to-correct.
- Correcting the row's period basis is real, but the fold's growth–mortality tradeoff means it
  cannot improve both BA and TPH. Shipping it would trade one defect for another.
- The dense stand is outside the training domain (112–153 BA vs a training maximum of 80.8)
  and is a single 16-year interval. A high-BA interaction cannot be identified from it.

The honest next step is data, not tuning: CDF high-BA intervals (BA > 100) in training, or a
repeated high-BA site, to fit the growth–mortality interaction. Until then the 33 m²/ha is
recorded as out-of-domain rather than tuned away.

## Reproduce

- Fit: `~/workspace/bwbs-work/fit_cdf_fd_density.py` (local).
- Sweeps: `~/workspace/bwbs-work/cdf_fd_sweep/` (local; W19 × FD BAI/MORT and BAMAX grids).
- Shipped verification: `~/workspace/bwbs-work/cdf_verify_shipped/` reproduces test
  −3.12 / 3.46, TPH −8.8 / 66.80 and dense 117 BA / 370 TPH.
