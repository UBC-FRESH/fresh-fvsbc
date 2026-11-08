# D9.55 non-PSP domain baseline and the first tiered BC surface

Status: **first independent domain screen; one external-checked pilot, five evidence-leaning defaults,
seven domains that still need work, four with insufficient data**
Date: 2026-11-08
Code: `nonpsp_domain_baseline.py`
Evidence: `d9-faib-nonpsp-domain-baseline.csv`, `d9-faib-nonpsp-domain-candidates.csv`,
`d9-tiered-domain-status.csv`

This is the first screen that puts **every calibration domain** on the same independent cohort. It
is not a calibration certificate. Its job is to decide which domains a bundle may speak for, which
should fall back to the identity default, and which have no defensible answer yet.

## 1. Data and method

The cohort is the repeated FAIB non-PSP archive (`nonpsp4`), rebuilt at the common 4 cm target:

- 1,733 intervals across 141 BEC labels;
- 4,370 visits and 202,185 tree rows;
- **zero site-ID overlap with the PSP**;
- input SHA-256 values are in the runtime `manifest.json`.

Each zone was run separately with `scripts/run_calibration_probe.py` on a capped sample of five
intervals per BEC. The cap keeps the screen reproducible on one workstation; it is a **sample**, not
the whole cohort. Eligibility is the same as the calibration design: initial BA at least 15 m2/ha,
initial QMD at least 6 cm, and mortality no more than 40 percent. The final table has **476
intervals across 416 sites and 16 domains**.

The installed 0.4.1 wheel did not resolve `ESSFwmw`; the two intervals with that label were removed
from the ESSF input before the run. The exclusion is named rather than silently dropped. No raw tree
rows or site identifiers are tracked.

The BA and TPH bands are the pre-registered ones: BA within ±3 m2/ha or ±10 percent, TPH within
±15 percent. The 95 percent interval is a **site bootstrap** (2,000 resamples, fixed seed), not a
prediction interval. A domain that is inside the band on its point estimate but whose bootstrap
crosses the band is called `leans-pass`, not `passes`.

## 2. Default residual by domain

The default is the uncalibrated FVS-BC model. Positive means FVS is high.

| Domain | n | Sites | BA % (95% CI) | TPH % (95% CI) | Site pass BA / TPH | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| CWH | 67 | 61 | −17.8 (−21.9 to −13.4) | −9.5 (−13.8 to −4.5) | 10/61 / 37/61 | fails |
| ICHwet | 66 | 60 | −7.6 (−11.9 to −2.5) | −3.9 (−8.7 to +1.6) | 27/60 / 36/60 | leans-pass |
| ICHdry | 33 | 27 | −7.2 (−11.7 to −3.4) | −6.2 (−15.7 to +2.4) | 17/27 / 19/27 | leans-pass |
| IDFdk | 18 | 16 | +3.0 (−5.2 to +16.5) | +1.0 (−8.9 to +16.2) | 9/16 / 11/16 | leans-pass |
| IDFdry | 15 | 13 | −11.0 (−22.5 to −0.2) | −6.6 (−17.6 to +5.4) | 7/13 / 5/13 | fails |
| IDFxm | 1 | 1 | −7.8 | +24.6 | 1/1 / 0/1 | insufficient |
| SBSdry | 41 | 34 | −7.8 (−17.0 to +0.7) | −4.0 (−9.6 to +1.6) | 7/34 / 23/34 | leans-pass |
| SBSwet | 32 | 26 | +4.7 (−6.2 to +22.0) | −11.8 (−24.7 to +0.5) | 13/26 / 16/26 | leans-pass |
| BWBS | 23 | 23 | −24.9 (−32.0 to −18.4) | −4.8 (−15.6 to +7.8) | 1/23 / 13/23 | fails |
| ESSFdry | 62 | 56 | −22.4 (−25.3 to −19.6) | −16.5 (−19.3 to −13.7) | 4/56 / 28/56 | fails |
| ESSFwet | 47 | 40 | −17.5 (−21.0 to −14.1) | −11.3 (−18.3 to −5.4) | 8/40 / 24/40 | fails |
| MS | 47 | 38 | −20.5 (−25.2 to −13.3) | −11.2 (−15.4 to −4.8) | 5/38 / 18/38 | fails |
| SBPS | 17 | 14 | +71.2 (+35.6 to +116.7) | −5.5 (−11.7 to +7.5) | 1/14 / 10/14 | fails |
| MH | 5 | 5 | −21.5 (−25.6 to −16.9) | −30.2 (−41.5 to −14.9) | 0/5 / 1/5 | fails |
| CDF | 1 | 1 | −41.9 | −43.4 | 0/1 / 0/1 | insufficient |
| PP | 1 | 1 | −26.9 | −12.3 | 0/1 / 1/1 | insufficient |

