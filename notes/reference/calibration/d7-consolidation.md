# D7.6 consolidation: bundle, holdouts, periodic establishment, domain reuse, density

Status: **all five D7.4 follow-ups are implemented and measured.** The IDFdk pilot now has a
bundle-carried ingrowth model, two additional holdouts, periodic establishment, a cross-domain
screen, and a density/QMD-refined model. It is still a pilot, not a certificate.
Date: 2026-11-03
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`

## 1. Bundle and provenance

The bundle contract now has an optional `ingrowth` section:

- `IngrowthRate` is one BEC/species rate with optional initial-BA and QMD ranges.
- `IngrowthModel` loads, validates, selects the matching rows, and renders an `ESTAB` block.
- `CalibrationBundle.ingrowth` is optional; old bundles load unchanged.
- `scripts/run_calibration_probe.py --bundle` uses the bundle's ingrowth block and calls
  `run_case(..., calibration=bundle)`, so `provenance.json` names the bundle.

The pilot bundle is `d7-idfdk-bundle.json`; it carries 22 constant rates, `BAMAX 53.0`, and the
D7.4 claim. A probe with that bundle reproduces the D7.4 result exactly:

| Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | ---: | ---: | ---: | ---: |
| train (22) | -0.08 | 3.23 | +144.65 | 358.55 |
| test (7) | -1.90 | 1.93 | -207.35 | 370.05 |

The run's provenance records `calibration_id: idfdk-ingrowth-pilot-2026-11-03`. The bundle is
unsigned and carries the warning that it is a pilot, not a certificate.

## 2. Second spatial and temporal holdouts

The 100 Mile House result is the original spatial holdout. Two more splits were fitted with the
same public recruitment table:

| Split | Test | BA bias | BA MAE | TPH bias | TPH MAE | TPH percent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 Mile House TSA | 7 | -1.90 | 1.93 | -207.4 | 370.1 | -8.7% |
| Kamloops TSA | 7 | +0.35 | 6.55 | +191.0 | 563.5 | +14.1% |
| temporal, fit ≤1990 | 7 | -0.59 | 4.87 | +267.4 | 526.6 | +14.7% |

All three are inside the BA ±3 m2/ha (or 10%) and TPH ±15% bias thresholds. Kamloops and the
temporal split sit close to the TPH limit; they are not as strong as the 100 Mile split. The
training rates for each split exclude the held-out sites/period.

The rate models for each split are in the local validation runs; the committed evidence is
`d7-idfdk-kamloops-summary.csv` and `d7-idfdk-temporal1990-summary.csv`.

## 3. Periodic establishment

`IngrowthModel.estab_keyword()` accepts `cycles` and writes one `NATURAL` line per cycle. The probe
now changes `TIMEINT` and `NUMCYCLE` when `--cycles` is greater than one, so the extra lines are
actually executed. A two-cycle run on the 100 Mile holdout produced **8 establishment events**
(4 species × 2 cycles) and:

| Fold | BA bias | BA MAE | TPH bias | TPH MAE | TPH percent |
| --- | ---: | ---: | ---: | ---: | ---: |
| train (22) | -0.30 | 3.33 | +140.1 | 354.8 | +8.7% |
| test (7) | -2.33 | 2.33 | -203.8 | 368.5 | -8.6% |

The periodic result is slightly lower in TPH than the one-pulse result but still passes. The
establishment schedule is still a fixed rate per cycle; it is not yet a climate- or density-driven
regeneration model.

## 4. Reuse across domains

A public-data recruitment model was fitted to **all-zone** intervals with the D6 one-per-BEC sample
sites excluded: **16,807 training intervals** and **354 rate rows**. The D6 139-interval sample was
then run with the model. This is a **screening**, not a domain calibration.

| Zone | n | TPH bias before | TPH bias after | Ingrowth cases |
| --- | ---: | ---: | ---: | ---: |
| BWBS | 5 | -275.74 | -47.14 | 5 |
| CDF | 1 | -143.46 | -124.46 | 1 |
| CMA | 1 | -14.20 | -14.20 | 0 |
| CWH | 21 | -151.53 | -16.34 | 20 |
| ESSF | 30 | -734.31 | -688.38 | 26 |
| ICH | 26 | -586.28 | -435.28 | 24 |
| IDF | 18 | -1067.97 | -893.63 | 18 |
| MH | 3 | -335.63 | -323.97 | 1 |
| MS | 10 | -624.40 | -466.70 | 8 |
| PP | 2 | +64.47 | +91.47 | 1 |
| SBPS | 4 | +1.53 | +204.03 | 3 |
| SBS | 18 | +770.18 | +920.46 | 14 |

The generic all-zone rates improve the TPH bias in CWH, BWBS, ICH, IDF, MS, ESSF, MH, and CDF.
They over-recruit SBPS, SBS, and PP; those domains need their own rates and eligibility rules. The
five zones (CWH, CDF, BWBS, CMA, MH) ran through the local five-zone parser; the wrapper still
refuses them, so this is not a released five-zone capability.

D7.7 addendum: a domain-specific SBS test found a different working lever. `d7-sbs-bundle.json` uses
`MORTMULT 2.0` for FD/PL/SE/HW and no ingrowth; on a five-per-BEC SBS sample with the 100 Mile
House TSA held out it gives test BA -0.77 / MAE 4.29 (-1.8%) and TPH +109.9 / MAE 489.0 (+3.7%),
inside both thresholds. Training BA is -2.54 / MAE 6.16 and TPH -98.7 / MAE 428.2. The SBS bundle
is a pilot and uses a mortality lever, not the IDFdk ingrowth model. The D7.2 SBPS candidate
(`BAMAX 50`, `MORTMULT 0.5`) passes SBPSdc and SBPSmk but not SBPSxc; SBPSmc remains
validation-only. PP has only two intervals and is validation-only.

Evidence: `d7-ingrowth-screen-by-zone.csv`, `d7-ingrowth-screen-by-bec.csv`,
`d7-all-zone-ingrowth.json`.

## 5. Density and age refinement

The model can carry initial-BA and QMD ranges. On IDFdk, rates were fitted in bins:

- BA: 15–25, 25–35, 35+
- QMD: 6–12, 12–20, 20+

The binned model has **116 rows**. On the 100 Mile holdout it improves TPH:

| Model | BA bias | BA MAE | TPH bias | TPH MAE | TPH percent |
| --- | ---: | ---: | ---: | ---: | ---: |
| constant | -1.90 | 1.93 | -207.4 | 370.1 | -8.7% |
| binned | -1.90 | 1.93 | **-102.6** | 363.9 | **-4.3%** |

Training TPH bias is +36.4 (2.3%). The binned model is the preferred D7.6 pilot; the constant model
is retained as the simpler fallback. The bins are still BEC × species means within a BA/QMD class;
they are not a continuous age-dependent recruitment function.

## 6. Decision and next steps

The five follow-ups are complete for the IDFdk pilot:

1. bundle/provenance: done;
2. second spatial and temporal holdouts: done, all pass bias thresholds;
3. periodic establishment: done and exercised;
4. other domains: screened; CWH/BWBS/ICH/IDF/MS improve, SBS now has a MORTMULT pilot, SBPSdc/mk have the D7.2 candidate, PP is validation-only;
5. density/QMD refinement: done and improves the holdout.

The next release step is to make the binned model the canonical bundle, add the same holdout
protocol per domain, and only then issue certificates. The five-zone wrapper and the dense
province-wide calibration remain future work.

## 7. Claim boundary

Every number here is a pilot result on public PSP data. The binned model has one spatial holdout;
the other domains are a screening, not validation. No bundle is signed, no default changed, and no
yield, AAC, legal, or whole-block claim is made.
