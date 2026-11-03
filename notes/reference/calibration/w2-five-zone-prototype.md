# Five-zone prototype: parser, defaults, and 32-label smoke

Status: built and smoke-tested on 2026-11-03; **not pinned, not released**
Base pins: PyFVS `e95172baec0143bd8ccf2c0d21f9f5ffc62da601`; FVS `ef5fa8470cc89f81ca445e7c906e274f200e80fd`
Patches: `w2-subzones.patch.gz` (the 19 supported-zone subzones), then `w2-five-zone.patch.gz`
Wheel: `fresh-fvsbc-pyfvs 0.4.0` (local build)

This is the runnable prototype for the five zones. It adds `CWH`, `CDF`, `BWBS`, `CMA`, and `MH` to the
BEC parser and gives the 32 PSP labels a provisional `BAMAX`. Species are the existing 15 `JSP` codes;
the seven high-priority species are donor-mapped by `bcspp.f` for this prototype.

## 1. Parser changes

`canada/bc/habtyp.f`:

- `ZN(7)` → `ZN(12)`; add `CWH`, `CDF`, `BWBS`, `CMA`, `MH`.
- `SZ(29)` → `SZ(34)`; add `DS`, `MS`, `VH`, `VM`, `WS`.
- Zone loop `DO I = 1,7` → `1,12`; subzone loop `DO I = 1,29` → `1,34`.
- **Anchor the grammar.** The first attempts failed because `CWH` contains `WH` and `MH` contains `MH`, so
  the subzone search matched inside the zone name. The parser now checks the region at columns 1–3, the
  zone immediately after it, and the subzone only after the zone. `CWHms1` also exposed that a zone token
  (`MS`) could be found inside a subzone; anchoring fixes both classes.

`canada/bc/sitset.f` adds cases for all 32 labels, with the provisional `BAMAX` values from
`w2-five-zone-defaults.csv`.

## 2. Build and smoke

Built from the pinned fork with the base patch sets, `w2-subzones.patch.gz`, and
`w2-five-zone.patch.gz`:

```bash
SETUPTOOLS_SCM_PRETEND_VERSION=0.4.0 \
  python -m pip wheel --no-build-isolation --no-deps . \
  --config-settings=setup-args="-Dfvsvariants=bc"
```

`pyfvs.list_variants()` reports `{'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}`.

**32 of 32 labels pass**: each echoes its own `STDINFO BEC=`, echoes the expected provisional `BAMAX`,
and writes `FVSOut.db`. The evidence is `w2-five-zone-smoke.csv`.

| Zone | Labels | Result |
| --- | ---: | --- |
| CWH | 22 | all pass |
| BWBS | 5 | all pass |
| CDF | 1 | pass |
| MH | 3 | all pass |
| CMA | 1 | pass |

This is a parser/defaults prototype. It does **not** prove the growth, mortality, crown, bark, volume, or
regeneration coefficients for the five zones. The smoke population is `FD`; the seven missing species are
mapped by `bcspp.f` to donors and must be tested with species-specific populations in D3.

## 3. Donor mappings in this prototype

`canada/bc/bcspp.f` already maps most of the missing species:

| Species | First-pass donor | Note |
| --- | --- | --- |
| `Ss` Sitka spruce | `SE` | same spruce group |
| `Sb` black spruce | `SE` | same spruce group |
| `Ba` amabilis fir | other conifer (`OC`) | no true balsam/amabilis table yet |
| `Hm` mountain hemlock | `HW` | same hemlock group |
| `Yc` yellow-cedar | other conifer (`OC`) | no true yellow-cedar table yet |
| `Dr` red alder | other hardwood (`OH`) | no true alder table yet |
| `Mb` bigleaf maple | other hardwood (`OH`) | no true maple table yet |

The wrapper's tree-list writer may refuse a species code outside the 15; D3 owns the alias layer and the
species-specific smoke.

## 4. What the patch does not do

- It does not add the seven species to `MAXSP` or to the growth/mortality/crown/bark/volume/regeneration
  arrays.
- It does not calibrate the five zones. `BAMAX` is PSP p99, provisional; the mortality/growth defaults
  are the existing BC tables.
- It is not in a released wheel. `w2-five-zone.patch.gz` is applied by the CI/wheel recipe and builds
  local `0.4.1`, but that wheel is not published; the wrapper still refuses the five zones.

## 5. Next

1. D3: species alias layer and one smoke per missing species.
2. D4: add the five-zone patch to the build recipe, build, and record the pin. The recipe now builds
   local `0.4.1`; publication and the wrapper pin are still open.
3. D5: all-zone baseline; this is where the five-zone coefficients get measured.
