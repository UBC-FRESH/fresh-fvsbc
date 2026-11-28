# fresh-fvsbc 0.41.22

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.21

- **Public disturbance observations materialized.** The BC Data Catalogue fire-severity, fire-
  perimeter and consolidated-cutblock layers were resolved through OpenMaps WFS. A South Coast AOI
  returned 150 severity polygons, 692 fire perimeters and 7,840 cutblocks; joining to PSP header
  points gave **24 events at 20 sites** (20 fire, 4 harvest). Two harvest events fall inside
  calibration intervals. No severity polygon covered a PSP point, so fire events carry a
  perimeter-default severity until a severity-rated overlap exists.
- **Harness reports interval matches.** `interval_coverage()` and the CLI now count events whose
  year lies between an interval's two visits, not just site coverage.
- **CDF high-BA leave-one-site-out tested.** The existing 20 intervals at BA ≥60 (five sites) were
  held out one site at a time. All-species MORTMULT 0.25 and 60+ ingress ×2 + MORTMULT 0.5 improve
  both mean BA and mean TPH (TPH MAE 47.2 → 41.9 / 40.4). But a BA-scoped 60–90 term (W34 ×0.5)
  fails the full clean fold (BA 1.318 → 1.377, TPH 36.10 → 36.96). **No CDF parameter ships.**
- **W33 donor-preserving CW tall term tested.** It halves the pair tall-end bias (−0.64 → −0.30) and
  moves top height −5.55 → −5.53 and volume −106.98 → −106.57, but BA and held-out TPH are
  unchanged. **No CW change ships.**

No bundle or engine parameter changed. The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**.

```
pip install "fresh-fvsbc[fvs]==0.41.22"
```

## Gaps that remain

- CDF dense stand: TPH mixed-sign; the BA-scoped term trades the 60–81 sites against the dense
  early intervals.
- CW large-tree height: donor; the tall term is too small to move BA/TPH.
- Disturbance: public observations now cover 24 events; only 2 fall inside calibration intervals.
- No A/B support cells.

## fresh-fvsbc 0.41.21

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.20

- **New-form CW height equation: tested and rejected.** On the CWH remeasurement pairs the new form
  improves RMSE 1.49 → **1.06 m/decade** and halves the tall-end bias (−0.64 → −0.32). But on the
  held-out CWH fold the TPH MAE moves 171.41 → 171.51 and the stand A/B worsens
  (BA −4.737 → −4.782, top height −5.55 → −5.66, volume −106.98 → −109.74). The CW donor stays;
  no engine change ships.
- **Disturbance validation harness prepared.** `fresh_fvsbc.disturbance` and
  `scripts/validate_disturbance.py` load a documented observed-event CSV, check coverage against
  the PSP intervals, and score BA/TPH bias and MAE by type and severity once predictions exist.
  A header-only template and the input contract are in `notes/reference/disturbance-validation.md`.
  No BC fire/severity or harvested-block observations are in the repository yet.

No bundle or engine parameter changed. The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**.

```
pip install "fresh-fvsbc[fvs]==0.41.21"
```

## Gaps that remain

- CDF dense stand: TPH mixed-sign; needs an independent BA >90 remeasurement site.
- CW large-tree height: donor; the new form failed the stand test.
- Disturbance: harness ready, observations missing (BC fire/severity and harvested blocks).
- No A/B support cells.

## fresh-fvsbc 0.41.20

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.19

- **CDF high-BA ingress/mortality was tested and rejected.** On the cleaned held-out fold the
  shipped `cdf-v3` has the lowest TPH MAE (**36.1**). Recruitment (scale 0.4–1.5), 60+ bin boosts
  (×2–×4), 40–60 and 30–40 boosts, and all-species mortality (0.25–0.5) all raise it (38.6–54.5);
  none improves both BA and TPH.
- **The train fold cannot identify a >90 m²/ha term.** Its BA range is 29–56; the only BA >90
  intervals in the calibration set belong to the held-out dense site itself. The expanded train
  adds only 63–81 m²/ha intervals. A >90 fit would be validated on the same site it was fitted on.
- **New data screen: `--max-unaccounted-removal`.** It drops intervals whose TPH/BA loss is not
  explained by recorded dead trees (harvest/plot changes). On the CDF fold it removes
  `4002933|1|2008|2022`, `4002809|1|2002|2022` and `4002975|1|1944|1947`; with the tree-84 screen
  the held-out TPH MAE falls from 50.6 to **36.1**.

**No shipped parameter changed**; `cdf-v3` and the engine stay as in 0.41.19.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.20"
```

## Gaps that remain

- CDF dense stand: TPH still mixed-sign; needs an independent BA >90 remeasurement site.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.19

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.18

- **The CDF dense-stand BA gap was a keying error.** The 2008–2024 interval's observed 153.1 m²/ha
  contains tree 84 at **401.7 cm**; its 2008 DBH was 98.3 cm and its height grew normally. Corrected
  to 101.7 cm, observed BA is 123.8 against the model's 125. The reported ~28 m²/ha defect is not a
  growth response.
- **New calibration screen: `--max-dbh-growth-rate`.** The probe matches live trees at both visits
  and drops intervals with an impossible DBH jump. At 5 cm/yr it flags exactly the `4002349|1|2008|2024`
  interval and writes `screened_intervals.csv`.
- **Held-out CDF fold:** BA MAE **3.01 → 1.34**, TPH MAE 50.6 → 50.2 with the interval screened.
  Correcting the observation instead of dropping the interval gives BA 1.33, so the two agree.
- **No shipped parameter changed.** The remaining CDF TPH gap (~56 on the interval, ~50 MAE on the
  fold) is a real high-BA ingress/mortality gap, not a discontinuity.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.19"
```

## Gaps that remain

- CDF dense stand: TPH still ~56 low; the fold applies no recruitment.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.18

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.17

- **Zone-level bundles rechecked on stable-DBH-limit folds.**
  - **Kept:** `cwh-v3`, `mh-v3`, `cdf-v3`, `pp-v3` still improve both held-out BA and TPH.
  - **Refit:** `sbs-v3` drops from `MORTMULT 1.85` to **1.1** for FD/PL/SE/HW; test
    7.010/543.1 → **6.760/538.6**, train 4.687/333.7 → **4.617/331.8**.
  - **Withdrawn:** `sbps-v3`, `ms-v3`, `essf-v3`. On the stable fold each improves BA but leaves
    TPH flat-to-worse, and no clean candidate improves both. The engine still runs those zones on
    V3; only the multiplier/recruitment bundles are gone.

  | Zone | Old bundle on stable fold | Action |
  | --- | --- | --- |
  | CWH | 5.59/206.7 → **3.38/171.4** test | keep |
  | MH | 2.71/99.7 → **2.04/85.7** test | keep |
  | CDF | 5.26/30.8 → **1.06/29.3** test | keep |
  | PP | 2.01/80.3 → **1.26/79.8** test | keep |
  | SBS | 543 → 577 TPH at 1.85 | refit to 1.1 |
  | SBPS | 847 → 1218 TPH | withdraw |
  | MS | 307 → 311 TPH | withdraw |
  | ESSF | 394.9 → 396.6 TPH | withdraw |

- **No zone or subzone bundle carries recruitment now.** The standalone `recruitment-bc-v1`
  bundle remains available.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.18"
```

## Gaps that remain

- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.17

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.16

- **Root cause found: the DBH-limit break.** Early PSP visits tally only trees above 9.1 cm; later
  visits tally from 2 cm. The calibration fold read those small stems as growth, which is why the
  SBS subzones looked TPH-deficient. **2,797 of 17,151 intervals (16%)** change `DBH_LIMIT_TAG`
  between visits. `scripts/run_calibration_probe.py --stable-dbh-limit` drops them.
- **`sbsmk1-v3` is withdrawn.** On the stable fold it makes both folds worse (test BA/TPH
  5.14/381 → 5.55/427; train 4.81/430 → 5.36/500), and no clean candidate improves BA and TPH in
  both folds. SBSmk1 ships no subzone bundle.
- **Four subzone bundles are refit on clean folds** (all four MAE measures improve):

  | Bundle | Contents | Test (base → clean) | Train (base → clean) |
  | --- | --- | --- | --- |
  | `sbsmw-v3` | `BAIMULT 0.95` | 4.88/239 → **4.77/231** | 4.06/139 → **4.00/139** |
  | `sbswk2-v3` | `BAIMULT 2.0`, `MORTMULT 1.2` | 3.78/245 → **3.77/222** | 4.18/441 → **4.01/373** |
  | `sbsdw1-v3` | `MORTMULT 1.25` | 6.72/222 → **4.24/211** | 7.81/216 → **6.79/211** |
  | `sbsmc2-v3` | `BAIMULT 0.3`, `MORTMULT 1.15` | 7.29/677 → **6.25/655** | 7.75/495 → **6.75/468** |

- **Recruitment is no longer carried by any subzone bundle.** Once the limit break is removed it
  either does nothing or adds variance.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.17"
```

## Gaps that remain

- The 16% limit-break share is not SBS-specific; the **zone-level bundles** were calibrated before
  the flag and need rechecking on stable folds.
- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.16

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.15

- **First SBSdw1 bundle.** SBSdw1's 43 repeat sites over-predicted BA (+5.8) and its TPH error
  changed sign. `sbsdw1-v3` pairs `BAIMULT 0.7` + `MORTMULT 1.3` with recruitment v1 at scale 0.4.
- **All four MAE figures improve.** Held-out BA 6.38 → **4.00**, TPH 268.6 → **263.7**; train BA
  7.29 → **6.32**, TPH 245.8 → **237.6**. BA improves strongly in both folds; the held-out TPH
  gain is small because the fold has only 11 intervals, so it is provisional.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.16"
```

## Gaps that remain

- SBSmk1 −409 TPH; SBSmc2 +2.2 / −323; SBSdw1 provisional TPH.
- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.15

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.14

- **First SBSwk2 bundle.** SBSwk2's 90 repeat sites under-predicted BA (−4.48) and TPH (−270) on
  both folds. `sbswk2-v3` carries `BAIMULT 2.0`, `MORTMULT 0.85` and recruitment v1 at scale 0.6.
- **All four MAE figures improve.** Held-out BA 5.95 → **5.35**, TPH 489 → **406**; train BA
  6.30 → **5.78**, TPH 735 → **647**. Both TPH biases fall to single digits.
- **Probe fix: `--exact-bec`.** A prefix match let the SBSmc fold absorb SBSmc2. SBSmc's exact
  fold is already well calibrated (−0.80 / 1.93 BA, −22 / 71 TPH held out), so it needs no bundle.
- **Negative:** the SBSmk1 stem-shape term and the SBSdw1 coupled grid do not improve all four
  measures; neither ships.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.15"
```

## Gaps that remain

- SBSmk1 −409 TPH; SBSmc2 +2.2 / −323; SBSdw1 fold divergence.
- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.14

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.13

- **`sbsmk1-v3` gains the recruitment block.** The growth/mortality pair fixed BA but left TPH under
  (−669). Recruitment v1 at scale 0.4 supplies the stems.
- **All four MAE figures improve again.** Held-out BA 6.37 → **6.33**, TPH 873 → **810**; train
  BA 6.12 → **6.09**, TPH 766.5 → **743.0**. TPH bias improves from −669 to −409 (test) and from
  −409 to −144 (train).

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.14"
```

## Gaps that remain

- SBSmk1 still −409 TPH biased; SBSmc2 +2.2 / −323; SBSmw −128.
- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.13

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.12

- **First SBSmw bundle.** SBSmw's BA is already calibrated (+0.16 / 5.18), but TPH is under
  (−282 / 421). `sbsmw-v3` raises the recruitment v1 scale to **1.2** without touching growth or
  mortality.
- **All four MAE figures improve.** Held-out BA 5.18 → **5.15**, TPH 421 → **403**; train BA
  4.626 → **4.622**, TPH 295.6 → **293.7**. The TPH bias improves from −282 to −128 (held out)
  and from −201 to −47 (train).

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.13"
```

## Gaps that remain

- SBSmw still −128 TPH biased; SBSmk1 −2.0 / −669; SBSmc2 +2.2 / −323.
- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.12

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.11