The site pass column is the share of sites whose own aggregate error is inside the band. It is much
weaker than the domain mean for every domain; a domain mean is not a stand-level guarantee.

## 3. Bundle comparisons on the same sample

The candidate runs use the same capped sample and build as the default run, so the comparison is
fixed-parameter and apples-to-apples.

| Domain | Model | BA % (95% CI) | TPH % (95% CI) | Site pass BA / TPH | Verdict |
| --- | --- | ---: | ---: | ---: | --- |
| CWH | default | −17.8 (−21.9 to −13.4) | −9.5 (−13.8 to −4.5) | 10/61 / 37/61 | fails |
| CWH | CWH 4 cm pilot | **+1.2 (−4.8 to +8.5)** | **+0.5 (−4.2 to +6.3)** | **30/61 / 35/61** | **passes** |
| IDFdk | default | +3.0 (−5.2 to +16.5) | +1.0 (−8.9 to +16.2) | 9/16 / 11/16 | leans-pass |
| IDFdk | BAMAX 53 | +2.6 (−5.7 to +16.4) | +0.7 (−9.6 to +16.0) | 9/16 / 11/16 | leans-pass |
| SBSdry | default | −7.8 (−17.0 to +0.7) | −4.0 (−9.6 to +1.6) | 7/34 / 23/34 | leans-pass |
| SBSdry | MORTMULT 2.0 | −11.3 (−19.8 to −3.1) | −7.1 (−12.0 to −1.9) | 7/34 / 21/34 | fails |
| SBSwet | default | +4.7 (−6.2 to +22.0) | −11.8 (−24.7 to +0.5) | 13/26 / 16/26 | leans-pass |
| SBSwet | MORTMULT 2.0 | +0.3 (−9.4 to +15.9) | −15.0 (−27.5 to −2.8) | 11/26 / 18/26 | leans-pass |
| BWBS | default | −24.9 (−32.0 to −18.4) | −4.8 (−15.6 to +7.8) | 1/23 / 13/23 | fails |
| BWBS | BWBS pilot | **+0.6 (−7.2 to +8.8)** | +10.6 (−1.4 to +24.5) | 5/23 / 12/23 | leans-pass |

The CWH 4 cm pilot is the only candidate that moves a failing default into a passing band and keeps
both bootstrap intervals inside it on this sample. It is still an unsigned pilot, and its external
matched volume is −12.6 percent, unresolved. The SBS pilot is worse than the default. The BWBS pilot
corrects BA but moves TPH the wrong way and only 5 of 23 sites pass BA, so it is not promoted. BAMAX
53 is indistinguishable from the default for IDFdk.

## 4. The tiered surface

`d9-tiered-domain-status.csv` is the decision table. The tiers are:

| Tier | Meaning |
| --- | --- |
| `A-pilot-external` | A domain bundle improves a failing default and passes independent BA/TPH. It is still a pilot, not a certificate. |
| `B-tsa-pilot` | A local or TSA-scoped PSP candidate with no independent external cohort. |
| `C-default` | Identity default; independent point estimates inside the bands, but at least one bootstrap interval crosses a band. |
| `D-needs-work` | Identity default fails; no validated domain bundle. A direct fit or structural work is required. |
| `E-insufficient` | Fewer than five independent intervals, or no repeated non-PSP data. |

