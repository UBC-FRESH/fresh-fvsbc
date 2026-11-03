# D6.4 — the SBPS small-tree overflow and its fix

Status: fixed and published as `fresh-fvsbc-pyfvs 0.4.1`; the wrapper `fvs` extra moves to it in
`fresh-fvsbc 0.21.3`.

Evidence: `d6-sbps-fixed.csv`, and the four SBPS runs under
`.opencode/tmp/opencode/d6-sbps-fixed-default/` (local run directory).

## The symptom

D5 found the four SBPS intervals exploding while their initial stands reproduced:

| BEC | observed BA1 | D5 predicted BA1 | observed TPH1 | D5 predicted TPH1 |
| --- | ---: | ---: | ---: | ---: |
| `SBPSdc` | 11.23 | 4,705.0 | 1,889.9 | 691.0 |
| `SBPSmc` | 30.65 | 457,348.0 | 4,453.0 | 2,762.0 |
| `SBPSmk` | 32.72 | 3,531.0 | 620.1 | 635.0 |
| `SBPSxc` | 34.39 | 10.0 | 2,776.9 | 360.0 |

The initial metric rows were normal (QMD 8.6 cm on `SBPSmc`, BA 31 m2/ha), so the defect was in
the growth or mortality path, not the tree-list handoff. A `MORTMULT` grid made the numbers smaller
but never physical; `BAMAX` was a cliff (30 killed the stand, 31 still produced 33 m2/ha and 32
produced 19,474 m2/ha). Those were symptoms, not levers.

## The root cause

`REGENT` has two small-tree height forms. The `SBS`/`SBPS` fitted models are the hyperbolic form:

```
HTGRL = (CON + HT * H1) /
        (1 + EXPMLT * EXP(HCCFL * H1 / MAX(CCFL,36) + CCFSL * CCFS / MAX(CCFL,36)))
```

The other form is exponential and is for the IDF/ICH models:

```
HTGRL = EXP(CON + LNHT * log(H1) + HT * H1 + BAL * BAL_term + CCF * RDJ)
```

`canada/bc/regent.f` selected the hyperbolic form with `INDEX(BEC%Zone,'SBS') .GT. 0`. `SBPS`
does **not** contain the substring `SBS` (`S B P S`), so every SBPS stand took the exponential
branch. The `ST_COEF` values for PL/SE in SBPS are the SBS-form coefficients; for `SBPSmc` PL the
constant is `301.2` and the height term is `14.4134`. The exponential branch therefore computed
`HTGRL` near 380, `EXP(380)` overflowed to `Infinity`, and the small-tree diameter was assigned
from `Infinity`:

```
REGENT: HTGRL         Infinity
REGENT: H2            Infinity
I,ISPC,AA,BB,DADJ,H1,D1,H2,D2,DGJ=  1 7 ... 18.04 2.30 Infinity Infinity Infinity
```

The finite tree list then carried DBHs in the hundreds of centimetres and QMD 1,451 cm, which is
the 457,348 m2/ha summary.

The five `INDEX(BEC%Zone,'SBS')` tests in `regent.f` are all on the same model selection:

- the cumulative small-tree CCF calculation in both `REGENT` entry paths;
- the subcycle `CCFS`/`CCFL` calculation;
- the subcycle height-growth form;
- the final diameter/height assignment form.

Each now accepts `SBS` **or** `SBPS`.

## The patch

`w4-sbps-small-tree.patch.gz` (sha256
`738ad50e08abb9d41166cfc1fa837a1086f756b07e106ec5820baaee42245c27`) changes
`canada/bc/regent.f` only, with five condition hunks. It applies after the base patch set and the
W2/W3 patches. The local build is:

```bash
SETUPTOOLS_SCM_PRETEND_VERSION=0.4.1 \
  python -m pip wheel --no-build-isolation --no-deps . \
  --config-settings=setup-args="-Dfvsvariants=bc"
```

`pyfvs.list_variants()` reports `{'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}`.

The regression test is `tests/test_d6_sbps.py`: a dense 10-tree PL stand below the 4.5-inch
small-tree threshold in `SBPSmc`. On the local 0.4.1 build it passes (end BA below 200 m2/ha); on
the pre-fix 0.4.0 wheel it fails with an end BA of **36,077 m2/ha**. The test skips when the
extension is absent, like the other extension cases.

## Corrected SBPS baseline

Same D5 sample, same keywords, no calibration:

| BEC | observed BA1 | fixed predicted BA1 | observed TPH1 | fixed predicted TPH1 | observed QMD | fixed predicted QMD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `SBPSdc` | 11.23 | 28.0 | 1,889.9 | 1,937.0 | 8.70 | 13.68 |
| `SBPSmc` | 30.65 | 48.0 | 4,453.0 | 4,242.0 | 9.36 | 12.05 |
| `SBPSmk` | 32.72 | 35.0 | 620.1 | 842.0 | 25.92 | 23.31 |
| `SBPSxc` | 34.39 | 53.0 | 2,776.9 | 2,725.0 | 12.56 | 15.73 |

The catastrophe is gone and the corrected numbers are physical. They are still biased:

- `SBPSdc` is 2.49x the observed BA and 1.57x the QMD; the stand is too sparse in TPH but has too
  much diameter growth.
- `SBPSmc` is 1.57x the observed BA and 1.29x the QMD, with essentially the observed TPH.
- `SBPSmk` is only 1.07x the observed BA but has 1.36x the TPH and a smaller QMD.
- `SBPSxc` is 1.54x the observed BA and 1.25x the QMD.

There are no envelope flags in the fixed run; the residuals are the calibration target for D7, not
a claim that SBPS is calibrated. `SBPSmc` also sits near the default `BAMAX` of 50 m2/ha, which is
one candidate for the D7 parameter fit, not a D6 patch.

## Corrected all-zone context

The same D5 sample was rerun on the fixed 0.4.1 build with the D3 donor alias layer: **139 intervals,
139 BECs, 0 skipped**. The initial stand is unchanged (BA bias -0.69, MAE 0.84). The end-of-interval
BA bias is **-4.17 m2/ha** and MAE **8.65** over all rows; the all-row mean is now usable. There are
five `above_max` flags and one `above_p99` flag. The corrected SBPS rows above replace the D5
`SBPS` rows; no other supported-zone row changes materially. The all-zone rerun uses the D3 donor
alias layer (`Ba` -> `BG` rather than the D5 `BL`), so it is not a byte-for-byte reproduction of D5.

## What this does not establish

- The build is local. The CI/wheel recipe now applies `w4-sbps-small-tree.patch.gz` and builds
  `fresh-fvsbc-pyfvs 0.4.1`; the wrapper pin moves to it in `0.21.3`.
- The wrapper source still refuses `CWH`, `CDF`, `BWBS`, `CMA`, and `MH`; the five-zone baseline
  uses the prototype parser patch at runtime. That is a separate release task.
- The fix does not prove the SBPS growth, mortality, or regeneration coefficients are calibrated.
  It removes an overflow that made the residuals uninterpretable.
- The D5 all-zone summary still carries the pre-fix SBPS rows. The corrected SBPS rows above are
  the D6 replacement; a full all-zone rerun is the next comparison, not a release claim.