- **First SBSmk1 bundle.** The province data showed SBSmk1 far worse than the SBS zone average:
  **−5.18 BA / −637 TPH** on a 56-interval held-out fold. `sbsmk1-v3` carries **`BAIMULT 2.0`**
  and **`MORTMULT 0.85`**.
- **All four MAE figures improve.** Held-out BA 7.00 → **6.37**, TPH 881 → **873**; train BA
  6.54 → **6.12**, TPH 780 → **767**. Held-out BA bias improves from −5.18 to −1.97.
- **W22 was not the cause.** Scoping the SBS-wide BL density term to SBSmc2 changed SBSmk1 and
  SBSmc by zero; the gap is subzone calibration, not a W22 regression.

The engine stays **`fresh-fvsbc-pyfvs 0.4.16`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.12"
```

## Gaps that remain

- SBSmk1 still −2.0 m²/ha / −669 TPH biased (MAE improved).
- SBSmc2 +2.2 m²/ha / −323 TPH on the matched fold.
- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.11

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.10

- **The CDF high-BA mortality term is stronger (×0.1, was ×0.25).** The dense site's raw visit
  history shows one permanent 0.405 ha plot with the same design and DBH limit at 2008 and 2024,
  so its 153 m²/ha end is real. The model's QMD is close; its TPH is low, i.e. mortality is still
  too high above BA 90.
- **Held-out CDF improves again.** BA MAE 3.07 → **3.01**, TPH MAE 51.4 → **50.6**; the train
  fold is unchanged (BA ≤ 90, term inert).
- **Dense interval:** 123 BA/447 TPH → **125 BA/462 TPH** against 153/518.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.16`** (W2–W22 + W28 + W30 ×0.1). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.11"
```

## Gaps that remain

- The CDF dense stand is still ~28 m²/ha / ~56 TPH short.
- SBSmc2 is +2.2 m²/ha / −323 TPH on the matched fold.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.10

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.9

- **CDF dense stands get a high-BA mortality interaction.** Above **90 m²/ha**, CDF mortality is
  multiplied by **0.25**. The dense site under-predicted TPH from 1977 onward (observed 589 vs
  predicted 400 at BA 94) while its pre-2008 BA growth was already right.
- **Held-out CDF fold improves on both measures.** BA MAE 3.46 → **3.07**, TPH MAE 66.8 →
  **51.4**; the train fold is unchanged (its BA never reaches 90, so the term is inert there).
- **The dense stand improves but is still short.** 2008–2024 moves from 117 BA/370 TPH to
  **123 BA/447 TPH** against 153/518 measured. The last interval remains a growth discontinuity
  (BA +40.6 after +2.9 in the prior 11 years), which the mortality term cannot address.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.15`** (W2–W22 + W28 + W30). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.10"
```

## Gaps that remain

- The CDF dense stand is still ~30 m²/ha / ~71 TPH short.
- SBSmc2 is +2.2 m²/ha / −323 TPH on the matched fold.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.9

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.8

- **First PP bundle.** `pp-v3` carries **`BAIMULT 3.0`** and **`MORTMULT 0.8`**. PP had no bundle
  and its old held-out fold was only 5 intervals on 2 of 10 sites.
- **Validated leave-one-site-out across all 10 PP sites.** BA MAE 2.58 → **1.76**, TPH MAE
  66.05 → **65.30**. BA improves on all 8 sites that carry intervals; TPH improves on 5 and
  worsens on 3 (largest +5 on a 2-interval site).
- **Why LOSO.** With 10 sites, leave-one-site-out uses every site as held-out once instead of
  relying on a 2-site split.

The engine stays **`fresh-fvsbc-pyfvs 0.4.14`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.9"
```

## Gaps that remain

- SBSmc2 is +2.2 m²/ha / −323 TPH on the matched fold.
- The CDF dense stand is still 33 m²/ha short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.
- All zones remain unsigned **C** pilots.

## fresh-fvsbc 0.41.8

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.7

- **First MS bundle.** `ms-v3` carries **`BAIMULT 1.6`** for all species plus the recruitment v1
  block. MS had no bundle and both folds under-predicted BA and TPH.
- **All four MAE figures improve.** Held-out BA MAE 3.80 → **3.75**, TPH 258.3 → **250.5**; train
  BA 5.92 → **5.78**, TPH 751.6 → **729.3**. The held-out TPH bias moves from −46 to +66; the
  train TPH bias improves from −200 to −8.
- **Why growth + recruitment, not a per-bin mortality shape.** Per-BA-bin mortality/ingrowth
  responses had opposite signs on train and held out; no bin improved both. Recruitment alone
  fixed TPH with BA unchanged; a partial growth correction supplied the BA improvement.

The engine stays **`fresh-fvsbc-pyfvs 0.4.14`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.8"
```

## Gaps that remain

- PP still has no bundle; its held-out fold is 5 intervals on 2 sites.
- SBSmc2 is +2.2 m²/ha / −323 TPH on the matched fold.
- The CDF dense stand is still 33 m²/ha short.
- CW large-tree height is still the donor.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.7

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.6

- **SBSmc2 ingress is fitted with a variance-aware shape, not a global scale.** The matched
  BA-stratified fold showed the model at +2.2 m²/ha / −386 TPH. Raising recruitment globally
  fixes the mean but adds variance; only the **20–30 m²/ha BA bin** improves train TPH MAE, so
  that bin's recruitment rate is **doubled** in `sbsmc2-v3`.
- **Held-out and train both improve or hold.** Held-out BA MAE 7.89 → **7.84** and TPH MAE
  828 → **794**; train TPH MAE 610 → **609**, train BA 8.09 → 8.10 (flat).
- **The stratified fold is the representative estimate.** Matching the held-out and train
  stand-density distributions moves SBSmc2 from the random split's +6.9/−729 to **+2.2/−386**.

The engine stays **`fresh-fvsbc-pyfvs 0.4.14`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.7"
```

## Gaps that remain

- SBSmc2 still +2.2 m²/ha / −386 TPH; the remaining deficit is ingress in other BA bins.
- The CDF dense stand is still 33 m²/ha short.
- CW large-tree height is still the donor.
- MS and PP have no validated bundle.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.6

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.5

- **SBSmc2 gets a stem-shape mortality term.** The full subzone still had too few stems and too
  much basal area (+9.1 m²/ha / −908 TPH). W28 saves small stems and thins large ones:
  `X *= 0.5` for DBH < 10 cm and `X *= 2.5` for DBH ≥ 20 cm (SBSmc2 only).
- **Both errors improve on both folds.** Held-out BA MAE 12.52 → **11.61**, TPH 1212 → **1081**;
  train BA 7.66 → **7.13**, TPH 566 → **545**. Biases improve to +6.9 / −729 (test) and +0.4 /
  −183 (train).
- **The shape matters.** Saving small stems alone raised BA; thinning large stems alone lost TPH.
  The two-sided term is what moves both.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.14`** (W2–W22 + W28). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.6"
```

## Gaps that remain

- SBSmc2 still +6.9 m²/ha / −729 TPH; the remaining deficit is ingrowth/ingress.
- The CDF dense stand is still 33 m²/ha short; it needs high-BA (>100) training data.
- CW large-tree height is still the donor.
- MS and PP have no validated bundle.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.5

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.4

- **The SBSmc2 validation sample was wrong, and this fixes the calibration on the real subzone.**
  The SBS fold sampled only 10 SBSmc2 intervals; the data has **249 intervals on 126 sites**. On a
  dedicated 20% site split the full subzone was **+11.6 m²/ha BA and −1,064 TPH** — far worse than
  the sampled +1.5/−81.
- **New `sbsmc2-v3` bundle.** `BAIMULT 0.3` for all species plus the recruitment v1 ingrowth block.
  It improves both errors on both folds: held-out BA MAE 14.04 → **12.52** and TPH 1,298 → **1,212**;
  train BA MAE 8.37 → **7.66** and TPH 574 → **566**. Biases also improve (held-out BA +11.6 → +9.1,
  TPH −1,064 → −908).
- **Why growth, not small-stem mortality.** Lighter <10 cm mortality cut TPH error but raised BA;
  the small-stem path trades one error for the other. Reducing growth lowers BA and raises TPH
  together, which is what the over-BA/under-TPH subzone needs.

This is a **partial** correction: SBSmc2 is still +9.1 m²/ha / −908 TPH. The engine stays
**`fresh-fvsbc-pyfvs 0.4.13`**.

```
pip install "fresh-fvsbc[fvs]==0.41.5"
```

## Gaps that remain

- SBSmc2 still +9.1 m²/ha / −908 TPH on the full subzone.
- The CDF dense stand is still 33 m²/ha short; it needs high-BA (>100) training data.
- CW large-tree height is still the donor.
- MS and PP have no validated bundle.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.4

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.3

- **The first ESSF bundle.** `essf-v3` carries **`BAIMULT 2.5`** and **`MORTMULT 0.9`** for all
  twelve species, a coupled partial ten-year-basis growth correction plus lighter mortality.
- **Both folds improve on both measures.** Held-out BA MAE 5.49 → **5.15**, TPH MAE 530.2 →
  **528.8**; train BA MAE 6.31 → **6.14**, TPH MAE 553.4 → **551.2**. BA bias also improves from
  −3.07 to −2.21 (held out).
- **The full ten-year correction overshoots.** The ESSF rows are annual-basis, but a full ×10
  diameter correction predicts about 6× growth where the fold needs ~1.6×. The train-only
  coupled grid selected the partial correction (DG ×1.58) with mortality ×0.9; applying the
  full basis change would over-predict BA and cost TPH.

The engine stays **`fresh-fvsbc-pyfvs 0.4.13`**. Install:

```
pip install "fresh-fvsbc[fvs]==0.41.4"
```

## Gaps that remain

- MS and PP still have no bundle; their held-out and train folds diverge.
- The CDF dense stand is still 33 m²/ha short; it needs high-BA (>100) training data.
- SBSmc2 is still +1.5 m²/ha / −81 TPH.
- CW large-tree height is still the donor; the taper-free form failed stand-level A/B.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.3

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.2

- **The SBSmc2 dense small-tree cell is largely fixed.** The cell moves from **+2.8 to +1.5 m²/ha**
  and from **−200 to −81 TPH**.
- **SBS BL now has a stand-density term.** The BL row's CCF coefficient is **−0.35**, so growth
  falls at high density; the bundle's `MORTMULT` for FD/PL/SE/HW moves from **2.0 to 1.85**.
  The pair data show a milder slope than the engine's existing response, so the term is a
  targeted cell correction, not a direct pair fit; it was selected on the train fold and
  validated held out.
- **Both fold errors improve.** Held-out BA MAE 6.09 → **5.91**, TPH 658.9 → **644.3**; train
  BA 5.22 → **4.94**, TPH 398.3 → **396.9**. The held-out TPH bias moves from −22 to +20 on a
  mean of about 650; the cell TPH bias improves by 119.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.13`** (W2–W18 + W21 + W22). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.3"
```

## Gaps that remain

- The SBSmc2 cell is still +1.5 m²/ha / −81 TPH.
- The CDF dense stand is still 33 m²/ha short; it needs high-BA (>100) training data.
- CW large-tree height is still the donor; CWH small-tree density is now fitted.
- MS, ESSF, and PP have no bundle; held-out and train folds diverge.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.2

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.41.1

- **CWH small trees now respond to stand density in both diameter and mortality.** Direct
  remeasurement pairs show diameter growth falling from 0.48 cm/yr below CCF 100 to 0.08 above
  300, and mortality rising from 0.7% to 5.5%/yr. The height-derived engine model was flat in
  diameter and had no CCF term in mortality.
- **The joint term fixes both fold errors.** With `BAIMULT 8`, held-out BA MAE 4.000 → **3.778**
  and TPH MAE 273.0 → **234.9**; train BA 5.030 → **4.983** and TPH 357.3 → **337.2**.
- **The diameter-only version was not enough.** It improved BA but raised TPH (297.8); pairing it
  with the fitted density mortality was what brought TPH down by 38 stems on the held-out fold.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.12`** (W2–W18 + W21). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.2"
```

