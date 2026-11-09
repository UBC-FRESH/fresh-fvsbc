# FreshForge calibration workflows

`quesnel_background.yaml` is the executable workflow for the provincial fit and
Quesnel target-calibration evidence.

```sh
freshforge validate workflows/freshforge/quesnel_background.yaml
freshforge plan workflows/freshforge/quesnel_background.yaml
freshforge run workflows/freshforge/quesnel_background.yaml --workdir . \
  --evidence runtime/freshforge-quesnel-evidence.json
```

The provider is `fresh_fvsbc.freshforge.native_script`. It runs the declared
repository script with an explicit argument list, records stdout/stderr and the
return code, and resolves declared artifacts against the work directory.

The workflow writes aggregate CSVs only. Raw PSP and site-level data stay under
the external data path.
