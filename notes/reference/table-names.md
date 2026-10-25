# The table names: the contract lists the base schema, and BC builds the metric one

Found while exposing more tables (`P12`). **The contract's 33-name list is the *base* schema's**, and
this project builds the **metric** variant, whose tables are named differently.

## Evidence

`dbsqlite/` — the base schema, which the list came from — creates `FVS_Down_Wood_Vol`, `FVS_SnagDet`,
`FVS_SnagSum`, `FVS_Fuels` and so on.

`metric/dbsqlite/` — the schema the metric build uses, which is BC's — creates:

```text
FVS_BurnReport_Metric        FVS_Down_Wood_Cov_Metric    FVS_RD_Beetle_Metric
FVS_Carbon_Metric            FVS_Down_Wood_Vol_Metric    FVS_RD_Det_Metric
FVS_Climate_Metric           FVS_EconHarvestValue_Metric FVS_RD_Sum_Metric
FVS_Consumption_Metric       FVS_EconSummary_Metric      FVS_Regen_Ingrow_Metric
FVS_DM_Spp_Sum_Metric        FVS_Fuels_Metric            FVS_Regen_Sprouts_Metric
FVS_DM_Stnd_Sum_Metric       FVS_Mortality_Metric        FVS_Regen_Tally_Metric
FVS_DM_Sz_Sum_Metric         FVS_SnagDet_Metric           FVS_Stats_Species_Metric
FVS_DM_TreeList_Metric       FVS_SnagSum_Metric           FVS_Stats_Stand
FVS_StrClass_Metric
```

And the official case's own database confirms it: it writes `FVS_Down_Wood_Vol_Metric`,
`FVS_SnagDet_Metric` and `FVS_SnagSum_Metric`, none of which the list holds, and `FVS_InvReference`,
which the list also lacks.

## What this means

- **Twenty-four names in the contract are wrong for this variant**, and at least two real tables are
  absent from it: `FVS_InvReference` and the `_Metric` forms of the tables the official case writes.
- `EXPOSED_TABLES` was extended in `P9` with `FVS_Summary_Metric`, which the list also lacked — the same
  error, caught once and not recognised as a class.
- **The list needs to be derived from `metric/dbsqlite/`**, not from `dbsqlite/`, and the page and its
  test corrected with it.

## Why this is a note and not a fix

The metric schema also creates tables through a dynamic `CREATE TABLE ' // TRIM` path, and several names
(`FVS_CalibStats`, `FVS_TreeList_Metric`, the `FVS_Regen_*` family) do not appear in either grep. A list
written from a partial read would replace one wrong list with another, so the correction is its own task
with the schema read in full.