## Gaps that remain

- CWH remains an unsigned **C** pilot; CW large-tree height is still the donor (W11 form limit).
- The CDF dense stand is still 33 m²/ha short; it needs high-BA (>100) training data.
- SBSmc2 is still +2.8 m²/ha / −200 TPH.
- MS, ESSF, and PP have no bundle; their held-out and train folds diverge.
- Disturbance calibration is not done.
- No A/B support cells.

## fresh-fvsbc 0.41.1

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

**0.41.0 and engine 0.4.10 are superseded.** Their SBS BL row was parameterised on annual
growth, but FVS applies a **10-year** diameter increment, so those builds grew SBS BL about
ten times too slowly. Upgrade to 0.41.1 / engine 0.4.11.

## What changed since 0.41.0

- **The SBS BL row is parameterised correctly.** `ZNKONST(31)` predicts a 10-year increment
  in cm; the refit response is `10 * growth_cm` from 11,005 SBS BL pairs, with the 10–20 cm
  class weighted three times and a ×1.2176 smearing correction for the log fit.
- **The crown term that inflated dense stands is gone.** The legacy `3.1925 * crown` added
  1.44 to ln(growth) on the SBSmc2 cell (crown ratio 0.45) — a factor of 4.2. The refit uses
  the density terms V3 actually applies and no crown term, because the pairs carry no crown
  ratio.
- **The dense stand now grows at the measured rate.** 79 TPH, QMD 15.5 cm: measured 0.21
  cm/yr, legacy + crutch **0.50**, W18 **0.28**.
- **Held-out result.** Test TPH MAE 686.7 → **658.9**; train BA MAE 5.83 → **5.22**, TPH MAE
  435.5 → **398.3**. Test BA MAE is 6.00 → 6.09 (0.09, against a multiplier that was selected
  on this fold); against the same row with no multiplier, BA MAE improves 6.38 → 6.09.
- **SBSmc2 is essentially fixed.** The cell moves from **+9.2 to +2.8 m²/ha** and from
  **−635 to −200 TPH**.
- **`sbs-v3` has no `BAIMULT` for BL.** It keeps `MORTMULT 2` for FD/PL/SE/HW.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.11`** (W5–W18). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.1"
```

## Gaps that remain

- The BL row has no crown term; mapping `CR_CL` classes to midpoints is the next step.
- The CDF dense stand is still 33 m²/ha short on BA.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- MS, ESSF, and PP have no bundle.
- Disturbance calibration is not done.
- No A/B support cells; every forested zone is an unsigned **C** pilot.

## fresh-fvsbc 0.41.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.40.0

- **The SBS BL growth row is refitted, and the multiplier that masked it is gone.** The row predicted
  1.9 cm/yr for a 10–20 cm BL against 0.21 measured. `ZNKONST(31)` is now fitted from 11,005 SBS BL
  pairs with the 10–20 cm class weighted three times, and predicts 0.17 against 0.21.
- **SBSmc2 is essentially fixed.** The cell moves from **+9.2 to +0.1 m²/ha** and from **−635 to −45
  TPH**.
- **The fold improves.** Train BA MAE 5.83 → **4.95**, TPH MAE 435.5 → **400.4**; held-out TPH MAE
  686.7 → **650.7**. Held-out BA MAE rises from 6.00 to 6.20 while TPH improves — the one cost of
  removing the crutch.
- **`sbs-v3` drops `BAIMULT 0.5` for BL.** It changes the cell by 0.0 m²/ha once the row is fixed.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.10`** (W5–W18). Install:

```
pip install "fresh-fvsbc[fvs]==0.41.0"
```

## Gaps that remain

- The BL row drops the crown term; the pairs carry no crown ratio, so adding it is the next step.
- The CDF dense stand is still 33 m²/ha short on BA.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- MS, ESSF, and PP have no bundle.
- Disturbance calibration is not done.
- No A/B support cells; every forested zone is an unsigned **C** pilot.

## fresh-fvsbc 0.40.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.39.0

- **SBS's dense stands stop over-growing.** The SBSmc2 cell was BL-dominated and averaged +13.1 m²/ha
  of BA with 1,067 stems too few. With mortality off, BA reached 182 from 54 — growth was the driver,
  and the `BA/BAMAX` blend then turned the excess into self-thinning. `sbs-v3` gains **`BAIMULT 0.5`
  for BL**.
- **Held-out result.** BA MAE 6.38 → **6.00**, TPH MAE 699.6 → **686.7** on the held-out sites; train
  BA MAE 6.32 → **5.83**, TPH MAE 471.0 → **435.5**. TPH bias improves in both folds; the held-out BA
  bias moves from −0.24 to −0.74 (−1% of mean BA). The SBSmc2 cell moves from +13.1 to **+9.2 m²/ha**
  and from −1,067 to **−635 TPH**.
- **What it is not.** A stand-level correction: the W6 large-tree row over-predicts dense stems just
  above the 10 cm boundary, and re-fitting it with a small-DBH weight is the real repair.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.40.0"
```

## Gaps that remain

- SBSmc2 is still +9.2 m²/ha and −635 TPH; the BL large-tree row needs the refit.
- The CDF dense stand is still 33 m²/ha short on BA.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- MS, ESSF, and PP have no bundle.
- Disturbance calibration is not done.
- No A/B support cells; every forested zone is an unsigned **C** pilot.

## fresh-fvsbc 0.39.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.38.0

- **CDF's dense stands stop losing stems.** A held-out CDFmm stand at 112 m²/ha gained 41 m²/ha over
  16 years and lost 1% of its stems; the model lost 42% and gained nothing. Separating the two, the
  mortality was the larger defect at that density, so `cdf-v3` gains **`MORTMULT 0.5` for FD and AC**
  on top of `BAIMULT 8`.
- **Held-out result.** CDF fold: BA bias **−5.12 → −3.12 m²/ha** (MAE 5.32 → 3.46), TPH bias
  **−34.7 → −8.8** (MAE 85.9 → 66.8). Both improve on the held-out sites; the train intervals move
  slightly the other way.
- **The dense stand itself** moves from 271 TPH / 109 BA to **370 TPH / 117 BA**.
- **The probe applies a bundle's parameters.** `run_calibration_probe.py --bundle` rendered only the
  ingrowth block; it now renders the parameters too, so a shipped bundle can be tested exactly as it
  ships.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.39.0"
```

## Gaps that remain

- The dense CDF stand is still 33 m²/ha short on BA: its growth is an extreme the zone's `BAIMULT`
  cannot reach without breaking the rest of the fold. `notes/reference/cdf-dense-stand.md`.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- MS, ESSF, and PP have no bundle.
- Disturbance calibration is not done.
- No A/B support cells; every forested zone is an unsigned **C** pilot.

## fresh-fvsbc 0.38.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.37.1

- **`scripts/engine_smoke.py` checks the working surface end to end.** It loads every shipped bundle,
  runs a stand with `cwh-v3` and the recruitment model over two cycles, and builds a two-stand dataset
  with SQLite. `ci.yml` runs it in the job that has the BC extension, so "it works" is a gate rather
  than a claim.
- **The smoke reports failures instead of tracebacks**, and its own two tests run without the
  extension (fakes) so the quality job still covers the script.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.38.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- MS, ESSF, and PP have no bundle; their held-out folds are in the record.
- `SBSmc2` over-predicts at high basal area; CDF dense stands sit at −5 m²/ha.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- Disturbance calibration is not done.
- The dataset has no whole-province run or DOI yet.

## fresh-fvsbc 0.37.1

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.37.0

- **The dataset builder says what a manifest is missing.** A manifest whose `DATABASE` lines omit
  `TREELIDB` produced `UnknownTableError: 'FVS_TreeList_Metric'` from deep inside a run. It now raises
  `DatasetError` naming the stand and telling the caller to add `TREELIDB` and a `TREELIST` keyword.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.37.1"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- MS, ESSF, and PP have no bundle; their held-out folds are in the record.
- `SBSmc2` over-predicts at high basal area; CDF dense stands sit at −5 m²/ha.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- Disturbance calibration is not done.
- The dataset has no whole-province run or DOI yet.

## fresh-fvsbc 0.37.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.36.0

- **The command line takes a shipped bundle by name.** `fresh-fvsbc ... --calibration cwh-v3`
  resolves `bwbs-v3`, `cdf-v3`, `cwh-v3`, `mh-v3`, `sbps-v3`, `sbs-v3`, or `recruitment-bc-v1`; a path
  still works.
- **Recruitment runs from the command line.** With a recruitment bundle and two or more cycles the
  command writes the `ESTAB` block itself, so a shell user does not have to assemble it.
- **A block keyword is refused where it would break.** `--keyword DATABASE=...` wrote a block's
  options on one line, which FVS reads as one field and then misparses; it now points at `--block`.
- **A clear error when there is nowhere to insert.** A calibration without `PROCESS`/`STOP` used to
  raise a bare `ValueError`; it is now `KeywordPlacementError`, reported by the command with the fix.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.37.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- MS, ESSF, and PP have no bundle; their held-out folds are in the record.
- `SBSmc2` over-predicts at high basal area; CDF dense stands sit at −5 m²/ha.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- Disturbance calibration is not done.
- The dataset has no whole-province run or DOI yet.

## fresh-fvsbc 0.36.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.35.0

- **Recruitment finds its rates from the label a run actually carries.** `IngrowthRate.applies` now
  normalises `CWHvm1/01` and `CAR CWHvm1/01` to the `CWHVM1` key the rates use. Before, a caller who
  passed the run's own BEC label got `None` and no establishment block.
- **End-to-end check.** From the installed wheel: `load_default_bundle("cwh-v3")` renders the
  `BAIMULT` keywords, `load_default_bundle("recruitment-bc-v1").ingrowth_keyword(bec="CWHvm1/01", …)`
  returns an `ESTAB` block with five `NATURAL` entries, and a two-cycle run grows a stand from 17 to
  56 TPH.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.36.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- MS, ESSF, and PP have no bundle; their held-out folds are in the record.
- `SBSmc2` over-predicts at high basal area; CDF dense stands sit at −5 m²/ha.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- Disturbance calibration is not done.
- The dataset has no whole-province run or DOI yet.

## fresh-fvsbc 0.35.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.34.0

- **The calibration bundles ship in the wheel.** `DEFAULT_BUNDLES` and `load_default_bundle(name)`
  load `bwbs-v3`, `cdf-v3`, `cwh-v3`, `mh-v3`, `sbps-v3`, `sbs-v3`, and `recruitment-bc-v1` from the
  installed package, validated against the build's pins. A run no longer needs the repository.
- **`sbs-v3` joins the set.** The SBS bundle was untracked under its D7 name; it now carries a
  `sbs-v3` id with its joint BA/TPH claim.
- **A shipped-copy guard.** A test asserts the installed copies are byte-identical to the banked
  calibration artifacts, so the wheel cannot drift from the record.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.35.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- MS, ESSF, and PP have no bundle; their held-out folds are in the record.
- `SBSmc2` over-predicts at high basal area; CDF dense stands sit at −5 m²/ha.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- Disturbance calibration is not done.
- The dataset has no whole-province run or DOI yet.

## fresh-fvsbc 0.34.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.33.0

- **The dataset writes SQLite.** `build_dataset` now writes `dataset.sqlite` beside the CSVs, one
  table per dataset table plus `dataset_meta` with the id, version, and table list. `dataset.json`
  names the file. CSV stays the canonical text form.
- **A whole-TSA run, not a sample.** Every eligible Dawson interval: **221 runs, 442 stand-year rows,
  123,424 tree rows, 85 events** (75 cut rows), four BEC landscape rows, and the full disturbance set
  on the fire and removal stands. Site identifiers stay local.
- **The three new zones are validated out of sample.** A 20% site split reproduces the V3 gains:
  MS −9.25 → **−2.99 m²/ha**, ESSF −8.05 → **−3.07**, PP −3.73 → **−2.53**. A multiplier sweep trades
  BA for TPH in every zone, so no bundle was written.

The engine stays **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.34.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- MS, ESSF, and PP have no bundle; their folds are now held out, but the coefficients were fitted on
  all pairs, so the bounds carry some leakage.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Disturbance calibration is still not done; the dataset carries the wiring, not the coefficients.
- The dataset has no whole-province run or DOI yet.

## fresh-fvsbc 0.33.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.32.0

- **PP is on V3, and the V2 list is empty.** The last V2 zone gains fitted FD and PY diameter and
  height rows, the small-tree branches, and the hardwood mortality row.
- **The fold improves.** PP: BA bias **−4.98 → −2.58 m²/ha**, MAE 4.98 → 2.58, TPH bias −97 → **−0.1**,
  TPH MAE 117 → 66.
- **Eleven zones, one path.** ICH, IDF, SBS, SBPS, BWBS, CWH, MH, CDF, MS, ESSF, and PP all run V3;
  `check_zone_paths.py` reports them all agreeing with `becset.f`. CMA remains out of scope.
- **A caveat stated, not hidden.** PP's PY diameter fit explains nothing (r² −0.008 on 320 pairs);
  only its level is defensible. It was preferred to the ICH donor on the fold, and the row is one line
  to change if a future fold disagrees.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.9`** (W5–W17). Install:

