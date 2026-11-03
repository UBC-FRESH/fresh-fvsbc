# W2.3 subzone patch

Status: built and smoke-tested; banked as the third build-time patch set; wheel `0.3.12` not published
Date: 2026-11-03
Patch: `w2-subzones.patch.gz`
Defaults: `w2-subzone-defaults.csv`
Audit: `w2-source-audit.md`
Base pins: FVS `ef5fa8470cc89f81ca445e7c906e274f200e80fd`; PyFVS `e95172b`
Patch SHA-256: `ee019bbede50b75edd6066b6f3bc9d3554d846aa6a0b1bb432f2de442b157ce3`
Wheel version: `fresh-fvsbc-pyfvs 0.3.12` (built, not published)

This is the bounded W2.3 change from the audit. It adds the 19 supported-zone
subzones with PSP data to the parser and gives each a **provisional** default
maximum basal area. It does not add the five zones or any species.

## 1. The patch

`w2-subzones.patch.gz` changes two files:

- `canada/bc/habtyp.f`: `SZ` grows from 19 to 29 and gains `DH`, `DV`, `MV`,
  `VC`, `WH`, `WV`, `XV`, `XW`, `XX`, `UN`. **`HABTYP`'s loop must grow too**:
  the first patch left `DO I = 1,19`, so the ten new tokens were never searched;
  the corrected patch uses `DO I = 1,29`.
- `canada/bc/sitset.f`: adds default `BAMAX` cases for the 19 subzones.

The patch is generated against the pinned source and applies after the two
existing patch sets (ADR 0006). It is banked here as the **third build-time
patch set**; the FVS source pin does not move (ADR 0013).

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
- It does not publish the wheel or move the `fvs` extra pin. W2.3 closes when
  `fresh-fvsbc-pyfvs 0.3.12` is published and the wrapper accepts the subzones.

## 4. Build and smoke evidence

Built on 2026-11-03 from a clean PyFVS checkout at `e95172b` with the FVS source
at `ef5fa847`, applying all three patch sets:

```bash
git clone https://github.com/UBC-FRESH/PyFVS
git -C PyFVS checkout e95172b
git -C PyFVS submodule update --init --recursive
gunzip -c pyfvs-patchset.diff.gz  | git -C PyFVS apply -
gunzip -c fvsbc-patchset.diff.gz  | git -C PyFVS/fvs apply -
gunzip -c w2-subzones.patch.gz    | git -C PyFVS/fvs apply -
SETUPTOOLS_SCM_PRETEND_VERSION=0.3.12 \
  python -m pip wheel --no-build-isolation --no-deps ./PyFVS \
  --config-settings=setup-args="-Dfvsvariants=bc"
```

The wheel built and imported, and `pyfvs.list_variants()` reported
`{'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}`.

**19/19 subzones pass**: each echoed its own BEC and the expected provisional
`BAMAX`, and each wrote a database. The existing-zone controls were unchanged:
`ESSFdk/01` 64, `ICHmw2/01` 89, `IDFdk3/01` 53, `MSdm1/01` 63, `PPxh2/01` 32,
`SBSmc2/01` 55, `SBPSmk/01` 55.

The first build **failed the subzone smoke** because `HABTYP` still looped to
19; `ESSFdh1/01` echoed `ICHmw2/01`. The loop fix is why the corrected patch is
the banked one.

## 5. Pins and release state

- FVS base pin: `ef5fa8470cc89f81ca445e7c906e274f200e80fd` (unchanged).
- PyFVS base pin: `e95172b` (unchanged).
- Third patch: `w2-subzones.patch.gz`, SHA-256 above.
- Wheel built: `fresh-fvsbc-pyfvs 0.3.12`; not published.
- `pyproject.toml`'s `fvs` extra remains `0.3.11` until `0.3.12` is published.
- The wrapper's new `SUBZONES` tokens must land **with** the `0.3.12` pin, not
  before it; `0.3.11` does not carry the patch and would fall back to `ICHmw2/01`.

CI and `wheels.yml` apply the third patch and build `0.3.12`; `docs/installation`
names the three-patch recipe. ADR 0013 records the decision.

## 6. Claim boundary

This is a patch and a build, not a released pin and not a calibration. The
defaults are provisional and the mortality model is still the existing default.
W4 calibrates; W2.3 only makes the subzone representable.
