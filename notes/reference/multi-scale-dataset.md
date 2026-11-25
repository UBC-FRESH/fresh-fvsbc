# The multi-scale dataset

Status: **first cut: tree → stand → neighbourhood → landscape, manifest-driven, tested on a
two-stand pilot.** Date: 2026-11-25.

## What it is

`fresh_fvsbc.dataset.build_dataset(manifest, out_dir)` runs each stand in a JSON manifest through
FVS-BC and writes a normalised dataset:

| Table | Grain | Key columns |
| --- | --- | --- |
| `runs` | one stand-run | `run_id`, `stand_id`, `bec`, `neighbourhood`, `tsa`, `support` (JSON), hashes, pins |
| `stands` | run × year | `BA`, `Tph`, `QMD`, `TCuM`, and the rest of `FVS_Summary_Metric` |
| `trees` | run × year × tree | species, `DBH`, `DG`, `Ht`, `HtG`, `TPH`, `MortPH` |
| `neighbourhoods` | neighbourhood × BEC | mean stand metrics, `n_stands` |
| `landscape` | BEC | mean stand metrics, `n_stands` |

The **unit is BEC**: every table carries the stand's BEC, the landscape aggregates by BEC, and TSA
is only a descriptive column. The neighbourhood is a caller-supplied grouping (a polygon, a BEC
unit, a management block); it is not inferred from TSA.

`dataset.json` records the source manifest, its hash, the table list, and each table's schema, so a
dataset names the exact input that produced it.

## Manifest

```json
{
  "dataset_id": "pilot",
  "version": "0.1.0",
  "stands": [
    {
      "stand_id": "B1",
      "bec": "BWBSmw/01",
      "neighbourhood": "N1",
      "tsa": "Dawson Creek TSA",
      "trees": "trees/b1.csv",
      "calibration": null,
      "keywords": [
        {"name": "DATABASE", "lines": ["DSNOut", "FVSOut.db", "Summary", "TREELIDB"]},
        {"name": "STDINFO", "fields": ["CAR", "BWBSmw/01", "0", "200", "35", "16"]},
        {"name": "PROCESS"},
        {"name": "STOP"}
      ]
    }
  ]
}
```

`trees` and `calibration` are relative to the manifest. The keyword list is the run's full set,
so a disturbance schedule is expressed with the same `FMIN`/`THINBBA` blocks a normal run uses.

## Support travels with the data

`runs.support` is the provenance array: one `species`/`tier`/`reason`/`evidence` record per species.
A dataset row therefore says `C` or `X` in data, not in a caption.

## What this first cut does not do

- **Neighbourhoods are declared, not spatial.** The manifest supplies an ID; no geometry, adjacency,
  or area weighting yet.
- **No whole-TSA pilot yet.** A four-stand real pilot (BWBSmw, BWBSwk1, BWBSwk2, SBSwk2 in
  Dawson) produced 2,092 tree rows, 8 stand-year rows, and a BEC landscape; all four runs carried
  support `C`. The test itself remains two synthetic stands.
- **Disturbance events are in their own tables** (`FVS_CutList_Metric`, mortality, snags, DWD) as
  requested by the keywords; there is no normalised `events` table.
- **CSV only.** Parquet/SQLite and a published DOI are later.
- **No dataset-level validation** beyond the schema and the source-hash record.

## Real pilot

Four Dawson PSP stands (BWBSmw, BWBSwk1, BWBSwk2, SBSwk2), one interval each, untreated. The builder
wrote 4 runs, 8 stand-year rows, 2,092 tree rows, and four BEC landscape rows; every run carried
support `C`. The stand tree lists and manifest stay local because they carry PSP site identifiers.

## Next

1. A whole-TSA pilot with a fire and a removal.
2. A normalised `events` table (year, type, species, TPH, BA removed/killed).
3. A Parquet writer and a schema version.
