# FreshForge calibration workflows

## `quesnel_background.yaml`

The executable workflow for the provincial fit and Quesnel target-calibration
evidence.

```sh
freshforge validate workflows/freshforge/quesnel_background.yaml
freshforge plan workflows/freshforge/quesnel_background.yaml
freshforge run workflows/freshforge/quesnel_background.yaml --workdir . \
  --evidence runtime/freshforge-quesnel-evidence.json
```

The workflow writes aggregate CSVs and the frozen `model-card.json` only. Raw
PSP and site-level data stay under the external data path.

## `quesnel_mpb_segment.yaml`

One MPB segment through the linked BC extension. It requires the `fvs` and
`workflow` extras, plus three external inputs:

```sh
export FRESH_FVSBC_PSP4_GROWTH=/path/to/psp4-growth
export FRESH_FVSBC_TREE_DETAIL=/path/to/faib_tree_detail.csv
mkdir -p runtime
cat > runtime/mpb-case.json <<'JSON'
{"interval_id": "<site|visit|year0|year1>", "multiplier": 0.08}
JSON
freshforge run workflows/freshforge/quesnel_mpb_segment.yaml --workdir . \
  --evidence runtime/freshforge-quesnel-mpb-evidence.json
```

The case file is external because the interval key identifies a site. The
workflow writes aggregate JSON only: initial and final PL TPA, dead fraction,
the final size distribution, and the skipped-tree count. It splits intervals
longer than ten years into a ten-year MPB cycle plus a background tail, so the
MPB ten-year cap is not exceeded.

The second node, `freeze_boundary`, checks the aggregate 16-case panel and writes
`quesnel-candidate/small-tree-boundary.json`. It fails if the panel no longer
supports the boundary: more than 1 PL/ac above 15 cm, or a maximum live DBH above
20 cm.

The provider is `fresh_fvsbc.freshforge.native_script`. It runs the declared
repository script with an explicit argument list, records stdout/stderr and the
return code, and resolves declared artifacts against the work directory.
