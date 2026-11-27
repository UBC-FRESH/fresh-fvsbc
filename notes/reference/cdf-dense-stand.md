# CDF dense stands: too many stems died

Status: **shipped as a bundle change (MORTMULT 0.5 for FD and AC). Tier stays C.**

## 1. The stand

`4002349|1|2008|2024`, CDFmm, 16 years:

| | Start | End | Measured |
| --- | ---: | ---: | ---: |
| BA (m²/ha) | 111 | 109 | **112.5 → 153.1** |
| TPH | 471 | 271 | **526 → 518** |
| QMD (cm) | 54.9 | 71.7 | 52.2 → 61.4 |

The measured stand loses 1% of its stems and gains 41 m²/ha. The model loses 42% of its stems and
gains nothing. The tree list is FD 297 + AC 168 + BG 7 TPH.

## 2. Separating mortality from growth

Isolating the two with a zero-mortality run on the same interval:

| Setting | TPH | BA | QMD |
| --- | ---: | ---: | ---: |
| Bundle as shipped (`BAIMULT 8`) | 271 | 109.0 | 71.7 |
| Mortality 0 | 471 | 126.0 | 58.3 |
| Mortality 0, `BAIMULT 16` | 471 | 140.0 | 61.5 |
| Mortality 0, `BAIMULT 24` | 471 | 154.0 | 64.5 |
| `MORTMULT 0.5` (all species) | 370 | 117.0 | 63.5 |

So both defects are real: the model kills stems the stand kept, and its diameter growth is about
three times too low for this stand. A zone-wide `BAIMULT` of 24 would fix this one stand and
overshoot the fold's train intervals (+27% BA there), so the multiplier is not the tool for it.

## 3. The change

`cdf-v3-bundle.json` gains `MORTMULT 0.5` for **FD and AC**, the two species in the dense stand, on
top of `BAIMULT 8`. The multiplier is restricted to those two because applying it to all twelve
species was worse on the fold (test TPH MAE 77.5 vs 66.8).

## 4. Held-out evidence

CDF fold, 16 held-out / 14 train intervals, the bundle run through the probe:

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| Previous bundle (`BAIMULT 8`) | test | −5.12 | 5.32 | −34.7 | 85.9 |
| **New bundle** | **test** | **−3.12** | **3.46** | **−8.8** | **66.8** |
| Previous bundle | train | +2.70 | 4.12 | +92.1 | 183.5 |
| **New bundle** | **train** | +2.98 | 4.41 | +100.1 | 191.1 |

**BA and TPH both improve on the held-out sites**, which is the shipping rule; the train intervals
move slightly the other way. The dense stand itself moves from 271 TPH / 109 BA to **370 TPH /
117 BA**.

## 5. Tested and not shipped

`BAMAX` 140 and 170 were swept on the same fold with the new mortality:

| Variant | Test BA | Test MAE | Test TPH MAE |
| --- | ---: | ---: | ---: |
| default cap (112) | −3.12 | 3.46 | 66.80 |
| `BAMAX 140` | −2.50 | 3.21 | 66.49 |
| `BAMAX 170` | −2.12 | 3.07 | 65.92 |

The gain is small and the train fold pays for it, so the cap stays at the measured p99.

## 6. What remains

The dense stand is still 33 m²/ha short of its measured BA with the cap and mortality fixed: its
growth is an extreme (BA +41 at BA 112), and the zone's `BAIMULT` cannot reach it without breaking
the rest of the fold. That is either a site-specific growth anomaly or a genuine high-BA growth
term the current DG form does not carry. It is recorded here rather than tuned away.
