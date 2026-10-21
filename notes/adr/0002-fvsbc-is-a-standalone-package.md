# ADR 0002: fvsbc is a standalone package

Status: proposed
Date: 2026-10-21
Issues: TBD

## Context

`fvsbc` wraps the BC variant of the Forest Vegetation Simulator. Three candidate homes were weighed: a
new standalone repository, a module inside `femic`, and a module inside `nemora`.

The forces:

- **Audience.** A BC FVS wrapper is useful to anyone modelling BC forests, not only to FEMIC's BC-TSA
  pipeline.
- **Dependency weight.** `femic` depends on a heavy geospatial stack: `fiona`, `geopandas`, `rasterio`,
  `geocube`, `ipyparallel`, `swifter`, and Windows-only `pywinauto` and `comtypes`. An FVS user should
  not have to install that. In the other direction, `fvsbc` carries a Fortran build that FEMIC's other
  users should not need.
- **Domain fit.** `nemora` fits diameter-at-breast-height distributions to forest inventory tallies. It
  has no relationship to FVS.
- **Workflow.** The dev workflow gives each project one roadmap, one changelog, one dashboard, and one
  branch per phase. A module inside a larger project shares all of them.
- **Precedent.** `femic` uses git submodules only for data and instance repositories
  (`external/femic-*-instance`), never for code. `nemora` and `ws4` have no submodules at all.

## Decision

`fvsbc` is a standalone public package. It owns its roadmap, changelog, notes, docs, and CI. Consumers,
including `femic`, `ws3`, `ws4`, and `freshforge`, take it as an optional pinned dependency, never as a
vendored module or a git submodule.

`fvsbc` sits above the pinned fork of PyFVS (ADR 0001) and below its consumers:

```text
FVS Fortran  ->  fork of PyFVS (build, FFI)  ->  fvsbc (BC semantics, tidy I/O)  ->  femic, ws3, ws4, freshforge
```

## Consequences

- An FVS user installs `fvsbc` and its build layer without the lab's geospatial stack.
- `femic` takes `fvsbc` as an optional extra, so its default install and CI are unchanged.
- The BC layer has a stable public surface of its own, which is what embedded capabilities require.
- The lab maintains one more repository with its own release cadence.
- Three versions move together: the fork of PyFVS, `fvsbc`, and the FVS source submodule.
- Not yet verified: no consumer has taken `fvsbc` as a dependency, because `fvsbc` does not build yet.

## Alternatives considered

- A module inside `femic`. Rejected: it forces the geospatial stack on every FVS user, and it puts BC
  semantics inside a package whose stated scope is estate-level integration.
- A module inside `nemora`. Rejected: `nemora` fits DBH distributions and has no relationship to FVS.
- A git submodule of `fvsbc` inside `femic`. Rejected: this lab uses submodules for data, not for code.
- One shared monorepo for the lab's modelling packages. Rejected for now: it would couple the release
  cadences and dashboards that the dev workflow deliberately keeps separate.
