# D9.85 Quesnel and Okanagan candidate review package

Status: **published for independent review**
Package id: `d9-candidate-review-v0`
Decision: **pending**
Manifest: `review-manifest.json`
Instructions: `REVIEW-INSTRUCTIONS.md`

## 1. Purpose

This package asks for one bounded, read-only review of the frozen background
candidate layers and the Quesnel MPB boundary. It is a review gate, not a bundle
approval.

The reviewer answers one question: **do the frozen cards and workflows support
the claims written around them?**

## 2. Scope

| Layer | Identity | Evidence |
| --- | --- | --- |
| Quesnel non-PL background | `quesnel-sbsmw-background-v0` | `quesnel-candidate/model-card.json`, `JOINT-REPORT.md` |
| Quesnel large-tree MPB | local `INITMORT` segment | `d9-freshforge-mpb.md`, `mpb_segment.py` |
| Quesnel small-tree PL boundary | `quesnel-pl-small-tree-v0` | `quesnel-candidate/small-tree-boundary.json` |
| Okanagan background | `okanagan-background-v0` | `okanagan-candidate/model-card.json`, `metrics.csv` |

**Excluded from this review**

- 100 Mile, which is retracted;
- IDFdk, which has no bundle;
- ICHmw2, which is unsigned;
- the CWH 4 cm volume question;
- SBPSmk mature;
- any new TSA, global screen, or provincial multiplier.

## 3. Headline metrics

**Quesnel non-PL**

- all-period: n = 20,047, mean 0.153 vs 0.163, AUC **0.792**, log loss 0.408;
- post-2000: n = 3,918, mean 0.191 vs 0.220, AUC 0.713, log loss 0.486;
- conditional local mean 0.139, log loss 0.408.

**Okanagan background**

- n = 134,149, mean **0.144** vs 0.147, AUC **0.792**, log loss **0.345**;
- local calibration not applied.

**Quesnel MPB and boundary**

- 0.08x `INITMORT`: **85.3%** dead PL at the interval end;
- survivors below 15 cm; live PL above 15 cm = 0.04/ac in the 16-case panel.

These are diagnostic results, not yield or AAC claims.

## 4. Reviewer questions

1. Is the target TSA excluded from training **and** from preprocessing choices?
2. Do the model-card metrics match the workflow outputs and metrics tables?
3. Is the Quesnel calibration rule clearly labeled as deployment-time, not a
   held-out result?
4. Does the MPB segment respect the ten-year cap and the local-severity rule?
5. Does the boundary card reject material live PL above 15 cm?
6. Are the claims limited to diagnostic candidates, with no bundle or
   certificate?

## 5. Known open concern

`bp.load()` imputes missing crown, SI, H-D, and growth values with medians
computed on the full frame before the target split. The reviewer must decide
whether this is a blocker. If it is, the bounded fix is train-only imputation
followed by one rerun of the Quesnel and Okanagan background workflows.

This concern is disclosed rather than hidden because it affects the meaning of
"target-excluded."

## 6. Decision protocol

The reviewer returns exactly one of:

- **pass** — the package supports the stated candidate claims;
- **pass with conditions** — the claims hold only after named corrections;
- **fail** — the evidence does not support the claims.

Every finding names a severity, the exact artifact and line, and the command or
check that shows it. A pass does not authorize a bundle; it authorizes the next
decision.

## 7. What this package is not

It is not a bundle, certificate, yield table, AAC recommendation, legal opinion,
or whole-block result. It does not approve production use.
