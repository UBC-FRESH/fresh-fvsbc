# FVS tree output does not carry the observed TREE_NO

Status: **technical block.** No engine or bundle change ships.

## 1. What was tried

`psp_tree_records` was changed to write the observed `TREE_NO` as the FVS tree number (when
positive and unique), so the tree output could be matched back to the measurement. The change was
reverted after testing.

A representative CWH interval illustrates the problem:

| Source | Tree identifiers |
| --- | --- |
| Observed `cwh_height_pairs.csv` | 1, 2, 3, … 15 |
| FVS `FVS_TreeList_Metric.TreeId` | 15, 17, 140, 165, 183, 197, 1106, … |

Writing the observed number into the tree list does not change the output IDs. FVS assigns its own
internal `TreeId`; `TreeIndex` is also reordered.

## 2. Why this matters

The W37 CW height form was fitted against the engine's predicted DGM using a 1,107-tree sample
where the renumbering happened to coincide for some trees. A height-balanced tall-tree sample
(30 CWH intervals, 272 candidate matches) cannot be matched reliably, so the refit against engine
DGM is not trustworthy.

A clean mapping would require either:

1. carrying a stable observed tree key through `write_tree_file`/`TREEID` and reading it back; or
2. matching the **initial** output tree list to the input records by DBH/species, then using that
   `TreeIndex` for the end-of-period DG.

Neither is a height-equation change; both are tree-output interface work.

## 3. Consequence

W37 remains the best stand-level CW evidence: A/B top −5.55 → −5.376, volume −106.98 → −104.18,
BA flat, TPH marginally worse. It still fails the all-three-improve rule.

The decision on allowing BA/TPH-neutral CW height improvements is still required before W37 can
ship. No engine or bundle change was made; the shipped package remains 0.41.22 / engine 0.4.16.

## Reproduce

- Tree-output probe: `~/workspace/bwbs-work/probe_cwh_treeout.py`.
- Tall sample collection: `~/workspace/bwbs-work/collect_engine_dgm_balanced.py`.
