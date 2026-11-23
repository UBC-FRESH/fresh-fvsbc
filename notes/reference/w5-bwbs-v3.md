# W5: BWBS growth and mortality on the V3 path

Status: **built and calibrated; unsigned pilot.** The patch is banked, the base bundle is
provenance-only, and no BM/MM multiplier is required. Not a certificate.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w5-bwbs-v3.patch.gz`, applied after `fvsbc-patchset.diff.gz`, `w2-subzones.patch.gz`,
`w3-habtyp-boundary.patch.gz`, `w4-sbps-small-tree.patch.gz`, and `w2-five-zone.patch.gz`.
Bundle: `bwbs-v3-bundle.json` (supersedes `d8-bwbs-bundle.json`).

## 1. Why

`w2-five-zone.patch.gz` made `BWBS` resolve and gave it a provisional `BAMAX`. It did not give BWBS a
growth or mortality model. On the V3 path every table is keyed by BEC and no table listed BWBS:

| Table | Consequence when BWBS was absent |
| --- | --- |
| `canada/bc/regent.f` `ST_COEF` | no small-tree height-growth model |
| `canada/bc/dgf.f` `ZNKONST` | no large-tree diameter-growth zone coefficients |
| `canada/bc/dgf.f` `SSKONST` | no site-series match; the zone match alone is not enough |
| `canada/bc/htgf.f` `LTHG` | no large-tree height-growth site series |
| `canada/bc/morts.f` `LMRT` | `MORT%FIT=.FALSE.`, which sets `RIP=99.0`: **complete mortality** |

The last row is the dangerous one: with no BWBS entry, every aspen, cottonwood, and birch tree died in
a BWBS projection regardless of `MORTMULT`. A missing table is not a zero effect; in `morts.f` it is a
100 percent effect.

The SBS and SBPS V3 paths have their own version of the first four gaps: `SSKONST` has no SBS/SBPS site
series, so their large-tree DG also falls through. That is not fixed here; the W5 BWBS entry is.

## 2. What the patch does

- `becset.f`: adds BWBS to the V3 condition.
- `regent.f`: adds BWBS to the five SBS/SBPS CCF and height branches; adds six `ST_COEF` entries
  fitted from 3,316 same-tree small-tree pairs (AT, PL, BL, AC, EP, plus a pooled fallback).
- `dgf.f`: adds `BWBS/all` to the SBS donor `ZNKONST` entries; adds a fitted BWBS AT/AC aspen DG
  entry; adds the `SSKONST` BWBS zonal entry that makes the site-series match succeed.
- `htgf.f`: adds `BWBS/all` to eleven `LTHG` site-series blocks.
- `morts.f`: adds `BWBS/all` to the `LMRT(1)` hardwood entry (EP, AT, AC, OH), and applies a
  small-tree (<10 cm DBH) factor: `BWBSmw` 0.50, `BWBSwk1` 1.00, `BWBSwk2` 1.00, other BWBS 0.70.

The small-tree factor is a calibration from observed annual mortality below 10 cm, not a fitted
continuous model: 4.1 percent per year in `BWBSmw`, 9.1 in `BWBSwk1`, 2.4 in `BWBSwk2`.

## 3. Calibration

Dawson BWBS only: 143 intervals, 79 sampled sites, BECs `BWBSmw` (121), `BWBSwk1` (16), `BWBSwk2` (6).
The deterministic site split holds out every fourth site. The probe uses `per-bec 20`, giving ten
held-out intervals. No ingrowth is used: a year-0 `ESTAB` block makes FVS re-select its sample trees,
so recruitment belongs in the multi-cycle harness, not this probe.

`BAIMULT 1`, `MORTMULT 1` — the tables carry the calibration:

| Fold | Intervals | BA bias (m2/ha) | BA % | BA MAE | TPH % |
| --- | ---: | ---: | ---: | ---: | ---: |
| held out | 10 | **+2.33** | **+4.3** | 4.97 | **+0.2** |
| train | 28 | +5.94 | +14.1 | 9.26 | -3.3 |

By held-out BEC: `BWBSmw` -0.3 (0.0 percent, TPH +0.7), `BWBSwk1` +5.3 (+9.5), `BWBSwk2` +3.5 (+5.1).
The aggregate is inside the three-point gate; each held-out BEC is inside the ten-percent alternative.

The two named checks in the handoff:

| Check | BA | TPH | Volume |
| --- | --- | --- | --- |
| young Dawson stand | 46.0 vs 48.1 (-2.1) | 4,736 vs 5,272 (-10.2%) | 297 vs 303 (-2.1%) |
| mature Dawson stand | 39.0 vs 37.3 (+1.7) | +9.2% | 313 vs 317 (-1.4%) |

## 4. Build

```bash
git -C <fvs-source> apply <abs>/fvsbc-patchset.diff.gz   # or the banked recipe
git -C <fvs-source> apply <abs>/w2-subzones.patch.gz
git -C <fvs-source> apply <abs>/w3-habtyp-boundary.patch.gz
git -C <fvs-source> apply <abs>/w4-sbps-small-tree.patch.gz
git -C <fvs-source> apply <abs>/w2-five-zone.patch.gz
git -C <fvs-source> apply <abs>/w5-bwbs-v3.patch.gz
```

Then build the BC wheel as in ADR 0004. The patch is verified to apply against the pre-W5 tree with
`patch -p1 --dry-run`.

## 5. Claim boundary and open items

- `BWBSwk2` is the weak cell: +5.1 percent on the held-out interval, +42.8 percent on three training
  intervals. Do not make a zone-wide `wk2` claim.
- `BWBSdk`, `BWBSmk`, and `BWBSwk1` outside Dawson are not in this fold.
- Recruitment is not validated here.
- The bundle is unsigned. A signed review and a pin change are required before this is a claim about
  BWBS rather than a pilot.
- The large-tree DG period scaling (annual fit to the per-period `DDS`) is folded into the aspen
  coefficient; a later refit should fit per-period directly.

## 6. Supersedes

`d8-bwbs-bundle.json` is a two-parameter V2 pilot (`BAIMULT 5.5`, `MORTMULT 0.2`). On the V3 path it is
wrong: a multiplier large enough for the young stand drives a mature stand far above observation, and
the tables now carry the calibration directly. Use `bwbs-v3-bundle.json` instead.
