# D7.4 IDFdk ingrowth pilot — the TPH fix

Status: **pilot candidate passes the spatial holdout**; no release bundle yet
Date: 2026-11-03
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: public FAIB PSP tree detail and the all-zone interval table

This is the first D7 candidate that meets the pre-registered BA and TPH thresholds on an
independent spatial holdout. The fix is not a mortality multiplier. It is the missing ingrowth.

## 1. The diagnosis

The D7.3 TPH failure was not a mortality-rate error. Predicted initial TPH matches observed on the
test stands. The observed next stand gains TPH in the 100 Mile House IDFdk3 plots, while FVS
projects a loss:

| Interval | Observed TPH | Predicted TPH | New trees found in the next visit |
| --- | ---: | ---: | ---: |
| `4024432` 1997–2018 | 3,138 | 2,260 | 1,022 |
| `4024433` 1986–1997 | 3,255 | 2,310 | 2,165 |
| `4024433` 1997–2018 | 4,438 | 2,792 | 1,679 |

The new trees are overwhelmingly FD. The FVS base run has no natural-regeneration block, so it
cannot represent this ingrowth. A low `MORTMULT` compensated for it in D7.3 by saving existing
trees, which is the wrong mechanism.

## 2. The public-data ingrowth model

For every IDFdk interval in the public tree detail, the new live trees at the next visit were
counted by species and divided by the interval length. The model is a **mean annual recruitment
rate**, in trees per hectare per year, by BEC and species group:

- training: **712 intervals, 282 sites**;
- excluded spatial holdout: **100 Mile House TSA** (the D7.3 holdout);
- groups: FD, PL, SE, HW.

The rates are in `d7-idfdk-ingrowth.json`; no site identifiers are committed.

## 3. Applying it

`ingrowth_keyword()` renders an FVS `ESTAB` block with one `NATURAL` line per species. The annual
rate is multiplied by the interval length and converted from TPH to the trees-per-acre field FVS
reads. The `BAMAX` remains the default 53; no `MORTMULT` or `BAIMULT` is fitted.

The probe command was:

```bash
python scripts/run_calibration_probe.py \
  --data-dir runtime/calibration --psp-dir "$FAIB_PSP_DIR" \
  --out-dir runtime/idfdk-ingrowth --domain IDFdk --per-bec 5 \
  --candidates notes/reference/calibration/d7-idfdk-ingrowth-candidates.json \
  --ingrowth notes/reference/calibration/d7-idfdk-ingrowth.json \
  --test-sites 4024432,4024433,4024439,4025039,4025040
```

## 4. Result

| Fold | n | BA bias | BA MAE | BA percent | TPH bias | TPH MAE | TPH percent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 22 | -0.08 | 3.23 | -0.3% | +144.6 | 358.5 | +9.0% |
| test | 7 | -1.90 | 1.93 | -6.0% | -207.4 | 370.1 | **-8.7%** |

Both folds are inside the pre-registered thresholds:

- BA bias within ±3 m2/ha or 10%: test -1.90, -6.0%.
- TPH bias within 15%: test -8.7%.
- No parameter is at a hard bound.
- The spatial holdout was not used to estimate the rates.

The baseline without ingrowth was BA -1.90 / MAE 1.93, TPH -487.8 / MAE 518.4 (-20.6%). The
ingrowth model removes most of the TPH bias without changing the BA result materially.

## 5. What this is not

- It is a **pilot model**, not a released `CalibrationBundle`. The bundle contract has no field for
  an `ESTAB` block yet; the next release step is to add an ingrowth section to the bundle schema
  and record the rates in provenance.
- The rates are a BEC × species mean, not a density- or age-dependent recruitment model.
- The `ESTAB` block is applied at cycle 1 with the total interval recruitment. A multi-cycle
  projection needs periodic establishment; that is a D8 deployment detail.
- The validation is one spatial holdout. A second holdout (leave-one-TSA-out) and a temporal
  holdout are still needed before a certificate.
- The model is fitted on IDFdk only. It does not cover SBS, ICH, ESSF, MS, SBPS, or the five zones.

## 6. Claim boundary

The defensible statement is:

> On the 100 Mile House IDFdk holdout, the FVS-BC default capacity plus a public-data
> BEC × species recruitment model reduces held-out TPH bias from -20.6% to -8.7% and keeps BA bias
> at -6.0%, meeting the D7 thresholds. It is a pilot model, not a certificate.

The next work is to package the ingrowth section in the calibration bundle, add a second spatial
holdout and a temporal holdout, and then run the same model on the other supported domains.
