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

## `okanagan_background.yaml`

Second-TSA replication of the background template. It fits the target-excluded
growth-free model, scores Okanagan, and freezes aggregate metrics and
coefficients:

```sh
freshforge run workflows/freshforge/okanagan_background.yaml --workdir . \
  --evidence runtime/freshforge-okanagan-evidence.json
```

It writes `okanagan-candidate/metrics.csv` and
`okanagan-candidate/model-card.json`. No site-level rows are written.

## `north_island_background.yaml`

Third background candidate and the first coastal CWH test:

```sh
freshforge run workflows/freshforge/north_island_background.yaml --workdir . \
  --evidence runtime/freshforge-north-island-evidence.json
```

It writes `north-island-candidate/metrics.csv` and
`north-island-candidate/model-card.json`. PL is below the 500-tree support
minimum and is omitted; the layer is coastal HW/FD/OTHER background only.

## `kamloops_background.yaml`

Fourth background candidate and the second southern-interior test:

```sh
freshforge run workflows/freshforge/kamloops_background.yaml --workdir . \
  --evidence runtime/freshforge-kamloops-evidence.json
```

It writes `kamloops-candidate/metrics.csv` and
`kamloops-candidate/model-card.json`. The card records the 20-site conditional
rule evaluation; the rule is not applied because it does not improve held-out
log loss.

## `prince_george_background.yaml`

Fifth background candidate and the first northern SBS test:

```sh
freshforge run workflows/freshforge/prince_george_background.yaml --workdir . \
  --evidence runtime/freshforge-prince-george-evidence.json
```

It writes `prince-george-candidate/metrics.csv` and
`prince-george-candidate/model-card.json`. No local calibration is applied.

## `cranbrook_background.yaml`

Sixth background candidate and the first southeast Interior test:

```sh
freshforge run workflows/freshforge/cranbrook_background.yaml --workdir . \
  --evidence runtime/freshforge-cranbrook-evidence.json
```

It writes `cranbrook-candidate/metrics.csv` and
`cranbrook-candidate/model-card.json`. No local calibration is applied.

## `arrow_background.yaml`

Seventh background candidate and the first interior wet-belt test:

```sh
freshforge run workflows/freshforge/arrow_background.yaml --workdir . \
  --evidence runtime/freshforge-arrow-evidence.json
```

It writes `arrow-candidate/metrics.csv` and
`arrow-candidate/model-card.json`. No local calibration is applied; the
candidate is weaker than the previous six.

## `fraser_background.yaml`

Eighth background candidate and the mainland coastal-transition test:

```sh
freshforge run workflows/freshforge/fraser_background.yaml --workdir . \
  --evidence runtime/freshforge-fraser-evidence.json
```

It writes `fraser-candidate/metrics.csv` and
`fraser-candidate/model-card.json`. The card records the conditional local-rule
evaluation; deployment offsets are not embedded.

## `mackenzie_background.yaml`

Ninth background candidate and the first northern boreal test:

```sh
freshforge run workflows/freshforge/mackenzie_background.yaml --workdir . \
  --evidence runtime/freshforge-mackenzie-evidence.json
```

It writes `mackenzie-candidate/metrics.csv` and
`mackenzie-candidate/model-card.json`. The card records the conditional rule and
the boreal PL gap; deployment offsets are not embedded.

## `haida_gwaii_background.yaml`

Tenth background candidate and the hypermaritime CWH test:

```sh
freshforge run workflows/freshforge/haida_gwaii_background.yaml --workdir . \
  --evidence runtime/freshforge-haida-gwaii-evidence.json
```

It writes `haida-gwaii-candidate/metrics.csv` and
`haida-gwaii-candidate/model-card.json`. PL is below the support minimum and is
omitted.

## `kootenay_lake_background.yaml`

Eleventh background candidate and the ICH wet-belt completion:

```sh
freshforge run workflows/freshforge/kootenay_lake_background.yaml --workdir . \
  --evidence runtime/freshforge-kootenay-lake-evidence.json
```

It writes `kootenay-lake-candidate/metrics.csv` and
`kootenay-lake-candidate/model-card.json`. No local calibration is applied.

## `boundary_background.yaml`

Twelfth background candidate and the deferred Boundary hard case:

```sh
freshforge run workflows/freshforge/boundary_background.yaml --workdir . \
  --evidence runtime/freshforge-boundary-evidence.json
```

It writes `boundary-candidate/metrics.csv` and
`boundary-candidate/model-card.json`. The card records the symmetric 20-site
local-rule evaluation; deployment offsets are not embedded.

## `symmetric_audit.yaml`

Compares the base candidate metrics with the symmetric 20-site local rule across
the candidate set:

```sh
freshforge run workflows/freshforge/symmetric_audit.yaml --workdir . \
  --evidence runtime/freshforge-symmetric-audit-evidence.json
```

It writes one aggregate row per target to `d9-symmetric-audit.csv`. No candidate
card is modified.

## `calibration_policy.yaml`

Validates the candidate calibration contract:

```sh
freshforge run workflows/freshforge/calibration_policy.yaml --workdir . \
  --evidence runtime/freshforge-calibration-policy-evidence.json
```

The check covers the supported symmetric Boundary/MacKenzie cards, the frozen
minimums, the not-frozen Invermere decision, and the excluded layers.
