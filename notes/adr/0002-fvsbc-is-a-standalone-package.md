# ADR 0002: fvsbc is a standalone package

Status: accepted
Date: 2026-10-21
Issues: #8

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
- **Domain fit, and the direction of the dependency.** `nemora` is not unrelated to FVS. FVS needs a
  tree list as input, and `nemora.synthesis` generates synthetic stem populations from fitted or
  user-defined distributions. That makes `nemora` an upstream *producer* of `fvsbc` input, not a
  consumer and not a home. Housing the wrapper inside `nemora` would invert the dependency: a
  distribution-fitting library would take on the simulator's Fortran-backed I/O and its BC variant
  semantics.
- **Workflow.** The dev workflow gives each project one roadmap, one changelog, one dashboard, and one
  branch per phase. A module inside a larger project shares all of them.
- **Precedent.** `femic` uses git submodules only for data and instance repositories
  (`external/femic-*-instance`), never for code. `nemora` and `ws4` have no submodules at all.

## Decision

`fvsbc` is a standalone public package. It owns its roadmap, changelog, notes, docs, and CI. Consumers,
including `femic`, `ws3`, `ws4`, and `freshforge`, take it as an optional pinned dependency, never as a
vendored module or a git submodule.

`fvsbc` sits above the pinned fork of PyFVS (ADR 0001), below its consumers, and downstream of `nemora`
on the input side:

```text
FVS Fortran  ->  fork of PyFVS (build, FFI)  ->  fvsbc (BC semantics, tidy I/O)  ->  femic, ws3, ws4, freshforge
                                                       ^
                                                       |
                                      nemora (synthetic stem populations)
```

## Consequences

- An FVS user installs `fvsbc` and its build layer without the lab's geospatial stack.
- `femic` takes `fvsbc` as an optional extra, so its default install and CI are unchanged.
- The BC layer has a stable public surface of its own, which is what embedded capabilities require.
- The lab maintains one more repository with its own release cadence.
- Three versions move together: the fork of PyFVS, `fvsbc`, and the FVS source submodule.
- `fvsbc` must accept synthetic stem populations, so tree-list ingestion is a first-class interface, not
  a BC-only detail. Today `nemora.synthesis` emits `dbh`, `height_m`, and `crown_ratio` among others,
  but no `species` and no vigor, and `nemora` has no FVS export. A `nemora` to `fvsbc` bridge is
  therefore designed but unbuilt. That gap is a fact about `nemora`'s current surface, not about the
  design.
- Not yet verified: no consumer has taken `fvsbc` as a dependency, because `fvsbc` does not build yet.

## Alternatives considered

- A module inside `femic`. Rejected: it forces the geospatial stack on every FVS user, and it puts BC
  semantics inside a package whose stated scope is estate-level integration.
- A module inside `nemora`. Rejected: `nemora` generates the tree lists that FVS consumes, so it sits
  upstream of `fvsbc` rather than around it. Housing the wrapper there would invert the dependency and
  couple a distribution-fitting library to a Fortran-backed simulator and its BC variant.
- A git submodule of `fvsbc` inside `femic`. Rejected: this lab uses submodules for data, not for code.
- One shared monorepo for the lab's modelling packages. Rejected for now: it would couple the release
  cadences and dashboards that the dev workflow deliberately keeps separate.
