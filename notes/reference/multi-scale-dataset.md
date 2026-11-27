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
| `events` | run × year × event | `event_type` (cut/mortality), species, size class, DBH, TPH |
| `landscape` | BEC | mean stand metrics, `n_stands` |

Every table named in the manifest's `tables` list is also written as its own CSV (cut list, mortality,
snags, DWD, fuels, potfire, consumption, carbon, ATRT), with `run_id`/`stand_id`/`bec` prepended.

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

`trees` and `calibration` are relative to the manifest. The keyword list is the run's full set, and
it supports **nested** blocks, so a disturbance schedule is the same `FMIN`/`THINBBA` a normal run
uses:

```json
{"name": "FMIN", "nested": [{"name": "MORTREPT", "fields": ["1"]}]}
```

A top-level `"tables"` list names the pass-through outputs (cut list, mortality, snags, DWD, fuels,
potfire, consumption, carbon, ATRT). A table the run did not write is skipped; a name the reader does
not expose is refused.

## Support travels with the data

`runs.support` is the provenance array: one `species`/`tier`/`reason`/`evidence` record per species.
A dataset row therefore says `C` or `X` in data, not in a caption.

## What this first cut does not do

- **Neighbourhoods are declared, not spatial.** The manifest supplies an ID; no geometry, adjacency,
  or area weighting yet.
- **Whole-TSA pilot done.** Every eligible Dawson interval **221 runs, 442 stand-year rows, 123,424 tree rows, 85 events** (75 cut rows), 4 BEC landscape rows, and the full disturbance set on the fire and removal stands. A 20-stand Dawson pilot (BWBSmw, BWBSwk1, BWBSwk2, SBSwk2, five each)
  produced 20 runs, 95 events (91 cut, 4 mortality), all disturbance tables, and a BEC landscape; every
  run carried support `C`.
- **Parquet is optional.** CSV is always written; a `.parquet` copy is written when `pyarrow` is
  installed. It is not in this environment.
- **SQLite is written.** `dataset.sqlite` carries one table per dataset table plus `dataset_meta`
  (id, version, table list); `dataset.json` names it. CSV is still the canonical text form.
- **No DOI yet.**
- **No dataset-level validation** beyond the schema and the source-hash record.

## Real pilot

**Four stands, untreated:** 4 runs, 8 stand-year rows, 2,092 tree rows, four BEC landscape rows,
support `C`.

**Twenty stands, one fire and one removal:** 20 runs across BWBSmw, BWBSwk1, BWBSwk2, and SBSwk2
(five each), **95 events** (91 cut, 4 mortality), the full disturbance table set on the fire stand,
and a BEC landscape with `n_stands=5` per zone. Every run support `C`. The tree lists and manifest
stay local because they carry PSP site identifiers.

## Next

1. A whole-province run, not one TSA.
2. A normalised `events` table (year, type, species, TPH, BA removed/killed).
3. A schema version on the Parquet/SQLite pair.
