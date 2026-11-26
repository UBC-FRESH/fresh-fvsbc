# W12: SBS maximum basal area per subzone

Status: **built and calibrated on the SBS fold.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w12-sbs-bamax.patch.gz`, applied after `w11-cwh-height.patch.gz`.
Bundles: unchanged. `d7-sbs-bundle.json` still carries `MORTMULT 2`.

## 1. Why

`BAMAX` is the stand maximum basal area. In `morts.f` the projection sends a `BA/BAMAX` share of the
predicted basal-area increment to mortality, so a stand near its cap cannot gain basal area. Every
zone in the variant has a subzone table of caps except SBS, which had a **single flat 55 m²/ha**.

The measured p99 of every SBS subzone is above 55:

| Subzone | Measured p99 | Old cap | New cap |
| --- | ---: | ---: | ---: |
| dh1 | 74.6 | 75 | 75 |
| dh2 | 67.8 | 55 | 68 |
| dk | 59.3 | 55 | 59 |
| dw1 | 64.0 | 55 | 64 |
| dw2 | 59.2 | 55 | 59 |
| dw3 | 72.8 | 55 | 73 |
| mc | 65.1 | 55 | 65 |
| mc2 | 68.0 | 55 | 68 |
| mc3 | 43.5 | 55 | 44 |
| mh | — | 60 | 60 |
| mk1 | 65.0 | 55 | 65 |
| mk2 | 58.0 | 55 | 58 |
| mm | 61.6 | 55 | 62 |
| mw | 58.3 | 55 | 58 |
| un | 16.1 | 16 | 16 |
| vk | 65.2 | 55 | 65 |
| wk | 70.7 | 55 | 71 |
| wk1 | 59.5 | 55 | 60 |
| wk2 | 62.3 | 55 | 62 |
| wk3 | 47.3 | 55 | 47 |

The p99 convention is the one the table already uses elsewhere: CWHdm's cap of 112 matches a measured
p99 of 111.7, CDFmm's 112 matches 111.9, MHmm1's 123 matches 122.5.

## 2. What changed

`sitset.f` only. The SBS `CASE` gains a subzone table; the zone default stays 55 for a label the table
does not name. No other zone changes.

## 3. Evidence

SBS fold, W11 engine against W12, same sites and the shipped bundle (`MORTMULT 2` on FD, PL, SE,
and HW):

| Build | Folder | Intervals | BA bias (m²/ha) | BA MAE |
| --- | --- | ---: | ---: | ---: |
| W11 (flat 55) | test | 38 | −2.53 | 6.12 |
| **W12** | **test** | **38** | **−1.21** | **6.17** |
| W11 (flat 55) | train | 106 | −1.19 | 7.97 |
| **W12** | **train** | **106** | **+0.38** | **8.10** |

The caps move the bias toward zero and leave MAE unchanged: this is a bias correction, not an
accuracy gain. A global cap sweep (55 → 75) showed the direction before the subzone table was built;
the subzone table avoids lowering `dh1`, whose 75 was already right.

## 4. What is left

With the shipped bundle the ten `SBSmc2` intervals no longer collapse; their errors run from −23 to
+55 m²/ha and average **+20**, so the cell now over-predicts at high basal area instead of
under-predicting. That is a growth/mortality shape problem and it stays on the backlog.

A caution for anyone re-running these folds: an earlier probe applied `MORTMULT 2` to all twelve
species rather than the bundle's four, and in the alder-rich `SBSmc2` stands that killed the whole
stand (two intervals predicted 0 BA and 0 TPH). The bundle is per species for a reason; the fold
numbers in this note use the shipped species set.

## 5. Tier and claim

SBS stays **C**. The cap table is now consistent with the other zones and the fold improves, but the
zone's growth and mortality rows are unchanged, the fold is unsigned, and `SBSmc2` remains wrong at
high basal area.

## 6. Build

Apply after W11; the wheel recipe does this. Verified against the full W2–W11 chain from the pinned
tree.
