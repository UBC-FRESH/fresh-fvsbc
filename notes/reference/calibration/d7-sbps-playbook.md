# D7 SBPS calibration playbook

Status: consolidated record through D7.8
Date: 2026-11-03
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Current candidate: `BAMAX 25` + 100 Mile-specific ingrowth, not yet certified

This note exists so the same false starts are not repeated. It records what was tried, which split
was used, why a result was accepted or retracted, and what the next agent should do first.

## 1. One-screen summary

| Step | Split | Result | Decision |
| --- | --- | --- | --- |
| D7.1 global probe (#346) | 5 intervals/BEC, site holdout | No global SBPS set meets BA and TPH | No bundle |
| D7.2 per-BEC capacity (#348) | all eligible, every-third-site test | BA moves; TPH fails | No bundle |
| D7.3 TPH/MORTMULT (#351) | every-third-site test | `BAMAX 50 + MORTMULT 0.5` appeared to pass | **Retracted** by D7.5 |
| D7.4 IDFdk ingrowth (#352) | pure TSA holdout | Ingrowth, not mortality, fixes TPH | Pilot passes |
| D7.5 SBPS ingrowth (#354) | pure 100 Mile TSA holdout | Baseline BA +50.8%; ingrowth does not transfer | D7.3 retracted |
| D7.6 100 Mile capacity (#357) | 7 eligible intervals, 2 test | `bamax30` test pass, unstable | No bundle |
| D7.7 100 Mile LOSO (#360) | 6 site folds over 7 intervals | `BAMAX 25` BA pass/TPH fail; `BAMAX 30` opposite | No capacity-only bundle |
| D7.8 100 Mile candidate (#362) | 6 site folds, site-specific ingrowth | `BAMAX 25` + 100 Mile ingrowth: BA +8.4%, TPH -13.1% | **Candidate** |
| D7.9 temporal holdout (#366) | train <=1998, test >=2001 | one eligible later interval; BA +33.4% | Not validated; data gap |

The only positive result is the last one. Everything before it is useful evidence, not a calibration.

## 2. What went wrong, and why

### 2.1 Every-third-site is not a spatial holdout

D7.2, D7.3, and D7.6 used every-third-site splits. Those folds share TSA, stand history, and
site-series distribution with training. D7.3's `BAMAX 50 + MORTMULT 0.5` passed that split, then
failed the pure 100 Mile TSA holdout with BA +17.03 and TPH +219.

**Rule:** a split that keeps sites from the same TSA in both folds is a **site** split, not a
**spatial** holdout. Label it that way. Do not use it to promote a bundle.

### 2.2 A two-interval test cannot select a parameter

D7.6 selected `bamax30` from a 2-interval test. D7.7's leave-one-site-out run gave the same candidate
BA +23.6%. The two-interval pass was noise.

**Rule:** a test fold needs at least a full site and, for a parameter claim, several sites. Report the
number of test intervals beside every result.

### 2.3 Capacity alone has a monotonic trade-off

D7.7 over six site folds:

| BAMAX | BA % | TPH % |
| ---: | ---: | ---: |
| 25 | +4.3% | -29.5% |
| 30 | +23.6% | -14.5% |
| 35 | +35.6% | -5.1% |
| 38 | +40.7% | -1.3% |
| 50 | +50.8% | +7.5% |

Lowering BAMAX fixes BA and loses TPH. Raising it fixes TPH and loses BA. No BAMAX value passes both.
`BAIMULT 0.5` did not move BA in the 100 Mile test (BA +39.8% at BAMAX38 vs +40.7% without), so it is
not the missing lever either.

**Rule:** when BA and TPH move in opposite directions, the next lever is a process the parameter does
not represent (recruitment, ingrowth, mortality timing), not another value of the same parameter.

### 2.4 Other-TSA ingrowth does not transfer to 100 Mile

D7.5 trained SBPS recruitment without 100 Mile and tested 100 Mile. Baseline BA was already +50.8%;
ingrowth made BA/TPH worse. Scaling the rate down did not remove the BA error.

**Rule:** for a TSA-specific stratum, train recruitment **within** that TSA or hold out the TSA from
the start. Cross-TSA rates are not a substitute for a TSA effect.

### 2.5 Mortality is not a TPH fix

D7.4's IDFdk diagnosis is the pattern: the TPH deficit was missing ingrowth, not excess mortality.
`MORTMULT` below 1 raises TPH by saving existing trees, which also raises BA. The D7.3 candidate did
that and did not transfer.

**Rule:** use `MORTMULT` for a mortality residual, not for missing recruitment.

## 3. The candidate that works

### 3.1 Domain and sample

- `SBPSmk` in `100 Mile House TSA`.
- 16 intervals / 10 sites; eligibility leaves 7 intervals / 6 sites.
- Six leave-one-site-out folds; each eligible site is test once.
- Recruitment rates for each fold are trained on the **other 100 Mile sites**, not other TSAs.

### 3.2 Parameters

- `BAMAX 25`
- no `MORTMULT`, `BAIMULT`, or `HTGMULT`
- one `ESTAB` block with 100 Mile-specific `NATURAL` lines, annual rates by species group:

| Group | Annual TPH |
| --- | ---: |
| FD | 4.00 |
| HW | 13.29 |
| PL | 75.71 |
| SE | 11.36 |

The canonical rate file is `d7-100mile-ingrowth.json`. The LOSO evidence uses fold-specific rates
(the JSON is the deployment fit on all 16 intervals).

### 3.3 Result

Six site-grouped folds, seven test intervals:

| Metric | Value | Threshold |
| --- | ---: | --- |
| BA bias | +2.60 m2/ha | ±3 m2/ha |
| BA percent | +8.4% | ±10% |
| TPH bias | -253.5 | — |
| TPH percent | -13.1% | ±15% |

Both pass. This is a **candidate**, not a certificate.

### 3.4 Why it works

`BAMAX 25` fixes the BA side. The TSA-specific ingrowth fixes the TPH side without a mortality
multiplier. Neither component alone passes; the combination does.

## 4. Reproduce it

Use the pinned build and the all-zone dataset. Paths are relative; the PSP directory is the caller's.

```bash
# 1. filter the TSA into its own data directory
#    intervals.csv and visits.csv only; tree rows stay in the PSP directory
python - <<'PY'
import pandas as pd
i = pd.read_csv("runtime/calibration/intervals.csv")
sel = i[(i.BEC == "SBPSmk") & (i.TSA_DESC == "100 Mile House TSA")]
sel.to_csv("runtime/sbpsmk-100mile/intervals.csv", index=False)
v = pd.read_csv("runtime/calibration/visits.csv")
v[v.SITE_IDENTIFIER.astype(str).isin(set(sel.SITE_IDENTIFIER.astype(str)))].to_csv(
    "runtime/sbpsmk-100mile/visits.csv", index=False
)
PY

# 2. capacity-only LOSO screen
python scripts/run_calibration_probe.py \
  --data-dir runtime/sbpsmk-100mile --psp-dir "$FAIB_PSP_DIR" \
  --out-dir runtime/d7-100mile-loocv-eligible --domain SBPSmk --per-bec 1000 \
  --candidates notes/reference/calibration/d7-100mile-loocv-candidates.json \
  --test-sites "<all eligible site ids>"

# 3. 100 Mile-specific ingrowth via fold-specific rate files
#    For each eligible site: train rates on the other sites, then run
python scripts/run_calibration_probe.py \
  --data-dir runtime/sbpsmk-100mile --psp-dir "$FAIB_PSP_DIR" \
  --out-dir runtime/d7-100mile-ingrowth-<site> --domain SBPSmk --per-bec 1000 \
  --candidates notes/reference/calibration/d7-100mile-ingrowth-candidates.json \
  --ingrowth runtime/d7-100mile-ingrowth-<site>/rates.json \
  --test-sites "<held-out site id>"
```

The test site lists are site identifiers. Keep them in `runtime/`; do not commit them.

## 5. Do not repeat these

- Do not use every-third-site as a spatial holdout.
- Do not promote a parameter from a two-interval test.
- Do not tune `BAMAX` against the test fold.
- Do not use `MORTMULT` to compensate for missing ingrowth.
- Do not apply other-TSA recruitment rates to 100 Mile.
- Do not pool SBPSdc, SBPSmk, and SBPSxc.
- Do not treat a candidate as a certificate; the sample is one TSA.

## 6. Next steps

1. **Temporal holdout (D7.9):** the later visits have only **one eligible interval**; it fails BA (+33.4%). The candidate remains **unvalidated temporally**. Do not issue a bundle until newer/extra 100 Mile data or a second TSA supplies a usable split.
2. Freeze the canonical rates and record the training interval list and checksum.
3. Add an `ESTAB`/ingrowth section to the calibration-bundle schema and provenance.
4. If a usable temporal holdout passes, issue a **100 Mile candidate bundle** with the claim boundary.
5. Then repeat the same playbook for SBPSdc (Quesnel) and the other SBPS TSAs; do not transfer the
   100 Mile rates.

## 7. Claim boundary

The D7.8 result is a candidate on six site-grouped folds in one TSA. It is not a certified
calibration, not a provincial model, and not a yield, AAC, legal, or whole-block claim.
