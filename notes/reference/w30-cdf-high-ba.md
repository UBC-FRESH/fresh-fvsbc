# W30: CDF high-BA mortality interaction

Status: **shipped in 0.41.11 on engine 0.4.16 (×0.1); verified from PyPI.** Tier stays C (unsigned).

## 1. The dense site

`4002349|1|2008|2024` starts at BA 112.5 and ends at 153.1, with TPH 526 → 518. Under `cdf-v3`
the model ends at 117 BA / 370 TPH. The site's earlier intervals localize the failure:

| Interval | BA0 | Observed BA1 | Predicted | Obs TPH1 | Pred TPH1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1966–1977 | 85.2 | 93.6 | 92.0 | 423 | 415 |
| 1977–1987 | 93.6 | 102.8 | 99.0 | 589 | 400 |
| 1987–1997 | 102.8 | 109.6 | 107.0 | 636 | 481 |
| 1997–2008 | 109.6 | 112.5 | 113.0 | 526 | 447 |
| 2008–2024 | 112.5 | 153.1 | 117.0 | 518 | 370 |

BA growth is right through 2008. TPH is under from 1977, when the observed stand gains stems.
The last interval is a **growth discontinuity** (BA +40.6 after +2.9 in the prior 11 years), not
a smooth high-BA response; no mortality term can supply it.

## 2. The term

CDF, V3, above **90 m²/ha**:

```
X = X * 0.10          ! mortality
```

It is inert below 90, so the CDF train fold (BA ≤ 81) is unchanged and the dense site's
multi-interval record is the only place it acts.

## 3. Evidence

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.41.9 | test | −3.12 | 3.46 | −8.8 | 66.8 |
| **W30 ×0.1** | **test** | **−1.75** | **3.01** | **+12.0** | **50.6** |
| 0.41.9 | train | +2.98 | 4.41 | +100.1 | 191.1 |
| **W30** | **train** | +2.98 | 4.41 | +100.1 | 191.1 |

The held-out fold improves on both measures; the train fold is untouched. The dense interval
moves 117/370 → **123/447** (measured 153/518); the pre-2008 intervals also move toward the
observed TPH.

## 4. What remains

The dense site is still ~30 m²/ha and ~71 TPH short, and its final BA jump is unexplained by a
smooth interaction. The next step would need the stand's measurement history (plot boundary or
remeasurement change) rather than another growth/mortality term.

## Reproduce

- Dense-site runs: `~/workspace/bwbs-work/probe_cdf_w30/`, `probe_cdf_w30b/`.
- Full fold: `probe_cdf_w30b/`.

## 5. The growth half fails

The other half of the interaction was tested: CDF growth ×2 above BA 90, on top of W30 mortality.

| Interval | BA0 | Obs BA1 | W30 pred | W31 pred |
| --- | ---: | ---: | ---: | ---: |
| 1977–1987 | 93.6 | 102.8 | 99.0 | 128.0 |
| 1987–1997 | 102.8 | 109.6 | 107.0 | 136.0 |
| 1997–2008 | 109.6 | 112.5 | 113.0 | 143.0 |
| 2008–2024 | 112.5 | 153.1 | 117.0 | 160.0 |

The last interval improves (−30 → +7), but every pre-2008 interval overshoots by +25 to +30.
The held-out fold BA MAE doubles (3.07 → 6.34); TPH MAE is flat-to-worse (51.4 → 52.6). The
pre-2008 intervals are the selection set, and they reject the boost; a boost fitted only to the
last interval is fitting the validation point.

The dense site's final BA jump is therefore a measurement/history discontinuity, not a high-BA
growth response. Reverted; W30 remains the shipped half.
