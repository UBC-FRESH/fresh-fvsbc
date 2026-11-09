# D9.82 FreshForge MPB segment workflow

Status: **the MPB segment is now an executable FreshForge node**
Date: 2026-11-09
Workflow: `workflows/freshforge/quesnel_mpb_segment.yaml`
Provider: `fresh_fvsbc.freshforge.native_script`

## 1. What the node does

`mpb_segment.py` runs one interval through the linked BC MPB extension. It:

1. reads the interval key and severity multiplier from an external case file;
2. builds the FVS tree list from the raw PSP start visit;
3. writes an `INITMORT` vector from observed PL mortality, scaled by the
   multiplier;
4. splits intervals longer than ten years into an explicit ten-year MPB cycle
   and a background tail;
5. runs the installed BC variant; and
6. writes aggregate JSON only.

The case file stays outside the repository, so the tracked workflow carries no
site-level key.

## 2. Case layout

```json
{"interval_id": "<site|visit|year0|year1>", "multiplier": 0.08}
```

The script reads `FRESH_FVSBC_PSP4_GROWTH` and `FRESH_FVSBC_TREE_DETAIL` from the
environment. It does not write raw rows.

## 3. Checked run

CLI:

```sh
freshforge run workflows/freshforge/quesnel_mpb_segment.yaml --workdir . \
  --evidence runtime/freshforge-quesnel-mpb-evidence.json --summary
```

Result: status `success`, one node, one artifact, zero diagnostics.

Aggregate result on the external case:

| Quantity | Value |
| --- | ---: |
| multiplier | 0.08 |
| initial live PL/ac | 165.12 |
| final live PL/ac | 24.30 |
| dead fraction | **85.3%** |
| observed dead fraction | 100% |
| maximum live PL DBH | 14.67 cm |
| live PL above 15 cm | 0.0/ac |
| live PL in 5–10 cm class | 20.07/ac |

## 4. Interpretation

- The explicit cycle form (`TIMEINT` cycle 1 = 10 years, cycle 2 = tail) parses
  correctly and ends at the interval end year.
- The ten-year cap stays in place: the first cycle is ten years, and the tail is
  background mortality.
- The residual is small live PL below 15 cm, consistent with the small-tree
  panel; it is not a large-tree tail.
- The result is a local diagnostic, not a provincial multiplier.

## 5. Claim boundary

This is an MPB segment diagnostic. It does not support a yield, AAC, legal,
whole-block, or certificate claim.
