# Problem statement and scope

Phase: P1 Scope and design
Issues: #5, #7
Date: 2026-10-21
Status: active

## The problem

The BC variant of the Forest Vegetation Simulator cannot be run today without substantial manual work.

Three separate obstacles stand in the way, and each was confirmed before this note was written:

1. **There is no BC build.** The official FVS repository ships the BC source under `canada/bc/`, but its
   source list is named `canada/bin/FVSbcc_notReady.txt`. The `_notReady` suffix is the upstream
   position. There is no `bin/FVSbc_sourceList.txt` in the official repository, and no official BC
   binary. A branch in the `forest-modeling` fork corrected the Canadian source lists and then excluded
   the BC variant from the build.
2. **No Python interface covers BC.** PyFVS builds and wraps FVS, and it is the right layer for that
   work, but its variant list is `pn, wc, so, op, oc, ec, ca, nc, bm, ie, ci, ak, ws`. The code `ca` is
   Central America, not Canada. BC is absent.
3. **No BC data layer exists.** FVS-BC consumes a fixed-width tree list and a keyword file, and it emits
   fixed-width output. It carries BC-specific concepts: BEC zones, site index, BC species codes, and a
   `BC.trf` tree file. Nothing in the lab's stack speaks that vocabulary.

The cost of the gap is paid by anyone who wants a BC growth projection: compile Fortran from a fork,
hand-assemble a column-sensitive tree list, write keyword files without a validator, and parse
fixed-width output by eye.

## Who this is for

| User | What they need |
| --- | --- |
| BC growth-and-yield analysts | Run FVS-BC on a stand or a set of stands, and get tidy results back |
| The FRESH lab's own pipelines | A pinned, reproducible FVS-BC engine that `femic`, `ws3`, and `ws4` can call |
| Graduate students and collaborators | An interface that fails clearly, instead of a Fortran executable that fails silently |
| Coding agents | Validated operations, per the embedded-capability pattern, rather than documentation alone |
| Reviewers and readers of published results | Provenance: which variant, which source revision, which keyword set produced a number |

## In scope

- **A reproducible `FVSbc` build** from the pinned fork, with the build recipe recorded.
- **The BC layer**: BC keywords, species codes, BEC zone and site index handling, and the `BC.trf` tree
  file.
- **Tree list ingestion**, including synthetic stem populations shaped like `nemora` output. The bridge
  lives here, per ADR 0003.
- **Tidy output**: FVS-BC result files parsed into dataframes, not fixed-width text.
- **Provenance for every run**: the fork commit, the FVS source submodule commit, the built variant list,
  and a hash of the keyword set.
- **A Python API and a CLI**, with parity between them.
- **Embedded capabilities** for the operations where a wrong answer is plausible and checkable, such as a
  species and BEC selection that must resolve against the built variant's real state.

## Out of scope

| Item | Why it is excluded |
| --- | --- |
| Other FVS variants | PyFVS owns the build and the bindings for those. `fvsbc` wraps BC only. See ADR 0001 |
| Editing the FVS Fortran in this repository | The Fortran lives in the pinned fork and its submodule. A change is made there, and the new pin is recorded here |
| An FVS exporter inside `nemora` | It would invert the dependency and put FVS record conventions in a format-agnostic package. See ADR 0003 |
| Reimplementing the FVS growth models | The models are the reason to use FVS. A reimplementation would be a different project with a different validation burden |
| A graphical or web interface | A CLI and an API cover the users above. A UI would add a release surface without changing what the model can do |
| BC inventory curation, TSA data assembly, and instance management | That is `femic`'s role, and it already does it |
| Carbon accounting and wood-supply optimization on FVS output | That is `ws3`, `ws4`, and `femic`. `fvsbc` stops at tidy simulation output |
| Validating the FVS-BC growth models against BC ground plots | `fvsbc` validates its own wrapper and its own I/O. Model accuracy is the model's own question, and answering it is a research programme, not a packaging task |
| Distributing a prebuilt BC binary before the build is reproducible | A binary that cannot be rebuilt cannot be trusted or audited. The build comes first |

## What this note does not decide

Interfaces and data contracts are P2. The build recipe is not settled: whether adding `bc` to the PyFVS
variant matrix is sufficient, or the FVS source submodule needs a patch, is unverified. ADR 0001 records
that uncertainty, and the build-recipe ADR is deliberately deferred until a spike produces evidence.
