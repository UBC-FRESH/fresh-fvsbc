# W2.3 subzone patch

Status: built, smoke-tested, and banked; pinned by the base source plus this patch
Date: 2026-11-02; build and smoke 2026-11-03
Patch: `w2-subzones.patch.gz` (`sha256:ee019bbede50b75edd6066b6f3bc9d3554d846aa6a0b1bb432f2de442b157ce3`)
Defaults: `w2-subzone-defaults.csv`
Smoke: `w2-subzone-smoke.csv`
Audit: `w2-source-audit.md`
Pins: FVS `ef5fa8470cc89f81ca445e7c906e274f200e80fd`; PyFVS `e95172baec0143bd8ccf2c0d21f9f5ffc62da601`

This is the bounded W2.3 change from the audit. It adds the 19 supported-zone
subzones with PSP data to the parser and gives each a **provisional** default
maximum basal area. It does not add the five zones or any species.

## 1. The patch

`w2-subzones.patch.gz` changes two Fortran files:

- `canada/bc/habtyp.f`: `SZ` grows from 19 to 29 and gains `DH`, `DV`, `MV`,
  `VC`, `WH`, `WV`, `XV`, `XW`, `XX`, `UN`; the subzone search loop widens
  from `DO I = 1,19` to `DO I = 1,29`. **The loop bound is part of the fix.**
  The first build widened only the array, so the new tokens were never searched
  and every case fell back to `ICHmw2/01`.
- `canada/bc/sitset.f`: adds default `BAMAX` cases for the 19 subzones.

The same change set updates `src/fresh_fvsbc/bec.py` so the wrapper accepts the
new tokens, and adds a test that all 19 codes parse. Without that change the
wrapper refuses the codes before FVS sees them.

The patch was generated against the pinned source, applies after the base
`fvsbc-patchset.diff.gz`, and was applied to a clean `ef5fa847` worktree in the
build. This project's recipe pins the base commits and applies the banked patch
sets; the W2.3 patch is not an FVS upstream commit. The exact build is the two
base commits plus the three patch hashes recorded here and in the changelog.

## 2. The 19 subzones

| BEC | Zone | Token | PSP p99 | PSP max | Provisional BAMAX |
| --- | --- | --- | ---: | ---: | ---: |
| `ESSFdh1` | ESSF | `DH` | 77.1 | 77.7 | 77 |
| `ESSFdv1` | ESSF | `DV` | 75.8 | 75.9 | 76 |
| `ESSFmv` | ESSF | `MV` | 78.0 | 102.5 | 78 |
| `ESSFmv1` | ESSF | `MV` | 39.5 | 40.0 | 40 |
| `ESSFmv2` | ESSF | `MV` | 55.7 | 55.8 | 56 |
| `ESSFmv3` | ESSF | `MV` | 77.9 | 85.3 | 78 |
| `ESSFmv4` | ESSF | `MV` | 63.2 | 64.9 | 63 |
| `ESSFvc` | ESSF | `VC` | 17.0 | 17.0 | 17 |
| `ESSFwh1` | ESSF | `WH` | 75.6 | 83.3 | 76 |
| `ESSFwv` | ESSF | `WV` | 47.1 | 47.2 | 47 |
| `ESSFxv2` | ESSF | `XV` | 43.4 | 43.6 | 43 |
| `ICHvc` | ICH | `VC` | 76.9 | 77.3 | 77 |
| `ICHxw` | ICH | `XW` | 47.0 | 47.4 | 47 |
| `IDFdh` | IDF | `DH` | 43.6 | 43.9 | 44 |
| `IDFxw` | IDF | `XW` | 31.3 | 34.0 | 31 |
| `IDFxx2` | IDF | `XX` | 42.7 | 43.2 | 43 |
| `MSxv` | MS | `XV` | 54.8 | 56.4 | 55 |
| `SBSdh1` | SBS | `DH` | 74.6 | 79.1 | 75 |
| `SBSun` | SBS | `UN` | 16.1 | 16.2 | 16 |

The default is the PSP p99 rounded to the nearest integer. It is a **provisional
capacity target**, not a calibrated parameter. Some p99 values are high because
the subzone has few plots or a high-BA outlier; the value is recorded with its
source and W4 owns the final capacity decision.

## 3. What the patch does not do

