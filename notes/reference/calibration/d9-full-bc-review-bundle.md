# D9.113 full-BC review bundle

Status: **published for independent review**
Bundle id: `d9-full-bc-review-v0`
Decision: **pending**
Manifest: `full-bc-review-manifest.json`
Instructions: `FULL-BC-REVIEW-INSTRUCTIONS.md`

## 1. Purpose

This bundle asks for a bounded review of the full-BC calibration candidate set:
all 40 TSA cards, the BEC hierarchy audit, the nested support-aware policy, and
the deployment contract.

It is not a production bundle, certificate, yield table, AAC recommendation, or
legal opinion.

## 2. What is included

- **40** base cards and metrics.
- Candidate registry with checksums and review status.
- BEC zone/subzone/variant audit and pooled units.
- Full base, local, partial, BEC-unit, domain, and support-policy evidence.
- Frozen fixed calibration policy.
- Frozen nested support-aware policy.
- Deployment offset helper and raw scoring helper.
- Existing Quesnel/Okanagan review package and addendum.

## 3. Review status

| Item | Count |
| --- | ---: |
| Cards in bundle | 40 |
| Detailed review pending | 2 (Quesnel, Okanagan) |
| Coverage evidence, not individually reviewed | 38 |
| Evidence-only cards | Invermere, 100 Mile House |

The full bundle does **not** claim that all 38 cards have been individually
reviewed. The reviewer checks the registry mechanically and samples the
statistical evidence.

## 4. Headline evidence

| Item | Result |
| --- | --- |
| Base sweep | 40 TSA labels, median AUC 0.772, median log loss 0.386 |
| Nested support policy | 33/40 holdouts improve; median Δ log loss −0.00574 |
| Fixed local rules | 12–24/40 improve; worse tail |
| BEC hierarchy prototype | null against the current base |
| Imputation sensitivity | max Δ log loss 5.1×10⁻⁹ |
| 100 Mile mortality | AUC 0.766, log loss 0.388 |
| Invermere | AUC 0.704, log loss 0.440; evidence-only |

## 5. Known caveats

- Small TSAs — Lakes, Lillooet, Soo, Bulkley, Kingcome — have few sites and
  remain data-limited.
- The support-aware policy can choose base when local support is insufficient.
- The BEC hierarchy fit was a null; the base already uses BEC subzone effects.
- 100 Mile’s earlier retraction was the SBPS ingrowth candidate, not mortality.
- Full-frame imputation is disclosed; train-only sensitivity is included.
- No card is certified for production.

## 6. Reviewer decision

Return exactly one:

- **pass** — the bundle supports the stated candidate evidence and deployment
  contract;
- **pass with conditions** — only after named corrections;
- **fail** — the evidence does not support the bundle claims.

A pass is not a production bundle or certificate.

## 7. Claim boundary

Review bundle only. No production bundle, certificate, yield, AAC, legal, or
whole-block claim.
