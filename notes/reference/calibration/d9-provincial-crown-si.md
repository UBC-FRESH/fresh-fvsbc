# D9.42 provincial mortality with crown class and site index

Status: **large discrimination gain and good Okanagan calibration; Quesnel still needs local correction**
Date: 2026-11-08
Code: `bcmort_provincial.py`
Evidence: `d9-provincial-crown-si-summary.csv`

## 1. Model

The D9.41 provincial model was extended with:

- crown class from the PSP tree record (D/C/I/S; 96.6% coverage);
- site index from the tree record (12.6% coverage; median fill + missing flag);
- height/DBH and individual-tree prior growth retained;
- species-group Poisson hazards, BEC-zone effects.

Validation now holds out **one TSA per BEC**: Okanagan (MSdm1) and Quesnel (SBSmw). Boundary and
Prince George remain in training, so the held-out BECs are represented.

## 2. Overall held-out result

| TSA | n | AUC | Mean predicted | Observed | Brier | Log loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Okanagan | 134,149 | **0.803** | 0.149 | 0.147 | 0.102 | **0.338** |
| Quesnel | 70,989 | **0.709** | 0.268 | 0.161 | 0.142 | 0.457 |

Compared with D9.41:

- Okanagan AUC 0.730 → **0.803**, log loss 0.374 → **0.338**, mean bias nearly eliminated.
- Quesnel AUC 0.679 → **0.709**, log loss 0.464 → **0.457**, but the level overprediction remains
  (0.268 vs 0.161).

The species-group table shows the Quesnel residual is concentrated in PL and OTHER. Okanagan is
well calibrated overall despite species-level variation.

## 3. Interpretation

- Crown class and site index add real provincial signal; this is the first model that both uses all
  BC data and gets a held-out TSA mean nearly right.
- The Quesnel residual is a target-TSA/species level effect, not a global discrimination failure.
- Site index coverage is low (12.6%); the fit is not yet a clean SI test.
- Prior growth is still observed, not FVS-predicted; this remains an oracle-covariate diagnostic.
- A local target-TSA correction is still needed for Quesnel; it is now a calibration-layer problem,
  not a model-discovery problem.

## 4. Decision

- Promote this to the provincial mortality baseline.
- Add full BEC/TSA hierarchical effects and a target-TSA calibration layer next.
- Replace observed growth with FVS-predicted growth before any deployment claim.
- Do not integrate into FVS and do not issue a bundle.

## 5. Limits

- One held-out TSA per BEC; no temporal validation yet.
- Crown class is ordinal, not continuous crown ratio.
- Site index is sparse and tree-level.
- Prior growth is observed.
- No dynamic climate or period effect.

## 6. Claim boundary

This is a diagnostic provincial prototype. It does not support a yield, AAC, legal, or whole-block
claim, and it is not a certificate.