```
pip install "fresh-fvsbc[fvs]==0.33.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- No zone has a held-out split and bundle for MS, ESSF, or PP; MS/ESSF/PP minor species keep donors.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Recruitment, disturbance calibration, and the dataset's SQLite/whole-TSA work remain.

## fresh-fvsbc 0.32.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.31.0

- **ESSF is on V3.** The last large V2 zone (620 intervals, 278 sites) gains the full wiring: the
  condition, the small-tree/height branches, five large-tree diameter rows, three height blocks, and
  the hardwood mortality row.
- **The fold improves.** ESSF: BA bias **−7.86 → −1.91 m²/ha**, MAE 8.78 → 6.20. TPH bias −242 → −151.
- **The MSdk substitution is gone for ESSF.** On V3 the run returns before the habitat table, so
  `ESSFdk2`, `ESSFmv1`, and `ESSFwc4` all report `bec_substitution = null`.
- **One honest compromise.** ESSF lodgepole's free height fit landed on its bounds and predicted
  7.5 m per decade for a 2 m tree; that species uses a scale-only fit on the donor shape.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.8`** (W5–W16). Install:

```
pip install "fresh-fvsbc[fvs]==0.32.0"
```

## Gaps that remain

- PP (27 intervals) is the only zone left on V2, and it needs its growth rows before it can be
  calibrated.
- ESSF and MS have no held-out split or bundle, and their minor species keep donors.
- No A/B support cells; every forested zone is an unsigned **C** pilot.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Recruitment, disturbance calibration, and the dataset's SQLite/whole-TSA work remain.

## fresh-fvsbc 0.31.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.30.0

- **MS is on V3.** The largest remaining V2 zone (1,037 intervals, 307 sites) now has the full wiring:
  the condition, the small-tree/height branches, seven large-tree diameter rows, five height blocks,
  and the hardwood mortality row.
- **The fold improves sharply.** MS held-out-free fold: BA bias **−9.01 → −2.81 m²/ha**, MAE 9.32 →
  5.62, TPH bias −389 → −178. No bundle was added; a candidate sweep (`BAIMULT 4` → −1.82) is
  recorded for a proper held-out pass.
- **The registry now reads 9 V3 zones.** `check_zone_paths.py` reports MS among the V3 zones; ESSF and
  PP remain V2, which is now the whole V2 list.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.7`** (W5–W15). Install:

```
pip install "fresh-fvsbc[fvs]==0.31.0"
```

## Gaps that remain

- ESSF (620 intervals) and PP (27) are the remaining V2 zones; PP also needs its growth path before it
  can be calibrated.
- MS has no held-out split or bundle, and CW/EP/AC keep their donors there.
- No A/B support cells; every forested zone is an unsigned **C** pilot.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Recruitment, disturbance calibration, and the dataset's SQLite/whole-TSA work remain.

## fresh-fvsbc 0.30.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.29.0

- **The zone path is now data, not prose.** `support.ZONE_PATH` maps every zone to the growth path the
  engine runs (`V3`, `V2`, `X`), every support record carries it, and the provenance writes `path` per
  species. `scripts/check_zone_paths.py` compares the registry with the `LV2ATV` list in
  `becset.f` and fails on any divergence, so a zone can no longer be *described* as V3 while the
  engine runs V2.
- **Tree counts fit their field again.** `F6.2` could not hold a count above 999.99, and a small MS
  plot represents about a thousand trees per hectare in one record; the field is now `F8.2`
  (0.01–999999.99). This was a regression introduced by the decimal-count fix in 0.26.0.
- **The registry states the truth.** ICH, IDF, SBS, SBPS, BWBS, CWH, MH, and CDF are V3. MS, ESSF,
  and PP are V2 — 1,684 intervals, about 10% of the calibration set, including MS's 1,037.

The engine stays **`fresh-fvsbc-pyfvs 0.4.6`** (W5–W14). Install:

```
pip install "fresh-fvsbc[fvs]==0.30.0"
```

## Why the remaining zones are still V2

`becset.f` decides V3 with one hard-coded list of eight zones, and 72 further
`INDEX(BEC%Zone,...)` checks across `regent`, `dgf`, `htgf`, and `morts` each carry their own list.
A zone needs coordinated rows in all four files, which is what W5–W9 did for eight zones. MS, ESSF,
and PP were left out and the support text wrongly claimed otherwise. Measured now: **MS on V2 is
−9.01 m²/ha** (134 intervals), worse than any V3 zone, so the wiring is the next work package.

## Gaps that remain

- MS (1,037 intervals), ESSF (620), and PP (27) need the V3 wiring: condition, small-tree branch,
  large-tree rows, height blocks, and mortality routing.
- PP resolves as PP now but still runs V2, which is why it barely grows.
- No A/B support cells; every forested zone is an unsigned **C** pilot.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Recruitment, disturbance calibration, and the dataset's SQLite/whole-TSA work remain.

## fresh-fvsbc 0.29.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.28.0

- **PP runs as PP.** The variant listed only a handful of PP site series, so `PPxh` and `PPxh2`
  (written as `/01`) fell to the `MSdk/01` default. They now map to the PP habitat and reuse the
  adjustment index of the listed series in the same subzone.
- **PP gets its measured caps.** `PPxh` had no case and took a 10 m²/ha fallback with a warning;
  `PPxh2` series 1–4 was capped at 32 against a measured p99 of 47.7. They are now 30 and 48.
- **The PP fold is real and slightly better.** BA bias −5.26 → **−4.98 m²/ha**, TPH MAE 139.6 →
  117.2, on 25 intervals that previously ran as MSdk.
- **What it exposes.** PP, MS, and ESSF are not on the V3 path — `becset.f` keeps `LV2ATV` true for
  them. PP's stands barely grow because of it, which is the −5 m²/ha above. The support matrix now
  says "V2 path" for those zones instead of "V3 via defaults".

The engine moves to **`fresh-fvsbc-pyfvs 0.4.6`** (W5–W14). Install:

```
pip install "fresh-fvsbc[fvs]==0.29.0"
```

## Gaps that remain

- PP needs the V3 wiring W5–W9 gave the other zones before it can be calibrated; it is V2 today.
- MS and ESSF keep the `MSdk/01` default for unmapped series; the substitution is recorded in
  provenance.
- No A/B support cells; every forested zone is an unsigned **C** pilot.
- `SBSmc2` over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal.
- Disturbance calibration is not done.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.28.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.27.0

- **BEC substitution is recorded, not hidden.** For a site series outside the V3 zones that the
  variant has no habitat mapping for, `becset.f` keeps the requested label and switches the
  recalibration to `MSdk/01`. The `STDINFO` echo still shows the requested code, so nothing caught
  it. `Provenance.bec_substitution` now carries `(requested, engine)`, and the record writes it as
  `{"requested": ..., "engine": ...}` with `null` when the run kept its BEC.
- **Measured reach.** `PPxh2`, `PPxh`, `MSdm1`, and `ESSFdk2` all run as `MSdk/01`; the V3 zones
  (ICH, IDF, SBS, SBPS, BWBS, CWH, MH, CDF) return before that table and are unchanged.
- **Support reasons say so.** PP, MS, and ESSF name their mapped site series and state that an
  unmapped series is modelled as `MSdk/01`.
- **Nothing is refused.** The W2 zone prototype gives these zones a default habitat on purpose; the
  record makes the choice visible to a caller who wants strict zone fidelity.

The engine stays **`fresh-fvsbc-pyfvs 0.4.5`** (W5–W12); this release is wrapper-side. Install:

```
pip install "fresh-fvsbc[fvs]==0.28.0"
```

## Gaps that remain

- PP and MS have only 11 mapped site-series labels in total, so a zone calibration cannot start
  until the zone's own series map to its habitat. A PP maximum-basal-area fix is prepared and
  unshipped because a substituted run never reaches the PP caps.
- No A/B support cells; every forested zone is an unsigned **C** pilot.
- `SBSmc2` now over-predicts at high basal area (+20 m²/ha across ten intervals).
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal.
- Disturbance calibration is not done.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.27.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.26.0

- **SBS gets a maximum basal area per subzone.** The variant had one flat 55 m²/ha cap for all of
  SBS, while every subzone's measured p99 is 58–75. Ordinary stands therefore sat near the cap and a
  share of their growth was booked as mortality. The caps now follow the measured p99, the same
  convention CWH, CDF, and MH already use.
- **The SBS fold improves.** Held-out BA bias moves from −2.53 to **−1.21 m²/ha** and the training
  fold from −1.19 to **+0.38**. MAE is essentially unchanged (6.12 → 6.17 test, 7.97 → 8.10 train):
  the caps correct bias, not accuracy.
- **No bundle moved.** `d7-sbs-bundle.json` still carries `MORTMULT 2`.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.5`** (W5–W12). Install:

```
pip install "fresh-fvsbc[fvs]==0.27.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- `SBSmc2` is still about −34 m²/ha on its held-out intervals; that is a growth/mortality gap, not a
  cap gap.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site.
- PPxh2's cap of 21 m²/ha binds for almost every PP interval; PP is unsigned and uncalibrated.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal.
- Disturbance calibration is not done.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.26.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.25.0

- **Tree counts keep their decimals.** The wrapper wrote `tree_count` under the variant's compiled
  `F6.0`, so a PSP expansion factor of 2.47 became 2 and a dense stand started up to 19% below its
  measured basal area. The wrapper now declares `TREEFMT` with `F6.2` (same width, same layout), and
  a real CDFmm interval starts at 111 m²/ha against 112.5 measured instead of 90.
- **Every zone fold re-run.** CDF's held-out BA bias at `BAIMULT 8` moves from −16.1 to **−5.1**
  m²/ha; CWH holds `BAIMULT 8` with held-out bias **+0.15** and MAE **4.01**; MH's held-out bias
  improves to **+1.47**. SBPS and SBS stay on `MORTMULT 2` with no BAIMULT. No bundle moved.
- **A wrong conclusion corrected.** Part of what read as a coastal growth gap was lost density, not
  a growth problem. The CDF dense-stand gap is smaller than the W10 note recorded, and the remaining
  bias there is genuine high-BA mortality error.

The engine stays **`fresh-fvsbc-pyfvs 0.4.4`** (W5–W11); this release is wrapper-side. Install:

```
pip install "fresh-fvsbc[fvs]==0.26.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- CDF dense stands still lose about 5 m²/ha on the held-out site; SBS holds a −6 m²/ha bias with a
  large MAE.
- MH and CDF keep the coastal large-tree donor outside HW/BG and FD/AT.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal.
- Disturbance calibration is not done.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.25.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.24.0

- **CWH large-tree height growth is fitted, not borrowed.** Six single-species height-growth blocks
  now lead the `LTHG` table, so a CWH stand matches them before the ICH/IDF site rows it used to
  borrow: hemlock, Douglas-fir, amabilis fir, spruce, red alder, and lodgepole pine.
