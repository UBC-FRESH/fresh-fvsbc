# W2.3 subzone patch

Status: patch prepared and apply-checked; not built or pinned
Date: 2026-11-02
Patch: `w2-subzones.patch.gz`
Defaults: `w2-subzone-defaults.csv`
Audit: `w2-source-audit.md`
Pins: FVS `ef5fa8470cc89f81ca445e7c906e274f200e80fd`; PyFVS `e95172b`

This is the bounded W2.3 change from the audit. It adds the 19 supported-zone
subzones with PSP data to the parser and gives each a **provisional** default
maximum basal area. It does not add the five zones or any species.

## 1. The patch

`w2-subzones.patch.gz` changes two files:

- `canada/bc/habtyp.f`: `SZ` grows from 19 to 29 and gains `DH`, `DV`, `MV`,
  `VC`, `WH`, `WV`, `XV`, `XW`, `XX`, `UN`.
- `canada/bc/sitset.f`: adds default `BAMAX` cases for the 19 subzones.

The patch was generated against the pinned source and `git apply --check`
passes after decompression. It is not committed to the FVS fork yet, and the BC variant has not been
rebuilt from it.

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
- It does not build or pin the fork. That is the next step.

## 4. Build and smoke plan

```bash
# 1. a clean PyFVS fork at the pin
git clone https://github.com/UBC-FRESH/PyFVS
git -C PyFVS checkout e95172b
git -C PyFVS submodule update --init --recursive

# 2. apply the W2.3 patch to the FVS source submodule
gunzip -c w2-subzones.patch.gz > /tmp/w2-subzones.patch
git -C PyFVS/fvs apply /tmp/w2-subzones.patch

# 3. build the BC variant
SETUPTOOLS_SCM_PRETEND_VERSION=0.3.11 \
  python -m pip install --no-build-isolation ./PyFVS \
  --config-settings=setup-args="-Dfvsvariants=bc"

# 4. for each subzone, run one case with STDINFO=CAR,<bec>/01,...
#    and read run.out for:
#      STDINFO    BEC=<bec>/01
#      MAXIMUM BASAL AREA FOR <bec>/01 IS SET BY DEFAULT TO: <value> SQ M/HA
```

Smoke cases:

- 19 subzones, one case each.
- The existing seven zones, one case each.
- The official case, unchanged.

Acceptance for the build step:

- Every subzone echoes its code.
- The default BAMAX echo matches `w2-subzone-defaults.csv`.
- Every smoke run writes a database.
- The existing case is unchanged.
- The new FVS and PyFVS pins are recorded here, and the patch set is banked.

## 5. Claim boundary

This is a patch and a plan. The variant does not yet resolve the subzones in a
released build. The defaults are provisional and the mortality model is still
the existing default. W4 calibrates; W2.3 only makes the subzone representable.
