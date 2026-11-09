# D9.79 FreshForge calibration workflow

Status: **the provincial fit and Quesnel calibration run as a persistent FreshForge workflow**
Date: 2026-11-08
Workflow: `workflows/freshforge/quesnel_background.yaml`

## 1. Workflow

The workflow has two executable nodes:

| Node | Provider | Script | Artifact |
| --- | --- | --- | --- |
| `fit_provincial` | `fresh_fvsbc.freshforge.native_script` | `bcmort_provincial.py` | `d9-provincial-crown-si-summary.csv` |
| `calibrate_quesnel` | `fresh_fvsbc.freshforge.native_script` | `bcmort_provincial_calibration.py` | `d9-provincial-calibration-summary.csv` |
| `freeze_model` | `fresh_fvsbc.freshforge.native_script` | `freeze_model.py` | `quesnel-candidate/model-card.json` |

`calibrate_quesnel` depends on `fit_provincial`; `freeze_model` depends on both. The provider records stdout, stderr, return code,
and declared artifact paths.

## 2. Reproduction

```sh
freshforge validate workflows/freshforge/quesnel_background.yaml
freshforge plan workflows/freshforge/quesnel_background.yaml
freshforge run workflows/freshforge/quesnel_background.yaml --workdir . \
  --evidence runtime/freshforge-quesnel-evidence.json
```

The checked run:

- workflow id: `quesnel_background_calibration`
- status: **success**
- nodes: `fit_provincial` success, `calibrate_quesnel` success, `freeze_model` success
- evidence: `runtime/freshforge-quesnel-evidence.json`
- CLI run: `freshforge run ... --evidence runtime/freshforge-quesnel-cli-evidence.json --summary`
  - status: success
  - nodes: 3 success
  - artifact count: 3
  - diagnostics: 0

## 3. Provider

- Module: `src/fresh_fvsbc/freshforge.py`
- Provider id: `fresh_fvsbc.freshforge`
- Node type: `native_script`
- Entry point: `freshforge.providers` in `pyproject.toml`
- Optional dependency: `fresh-fvsbc[workflow]`

The provider is a domain adapter, not a generic shell node. It runs a declared repository script with
an explicit argument list from the workflow work directory.

## 4. Boundaries

- The workflow writes aggregate CSVs; raw PSP and site-level data stay external.
- It is a serial local workflow, not a scheduler or cache.
- It does not yet include MPB segment or Quesnel residual steps.
- No bundle or certificate.

## 5. Claim boundary

This is a reproducibility/integration artifact. It does not support a yield, AAC, legal, or
whole-block claim, and it is not a certificate.
