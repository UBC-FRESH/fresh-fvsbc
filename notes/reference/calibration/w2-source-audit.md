# W2 source audit

Status: audit for the go/no-go; no Fortran changed
Date: 2026-11-02
Pins: PyFVS `e95172b`; FVS source `ef5fa8470cc89f81ca445e7c906e274f200e80fd`
Gap table: `w2-source-gaps.csv`
Crosswalk: `w2-crosswalk.md`

This note reads the pinned source, not `main`. It records what the BC variant
can carry today and what a full-domain extension would need.

## 1. What the source has

| Component | File | What exists |
| --- | --- | --- |
| Regions | `canada/bc/habtyp.f` 30–32 | `CAR`, `KAM`, `NEL` |
| Zones | `canada/bc/habtyp.f` 34–40 | `ESSF`, `ICH`, `IDF`, `MS`, `PP`, `SBS`, `SBPS` |
| Subzones | `canada/bc/habtyp.f` 42–60 | 19 two-letter tokens |
| Species | `canada/bc/blkdat.f` 74–75 | 15 `JSP` species |
| Default max BA | `canada/bc/sitset.f` 61–242 | A subset of subzones and site series |
| Large-tree DG | `canada/bc/becset.f` | 15 species; 12 subzone modifiers; V3 for ICH/IDF/SBS/SBPS, V2 for ESSF/MS/PP |
| Height growth | `canada/bc/htgf.f` 111–127, 134–1226 | 15 species; 44 BEC/site-series entries |
| Mortality | `canada/bc/morts.f` 203–349, 1096–1107 | 15 species; tabular classes only for ICH and IDF |
| Crown | `canada/bc/crown.f` 91–143 | 15 species |
| Bark | `canada/bc/bratio.f` 26–30 | 15 species |
| Diameter variance | `canada/bc/dgdriv.f` 104–107 | 15 species |
| Volume/taper | `canada/bc/min.f` 90–92 | 15 species mapped to Kozak codes |
| Regeneration | `canada/bc/regent.f` 186–208 | 15 species arrays; 27 `ST_COEF` entries |
| Site index | `canada/bc/initre.f` 477–481 | **not used in this variant** |

The full matrix with line references is in `w2-source-gaps.csv`.

## 2. The three findings that change the plan

### 2.1 Site index is not a gap

`initre.f` 477–481 prints: **"SITE INDEX IS NOT USED IN THIS VARIANT."** The
`SITECODE` and `SETSITE` keywords are accepted and the values are reported, but
the growth engine does not use them. W2 does not need coastal or boreal
site-index curves. The W2 package's site-index row is corrected.

### 2.2 Default max BA is partial, and the fallback is 10 m²/ha

`sitset.f` 61–242 covers a subset: IDF dk1–4, dm1–2, mw1–2, xh1–2, xm; ICH mk1,
mw2, mw3, wk1, dw; ESSF dk, wc4, wm; MS dk, dm1; PP dh2, xh2; all SBS; all SBPS.
A unit outside those cases falls through to lines 244–250, where `BAMAX` is set
to **10 m²/ha** with a warning.

That is not a safe default for a new zone or subzone. W2.3 must either add a
source-backed default or refuse the unit explicitly. A parser-only extension
that leaves the 10 m²/ha fallback is worse than no extension.

### 2.3 Mortality has only two tabular classes

`morts.f` 1096–1107 sets `BECCLS` to ICH or IDF:

- ICH: ICH, SBS (except `SBSdw2`), and the default;
- IDF: IDF, SBPS, and `SBSdw2`.

ESSF, MS, and PP therefore use the **ICH** mortality table by default. That is a
pre-existing structural assumption in the supported zones, not only a missing-
zone problem. A new zone would inherit it unless a table is added.

## 3. Species model

Every major component is indexed by the 15 `JSP` species:

- species list and FIA/plant codes (`blkdat.f`);
- large-tree DG, height growth, mortality, crown, bark, diameter variance,
  volume/taper, regeneration.

The seven high-priority species from `w2-crosswalk.md` are absent from all of
them:

| Code | Species | Components that need an entry |
| --- | --- | --- |
| `DR` | red alder | species list, DG, height, mortality, crown, bark, volume, regeneration |
| `SS` | Sitka spruce | same; plus the spruce-group decision |
| `BA` | amabilis fir | same |
| `HM` | mountain hemlock | same |
| `YC` | yellow-cedar | same |
| `SB` | black spruce | same; spruce-group decision |
| `MB` | bigleaf maple | same |

Adding a species is not a parser change. It is a parameter-development task in
every table.

## 4. Go/no-go

| Target | Answer | Why |
| --- | --- | --- |
| 18 subzones with PSP data | **Partial go** | The zones are supported; 18 of 19 are in CCISS. Adding the parser tokens and source-backed `BAMAX` defaults is tractable. Growth/mortality for ESSF/MS subzones still use V2/ICH defaults and must be validated, not claimed. |
| `CWH` | **No-go without a parameter source** | 19 BGC units, six missing species, no growth/mortality/crown/bark/volume/regeneration tables. A parser-only extension would use ICH mortality and the 10 m²/ha fallback. |
| `CDF` | **No-go without a parameter source** | One BGC unit and two main missing species, but the same model-table gap. Smaller scope, not a wrapper task. |
| `BWBS` | **No-go without a parameter source** | Seven BGC units; `Sb`/`Lt` missing; no BWBS growth/mortality tables. `Sx` may map to `SE`, but that is a modelling decision. |
| `MH` | **No-go without a parameter source** | Eight BGC units; four missing species; no mountain-hemlock/amabilis/yellow-cedar tables. |
| `CMA` | **No-go** | Three units, no CCISS suitability rows; no evidence base. |

The honest conclusion: **the 18 subzones are a bounded W2.3 task; the five zones
are a separate parameter-development project.** A source change that only makes
the parser accept the five zones would produce plausible wrong numbers, which is
the failure this programme exists to prevent.

## 5. What W2.3 should do

1. Add the 18 subzones with PSP data to `habtyp.f`, with source-backed `BAMAX`
   defaults in `sitset.f`; refuse any unit that has no default.
2. Check the V2/V3 calibration path for each subzone; record which use ICH/IDF
   mortality and which have a real subzone modifier.
3. Add no new species unless the subzone evidence shows one is needed; the
   interior 15 cover most of the 18.
4. Build and smoke-test each subzone; compare the default `BAMAX` echo and a
   no-cut run with the PSP envelope.
5. Leave the five zones as a separate go/no-go with a coastal/boreal partner and
   a parameter source.

## 6. Claim boundary

This is a source audit. It does not add a zone, a species, or a parameter. It
says what the pinned source can carry and what a real extension would require.
The five-zone answer may be "not feasible without X"; that is a valid W2 result.
