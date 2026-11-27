# `ms-v3`: MS growth plus recruitment

Status: **shipped in 0.41.8; verified from PyPI.** Engine unchanged at 0.4.14. Tier stays C (unsigned).

## 1. Starting point

MS had no bundle. Both folds under-predicted BA and TPH:

| Fold | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: |
| test (19) | −2.99 / 3.80 | −46 / 258 |
| train (115) | −2.78 / 5.92 | −200 / 752 |

## 2. The per-bin mortality/ingrowth shape failed

Per-BA-bin TPH-MAE responses between recruitment scale 0.4 and 0.8:

| BA bin | Train MAE (0.4→0.8) | Test MAE (0.4→0.8) |
| --- | ---: | ---: |
| 0–20 | 323 → 551 | 716 → 407 |
| 20–35 | **820 → 770** | 270 → 392 |
| 35–50 | 568 → 680 | 136 → 173 |
| 50–65 | 809 → 930 | 89 → 128 |
| 65+ | 767 → 851 | — |

Only 20–35 improves train; it worsens test. The other bins that improve test worsen train. No
bin improves both, so a variance-aware per-bin shape cannot pass.

## 3. The change

- Recruitment v1 at scale **0.4** (fixes TPH with BA essentially unchanged).
- **`BAIMULT 1.6`** for all species (partial ten-year-basis growth correction; supplies the BA
  improvement and trims the recruitment-driven TPH overshoot).

## 4. Evidence

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| base | test | −2.99 | 3.80 | −46 | 258.3 |
| **ms-v3** | **test** | **−2.83** | **3.75** | **+66** | **250.5** |
| base | train | −2.78 | 5.92 | −200 | 751.6 |
| **ms-v3** | **train** | **−2.49** | **5.78** | **−8** | **729.3** |

All four MAE figures improve. The held-out TPH bias flips from −46 to +66; the held-out MAE still
improves, and the train bias improves from −200 to −8.

## 5. What remains

PP still has no bundle (5 held-out intervals on 2 sites). The MS fold is unsigned; the remaining
BA/TPH errors are much smaller than the other zones.

## Reproduce

- Per-bin grid: `~/workspace/bwbs-work/probe_ms_rec{40,80}/`.
- Growth grid: `probe_ms_rec_growth/`.
- Bundle run: `probe_ms_bundle/`.
