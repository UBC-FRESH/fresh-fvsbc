# W11: CWH height growth fitted from CWH pairs

Status: **built and calibrated on an interval-held-out CWH sample.** Unsigned pilot, tier C.

Pins: PyFVS `e95172b`, FVS source `ef5fa847`, variant `bc`.
Patch: `w11-cwh-height.patch.gz`, applied after `w10-mh-cdf-own-dg.patch.gz`.
Bundles: unchanged. `cwh-v3-bundle.json` still carries `BAIMULT 8`.

## 1. Why

W8 put CWH on the V3 path but left large-tree height growth as a donor: every CWH stand matched
the first `LTHG` block that lists `CWH/all`, which are the ICH/IDF site-series blocks. On the
dominant and codominant trees — the ones that carry top height and most of the volume — the donor
under-predicts ten-year height growth:

| Species | n (train) | Observed 10-yr height growth (m) | Donor |
| --- | ---: | ---: | ---: |
| HW | 80,149 | 2.45 | 1.71 |
| FD | 47,527 | 2.23 | 1.72 |
| SE (SS) | 14,053 | 2.64 | 1.47 |
| BG (BA) | 7,523 | 2.96 | 2.60 |
| AT (DR) | 7,733 | 1.75 | 1.47 |
| PL | 1,485 | 0.93 | 1.35 |

## 2. What changed

`htgf.f` only. Six single-species `LTHG` blocks are inserted at the head of the table, so a CWH
stand matches them before the ICH/IDF rows. The existing 57 blocks renumber to 7–63 and `P_MD`
moves 57 → 63. Every block lists only `CWH/all`, so no other zone can match it.

The model is the variant's own, `HTGM = (A1 + SI) * HTM^(B1 + B2*D + B3*DGM) * exp(C*HTM²)` for the
old-form species and `(CN + CNSI + DG*DGM + DG2*DGM²) * HTM^(DBH1 + DBH2*D) * exp(HT2*HTM²)` for
the new form, with `HTM` in metres and `DGM` the ten-year diameter increment (`YR = 10.0`).

| Species | Form | SI | B3 | C | CNSI | DG | DG2 | DBH1 | DBH2 | HT2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HW | old | −0.61544 | 0.07515 | −0.00043 | | | | | | |
| FD | old | +0.48669 | 0.07020 | −0.00020 | | | | | | |
| BG | old | +0.02000 | 0.06543 | −0.00084 | | | | | | |
| SE | new | | | | 0.17097 | 0.84906 | −0.01356 | 0.07372 | −0.00138 | −0.00041 |
| AT | new | | | | 0.53662 | 3.39671 | −0.10394 | −0.35942 | −0.00457 | −0.00087 |
| PL | new | | | | 0.17668 | 0.53005 | −0.01984 | 0.13416 | 0.00643 | −0.00215 |

The fits use CWH remeasurement pairs: same tree, two visits, live both times, DBH ≥ 10.16 cm, and
crown class D or C. Each height decile carries equal weight so the tall stems are not buried by the
many mid-size ones. The donors and the fit are scored on a 20% of intervals holdout.

| Species | n test | Donor bias (m) | Fit bias (m) | Donor RMSE | Fit RMSE |
| --- | ---: | ---: | ---: | ---: | ---: |
| HW | 19,825 | −0.748 | −0.152 | 1.575 | **1.234** |
| FD | 12,323 | −0.538 | −0.150 | 1.341 | **1.223** |
| BG | 1,949 | −0.409 | −0.138 | 1.238 | **1.147** |
| SE | 3,111 | −1.250 | −0.281 | 2.010 | **1.440** |
| AT | 1,690 | −0.157 | −0.243 | 1.298 | **1.179** |
| PL | 480 | +0.497 | −0.029 | 0.807 | **0.609** |

## 3. CW is deliberately not fitted

CW's fitted row (SI −0.69857, B3 0.06737, C −0.00048) matched CW's own mean but halved tall-cedar
height growth: on a real CWHdm interval, CW growth fell from 0.277 to 0.134 m/yr, and that tree
carried most of the stand. The variant's form cannot represent both CW's observed decline with
height and its level, so the row cost stand volume. CW keeps the donor until a form that fits the
tall end exists. This is the same rule the project applies everywhere else: a donor that is close
(CW's donor is 4% low on dominants) is better than a fit that is wrong where it matters.

## 3b. A new-form CW equation was tested later and also rejected

The 0.41.21 test fitted the new form to CW pairs: pair RMSE 1.49 → 1.06 and tall-end bias
−0.64 → −0.32, but the held-out CWH TPH MAE moved 171.41 → 171.51 and the stand A/B worsened
(BA −4.737 → −4.782, top height −5.55 → −5.66, volume −106.98 → −109.74). The donor stays. See
`w11-cw-height-new-equation-negative.md`.

## 4. Stand-level A/B

246 CWH intervals (12 per BEC) grown untreated for their measured length, W10 engine against W11,
identical tree lists:

| Metric | W10 | W11 |
| --- | ---: | ---: |
| Mean BA bias (m²/ha) | −4.184 | −4.176 |
| Mean volume bias (m³/ha) | −105.27 | −105.55 |
| Mean top-height bias (m) | −5.518 | −5.538 |

Observed mean volume is 712 m³/ha, so the volume change is −0.04%. Per BEC the volume delta runs
from −3.25 to +2.17 m³/ha; nine BECs improve and eleven move the other way. That is neutral, as
expected for 5–16-year intervals where height growth is a small part of standing volume.

`bias_top_height` is not a usable absolute check: FVS's `TopHt` and the FAIB `top_height` field are
different definitions — the same interval starts at 32.6 m observed and 23 m in FVS. It is reported
only as an A/B delta.

## 5. Residual gap

The fitted rows still under-predict the tallest trees. On CWH HW the fit gives about 1.2 m per
decade at a 40 m dominant height against 1.7 m observed. The form's quadratic size taper (`exp(C*HTM²)`)
trades the tall end against the mid-range, and no choice of `SI`, `B3`, `C` fixes both. That is a
form limitation, not a fitting failure, and it is the reason a future CWH height model should be a
new equation rather than another row edit.

## 6. Tier and claim

CWH stays **C**. Height is now fitted for six of its species; small-tree growth and mortality are
still donors, the CW height row is still the donor, the fold is unsigned, and the tall-end bias
above is open.

## 7. Build

Apply after W10; the wheel recipe does this. The patch is verified against the full W2–W10 chain from
the pinned tree.
