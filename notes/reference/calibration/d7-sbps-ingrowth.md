> **D9.24 correction:** the 100 Mile candidate is retracted; corrected run BA +13.0%/TPH +10.5%, 0/6 sites. See `d9-ingrowth-unit-impact.md`.

# D7.5 SBPS ingrowth on a TSA holdout

Status: **no SBPS candidate survives the TSA holdout**; the D7.3 candidate is retracted as a bundle
candidate
Date: 2026-11-03
Issue: #354
Build: `fresh-fvsbc-pyfvs 0.4.1`, `fresh-fvsbc 0.21.3`
Data: all-zone calibration dataset and public FAIB tree detail
Evidence: `d7-sbps-ingrowth-summary.csv`, `d7-sbps-ingrowth.json`

D7.4 found the IDFdk TPH failure was missing ingrowth, not mortality. This tests the same idea for
SBPS on a pure TSA holdout, with the rate model trained without that TSA.

## 1. The rate model

The model is a mean annual new-live-tree TPH rate by BEC and species group:

- all SBPS intervals except `100 Mile House TSA` are training;
- 630 BEC × species rows from 116 sites;
- the holdout TSA is `100 Mile House TSA` (`SBPSmk`).

Rates in `d7-sbps-ingrowth.json`:

| BEC | FD | PL | SE | HW | BL |
| --- | ---: | ---: | ---: | ---: | ---: |
| `SBPSdc` | — | 56.07 | 11.32 | 1.91 | — |
| `SBPSmc` | — | 1.14 | — | — | — |
| `SBPSmk` | 5.26 | 47.66 | 9.68 | 0.38 | 4.98 |
| `SBPSxc` | — | 22.49 | 10.96 | 24.11 | — |

The holdout is 10 sites / 7 eligible test intervals; 180 eligible intervals remain for training.

## 2. Result

Baseline and candidates on the pure `100 Mile House TSA` holdout:

| Candidate | Test BA bias | BA % | Test TPH bias | TPH % |
| --- | ---: | ---: | ---: | ---: |
| `BAMAX 50` baseline | +15.75 | +50.8% | +145 | +7.5% |
| + ingrowth, scale 1.0 | +16.60 | +53.6% | +350 | +18.1% |
| + ingrowth, scale 0.25 | +15.89 | +51.3% | +197 | +10.2% |
| + ingrowth, scale 0.50 | +16.03 | +51.8% | +248 | +12.8% |
| + ingrowth, scale 0.75 | +16.46 | +53.2% | +299 | +15.4% |
| `MORTMULT 0.5` | +17.03 | +55.0% | +219 | +11.3% |

No candidate meets the BA threshold. The baseline already overpredicts test BA by **50.8%**, so
ingrowth cannot fix the TSA failure; adding recruitment makes BA and TPH worse. Scaling the rate down
does not remove the BA error, and the TPH error crosses the 15% threshold at scale 0.75 and above.

Training error is much better (ingrowth scale 0.5: BA +3.5%, TPH -3.5%), which is exactly the
spatial-transfer problem: the model fits the other TSAs and does not transfer to 100 Mile House.

## 3. What this changes

- **D7.3's candidate is retracted as a bundle candidate.** Its every-third-site split was not a
  spatial holdout; the pure 100 Mile TSA holdout fails on BA even without any candidate parameter.
- **Ingrowth is not a universal TPH fix.** It helped IDFdk; on this SBPS holdout it overpredicts TPH
  and does not address the BA regime difference.
- **SBPS is not one domain.** 100 Mile House has a different BA response from the Quesnel and
  Williams Lake training intervals. The next fit must be TSA- or stratum-specific, or must leave one
  TSA out from the start.

## 4. Next

- Treat `100 Mile House TSA` as a validation-only stratum until it has independent training sites.
- Fit capacity per TSA/stratum, not per BEC, for SBPSdc and SBPSmk.
- Rebuild the ingrowth rates with leave-one-TSA-out for each SBPS TSA and report the transfer matrix.
- Do not promote a bundle from the D7.3 split.

## 5. Claim boundary

This is a transfer-failure report. It does not calibrate SBPS, does not change a default, and does not
support a yield, AAC, legal, or whole-block claim. The defensible statement is negative: on the 100
Mile House TSA holdout, no tested BAMAX, MORTMULT, or public-data ingrowth candidate meets the BA
threshold, and the baseline already overpredicts BA by 50.8%.
