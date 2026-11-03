# D7.1 SBPS calibration readiness

Status: probe complete; **no calibration bundle is issued**. The SBPS domain does not pass its
pre-registered holdout with one global parameter set.
Date: 2026-11-03
Build: `fresh-fvsbc-pyfvs 0.4.1` (D6.4 fix; pinned by `fresh-fvsbc 0.21.3`)
Data: all-zone calibration dataset; SBPS has 296 intervals
Evidence: `d7-sbps-probe-summary.csv`, `d7-sbps-probe-by-bec.csv`, `d7-sbps-site-index.csv`,
`d7-sbps-candidates.json`

## 1. Why this is a readiness gate

D7's protocol requires an eligible sample, a frozen split, an independent holdout, and a parameter
set that meets the pre-registered thresholds without sitting at a bound. The SBPS residual is large
enough to tempt a `BAMAX` or `MORTMULT` fit. The probe shows why that temptation is wrong.

The probe is not an optimizer. It evaluates a fixed candidate set on the same tree lists and
interval comparison as the baseline, then reports train and held-out-site error. A candidate that
cannot move the held-out error in the right direction is not a calibration.

## 2. Eligibility

The full SBPS sample contains young, dense stands and high-mortality intervals that the no-cut
projection cannot represent with one multiplier. The probe accepts an interval only when:

- initial BA is at least **15 m2/ha**;
- initial QMD is at least **8 cm**;
- dead BA is at most **40%** of initial BA.

After eligibility and a deterministic five-per-BEC selection, the probe compares **15 intervals**:
SBPSdc 5, SBPSmc 1, SBPSmk 5, SBPSxc 4. The one SBPSmc interval is a validation-only case; it has
no independent training support.

The exclusions are findings, not noise. A young stand at 3.5 m2/ha and 4,399 TPH grew to an
observed 11.8 m2/ha while FVS predicted 76; a small-tree stand at 26.4 m2/ha and 12,829 TPH
predicted 132. Those are ingrowth and small-tree structure, not a capacity multiplier.

## 3. Site index is not a lever

The PSP archive has a measured `SI_TREE` for most SBPS trees (PL median about 18 m). A run with
`SITECODE PL <measured SI>` is **identical** to the `SITECODE FD,20` placeholder: BA bias 17.15,
MAE 17.81, TPH bias 74.05, MAE 524.36 in both cases. FVS's own report says it:

```
NOTE: SITE INDEX IS NOT USED IN THIS VARIANT. VALUES ARE PRINTED FOR INFORMATIONAL PURPOSES.
```

Joining PSP site index is still worth doing for a future variant, but it cannot calibrate the
current BC build. The site-series coefficients, not `SITECODE`, carry the site effect.

## 4. Candidate result

The candidate set is `notes/reference/calibration/d7-sbps-candidates.json`. Held-out sites are one
SBPSmc site and three SBPSxc sites; the split is site-grouped, not random.

| Candidate | Fold | n | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `bamax50` | train | 11 | 2.24 | 3.15 | 41.94 | 121.24 |
| `bamax50` | test | 4 | 8.58 | 10.06 | -144.82 | 163.46 |
| `bamax45-baimult0.5` | train | 11 | 0.97 | 3.16 | 49.03 | 121.42 |
| `bamax45-baimult0.5` | test | 4 | 6.08 | 8.06 | -214.82 | 214.82 |
| `bamax48-baimult0.5` | train | 11 | 1.15 | 3.34 | 61.67 | 126.42 |
| `bamax48-baimult0.5` | test | 4 | 7.08 | 9.06 | -133.32 | 134.46 |
| `bamax55` | train | 11 | 2.52 | 3.31 | 61.76 | 128.14 |
| `bamax55` | test | 4 | 10.08 | 11.56 | -41.58 | 101.21 |
| `bamax40-mort2` | train | 11 | -3.03 | 5.37 | -736.43 | 764.41 |
| `bamax40-mort2` | test | 4 | -8.92 | 9.58 | -1,314.82 | 1,314.82 |

- `bamax45-baimult0.5` is the best compromise on the training split, but its held-out BA bias is
  **+6.08** and its TPH bias **-214.82**. It misses the BA threshold and trades too much TPH.
- `bamax55` improves TPH but makes held-out BA worse (**+10.08**).
- `bamax40-mort2` reduces BA by over-killing: TPH bias **-1,315** on held-out sites. Mortality is
  not a BA-growth substitute.
- No candidate sits at a bound, but none is identified by the held-out split. The parameter surface
  is a trade-off, not an optimum.

By BEC, the baseline `bamax50` is already close on SBPSdc (BA bias -0.39, MAE 1.35; TPH -47 / 80)
and poor on SBPSmc (BA +17.35) and SBPSxc (BA +4.08 on the four eligible intervals; the five-interval
pre-screen subset was +23.84). SBPSmk is intermediate (BA +5.46, TPH +132). This is not one domain.

## 5. Decision

**No SBPS bundle is promoted.** The test split fails the pre-registered thresholds, SBPSmc has one
eligible interval, and the excluded intervals are structural ingrowth or high-mortality cases.
A single `BAMAX`/`BAIMULT`/`MORTMULT` set would hide those failures.

The next D7 work is narrower:

1. Fit capacity per BEC (not one SBPS `BAMAX`) with more than five intervals, if the data support it.
2. Treat SBPSmc as validation-only until it has independent sites.
3. Model the excluded young/ingrowth stands separately; a multiplier is the wrong instrument.
4. Treat high-mortality intervals (MPB, fire, wind) as disturbances, not calibration targets.
5. Revisit `SITECODE` only with a variant that uses it.

The probe harness is `scripts/run_calibration_probe.py`; the pure selection and keyword helpers are
in `src/fresh_fvsbc/calibration_probe.py` and covered by `tests/test_calibration_probe.py`.

## 6. Claim boundary

This is a readiness report. It does not calibrate SBPS, does not change a default, and does not
support a yield, AAC, legal, or whole-block claim. The only defensible statement is the negative
one: on eligible SBPS intervals, the tested global parameter candidates do not meet the held-out BA
and TPH thresholds, and the largest residuals are in stands the current no-cut model cannot
represent.
