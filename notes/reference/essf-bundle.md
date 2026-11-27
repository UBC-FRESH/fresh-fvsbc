# The first ESSF bundle: a coupled partial basis correction

Status: **shipped in 0.41.4.** Engine unchanged at 0.4.13. Tier stays C (unsigned).

## 1. Why a bundle

ESSF had no bundle. Both folds under-predict BA and TPH:

| Fold | BA bias / MAE | TPH bias / MAE |
| --- | ---: | ---: |
| test (42) | −3.07 / 5.49 | −314 / 530 |
| train (260) | −1.72 / 6.31 | −124 / 553 |

The W16 rows are fitted on **annual** growth while the engine applies a ten-year increment.

## 2. The full correction overshoots

A train-only refit with a ten-year response gives BL CON ≈ +0.75, about **6× diameter growth**.
The fold needs about **1.6×**: observed BA growth is 3.54 m²/ha against a predicted 1.63. A full
basis change would over-predict BA and cost TPH through self-thinning.

## 3. The coupled fit

A train-only grid over growth (`BAIMULT`) and mortality (`MORTMULT`), all species, selected the
partial correction:

```
BAIMULT 2.5   (diameter growth ×1.58, equivalent to a row constant +ln(sqrt(2.5)))
MORTMULT 0.9
```

| Build | Fold | BA bias | BA MAE | TPH bias | TPH MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| base | test | −3.07 | 5.49 | −314 | 530.2 |
| **essf-v3** | **test** | **−2.21** | **5.15** | **−315** | **528.8** |
| base | train | −1.72 | 6.31 | −124 | 553.4 |
| **essf-v3** | **train** | **−0.57** | **6.14** | **−122** | **551.2** |

All four MAE figures improve. The held-out TPH bias is essentially unchanged (−314 → −315); the
gain is in the distribution, not the mean.

## 4. Why a bundle and not a row edit

A row-constant patch on the five fitted ESSF species (DG ×1.7) improved three metrics but left
the train TPH MAE 0.9 worse, because the minor species keep shared donor rows. The bundle is
ESSF-scoped and applies the correction to every species, including the donors, without touching
other zones. A full row refit would need per-zone donor copies.

## 5. What remains

- MS and PP still have no bundle.
- The ESSF fold is unsigned; the W16 rows remain annual-basis under the partial correction.
- A true ten-year recalibration needs a coupled growth **and** mortality row rewrite, not a
  multiplier; the current bundle is the validated partial step.

## Reproduce

- Grid: `~/workspace/bwbs-work/probe_essf_joint/` and `probe_essf_joint2/`.
- Bundle run: `~/workspace/bwbs-work/probe_essf_bundle/`.
- Bundle: `notes/reference/calibration/essf-v3-bundle.json`.
