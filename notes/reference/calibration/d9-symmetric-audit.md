# D9.96 symmetric local calibration audit

Status: **the symmetric rule helps material underprediction, but not uniformly**
Date: 2026-11-09
Workflow: `workflows/freshforge/symmetric_audit.yaml`
Summary: `d9-symmetric-audit.csv`

## 1. What was compared

For ten target-excluded candidates, with groups below 500 target trees omitted:

- base growth-free species-group model;
- symmetric 20-site/40-split local rule.

The audit writes aggregate rows only. It does not change any candidate card.

## 2. Result

Sorted by log-loss change:

| Target | Base log loss | Symmetric log loss | Delta |
| --- | ---: | ---: | ---: |
| Boundary | 0.3989 | 0.3874 | **−0.0114** |
| MacKenzie | 0.3945 | 0.3854 | **−0.0091** |
| Kootenay Lake | 0.4039 | 0.4007 | −0.0032 |
| Haida Gwaii | 0.3486 | 0.3472 | −0.0014 |
| Fraser | 0.3267 | 0.3254 | −0.0012 |
| Arrow | 0.3375 | 0.3365 | −0.0011 |
| Prince George | 0.3521 | 0.3527 | +0.0006 |
| Cranbrook | 0.3493 | 0.3504 | +0.0011 |
| Kamloops | 0.3867 | 0.3877 | +0.0011 |
| North Island | 0.2858 | 0.2874 | +0.0016 |

## 3. Interpretation

- Boundary is the clearest case: the one-sided rule could not correct it because
  the groups underpredict.
- MacKenzie is the second clear case: PL is badly underpredicted and the
  symmetric rule improves the aggregate.
- Kootenay Lake, Haida Gwaii, Fraser, and Arrow improve marginally.
- The clean, well-calibrated candidates (North Island, Kamloops, Cranbrook,
  Prince George) get slightly worse.

## 4. Decision

- Keep the one-sided rule for overprediction.
- Use the symmetric rule only where the base model materially underpredicts:
  Boundary and MacKenzie are the supported cases.
- Do not apply the symmetric rule globally.
- Do not rewrite the clean candidate cards.
- This is not a bundle or certificate.

## 5. Claim boundary

Diagnostic calibration audit only. Not a yield, AAC, legal, whole-block, or
certificate claim.