- **Dominant trees were growing 20–45% faster than the donor allowed.** On 209,902 dominant and
  codominant CWH pairs, the donor predicts 1.71 m per decade for hemlock against 2.45 observed, and
  1.47 against 2.64 for spruce. The fitted rows bring the held-out bias on those pairs from −0.75 to
  −0.15 m (hemlock), −1.25 to −0.28 m (spruce), and −0.54 to −0.15 m (Douglas-fir).
- **CW keeps the donor deliberately.** Fitting cedar halved tall-cedar height growth on a real
  CWHdm interval and cost stand volume; the donor is 4% low on dominants, so it stays.
- **Stand level is neutral, as expected.** Over 246 CWH intervals, mean BA bias moves −4.184 →
  −4.176 m²/ha and volume −105.27 → −105.55 m³/ha (−0.04% of the 712 m³/ha observed mean). Height
  growth is a small part of standing volume over 5–16-year intervals.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.4`** (W5–W11). Install:

```
pip install "fresh-fvsbc[fvs]==0.25.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- CWH small-tree growth and mortality are still donors; the CW height row is still a donor.
- The fitted CWH height rows still under-predict the tallest trees (about 1.2 m versus 1.7 m per
  decade at a 40 m hemlock); the variant's quadratic taper cannot fit both ends.
- MH and CDF keep the coastal large-tree donor outside HW/BG and FD/AT.
- CDF dense-stand growth is under-predicted by 15–20 m²/ha on its held-out sites.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal.
- Disturbance calibration is not done.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.24.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.23.0

- **MH and CDF get their own large-tree diameter rows.** W9 wired both zones onto the fitted coastal
  (CWH) rows as a donor. W10 fits the four species with enough pairs from the zones' own data:
  mountain hemlock (HW, n=536), amabilis fir (BG, n=358), coastal Douglas-fir (FD, n=3,642), and red
  alder (AT, n=593). Every other MH/CDF species keeps the coastal donor.
- **Why it matters.** The donor was visibly wrong: mountain hemlock grows ~40% slower than the
  coastal hemlock row predicts, and coastal Douglas-fir ~45% faster than the CWH Douglas-fir row.
- **Held-out evidence, same folds, donor vs own.** MH: held-out BA bias +2.47 → **+1.81**, MAE
  2.47 → **1.81**. CDF: −16.12 → **−15.87**, MAE 17.07 → **16.07**. `BAIMULT 8` is unchanged in both
  bundles.
- **CDF's dense stands remain biased.** The CDF held-out sites are high-density CDFmm stands; both
  builds under-predict them by 15–20 m²/ha. That is a mortality/height gap, not a diameter-growth-row
  gap, and it stays open.

The engine moves to **`fresh-fvsbc-pyfvs 0.4.3`** (W5–W10). Install:

