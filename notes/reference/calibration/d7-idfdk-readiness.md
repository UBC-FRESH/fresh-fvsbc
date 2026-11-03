# D7.3 IDFdk calibration readiness

Status: probe complete; **no IDFdk bundle is issued**. The default capacity/growth is close on BA,
but the held-out TPH bias is outside the pre-registered threshold and the only candidates that
close it use mortality below the soft bound.
Date: 2026-11-03
Build: `fresh-fvsbc-pyfvs 0.4.1` (pinned by `fresh-fvsbc 0.21.3`)
Data: all-zone calibration dataset; IDFdk has 915 intervals
Evidence: `d7-idfdk-probe-summary.csv`, `d7-idfdk-probe-by-bec.csv`,
`d7-idfdk-candidates.json`

## 1. Sample and split

The probe uses `IDFdk` (the six labels IDFdk, IDFdk1–IDFdk5), five intervals per BEC after the D7.1
eligibility filter (BA0 >= 15 m2/ha, QMD >= 6 cm, dead BA <= 40% of BA0). The spatial holdout is the
**100 Mile House TSA**: 7 intervals, all IDFdk or IDFdk3. The other 22 intervals are training.

The site-level identifiers stay in the runtime output; this report and the committed tables carry
only aggregates.

## 2. The default is close on BA

`bamax53` is the existing default. It is already a strong BA baseline:

| Fold | n | BA bias | BA MAE | BA percent | TPH bias | TPH MAE | TPH percent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 22 | -0.08 | 3.23 | -0.3% | -166.5 | 305.4 | -10.3% |
| test | 7 | -1.90 | 1.93 | -6.0% | -487.8 | 518.4 | **-20.6%** |

The BA bias is within the ±3 m2/ha or 10% target on both folds. TPH is not: the held-out bias is
-20.6%, outside the 15% target. The model is not failing to grow the stand; it is losing too many
trees, or missing the ingrowth that offsets the loss.

## 3. Capacity and KC candidates do not fix TPH

| Candidate | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| `bamax45` | test | -2.33 | 2.33 | -525.2 | 542.4 |
| `bamax50` | test | -2.04 | 2.04 | -499.9 | 526.3 |
| `bamax53` | test | -1.90 | 1.93 | -487.8 | 518.4 |
| `bamax55` | test | -1.76 | 1.79 | -481.8 | 514.7 |
| `bamax60` | test | -1.61 | 1.65 | -468.5 | 505.4 |
| `kc-v2c` | test | -8.90 | 8.90 | -946.2 | 946.2 |
| `kc-v2c-pl3` | test | -6.76 | 6.76 | -859.5 | 859.5 |

Raising `BAMAX` from 45 to 60 changes held-out TPH by only about 57 trees/ha; the KC v2c set is
much worse, because its mortality and BA multipliers were fitted to a different BEC and an
in-sample trajectory. The KC pilot does not transfer as a province-level IDFdk candidate.

## 4. The only passing TPH candidate is below the soft bound

`bamax60-mort0.3` reaches held-out BA **+0.10 / MAE 1.68** and TPH **-352.9 / MAE 432.2**
(**-14.9%**), which is just inside the TPH threshold. It does so with `MORTMULT 0.3`, below the
protocol's soft range of 0.5–3.0. The nearest defensible value, `MORTMULT 0.5`, gives held-out TPH
**-16.3%** and fails. A species-specific `FD 0.3` or `PL 0.3` also fails to close the gap and still
sits below the soft bound.

The probe therefore finds a **trade-off**, not an identified parameter set:

- capacity and BA growth are already right;
- the TPH deficit needs less mortality;
- the mortality value that works is outside the soft range;
- the residual is concentrated in IDFdk3/IDFdk, which suggests missing ingrowth or a
  species/size-specific mortality structure, not a global multiplier.

No parameter is at the hard bound, but the only passing candidate is outside the soft range and is
not a final set.

## 5. Decision

**No IDFdk bundle.** The default `BAMAX 53` is retained as the baseline. The next IDFdk work is:

1. Fit on the full IDFdk sample (915 intervals) rather than the 29-interval probe, with the same
   site-grouped split.
2. Test `MORTMSB`/size-specific mortality and an explicit ingrowth term; the TPH deficit is not a
   capacity problem.
3. Keep the 100 Mile House TSA as an untouched spatial holdout until the structural candidate is
   frozen.
4. Report IDFdk3 separately; its TPH residual is larger than the domain mean.

The probe is `scripts/run_calibration_probe.py`; the candidate set is
`d7-idfdk-candidates.json`. The result is reproducible from the dataset checksum, the fixed split,
and the 0.4.1 pin.

## 6. Claim boundary

This is a readiness report. It does not calibrate IDFdk, does not change a default, and does not
support a yield, AAC, legal, or whole-block claim. The defensible statement is that IDFdk's BA
trajectory is already close on the held-out TSA, while its TPH trajectory is not, and the tested
global multipliers cannot close that gap inside the soft parameter range.
