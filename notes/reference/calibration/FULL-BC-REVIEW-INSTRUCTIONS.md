# Reviewer instructions: full-BC review bundle

Version: `d9-full-bc-review-v0`
Bundle: `d9-full-bc-review-bundle.md`
Manifest: `full-bc-review-manifest.json`

## 1. Role and time box

You are the independent reviewer. Spend one bounded session, about four to six
hours. This is a bundle review, not a certification and not a production
approval.

## 2. Two tracks

### Track A — mechanical and registry

1. Verify `full-bc-review-manifest.json` against the files.
2. Confirm the registry contains 40 unique cards.
3. Confirm every card has `preprocessing.medians` and `preprocessing.zones`.
4. Confirm no site-level rows are in the tracked card/metrics files.
5. Confirm the policy links and checksums are present.
6. Confirm Quesnel is recorded as non-PL background.

### Track B — statistical sample

Do not attempt a full 40-card statistical audit. Review a documented sample:

- strong: Pacific, North Island, Kispiox;
- weak: Lakes, Soo, Lillooet, Bulkley, GBR North;
- small: Nass, Mid Coast;
- evidence-only: 100 Mile House, Invermere;
- detailed: Quesnel and Okanagan, using the existing package and addendum.

For each sampled card check:

- target exclusion;
- metric-to-card consistency;
- claimed scope and omitted groups;
- calibration rule;
- whether the support-aware policy result is plausible.

## 3. Priority questions

1. Does the registry honestly represent 40 cards without overclaiming review?
2. Is Quesnel correctly scoped as non-PL background?
3. Does the nested support policy avoid target leakage through outer folds?
4. Are the small-TSA base choices honestly reported?
5. Is the BEC hierarchy null described without overclaiming?
6. Is 100 Mile’s ingrowth retraction separated from its mortality card?
7. Does the deployment contract stop at diagnostic calibration?

## 4. Severity

- **blocker** — a bundle claim is unsupported or data leaked.
- **major** — material error or missing evidence.
- **minor** — clarity, documentation, or reproducibility issue.

Give path, line, evidence command, and smallest fix.

## 5. Decision

Return exactly one:

- **pass**;
- **pass with conditions**;
- **fail**.

A pass authorizes the next decision, not a production bundle.

## 6. Report

Write `notes/reports/d9-full-bc-review-<reviewer>.md` using:

```text
Reviewer:
Commit:
Decision:
Mechanical checks:
Sample reviewed:
Findings:
Known caveat disposition:
Claim check:
```

Also post a short summary on the review issue.

## 7. Out of scope

Do not add TSAs, tune on the test set, reopen the global screen, or approve a
production bundle. Those are separate tasks.
