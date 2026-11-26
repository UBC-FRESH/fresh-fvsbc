# W13/W14: PP runs as PP

Status: **built and validated on the PP fold.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patches: `w14-pp-site-series.patch.gz` (becset) and `w13-pp-bamax.patch.gz` (sitset), applied after
`w12-sbs-bamax.patch.gz`.
Bundles: none. PP has no calibration bundle.

## 1. Why

The PP zone was not running as PP. Two gaps compounded:

1. **Site series.** `becset.f` lists only `PPxh1/01`, `PPxh1/03`, `PPxh1/06`, `PPxh1/07`,
   `PPxh2/03`, `PPdh1/01`, `PPdh2/01` for the KAM/NEL regions. Any other PP label fell to the
   `CASE DEFAULT` that rewrites the run to `MSdk/01`. The calibration data's `PPxh` and `PPxh2`
   labels are written as `/01`, so **every PP interval ran as MSdk**.
2. **Cap.** `sitset.f` gives `PPxh2` series 1–4 a cap of 32 m²/ha (measured p99 47.7) and has no case
   for the `PPxh` subzone at all, which took the undefined-cap warning and a 10 m²/ha cap.

## 2. What changed

- **`becset.f`**: the missing PP series map to the PP habitat (IBEC 130) and reuse the adjustment
  index of the listed series in the same subzone — `PPxh2/*` uses `PPxh2/03`'s index (5, y 2),
  `PPxh1/02,04,05` uses `PPxh1/01`'s (1, y 1), and the zoneless `PPxh/01` label is treated as
  `PPxh1`. No new adjustment parameters were invented; only the mapping was added.
- **`sitset.f`**: `PPxh` gets 30 m²/ha and `PPxh2` series 1–4 gets 48, the measured p99 values.
  Series 6–7 keep 21 and `PPdh2` keeps 32 (no measured plots).

## 3. Evidence

| Build | Engine BEC | BA bias (m²/ha) | MAE | TPH MAE |
| --- | --- | ---: | ---: | ---: |
| 0.28.0 | `MSdk/01` | −5.26 | 5.26 | 139.6 |
| **W13+W14** | **`PPxh2/01`** | **−4.98** | **4.98** | **117.2** |

25 intervals (6 `PPxh`, 19 `PPxh2`), one cycle each, no calibration bundle. Per BEC after the change:
`PPxh` −5.72, `PPxh2` −4.74.

The caps alone do not move the fold: every PP stand is below its new cap and the model's own growth is
so small that the `BA/BAMAX` blend has no increment to distribute (`RZ` is near zero). The cap fix is
still right — it removes the undefined-cap warning for `PPxh` and makes the caps consistent with the
other zones — but it is not the lever here.

## 4. What this exposes

**PP is on the V2 path.** `becset.f` sets `LV2ATV = .FALSE.` only for ICH, IDF, SBS, SBPS, BWBS, CWH,
MH, and CDF. PP, MS, and ESSF keep `LV2ATV = .TRUE.` and run the legacy growth and mortality code with
the default habitat. That is why PP stands barely grow: predicted BA often ends below its start while
the measured stands gain 3–4 m²/ha. The support matrix said "V3 via defaults" for these zones; it now
says the V2 path.

Making PP usable needs the same V3 wiring W5–W9 gave the other zones: condition class, small-tree
branch, large-tree `ZNKONST` rows, height blocks, and mortality rows. That is a work package, not a
mapping.

## 5. Tier and claim

PP stays **C**: it now resolves as PP, with measured caps, but on the V2 path and without a
calibration bundle. The −5 m²/ha bias above is the V2 path showing through, not a PP calibration.

## 6. Build

Apply after W12. Both patches verified against the full W2–W12 chain from the pinned tree.
