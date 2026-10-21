# FVS-BC

`fvsbc` is a Python wrapper for the **BC variant** of the Forest Vegetation Simulator (FVS), the
individual-tree growth model maintained by the USDA Forest Service. It builds the `FVSbc` variant from
a pinned fork of [PyFVS](https://github.com/UBC-FRESH/PyFVS) and exposes BC keywords, species and BEC
handling, and tidy simulation I/O.

The FVS source is Fortran. `fvsbc` does not reimplement the build or the bindings: it pins the fork that
owns them and adds the BC layer on top.

## Where this sits

```text
FVS Fortran  ->  fork of PyFVS (build, FFI)  ->  fvsbc (BC semantics, tidy I/O)  ->  femic, ws3, ws4, freshforge
                                                       ^
                                                       |
                                      nemora (synthetic stem populations)
```

- **Upstream.** `nemora` generates synthetic stem populations from fitted or user-defined distributions.
  FVS needs a tree list as input, so `nemora` primes `fvsbc`. The bridge lives here, in `fvsbc`; `nemora`
  takes no dependency on FVS. See [ADR 0003](notes/adr/0003-fvsbc-owns-the-bridge.md).
- **Downstream.** `femic`, `ws3`, `ws4`, and `freshforge` take `fvsbc` as a pinned dependency. See
  [ADR 0002](notes/adr/0002-fvsbc-is-a-standalone-package.md).

## Status

Phase 0 (bootstrap) is active on `feature/p0-bootstrap`. `ROADMAP.md` lists the phases, and the GitHub
issues carry the live status.

**`fvsbc` does not build `FVSbc` yet.** Nothing is released, and no variant has been built. The build
recipe is Phase 3 work. See [ADR 0001](notes/adr/0001-fork-pyfvs-as-the-build-and-ffi-layer.md) for why
the BC variant is not buildable from the upstream repositories today.

## How this project works

This project follows the UBC-FRESH dev workflow. Work is planned as phases, tasks, and subtasks in
`ROADMAP.md`, mirrored in GitHub issues, and recorded in `CHANGE_LOG.md`. The agent operating contract is
in `AGENTS.md`. Read `AGENTS.md`, then `ROADMAP.md`, before you change anything.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/dashboard.py
```

`scripts/dashboard.py` runs every quality gate: lint, format, strict types, tests with the coverage
gate, the workflow validator, and the docs build with warnings as errors.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating contract for coding agents |
| `ROADMAP.md` | Plan of record and issue tracker map |
| `CHANGE_LOG.md` | Dated narrative of changes |
| `docs/` | Documentation site |
| `notes/adr/` | Decisions, one per file |
| `notes/reference/` | Facts with provenance |
| `notes/reports/` | Phase close-out reports |
| `scripts/check_workflow.py` | Workflow validator |
| `scripts/dashboard.py` | The green dashboard: every quality gate |
| `tests/` | pytest suite, including a check that the planning surfaces pass the validator |

## Decisions

| ADR | Decision |
| --- | --- |
| [0001](notes/adr/0001-fork-pyfvs-as-the-build-and-ffi-layer.md) | Fork PyFVS as the FVS build and FFI layer |
| [0002](notes/adr/0002-fvsbc-is-a-standalone-package.md) | `fvsbc` is a standalone package |
| [0003](notes/adr/0003-fvsbc-owns-the-bridge.md) | `fvsbc` owns the bridge from synthetic stem populations |

## License

`fvsbc` has no licence file yet, and a public repository without one grants no rights to use it. Choose
and add a licence before the first public release.