```
pip install "fresh-fvsbc[fvs]==0.24.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- CWH small-tree growth, large-tree height, and part of mortality are donors; MH/CDF keep the
  coastal donor for the species outside HW/BG and FD/AT.
- CDF dense-stand growth is under-predicted by 15–20 m²/ha on its held-out sites.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal, and the
  scale must be refit if the growth/mortality engine changes.
- Disturbance calibration is not done: fire severity, consumption, and harvest response need BC
  validation data.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.23.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator.

Pre-1.0, and the public API can change.

## What changed since 0.22.0

- **Recruitment v1.** A BC-wide `ESTAB` model: 2,255 mean annual rates by BEC × all fifteen species
  × initial-BA bin, in `recruitment-bc-v1-bundle.json`. New trees are the trees present at the second
  visit whose tree number was absent at the first. `recruitment_table`/`fit_rates` now carry all
  fifteen species.
- **The year-0 fix.** `estab_keyword` skips the inventory year for a multi-cycle projection and
  spreads the same total TPH over cycles 2..N; establishment at year 0 was re-selecting FVS's sample
  trees. Single-cycle `ESTAB` keeps the old behaviour and is not the validated path.
- **Held-out recruitment evidence.** Data model: 416 observed new TPH vs 388 predicted (−6.8%,
  corr 0.33). Through three FVS cycles, scale 1.0 is +26% TPH; the train-fit **scale 0.4** is
  **+1.3% TPH** on the held-out sites.
- **The multi-scale dataset.** `fresh_fvsbc.dataset.build_dataset(manifest, out_dir)` writes
  `runs`, `stands`, `trees`, `neighbourhoods`, `events`, and `landscape`, plus every pass-through
  table named in the manifest and a `dataset.json` with the source hash and schema. **BEC is the
  unit**; TSA is descriptive. Support travels in `runs.support`.
- **Events and disturbances as data.** Cut and mortality normalise into `events`; `FMIN`/`THINBBA`
  schedules are expressible as nested manifest keywords; a 20-stand Dawson pilot produced 95 events
  and the full disturbance set. Parquet is written beside CSV when `pyarrow` is present.

The engine remains **`fresh-fvsbc-pyfvs 0.4.2`** (W5–W9). Install:

```
pip install "fresh-fvsbc[fvs]==0.23.0"
```

## Gaps that remain

- No A/B support cells; every forested zone is an unsigned **C** pilot.
- CWH small-tree growth, large-tree height, and part of mortality are donors; MH/CDF large-tree rows
  are coastal donors.
- Recruitment is a mean-rate model; it has no QMD bin, seed year, climate, or dispersal, and the
  scale must be refit if the growth/mortality engine changes.
- Disturbance calibration is not done: fire severity, consumption, and harvest response need BC
  validation data.
- The dataset has no whole-TSA run, spatial neighbourhood geometry, SQLite writer, or DOI yet.

## fresh-fvsbc 0.22.0

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.21.4

- **BWBS runs V3, with fitted growth and mortality (W5).** Small-tree height entries fitted from
  same-tree PSP pairs; large-tree diameter entries, the missing site-series row, and the mortality
  entry that a missing BWBS string had turned into complete mortality (`RIP=99`). Held-out Dawson
  fold: BA **+2.33 m2/ha (+4.3%)**, TPH **+0.2%**. The young and mature checks pass.
- **SBS and SBPS large trees grow on V3 (W6/W7).** `SSKONST` held only ICH/IDF, so SBS and SBPS
  large-tree DG was zero. SBS is −2.66 with the D7 bundle; SBPS needed its own fitted rows and is
  **+2.01** with `MORTMULT 2`. W6's zero-intercept SBPS row was rejected after it overflowed to BA
  53,188.
- **CWH, MH, and CDF run V3 (W8/W9).** CWH has fitted large-tree DG for ten species and `BAIMULT 8`
  (**+0.31** held out); MH and CDF use the coastal donor rows (`BAIMULT 8`, **+2.47** and **−2.05**).
  Their V2 bundles are superseded.
- **Support is data, not prose.** `provenance.json` carries a `support` array per species with a tier:
  **A** fitted/validated, **B** donor/validated, **C** provisional, **D** unsupported, **X** out of
  scope. Every forested zone is C today; CMA is X by decision; no cell is A or B until a signed review.
- **CMA is out of scope.** Two sites and six intervals, both at `BAMAX`, in a non-forested zone. It is
  removed from the calibration backlog and graded X.
- **Disturbance wiring is validated on a calibrated zone.** Fire and removal write mortality, snag,
  DWD, fuels, potfire, consumption, carbon, cut, and attribute tables, and leave a live, growing
  residual. This is wiring, not a disturbance calibration.

The engine wheel moves to **`fresh-fvsbc-pyfvs 0.4.2`**, which applies W5–W9. Install:

```
pip install "fresh-fvsbc[fvs]==0.22.0"
```

## Gaps that remain

- **No A or B cells.** Every forested zone is an unsigned C pilot; the only route to A/B is a signed
  review.
- **CWH small-tree growth, large-tree height, and part of mortality are donors**; MH and CDF
  large-tree DG is the CWH donor. Fitting them from each zone's pairs is the next refinement.
- **Recruitment** is still the ad-hoc Dawson table; a year-0 `ESTAB` distorts the sample and the
  multi-cycle harness has not been run.
- **Disturbance calibration** is not done: fire severity, consumption, and harvest response need BC
  validation data.
- **The multi-scale dataset** (schema, manifest-driven orchestration, tree-through-landscape pilot)
  is not built.

## fresh-fvsbc 0.21.4

A Python wrapper for the BC variant of the Forest Vegetation Simulator. It writes the FVS-BC tree
list, validates a keyword set, runs a case, reads the outputs back, and records the provenance of every
run.

Pre-1.0, and the public API can change. The gaps that remain are listed at the end.

## What changed since 0.21.3

- **The wrapper accepts the five prototype zones.** `CWH`, `CDF`, `BWBS`, `CMA`, and `MH` join the
  accepted BEC grammar, along with the subzone tokens `DS`, `MS`, `VH`, `VM`, and `WS`. A case in one
  of those zones now reaches the W2.5 extension parser instead of being refused by the wrapper.
- **The `fvs` extra remains `fresh-fvsbc-pyfvs 0.4.1`.** That wheel already carries the five-zone
  parser; no new extension build is required for this change.
- **Calibration is not implied.** IDFdk and SBS have unsigned pilot models; CWH is a screening result
  with a failing BA plane; the five-zone wrapper support is not a certification.
- **Install:** `pip install "fresh-fvsbc[fvs]==0.21.4"`.

## What changed since 0.21.2

- **The `fvs` extra moves to `fresh-fvsbc-pyfvs 0.4.1`.** The new wheel fixes the SBPS small-tree
  overflow: `REGENT` selected the SBS height form with `INDEX(BEC%Zone,'SBS')`, which does not match
  `SBPS`; SBPS therefore took the exponential form with SBS-form coefficients and produced an
  infinite small-tree diameter. The five condition tests now accept `SBS` or `SBPS`.

- **Corrected SBPS baseline:** the four SBPS intervals in the D5 sample now end at 28–53 m²/ha
  rather than 10–457,348. The catastrophe is gone; the residuals are still above the observed
  values and are D7 calibration targets, not a calibration claim.

- **Install:** `pip install "fresh-fvsbc[fvs]==0.21.3"`. The `fvs` extra pins
  `fresh-fvsbc-pyfvs==0.4.1`.

## What changed since 0.21.1

- **The `fvs` extra moves to `fresh-fvsbc-pyfvs 0.3.13`.** The new wheel fixes a pre-existing BEC
  resolver bug: `KAM` + `MS` contains `MM` across the region/zone boundary, so `MSxk1` resolved as
  `MSmm`. The fourth build-time patch anchors the subzone token after the zone. The 19 W2.3
  subzones still resolve, and the `KAM`/`MS` regression is in the CI extension job.

- **W3.1 baseline:** the supported-domain baseline now compares **108 intervals with 0 skipped**,
  against 89 compared and 19 skipped in W1.4. The aggregate residual tables and
  `notes/reference/calibration/baseline_v3.md` are in the repository. This is a baseline, not a
  calibration.

- **Install:** `pip install "fresh-fvsbc[fvs]==0.21.2"`. The `fvs` extra pins
  `fresh-fvsbc-pyfvs==0.3.13`.

## What changed since 0.21.0

- **The `fvs` extra now installs `six`.** `fresh-fvsbc-pyfvs 0.3.12` imports `six` but its wheel
  metadata does not declare it, so a clean `pip install "fresh-fvsbc[fvs]==0.21.0"` installed the
  extension and `list_variants()` worked, while a real run failed at `from pyfvs import fvs` with
  `ModuleNotFoundError: six`. The `fvs` extra now names `six>=1.16`; the pin remains
  `fresh-fvsbc-pyfvs==0.3.12`. The 0.21.0 content is unchanged.

- **Packaging test:** `tests/test_fresh_fvsbc_package.py` asserts the `fvs` extra carries `six`, so the
  missing runtime dependency cannot return silently.

## What changed since 0.20.0

- **The web surface now draws the stand.** The `visuals` panel serves a 2D schematic map and a 3D
  three.js viewer over `FVS_TreeList_Metric` and `FVS_CutList_Metric`, with a year selector, species
  colours, DBH-sized trees, cut marking, hover values, pan/zoom, and orbit/zoom. FVS writes no x/y, so
  the layout is schematic; the 3D ground is flat because the per-tree tables carry no terrain. three.js
  is vendored, and the viewer loads only when chosen: no CDN, no Node build. The endpoint is
  `GET /api/runs/{id}/visuals?year=`.

- **The BC variant resolves 19 more supported-zone subzones.** `fresh-fvsbc-pyfvs 0.3.12` carries the
  W2.3 patch: ten subzone tokens, the `HABTYP` loop fix, and provisional maximum-basal-area cases for
  `ESSFdh1`, `ESSFdv1`, `ESSFmv`–`ESSFmv4`, `ESSFvc`, `ESSFwh1`, `ESSFwv`, `ESSFxv2`, `ICHvc`,
  `ICHxw`, `IDFdh`, `IDFxw`, `IDFxx2`, `MSxv`, `SBSdh1`, and `SBSun`. **The defaults are PSP p99
  values, not calibrated parameters.** `run_case` now compares the run's `STDINFO BEC=` echo with the
  requested code and refuses a silent `ICHmw2/01` fallback.

- **The calibration foundation is in place, but nothing is calibrated.** The release carries the
  validated BEC input, the provincial PSP ingest, the calibration-bundle contract, the uncalibrated
  baseline and envelope, the Knife Creek protocol/replication, and the 12-domain design (10
  calibration-ready, 2 validation-only). No parameter has been fitted and no domain has a certificate;
  W3–W5 are the next steps.

- **The five prototype zones.** The W2.2 audit recorded `CWH`, `CDF`, `BWBS`, `CMA`, and `MH` as
  **no-go without a parameter source**. W5–W9 have since put BWBS, CWH, MH, and CDF on calibrated
  paths. **`CMA` is a documented non-target: out of scope by decision, because it is not a forested
  BEC zone** (`notes/reference/cma-out-of-scope.md`).

- **Install:** `pip install "fresh-fvsbc[fvs]==0.21.0"`. The `fvs` extra pins
  `fresh-fvsbc-pyfvs==0.3.12`; if that wheel is not on your index yet, use the source recipe in
  `docs/installation.rst`. `fresh-fvsbc-pyfvs` is uploaded before the `v0.21.0` tag.

- **Claim boundary:** the 19 subzone defaults are placeholders, the five zones are not represented, and
  there is no calibration certificate. A number from this release is FVS-BC's own output with the
  existing defaults; it is not a calibrated growth-and-yield claim.

## What changed since 0.19.1

- **There is a wheel, and installing it needs no Fortran toolchain.** Until now, using this package
  meant owning `gfortran`, `meson`, `ninja` and two patch sets — which is the whole distance between
  "our lab uses it" and "another lab can".

  Each release carries a self-contained wheel for the pinned fork, built in `manylinux_2_28` for
  Python 3.10 to 3.13. `auditwheel repair` bundles `libgfortran` into it, so nothing has to be
  installed but the wheel:

  ```console
  $ pip install "fresh-fvsbc[fvs]"
  ```

  Both distributions are on PyPI: `fresh-fvsbc` and `fresh-fvsbc-pyfvs`.

  **Linux x86_64, glibc 2.28 or later** — RHEL 8+, Ubuntu 20.04+, Debian 10+, every current cluster.
  `docs/installation.rst` is the page, including what to do when there is no wheel for your platform.

- **The fork's distribution is renamed `fresh-fvsbc-pyfvs`.** It installs the same `pyfvs` import
  package as upstream, so a distinct distribution name is the only thing that stops the two being
  installed over each other. `fresh-fvsbc[fvs]` names it as an extra. **Do not install upstream
  `pyfvs` in the same environment** — pip will not stop you.

## What changed since 0.19.0

- **The web page no longer understates how much is verified.** Its badge read **"4 of 31 tables
  verified"** — the four the official dump carries — while **28** have been checked against a standalone
  `FVSbc`. A lab member reading the page to decide how far to trust the tool saw a number seven times too
  low.

  `GET /api/oracle` now reports both counts and both table lists, the per-table `oracle` flag means
  *checked against a reference* rather than *in the dump*, and the badge leads with the standalone count.
  Found by running the service against `0.19.0` and reading what it said.

## What changed since 0.18.0

- **`ESTAB`, `MISTOE` and `RDIN` are blocks of keywords, not raw lines.** A **breaking change** for
  anyone who built them with `lines=`, and the same defect `FMIN` had: a hand-spaced field is read as a
  different number and FVS reports nothing. It is not hypothetical — this line reached `MISIN` as
  species **PW**, proportion **0.50**, neither of which was written:

  ```
  MISTPINF        0        1       0.5
  ```

  ```python
  Keyword("RDIN", nested=(Keyword("RRINIT"), Keyword("RRDOUT")))
  Keyword("ESTAB", nested=(Keyword("PLANT", ("0", "FD", "3680", "90")),))
  ```

  Each body is checked against its own reader's table — `esin.f`'s 28, `misin.f`'s 27, `rdinie.f`'s
  40 — and a keyword from one of those tables written outside its block is refused. A name that is also
  a top-level keyword, `ESTAB` or `COMMENT`, stays valid there. From the shell:
  `--block "RDIN|RRINIT|RRDOUT"`.

  `LINES_KEYWORDS` is now only the three whose body really is text: `COMMENT`, `COMPUTE`, `DATABASE`.

## What changed since 0.17.0

- **`FVS_InvReference` is written, and it never was before.** The extension is driven by PyFVS's
  `src/api/fvs_step.f90`, an *extraction* of `fvs.f`'s initialisation. It called `STATS` and **omitted
  the `CALL DBSREFERENCE`** that follows it, and the original `fvs_` is dead code in the extension — so
  the writer was compiled in, linked, and never called. The build recipe's PyFVS patch set now carries
  the missing call.

  It needs no keyword: every run writes it, one row per species, with the site indices and volume
  equations FVS used. It now **matches a standalone `FVSbc` value for value**, verified from a clean
  clone of the pinned fork.

- **Twenty-eight of the thirty-one exposed tables match a standalone `FVSbc` value for value.**
  `FVS_Error` is the only one that is not comparable, and it is not a defect: FVS writes it only when it
  logs something.

  This is a **build-recipe change**. An environment built from an earlier recipe still has the defect
  and should be rebuilt.

## What changed since 0.16.1

- **There is now a recipe for every table.** Naming a table's option in a `DATABASE` block is **never
  enough on its own**: the option is accepted whether or not the run does what the writer reports on,
  and the table is then simply absent — the projection succeeds, the database is written, and nothing
  says the table is missing. The new :doc:`reference/table-recipes` page gives the second thing each
  one needs. Some of them are not obvious:

  - a **removal** for the cut list and the after-treatment tree list;
  - a **fire** for mortality and for consumption;
  - **more than one plot** for the stand statistics, which are the distribution among sample points;
  - an **infection** through the damage columns for the four dwarf-mistletoe tables, and `NEWSPRED` for
    the fourth;
  - a **`PLANT` line carrying stems per acre** for the regeneration tables;
  - an **`RDIN` block with `RRINIT` and `RRDOUT`** for root disease. Earlier revisions of the docs
    recorded its required parameters as undetermined; they are those two, and both tables are written
    and match.

- **Twenty-seven of the thirty-one exposed tables are checked against a standalone `FVSbc`** built from
  the same source, and match it **value for value** — including every per-tree row. That is up from
  thirteen, and from four before this stretch.

- **One table is not checked, and the reason is on the record.** `FVS_Regen_SitePrep`'s `PcntNone`,
  `PcntMech` and `PcntBurn` are the site-preparation allocation across plots, drawn from a random
  distribution. They differ from the standalone's, and the difference is **not in this package**: both
  runs agree on every observable input, this package's run is deterministic across seeds, and the writer
  is a pass-through. What is left is a hypothesis about the two drivers' draw streams, and
  `notes/triage.md` says so rather than guessing.

## What changed since 0.16.0

- **The command prints the keyword set's warnings.** `0.16.0` added a warning about the fire-model
  block ordering, and **nothing printed it**: the run's result carries FVS's warnings from `FVS_Error`,
  and the validator's warnings had no route out of the run. The fix shipped and reached nobody who uses
  the command — which is how most people use it.

  ```text
  fresh-fvsbc: warning: an FMIN block that asks for FUELOUT or POTFIRE must precede INVYEAR: ...
  ```

  Found by verifying `0.16.0` from a clean checkout, running the case its own notes describe.

## What changed since 0.15.1

- **The fuels and potfire tables were silently not written, and now they are.** `FUELOUT` and
  `POTFIRE` set `IFLALB` and `IPFLMB` to the inventory year when they are read, and `fmdout.f` and
  `fmpofl.f` treat **any positive value as "suppress this report"**. An `FMIN` block read after
  `INVYEAR` therefore switched its own reports off: the run succeeded and `FVS_Fuels_Metric`,
  `FVS_PotFire_Metric` and `FVS_PotFire_Cond_Metric` were simply absent.

  **The official case never hits it** — its inventory year arrives from the input database, so the year
  is still zero when the block is read — which is why it has gone unnoticed upstream and would have hit
  every user of this package, which writes the year as a keyword.

  The validator now **warns**, naming both keywords. This is a change to what `validate_keywords`
  returns: a set that puts the block after `INVYEAR` now carries a warning where it carried none.

- **Thirteen exposed tables are checked against FVS's own writer**, up from nine:
  `FVS_Carbon_Metric`, `FVS_Consumption_Metric`, `FVS_Down_Wood_Cov_Metric`,
  `FVS_Down_Wood_Vol_Metric`, `FVS_Fuels_Metric`, `FVS_Hrv_Carbon`, `FVS_PotFire_Cond_Metric`,
  `FVS_PotFire_Metric`, `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric`, `FVS_StrClass_Metric`,
  `FVS_Summary_Metric` and `FVS_TreeList_Metric` all match a standalone `FVSbc` **value for value**.
  To use them, put the fire-model block before `INVYEAR`:

  ```console
  $ fresh-fvsbc population.json --directory run \
      --block "FMIN|FUELOUT=2|POTFIRE=2|CARBREPT=2" \
      --keyword INVYEAR=2020 ...
  ```

## What changed since 0.15.0

- **A refused keyword set is reported, not raised.** `validate_keywords` raises `KeywordOrderError` for
  a `DATABASE` block after the stand setup — the exact mistake the check exists to catch — and the
  command did not list it among its input errors, so Python printed a **traceback over the message**.
  It has been that way since the order check was added, and every release before this one has it. The
  same applied to a fire-model keyword written outside its `FMIN` block.

  ```text
  fresh-fvsbc: a DATABASE block must precede the stand setup; FVS refuses it later with
  'KEYWORD ENTERED IS USED IN WRONG CONTEXT'. The official case puts it first
  ```

  Found by verifying `0.15.0` from a clean checkout, running the refusal the release notes describe.

## What changed since 0.14.0

- **`FMIN` holds keywords, not raw lines.** This is a **breaking change** for anyone who built the
  fire-model block with `lines=`. A raw line let the caller space FVS's ten-column fields by hand,
  and a mis-spaced field is **not refused — it is read as a different number**:
  `SNAGCLAS  0.0   10.0  20.0  40.0` reaches FVS as class 2 `20.0` and class 3 `0.0`, with no error.
  The block now takes `Keyword` values and the shared writer spaces them, the body is checked against
  `fmin.f`'s own **fifty-five** keywords, a fire-model keyword outside the block is refused because
  FVS would ignore it, and `FUELMODL` and `DEFULMOD` take their one supplemental record. From the
  shell: `--block "FMIN|SNAGOUT=1|SNAGSUM=2|CARBREPT=2"`.
- **Nine tables are now checked against FVS's own writer.** The oracle comparison is attributed — the
  `0 of 5` was never source drift — and it reports what it can prove:
  `FVS_Carbon_Metric`, `FVS_Down_Wood_Cov_Metric`, `FVS_Down_Wood_Vol_Metric`, `FVS_Hrv_Carbon`,
  `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric`, `FVS_StrClass_Metric`, `FVS_Summary_Metric` and
  `FVS_TreeList_Metric` all match a standalone `FVSbc` **value for value**, including all 3,996
  per-tree rows. Before this release, four tables had a check.
- **The comparison reports what it cannot compare, and why.** It counts matches, explained differences
  and out-of-reach tables apart, so a table only one side writes is never read as agreement. Two are
  out of reach and named: `FVS_Error` is written only when FVS logs something, and `FVS_InvReference`
  is written by the standalone on every run and never by this package's build, for a cause that is not
  established.

## What changed since 0.13.0

- **A run that logs nothing is no longer reported as failed.** FVS writes `FVS_Error` **only when it has
  something to log**, and the reader treated an absent table as a failure to read — on the premise, stated
  in the output contract, that the extension writes it on every run. **That premise was false.** A
  999-tree single-plot case raised no warning, wrote no such table, and the package reported a perfectly
  good run as failed. `read_errors` now answers an absent table with an empty frame of its columns, so
  silence reads as a clean run.
- **The oracle harness reads a run's trees.** The standalone `FVSbc` now gets them through a
  `DATABASE ... DSNin ... TreeSQL` input database built from the run's own tree list and keywords: **999
  trees load and it writes 3,996 per-tree rows**. The inline `TREEDATA` route is dead — its field 1 is a
  file reference number, `2` for an external file and `15` for inline records, and neither placement works.
- **The comparison runs, and it is not yet an oracle.** It reports **0 of 5 tables agreeing** and the
  differences are **unattributed**: the two builds come from different source revisions — the pin
  `e95172b`/`ef5fa847` against upstream `28fda8ed`, because the pin's standalone will not build (ADR 0008)
  — and that alone can move numbers. `notes/triage.md` says so rather than presenting a tool that runs as
  a check that passes.

## What changed since 0.12.0

- **`THINQFA` is usable.** The keyword reads **one supplemental record** whose first column names the units
  of its residual-density target — `0` basal area per acre, `1` trees per acre, `2` stand density index —
  and the wrapper could not write it. The command now takes it after a semicolon:
  `--keyword THINQFA=1,0,24,0,1.4,2,100;1`. **A set without the record is refused rather than written**,
  because FVS would read the next keyword as the units record and the run would be wrong without saying so.
  The source is what settles it: `cuts.f` reads `PRMS(1..6)` from the six fields after the year, which
  leaves `QFATAR = INT(PRMS(7))` for that record.
- **The service works behind the JupyterHub proxy.** The dev container is **pre-authenticated** — JupyterHub
  authenticates the browser and forwards a local port under
  `/jupyterhub32/user/<name>/codeserver/proxy/<port>/` — so the service must bind off loopback and answer
  **under the prefix**. A middleware strips the prefix when the request carries it, which is what JupyterHub
  does, and leaves a request that does not alone. Verified live on `0.0.0.0`: both forms 200, the assets
  200, the container's own address 200. **Two wrong answers preceded it**: FastAPI's deprecated `root_path`
  answered both forms, and uvicorn's `root_path` answered neither.
- **`scripts/oracle_compare.py`**, a first cut at checking a run against the standalone `FVSbc`. It renders a
  standalone-runnable keyword file from a run directory, runs the binary and compares every exposed table.
  **The tree handoff is unfinished**: the standalone reads inline `TREEDATA` records as keywords and writes
  1001 `FVS_Error` rows, where the official case feeds trees through a `DATABASE ... DSNin ... TreeSQL`
  block. The triage records it.

## What changed since 0.11.0

- **There is a browser surface.** `pip install 'fresh-fvsbc[web]'` then `fresh-fvsbc web --runs DIR`. It is
  **a reader over the artefacts a run already wrote** — `run.key`, `run.tre`, `FVSOut.db`, `run.sum`,
  `summary.csv`, `provenance.json`, `variants.json` — and it starts a run by invoking the CLI in a
  subprocess, never by importing the Fortran extension. FastAPI behind an optional extra, a **vanilla ES
  module shell with no build step**, and four validated **skins** (`analyst`, `carbon`, `reviewer`,
  `tables`) whose unknown panels and actions are refused by name.
- **The surface marks which tables are verified.** `ORACLE_TABLES` is now a fact in `outputs.py`: four of
  the 31 exposed tables are checked against FVS's own database dump and 27 are not. `GET /api/oracle`
  reports the counts, every table record carries `oracle`, and the front end says so above the rows. A
  number whose provenance is unchecked must not look like one whose provenance is checked.
- **A real BC case ran through it, and broke four things.** The 2022 workshop bundle's own
  `FVS-BC.Stand.Structure.Data.db` — one stand, 1540 trees, site index FD 15, inventory year 2020 — found:
  **one plot holds at most 999 trees** (BC's record shares columns 1 to 4 between the plot and the tree
  number), so a larger stand is now refused **by name with the reason**; a **failed child was reported as
  running forever**, and is now reported `failed` with its log at `GET /api/runs/{id}/log`; a run that died
  before writing `run.key` was **invisible**, and a directory holding the service's log is now discovered;
  and the start request **grouped blocks after keywords**, which the `DATABASE`-first rule refuses — the
  list is now one ordered sequence.
- **A 999-tree subset of that real stand writes 7 tables through the surface**, including 3,996 per-tree
  rows, with the oracle flag marking one of the seven as verified and six as not.

## What changed since 0.10.0

- **Two more tables, so the reader exposes thirty-one of 44.** `FVS_Regen_Tally_Metric` and
  `FVS_Regen_SitePrep`, from an `ESTAB` block.
- **`ESTAB` is a block, and its `NATURAL` line needs the stems per acre.** `esin.f` reports error 4 and
  drops the **whole keyword set** when that field is zero — which is why a bare `ESTAB` was refused in every
  earlier attempt.
- **`FVS_CalibStats` is deliberately not exposed.** `CALBSTDB` creates the table on every run and it carries
  **nothing** unless the run is calibrated. A table that is always empty does not belong in the public API,
  and `keywords.rst` says so.
- **The table work is finished, and the record says why.** `notes/reference/table-reachability.md` classifies
  all 44 with a verdict each: thirty-one exposed, and thirteen that are not, of which eight are candidates
  and five have no call site at all. Of the eight, six are blocked by something this project does not have —
  an external climate attribute file, the FIA variant, a calibrated run, a bark-beetle specification, or the
  sprout model — and one has a gate no valid input can satisfy.

## What changed since 0.9.0

- **Two more tables, so the reader exposes thirty-one of 44.** `FVS_Regen_Tally_Metric` and
  `FVS_Regen_SitePrep`, from an `ESTAB` block.
- **`ESTAB` is a block, and its `NATURAL` line needs the stems per acre.** `esin.f` refuses the line —
  and the whole keyword set with it — when that field is zero, which is why a bare `ESTAB` was refused in
  every earlier attempt.
- **`FVS_CalibStats` is deliberately not exposed.** The table is created on every run and carries **nothing**
  unless the run is calibrated, and this package does not calibrate. Exposing it would put an always-empty
  table in the public API.

- **Eight more tables are readable, and the reader exposes twenty-nine of 44.** In order: `FVS_Stats_Stand`,
  `FVS_Mortality_Metric`, the four dwarf-mistletoe tables, two of the three root-disease tables, and
  `FVS_CanProfile`.
- **Four behaviours this project had called unknown were each one line of the source.** `P30` ran
  experiments, they did not fire, and it recorded a conclusion about FVS. That was wrong, and the
  correction is the substance of this release:
  - **`DESIGN`'s fourth field is the inventory point count** (`initre.f:798`). Every run here passed `1`,
    which is why `FVS_Stats_Stand` — the distribution among sample points — could never be computed.
  - **`MORTREPT` sets `IFMMRB = -1`** (`fmin.f:1372`), which is what `fmfout.f:294` gates on. `MORTREDB`
    alone writes nothing. The burn report's `BURNREPT` sets its equivalent to the inventory year, which the
    same gate rejects — two options that look identical and behave oppositely.
  - **Damage codes 30 to 34 are the mistletoe rating** (`misdam.f:76`), with the severity as the Hawksworth
    rating. Code 21, an earlier guess, registers as no mistletoe at all.
  - **`MISTPRT` and `NEWSPRED` gate the last two DM tables** (`misprt.f` calls `DBSMIS3` inside
    `IF (PRTMIS)` and `DBSMIS5`/`DBSMIS6` inside `IF (NEWMOD)`), and **`RDIN` refuses the whole set**
    without `RRTINV` or `RRMAN`.
- **`RDIN` is a block**, and it joins the five the model already writes, so a caller can express root
  disease.
- **The fixture was never the constraint.** The adapter already maps one plot per stand, and the tree list
  carries five plot ids when given five stands. Nothing was added to the fixture, because nothing was shown
  to be missing.

## What changed since 0.8.0

- **Four more tables, so the reader exposes twenty-nine of 44.** `FVS_DM_Sz_Sum_Metric`,
  `FVS_DM_TreeList_Metric`, `FVS_RD_Sum_Metric` and `FVS_RD_Det_Metric`. **All four dwarf-mistletoe tables
  and two of the three root-disease tables are now readable.**
- **The two DM tables that stayed away were behind two sub-keywords of the `MISTOE` block.** `misprt.f`
  calls `DBSMIS3` inside `IF (PRTMIS)` and `DBSMIS5`/`DBSMIS6` inside `IF (NEWMOD)`; `MISTPRT` sets the
  first and `NEWSPRED` the second.
- **`RDIN` is a block, and it refuses the whole set without an initialization.** `rdin.f` reports
  "NEITHER TREELIST OR MANUAL INITIALIZATION SPECIFIED" at the block's `END` unless `RRTINV` or `RRMAN` was
  seen; `RRINIT` sets `RRMAN`, and `RRDOUT` adds the detail table.

- **Four more tables, and three questions answered by reading the source instead of guessing.**
  `FVS_Stats_Stand`, `FVS_Mortality_Metric`, `FVS_DM_Spp_Sum_Metric` and `FVS_DM_Stnd_Sum_Metric` join the
  twenty-one, so the reader exposes **twenty-five of 44**.
- **`DESIGN`'s fourth field is the inventory point count.** Every run here passed `1`, so `FVS_Stats_Stand`
  — the distribution among sample points — could not be computed and said so. With `5` it is written. The
  fixture never needed to change; the adapter already maps one plot per stand.
- **`MORTREPT` is what makes the mortality table appear**, because `fmin.f` sets `IFMMRB = -1` for it and
  `fmfout.f` gates the section on `IF (IFMMRB .LT. 0 .AND. IFIRE .GE. 0)`. `MORTREDB` alone is accepted and
  writes nothing. The burn report's `BURNREPT` sets its equivalent to the inventory year, which is why that
  one really is dead — two options that look identical and behave oppositely.
- **A mistletoe rating enters through the damage columns**: `misdam.f` maps damage codes **30 to 34** onto
  the Hawksworth rating, with the severity as the rating. Code 21, an earlier guess, registers as no
  mistletoe at all.
- **The previous release's "the fixture is the binding constraint" was wrong**, and
  `notes/reference/fixture-limits.md` now records the three answers with the lines they come from.

- **One more table, and a claim withdrawn.** `FVS_CanProfile` joins the twenty — the canopy fuels profile by
  height layer, which is the vertical structure a fuel or wildlife model wants — so the reader exposes
  **twenty-one of 44**. Its trigger, `CANFPROF` inside `FMIN`, was a guess in the candidate note and the
  guess was right.
- **"The fixture is the binding constraint" was tested and is mostly wrong.** Three experiments, in
  `notes/reference/fixture-limits.md`: the fixture **already** produces five plots (the tree list carries
  plot ids 1 to 5), yet FVS reports `DISTRIBUTION OF ATTRIBUTES AMONG SAMPLE POINTS CANNOT BE COMPUTED WITH
  ONE SAMPLE POINT`; a five-plot population with **200 trees** under a 100 percent burn still writes no
  mortality table; and `damage1 = 21` does not register as dwarf mistletoe at all. **Nothing was added to
  the fixture**, because nothing was shown to be missing.

- **Six more tables are readable, and the reader exposes twenty of 44.** Two of them close the biggest
  hole the package had: `FVS_TreeList_Metric` and `FVS_CutList_Metric` are its **first per-tree output
  ever** — one row per tree per period, with the FVS, PLANTS and FIA species codes, so a result can be
  joined to anything else. The other four are `FVS_Down_Wood_Cov_Metric`, `FVS_Stats_Species_Metric`,
  `FVS_StrClass_Metric` and `FVS_ATRTList_Metric`.
- **`FVS_StrClass_Metric` carries the structural stage** — the class British Columbia uses for old-growth
  and habitat assessment, and nothing else in the package carried it.
- **An option alone is not enough, and that is now the rule rather than the exception.** The `DATABASE`
  block names the table; a second keyword asks FVS to produce the rows. `TREELIDB` needs `TREELIST`,
  `CUTLIDB` needs `CUTLIST`, `INVSTATS` needs `STATS`, `DWDCVDB` needs `DWDCVOUT`, `STRCLSDB` needs
  `STRCLASS`, `ATRTLIDB` needs `ATRTLIST`. Without the second keyword the option is accepted and writes
  nothing.
- **The attribute list has three failure modes, and all three were hit.** Its writer returns unless it is
  called from `cuts.f`, so it is written only after a cutting operation. A residual above the stand's
  basal area cancels the thinning and writes no table; a removal that takes everything creates the table
  and inserts **nothing**; a **partial** removal — residual zero with half the selected trees taken — is
  what produces rows.
- **FVS spells one column differently in the two per-tree tables**: `CCum` in the tree list and `CCuM` in
  the cut list. The reader does not rename it, and the output contract says so.
- **Two of the six attempted tables resisted, and the reasons are recorded**: `FVS_Mortality_Metric` needs
  a fire that kills trees, and `FVS_Stats_Stand` is the distribution of attributes among sample points and
  the fixture has one.
- **The table classification is mechanical now, and it corrected an earlier note.** A sweep finds each
  table's writer by source mention and counts its call sites: **twenty exposed, 19 with a writer and a
  call site, five with a writer that nothing calls, and none without a writer.** It also showed that
  `0.8.0`'s gap list was wrong to say the dwarf-mistletoe and root-disease writers do not exist — they do,
  as `DBSMIS1` (called from `misprt.f`) and `DBSRD1` (called from `rdpr.f`), and the grep that "proved"
  otherwise searched for names that are not in the source. **The published `0.8.0` body keeps the original
  text**, because a release body is immutable.
- **`notes/reference/table-candidates.md` gives every remaining candidate a cost, a risk and a value**,
  with a proposed order. It is the plan for the other 24 tables, and it is written so it can be checked.

## What changed since 0.7.0

- **The consumption table is readable.** `FVS_Consumption_Metric` joins the thirteen, so the reader
  exposes **fourteen**.
- **It needs a fire, not an option.** A fire in FVS is an *activity*, not a keyword: `FMBURN` looks for
  activity 2506 with `OPFIND`, and the `FMIN` option `SIMFIRE` schedules it. `DBSFMFUEL` is called from
  inside the routine that runs when something burns, so the `DATABASE` option `BURNREDB` alone writes
  nothing. One run reports 22.569 tonnes per hectare consumed and 77.31 percent of the duff.
- **The burn report beside it cannot be exposed.** `FVS_BurnReport_Metric` is written only inside
  `IF (IFMBRB .LT. 0)`, and `IFMBRB` is assigned `9999` at initialisation and the inventory year by
  `BURNREPT` — never negative unless `INVYEAR` is given an invalid negative year, which shifts the whole
  simulation. That is a dead branch in this source, and the pages say so.

## What changed since 0.6.0

- **Two carbon tables are readable.** `FVS_Carbon_Metric` and `FVS_Hrv_Carbon` join the eleven, so the
  reader exposes **thirteen**.
- **The trigger was an option, not a keyword.** `CARBREPT` inside an `FMIN` block is what sets `ICRPTB`
  and lets `fmcrbout.f` reach `DBSFMCRPT`, the carbon writer's only call site. The `DATABASE` option
  `CARBREDB` alone is accepted and writes nothing, which is why the previous release recorded carbon as
  unreachable.
- **A carbon total can be NULL.** `Total_Stand_Carbon` is NULL in a period where one of its components
  is undefined, and the reader returns `NaN` rather than inventing a zero — a zero there is a value, and
  a NULL is the absence of one.

## What changed since 0.5.0

- **Three more tables are readable.** `FVS_Fuels_Metric`, `FVS_PotFire_Metric` and
  `FVS_PotFire_Cond_Metric` join the eight, so the reader exposes **eleven**.
- **`FMIN` is the fourth line block.** `POTFIRE`, `FUELOUT` and `FUELREPT` are **options inside it, not
  keywords**, which is why the model could not express them: with `FMIN` written and a `DATABASE` block
  asking for `FuelsOut`, `FuelReDB` and `PotfirDB`, one run writes all three tables.
- **A record of which of the rest can be written at all**, in `notes/reference/table-reachability.md`.
  It found that carbon's writer has one call site in the fire-carbon report path and the `DATABASE`
  option alone does not reach it, and that the dwarf-mistletoe and root-disease writers **do not exist
  in this source**.

## What changed since 0.4.0

- **`IF` blocks can be written.** A caller can put keywords behind a condition — a thinning schedule, an
  establishment rule, anything FVS reads conditionally:
  `Keyword("IF", (), ("MOD(AGE,60) EQ 0",), (Keyword("THINBBA", ("0", "0.0")),))` renders as the
  condition, `THEN`, the body and `ENDIF`, with an optional `ELSE`.
- **The body is validated**, so an unknown keyword inside a conditional is refused like one outside it.
- **`ALSOTRY` is not modelled**, because no fixture here uses it.

## What changed since 0.3.1

- **The reader exposes eight tables, not four.** `FVS_Down_Wood_Vol_Metric`, `FVS_InvReference`,
  `FVS_SnagDet_Metric` and `FVS_SnagSum_Metric` join `FVS_Cases`, `FVS_Compute`, `FVS_Error` and
  `FVS_Summary_Metric`.
- **Four of them are checked against FVS's own database dump**, which turned out to be CSV with a header
  per table: 160 rows of down wood volume, 848 of snag detail, 160 of snag summary, against the same
  run's rendering. `FVS_InvReference` postdates the 2022 fixture and rests on the schema instead; the
  page says which is which.
- **The table list is corrected: 44 tables, not 33.** The old list was the *base* schema's, and this
  variant builds the *metric* one, so **twenty-four of its names were tables a run here never writes**.
  The list is derived from the schema's four layers with the most specific module winning, and the check
  is the official case's own database: seven tables, all of them in the list.

## The build this release wraps

Read from `src/fresh_fvsbc/provenance.py` and from the built extension:

| | |
| --- | --- |
| PyFVS fork | `UBC-FRESH/PyFVS` at **`e95172b`** |
| FVS source submodule | **`ef5fa847`** |
| Variant list | **`BC`**, status `OK` |
| Patch sets | `pyfvs-patchset`, `fvsbc-patchset`, `w2-subzones` |

The patch sets are banked in `notes/reference/` and are **not pushed to the fork**; ADR 0004, ADR 0006,
and ADR 0013 are the recipe.

## What is verified

- The variant builds from a clean clone at the pin, the three patch sets apply, and `list_variants()`
  reports `BC` as `OK`. **The build is not byte-reproducible** across machines.
- The suite passes where the extension is built; the two skips are the tests that the extension is
  *absent*, and they invert in an environment without it.
- **The 19 W2.3 subzones resolve in the built `0.3.12` wheel**: each echoes its own `STDINFO BEC=` and
  provisional `BAMAX`, writes a database, and the seven existing-zone controls are unchanged.
- **The web visuals panel was exercised against a real 999-tree run** in headless Chromium: the 2D map
  drew 14 live and 65 cut trees, hover returned the tree values, and the 3D canvas rendered with no
  console errors.
- The build agrees with FVS's own oracle on the first official case: zero differing lines across 164
  rows. **The oracle is a 2022 fixture** (`FS2022.4`), and the comparison covers one of the two official
  cases.
- The exposed tables the official dump carries hold its row counts, and a `DATABASE` block placed first
  makes them written.
- A run with `CARBREPT` writes both carbon tables, and the first period carries a non-zero total — 13.6
  tonnes of carbon per hectare on the synthetic stand.
- A run with `SIMFIRE` writes one consumption row, and it carries a non-zero consumption — 22.569 tonnes
  per hectare on the same stand.
- A run with `DESIGN`'s fourth field above one writes `FVS_Stats_Stand`; one with `MORTREPT` and a fire
  writes `FVS_Mortality_Metric`; an infected stand writes all four dwarf-mistletoe tables; and an `RDIN`
  block with `RRINIT` writes the root-disease summary and, with `RRDOUT`, the detail.
- A run with a `TREELIST` request writes the per-tree tables, and the cut list carries the same identity
  columns as the tree list; a run with `STRCLASS` writes the structural stage; a run with `ATRTLIST` and a
  **partial** removal writes the attribute list, and one with no removal writes it empty.
- The command runs a case end to end and exits `0`; `1` and `2` are tested with a faked drive and in a
  subprocess, not by a real failing run.
- The dashboard passes on Python 3.11 and 3.12 in CI.
- The mutation harness catches all **27** mutations in its set. The set is the author's choice.

## Known gaps

Fourteen, each with the reason it is open. `notes/triage.md` gives each a disposition and what would reopen
it.

1. **The reader exposes thirty-one of 44 tables.** The other 13 are classified in
   `notes/reference/table-reachability.md` with a verdict each: eight are candidates, five have a writer that
   nothing calls, and the burn report's gate cannot be satisfied by valid input. **Of the eight candidates,
   six are blocked by something this project does not have** — an external climate attribute file, the FIA
   variant, a calibrated run, a bark-beetle specification, the sprout model — and none is blocked by effort.
2. **One plot holds at most 999 trees.** BC's tree record shares columns 1 to 4 between the plot and the
   tree number, so the writer has three digits. A stand of 1540 trees — which the 2022 workshop's own case
   carries in one plot — is refused by name. Subdividing a stand into plots changes what the statistics
   mean, so it is a modelling decision and not a repair.
3. **The web surface has no authentication of its own, by design.** The dev container supplies it: the
   JupyterHub port proxy authenticates the browser, so the service is deployed with
   `--host 0.0.0.0 --allow-remote --root-path <proxy prefix>` and the proxy is what guards it. The service
   still refuses a non-loopback bind without `--allow-remote`, and its message says why. **This is a
   deployment assumption, not a defect** — reopened if the service is ever bound where no proxy fronts it.
4. **The second official case, `YSM-SkyRanch`, differs** on three stands, 328 of 375 rows identical,
   unexplained since `P2.3`.
5. **The oracle is a 2022 fixture, and the FVS project's own checker skips this variant.** Agreement is
   evidence, not proof.
6. **The residual on three dense stands** is attributed, not proven, to upstream changes.
7. **`run.py`'s drive body is covered only where the extension is built**: 84 percent in the quality
   job, which has no extension, and the gate is met at 97 percent overall because the build job covers
   the rest.
8. **A parameter passed to the command cannot contain a comma.**
9. **At `-O0` the variant writes no database at all**, so the optimiser is not optional.
10. **The package needs a separately built extension.** Installing it does not build FVS.
11. **The `nemora` adapter requires `species` and `tree_age`**, and species assignment is out of scope.
12. **`CWH`, `CDF`, `BWBS`, `CMA`, and `MH` are not represented.** The W2.2 audit records them as no-go
    without a new parameter source: species, growth, mortality, crown, bark, volume/taper, and
    regeneration tables. A parser-only change would silently use ICH mortality and the 10 m2/ha fallback.
13. **The 19 subzone `BAMAX` defaults are provisional.** They are PSP p99 values, not calibrated
    capacities. The values are recorded with their source and W4 owns the final decision.
14. **No domain has a calibration certificate.** W1 built the foundation and the design; W3–W5 have not
    run. A result from this release is not a calibrated growth-and-yield claim.

## What is not in this release

The five missing zones, fitted calibration parameters or certificates, the standalone `FVSbc` (proven and
not adopted, ADR 0008 and ADR 0009), any variant other than BC, and real inventory data. Both
distributions are on PyPI; `fresh-fvsbc-pyfvs 0.3.12` is uploaded before the tag.
