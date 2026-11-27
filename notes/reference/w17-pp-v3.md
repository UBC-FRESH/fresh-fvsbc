# W17: PP on the V3 path

Status: **built and calibrated on the PP fold.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w17-pp-v3.patch.gz`, applied after `w16-essf-v3.patch.gz`.
Bundles: none.

## 1. Why

After W16, PP was the only zone left on V2 (27 intervals, 10 sites). W13/W14 had already given it its
measured caps and its site series, but the zone still ran the legacy growth code: predicted BA often
ended below its start while measured stands gained 3–4 m²/ha, and the fold sat at **−4.98 m²/ha**.

## 2. What changed

The five-file package, anchored on the W16 state:

- **`becset.f`**: `PP` joins the `LV2ATV` list.
- **`regent.f`**: `PP` joins the five small-tree/height zone lists; `PP/all` on the pooled row.
- **`dgf.f`**: two `ZNKONST` rows (60–61) for FD and PY; `PP/all` on the zonal site-series row;
  `P_ZN` 59 → 61.
- **`htgf.f`**: two `LTHG` blocks (72–73) for FD and PY; `P_MD` 71 → 73.
- **`morts.f`**: `PP/all` on the hardwood row; conifers keep the tabular mortality.

Rows are appended; nothing renumbers. SE, BL, AT, and PL keep their donors.

With PP on V3 the habitat table is skipped, so the W14 site-series mapping is bypassed for PP (it is
kept for the label grammar). The W13 caps still apply: they come from `sitset.f`, which runs for every
path.

## 3. Fits

Diameter growth, live pairs 10.16–80 cm:

| Species | n | r² | Observed | Fitted |
| --- | ---: | ---: | ---: | ---: |
| FD | 625 | 0.158 | 0.237 | 0.208 |
| PY | 320 | −0.008 | 0.129 | 0.105 |

Height growth, dominant and codominant pairs, ten-year increments:

| Species | n | r² | Observed | Fitted |
| --- | ---: | ---: | ---: | ---: |
| FD | 649 | 0.274 | 2.071 | 2.025 |
| PY | 254 | 0.052 | 0.862 | 0.773 |

**PY's diameter fit explains nothing** (r² −0.008): with 320 pairs the form has no signal, and only the
level is defensible. It was still preferred to the ICH donor on the fold; if a future fold shows
otherwise, the switch is one row. This is recorded rather than hidden.

## 4. Evidence
> **In-sample.** The table below uses the intervals the rows were fitted from. The
> held-out check (`heldout-ms-essf-pp.md`) splits 20% of the sites and reproduces the
> direction and most of the size; quote that note for the defensible number.


PP fold, 25 intervals, one cycle each, no bundle:

| Build | Path | BA bias (m²/ha) | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 0.32.0 | V2 | −4.98 | 4.98 | −97 | 117 |
| **W17** | **V3** | **−2.58** | **2.58** | **−0.1** | **66** |

The TPH bias essentially vanishes (−97 → −0.1) and its MAE halves. No bundle: 25 intervals with no
held-out split.

## 5. Tier and claim

PP is **C**: V3 structure, fitted rows for FD and PY, tabular mortality, measured caps, and one fold.
It is not validated: 25 intervals, no held-out split, no bundle, and PY's diameter row has no
explanatory power.

## 6. Build

Apply after W16. Verified against the full W2–W16 chain from the pinned tree.