- It does not add the five zones or the seven missing species.
- It does not change the mortality table. ESSF/MS subzones still use the V2/ICH
  default; SBS uses ICH except `SBSdw2`, and SBPS uses IDF.
- It does not remove the 10 m²/ha fallback for a unit outside these cases. The
  19 subzones avoid it; another unit can still reach it.
- It does not commit the patch to an upstream FVS branch. The project's build
  recipe pins the base commits and applies the banked patch sets.

## 4. Build and smoke result

The BC variant was built from a clean clone on 2026-11-03:

```bash
git clone https://github.com/UBC-FRESH/PyFVS.git
git -C PyFVS checkout e95172b
git -C PyFVS submodule update --init --recursive

# base patch sets recorded by ADR 0004
gunzip -c fvsbc-patchset.diff.gz > /tmp/fvsbc.patch
gunzip -c pyfvs-patchset.diff.gz > /tmp/pyfvs.patch
git -C PyFVS/fvs apply /tmp/fvsbc.patch
git -C PyFVS apply /tmp/pyfvs.patch

# W2.3, after the base FVS patch
gunzip -c w2-subzones.patch.gz > /tmp/w2-subzones.patch
git -C PyFVS/fvs apply /tmp/w2-subzones.patch

SETUPTOOLS_SCM_PRETEND_VERSION=0.3.11 \
  python -m pip install --no-build-isolation ./PyFVS \
  --config-settings=setup-args="-Dfvsvariants=bc"
```

The three patch hashes are `fvsbc-patchset.diff.gz`
`sha256:ed2afe44ac78443950641a48bc9325489c8a046dcae81cc1bfac08d33f049323`,
`pyfvs-patchset.diff.gz`
`sha256:cc8643a6948b99c445b6fbf8da8bcba40c36ca6667759d56433c8de8220b0ccb`,
and `w2-subzones.patch.gz`
`sha256:ee019bbede50b75edd6066b6f3bc9d3554d846aa6a0b1bb432f2de442b157ce3`.

- **The build imports**: `pyfvs.list_variants()` returns
  `{'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}`.
- **The wrapper checks the resolved BEC**: `run_case` compares the run's
  `STDINFO BEC=` echo with the requested code and raises `BecCodeError` when
  they differ. An older build that falls back to `ICHmw2/01` now fails loudly
  instead of returning a plausible run.
- **19 smoke cases**: a synthetic FD stand, site 100, `CAR <bec>/01`, a
  10-year cycle, one cycle, seed 1. Every run wrote `run.out` and `FVSOut.db`.
- **19/19 echoed `STDINFO BEC=<bec>/01`.**
- **19/19 echoed the expected default BAMAX value** from
  `w2-subzone-defaults.csv`; the evidence is `w2-subzone-smoke.csv`.
- **The capability has a test**: `tests/test_w2_subzones.py` runs one case per
  subzone, asserts the BEC echo, the default BAMAX value, and the database, and
  is part of the CI extension job.
- **The existing suite is unchanged**: the official case matched its oracle and
  `tests/test_bec.py`, `tests/test_run.py`, and `tests/test_oracle.py` reported
  `108 passed, 1 skipped`.

### Echo caveat for ESSF and MS

For the 11 ESSF subzones and `MSxv`, the default-BAMAX line names `MSdk/01`.
For `ESSFdh1` it reads:

```text
MAXIMUM BASAL AREA FOR MSdk/01        IS SET BY DEFAULT TO:  77.0 SQ M/HA.
```

The **value** is the new case; the MSdk series-1 default is 48, not 77. The
`STDINFO BEC=ESSFdh1/01` line is also correct. The label changes because
`SITSET` calls `BECSET` first, and `BECSET` rewrites `BEC%PrettyName` to its V2
default when the subzone has no V2 parameter set (`becset.f` 935–942). That is
the existing V2 behavior, not the new default. W2.3 does not change it. Match
the value against the table; do not read the BAMAX label as the habitat code
that selected the case.

## 5. Claim boundary

This is a parser and default-BAMAX patch, not a calibration. It makes 19
supported-zone subzones representable and gives each a provisional capacity
default. ESSF/MS growth and mortality still use the V2/ICH defaults. The five
zones and the seven missing species remain out. The default is PSP p99, not a
fitted capacity; W4 owns the final decision. The patch is now in the repository's
build recipe: CI, the wheels workflow, and `docs/installation.rst` apply it. A
released wheel is not claimed until this change set ships and that workflow runs.