| Domain | Tier | Recommendation |
| --- | --- | --- |
| CWH | A-pilot-external | CWH 4 cm pilot; volume remains unresolved |
| ICHwet | C-default, with `B-tsa-pilot` option | identity default; ICHmw2 Arrow/Cascadia candidate is TSA-scoped only |
| ICHdry | C-default | identity default |
| IDFdk | C-default | identity default; BAMAX 53 is not better |
| IDFdry | D-needs-work | direct calibration required |
| IDFxm | E-insufficient | collect data; validation-only |
| SBSdry | C-default | identity default; MORTMULT 2 fails BA |
| SBSwet | C-default | identity default; MORTMULT 2 worsens TPH |
| BWBS | D-needs-work | direct calibration required; pilot not promoted |
| ESSFdry | D-needs-work | direct calibration required |
| ESSFwet | D-needs-work | direct calibration required |
| MS | D-needs-work | direct calibration required |
| SBPS | D-needs-work | direct calibration required; SBPSmk/Quesnel candidate is local only |
| MH | D-needs-work | direct calibration required |
| CDF | E-insufficient | collect data |
| PP | E-insufficient | collect data |
| CMA | E-no-data | collect data; no repeated non-PSP interval |

**The first full-BC result is therefore not a BC-wide calibration.** It is a complete, explicit
surface that says where a bundle exists, where the default is defensible, and where neither is true.
There are no silent uncalibrated BECs in this table: every domain has a tier and a recommendation.

## 5. What this changes

- The tiered decision no longer treats `IDFdk` and `SBS` as bundle domains. Their old pilots are
  worse than the default on the independent sample.
- CWH is the only domain with an external-checked growth pilot, and its volume gap stays visible.
- ICHmw2 stays a TSA-scoped candidate, not an ICHwet-wide calibration.
- BWBS, ESSF, IDFdry, MS, SBPS, and MH are named as direct-work domains rather than left implicit.
- CDF, PP, IDFxm, and CMA are explicit data gaps.

## 6. Limits

- The screen is capped at five intervals per BEC, not the full 1,733-interval cohort.
- The bootstrap resamples sites, but the cohort is not a probability sample of BC.
- The comparison is aggregate BA/TPH only. It does not test QMD, height, volume, species
  composition, or per-stand yield.
- CWH volume is not validated on the non-PSP cohort; the −12.6 percent matched-volume residual
  remains unresolved.
- The installed wheel could not resolve `ESSFwmw`; two intervals were excluded.
- No bundle is signed. No result here supports a yield, AAC, legal, or whole-block claim.

## 7. Reproduce

Run one zone at a time, then summarise. The command below is the shape used for every zone; replace
`ZONE` with `CWH`, `ICH`, `IDF`, `SBS`, `SBPS`, `ESSF`, `MS`, `BWBS`, `MH`, `CDF`, or `PP`.

```bash
PYTHONPATH=src python scripts/run_calibration_probe.py \
  --data-dir "$NONPSP4" \
  --psp-dir "$FAIB_NONPSP_REP" \
  --out-dir "$OUT/$ZONE" \
  --domain "$ZONE" --per-bec 5 --min-dbh 4 \
  --candidates baseline.json

python notes/reference/calibration/nonpsp_domain_baseline.py \
  --probe "$OUT/CWH/probe.csv" --probe "$OUT/ICH/probe.csv" \
  --probe "$OUT/IDF/probe.csv" --probe "$OUT/SBS/probe.csv" \
  --probe "$OUT/SBPS/probe.csv" --probe "$OUT/ESSF/probe.csv" \
  --probe "$OUT/MS/probe.csv" --probe "$OUT/BWBS/probe.csv" \
  --probe "$OUT/MH/probe.csv" --probe "$OUT/CDF/probe.csv" \
  --probe "$OUT/PP/probe.csv" \
  --out notes/reference/calibration/d9-faib-nonpsp-domain-baseline.csv
```

`baseline.json` is `[{"label": "baseline"}]`. The candidate runs use the same command with the
candidate file and, where the model is the bundle itself, the same parameters in the candidate file.
The CWH candidate is `baimult 7.0` for FD/HW/CW/BG/PW, `mortmult 0.30` for the eleven species in the
bundle, and `regdmul 2.0` for FD/HW/CW/BG/PW.

## 8. Claim boundary

This is an independent external screen and a domain-decision record. It does not calibrate the
failing domains, does not make the defaults certified, and does not turn the CWH pilot into a
certificate. It does not support a yield, AAC, legal, or whole-block claim.
