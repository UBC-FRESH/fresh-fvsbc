# ADR 0003: fvsbc owns the bridge from synthetic stem populations

Status: proposed
Date: 2026-10-21
Issues: TBD

## Context

ADR 0002 places `nemora` upstream of `fvsbc`. `nemora.synthesis` generates synthetic stem populations
from fitted or user-defined distributions, and FVS requires a tree list as input. Something must
translate between the two shapes, and that something has to live on one side or the other.

The forces:

- **Who owns the format.** `fvsbc` owns the FVS-BC tree-list conventions. They are part of the BC layer
  that ADR 0002 assigns to `fvsbc`.
- **Who stays neutral.** `nemora` is format-agnostic by design. Its stated scope is inventory ingestion,
  distribution fitting, synthesis, and inventory simulation. FVS is not in that list, and a search of its
  source finds no FVS mention at all.
- **Direction of dependency.** `fvsbc` sits below its consumers and above the PyFVS fork. An adapter on
  the `nemora` side would add a `nemora` to FVS coupling and re-open the inversion that ADR 0002
  rejected.
- **The fields do not line up yet.** `nemora.synthesis` emits `dbh`, `height_m`, `crown_ratio`,
  `basal_area_m2`, `biomass_tonnes`, `bark_thickness_cm`, and coordinates, but no `species` and no vigor.
  FVS-BC needs a species to select a growth model.

## Decision

`fvsbc` owns the bridge. It provides an ingestion adapter that accepts synthetic stem populations,
including `nemora`'s record shape, and emits an FVS-BC tree list. `nemora` takes no dependency on
`fvsbc`, on FVS, or on any simulator.

The adapter is a public interface of `fvsbc`. Its tests use fixture records shaped like `nemora` output,
so `fvsbc`'s test suite never imports `nemora`.

## Consequences

- The dependency arrows stay one-way: `nemora` to `fvsbc` to `femic`, never back.
- `nemora` stays format-agnostic and remains usable with any simulator.
- The FVS-BC tree-list conventions live in `fvsbc`, next to the rest of the BC knowledge.
- The adapter cannot be complete while `nemora` does not emit `species`. It needs a species assignment
  step, supplied by the caller or derived from a `nemora` fit. The documentation must state which fields
  the adapter requires and which it cannot supply.
- `fvsbc`'s CI needs no `nemora` install, because the fixtures are records, not imports.
- Not yet verified: no adapter exists, and no `nemora` output has been read by `fvsbc`. Whether
  `nemora`'s record shape is stable enough to freeze as an interface is unknown.

## Alternatives considered

- An FVS exporter inside `nemora`. Rejected: it creates a `nemora` to FVS coupling, puts FVS-BC record
  conventions in a format-agnostic package, and re-opens the dependency inversion that ADR 0002 rejected.
- A third bridge package between the two. Rejected: it adds a release line and a CI surface to translate
  between two packages, and it would own FVS-BC record conventions without owning FVS-BC.
- No adapter, and callers hand-build tree lists. Rejected: it pushes the BC record conventions onto every
  caller, and it makes the `nemora` to `fvsbc` workflow impossible to express in code.
