# Five-zone species donor aliases

Status: implemented and smoke-tested on 2026-11-03; not in a released pin
Code: `fresh_fvsbc.treelist.DONOR_SPECIES`, `resolve_species`
Evidence: `w2-five-zone-species-smoke.csv`

The seven high-priority missing species now pass through the wrapper as **explicit donor aliases**.
The tree list carries the donor code, not the caller's code; that is the substitution this phase
records, and D6 owns the true species tables.

## 1. The aliases

| Input | Species | Donor | Why |
| --- | --- | --- | --- |
| `Ss` | Sitka spruce | `SE` | same spruce group |
| `Sb` | black spruce | `SE` | same spruce group |
| `Ba` | amabilis fir | `BG` | nearest true fir in the 15 |
| `Hm` | mountain hemlock | `HW` | same hemlock group |
| `Yc` | yellow-cedar | `CW` | same cedar group |
| `Dr` | red alder | `AT` | pioneer broadleaf |
| `Mb` | bigleaf maple | `AC` | broadleaf |

`resolve_species` tries the 15 `JSP` codes, the FIA codes, and the PLANTS symbols first; a code that
is not in any of them is looked up in `DONOR_SPECIES`. An unknown code still raises
`UnknownSpeciesError`, and the message names the donor aliases. The alias is not a silent fallback:
the mapping is explicit, public, and tested.

## 2. Smoke

Built against the local `fresh-fvsbc-pyfvs 0.4.0` five-zone extension. Each case used the species
code as the caller supplies it and a five-zone BEC:

| Input | BEC | BEC echo | BAMAX | `SpeciesFVS` out | Database |
| --- | --- | --- | ---: | --- | --- |
| `SS` | `CWHdm/01` | `CWHdm/01` | 112 | `SE` | yes |
| `SB` | `BWBSdk/01` | `BWBSdk/01` | 51 | `SE` | yes |
| `BA` | `CWHdm/01` | `CWHdm/01` | 112 | `BG` | yes |
| `HM` | `CWHdm/01` | `CWHdm/01` | 112 | `HW` | yes |
| `YC` | `CWHdm/01` | `CWHdm/01` | 112 | `CW` | yes |
| `DR` | `CWHdm/01` | `CWHdm/01` | 112 | `AT` | yes |
| `MB` | `CWHdm/01` | `CWHdm/01` | 112 | `AC` | yes |

**7/7 pass.** The `SpeciesFVS` column is the donor, and `w2-five-zone-species-smoke.csv` is the
record.

## 3. What this does not do

- It does not add true species-specific growth, mortality, crown, bark, volume/taper, or
  regeneration tables. D6 owns that.
- It does not make the five zones a released pin. The five-zone patch is banked; the wrapper still
  refuses the five zones until the new extension is pinned.
- It does not test the donor coefficients against species-specific PSP data. D5 measures the
  residuals; D6 promotes a species to a true table where the donor fails.

## 4. Tests

`tests/test_treelist.py` covers:

- each of the seven aliases, in upper and lower case;
- the donor code written into the tree-list record;
- an unknown code still raising `UnknownSpeciesError`, with the donor list in the message;
- the existing 15 `JSP`, FIA, PLANTS, and ambiguity paths unchanged.
