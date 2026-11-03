# D6 — five-zone baseline at five intervals per BEC

Status: measured, not calibrated. Build: `fresh-fvsbc-pyfvs 0.4.1` (five-zone prototype plus
the D6 SBPS small-tree fix). The wrapper still refuses the five zones; this run uses the prototype
`bec` tokens at runtime, so it is **not** a released five-zone capability.

Evidence: `d6-five-zone-summary.csv`, and the local run directory
`.opencode/tmp/opencode/d6-five-zone-5/` (not committed because the interval table carries site
identifiers).

## Sample and build

The all-zone interval table has 153 BEC variants. `select_intervals(..., per_bec=5)` was applied to
the five prototype zones and then the same selector was used inside `run_backtest`:

| Zone | Labels | Intervals |
| --- | ---: | ---: |
| `CWH` | 21 | 105 |
| `CDF` | 1 | 5 |
| `BWBS` | 5 | 25 |
| `CMA` | 1 | 5 |
| `MH` | 3 | 13 |
| **Total** | **31** | **153** |

`MHwh1` has only three intervals in the archive; every other label has five. The sample is
BEC-stratified and deterministic, not random.

The tree list uses the D3 donor aliases: `Ss`/`Sb` → `SE`, `Ba` → `BG`, `Hm` → `HW`, `Yc` → `CW`,
`Dr` → `AT`, `Mb` → `AC`. The aliases are exercised heavily: 2,448 `Ba`, 503 `Ss`, 289 `Hm`, 219
`Yc`, 149 `Dr`, 129 `Mb`, and 67 `Sb` tree records in the sampled intervals. Six intervals have
trees whose PSP code is outside the 15 and outside the donor map (`KC`, `WS`, `DG`, `XC`); those
trees are skipped and counted. No interval is skipped for a BEC-resolution failure.

## Result

Initial stand reproduction is good: mean initial BA bias **-0.78 m2/ha**, median **-0.26**, MAE
**1.14**. The remaining error is the growth path.

| Zone | n | observed mean BA1 | predicted mean BA1 | BA bias | BA MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CWH` | 105 | 67.21 | 54.90 | -12.31 | 13.04 |
| `CDF` | 5 | 68.65 | 48.20 | -20.45 | 20.45 |
| `BWBS` | 25 | 31.15 | 21.68 | -9.47 | 9.47 |
| `CMA` | 5 | 90.07 | 84.40 | -5.67 | 5.67 |
| `MH` | 13 | 89.30 | 76.85 | -12.46 | 12.80 |
| **All** | **153** | — | — | **-11.90** | **12.44** |

The median BA error is **-10.19 m2/ha**; the overall TPH bias is **-271.9** and MAE **401.4**. The
model underpredicts end BA in every zone of this sample. There is one envelope flag: `CWHvh`
predicted 157.0 against an observed 190.9, above the empirical p99; none are above the observed
maximum. The D5 one-interval five-zone MAEs were CWH 11.75, BWBS 7.93, CDF 18.85, CMA 3.46, MH
11.94; the five-interval sample is slightly worse in every zone, so the D5 result was not an
artifact of one favourable interval.

The largest absolute BA errors are all underprediction: `CWHvm` -38.5, `CWHwm` -35.2, `CWHvh`
-33.9, `BWBSwk2` -31.6, and `CWHds2` -30.4. The only substantial overprediction in the per-BEC
table is `CWHvm` at +24.11 on the one-interval D5 sample; it does not persist in the five-interval
sample. That is why the larger sample is the one used for the D6 decision.

## Species decision

**No species is promoted to a true table from this run.** The donor aliases are adequate for a
first five-zone baseline, but the residuals are a broad growth underprediction across `CWH`,
`CDF`, `BWBS`, `CMA`, and `MH`, not a clean donor-species signal. Promoting a species now would fit
a species effect to a sample whose dominant error is the shared growth path.

The first candidates, in order, are `Ba` → `BG` and `Hm` → `HW`, because they are the largest
donor groups in the coastal sample (2,448 and 289 records respectively) and their `BG`/`HW` rows
carry some of the largest negative TPH and BA biases. A true `Ba` table needs amabilis-fir
coefficients and a species-specific validation sample, neither of which exists in this work
package. The D7 calibration should first test whether the underprediction is a site-index or
density/growth error; only then is a true species table interpretable.

`Ss`/`Sb` → `SE`, `Yc` → `CW`, `Dr` → `AT`, and `Mb` → `AC` are also donor aliases, not true
species models. The `SpeciesFVS` output code remains the donor; no claim of species-specific
prediction is made for any of the seven.

## What this does not establish

- The five-zone extension is in `0.4.1` (released as `0.21.3`), but the wrapper still refuses the
  five zones. CI remains on the supported patch set until a five-zone oracle fixture exists.
- The site index is the baseline placeholder (`FD,20`); the PSP site index is not joined.
- The site series is the diagnostic `/01`; the per-plot site series is not in the extract.
- The sample is BEC-stratified, not random, and `MHwh1` has three intervals rather than five.
- No parameter is fitted and no species table is added. These are residuals for D7.
