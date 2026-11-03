# ADR 0006: The build recipe is two patch sets

Status: accepted on 2026-10-23.
Date: 2026-10-23
Issues: #18 (P3.1)
Refines: ADR 0004

## Context

ADR 0004 lists twelve items that make the BC variant build. Ten of them change the FVS source
submodule, and they were exported to `notes/reference/fvsbc-patchset.diff.gz`. The first two change
PyFVS's own repository — `meson_options.txt` gains `bc` in the `fvsvariants` choices, and `meson.build`
gains the `CMPgcc`/`unix` project arguments and the `bcplot.f77` exclusion from the f2py signature
input — and **they were never exported.**

ADR 0004's rebuild instructions say to apply that one patch to the FVS checkout. A reader who follows
them, from a clean checkout of the pin, gets exactly this:

```text
../meson.build:4:0: ERROR: Value "bc" for option "fvsvariants" is not in allowed choices:
"pn, wc, so, op, oc, ec, ca, nc, bm, ie, ci, ak, ws"
```

That is the first run of the `Build the BC variant` job added by `P3.1`, which exists to answer whether
the build is reproducible outside a developer's scratch clone. It is not, and the job found it on its
first attempt. The claim in ADR 0004 that the exported patch "reproduces the working tree byte for
byte" is true of the FVS source tree and was read as true of the whole recipe.

## Decision

The recipe is **two patch sets**, applied at two roots:

1. `notes/reference/pyfvs-patchset.diff.gz` at the PyFVS checkout, for ADR 0004's items 1 and 2.
2. `notes/reference/fvsbc-patchset.diff.gz` inside its FVS source submodule, for items 3 to 12.

The PyFVS patch set carries two more changes. In `0.18.0`, **`src/api/fvs_step.f90` gains the
`CALL DBSREFERENCE` that `fvs.f` makes immediately after `CALL STATS`.** The file is an extraction of
`fvs.f`'s initialisation and had omitted it, so the extension never wrote `FVS_InvReference`. The
original `fvs_` is dead code in the extension, which is why the omission was invisible: the writer was
compiled, linked, and never called. `notes/triage.md` carries the evidence.

And in `0.20.0`, **`pyproject.toml`'s distribution name becomes `fresh-fvsbc-pyfvs`**, so a wheel of
this fork cannot be confused with, or installed over, upstream `pyfvs` from PyPI. The import package
stays `pyfvs`; only the distribution name differs. The wheel is built by the `wheels` workflow and
`auditwheel repair` bundles `libgfortran`, so installing it needs no Fortran toolchain —
`docs/installation.rst` is the reader's side of that.

```bash
git clone https://github.com/UBC-FRESH/PyFVS.git
git -C PyFVS checkout e95172b
git -C PyFVS submodule update --init --recursive
gunzip -c notes/reference/pyfvs-patchset.diff.gz | git -C PyFVS apply -
gunzip -c notes/reference/fvsbc-patchset.diff.gz | git -C PyFVS/fvs apply -
SETUPTOOLS_SCM_PRETEND_VERSION=0.3.11 python -m pip install --no-build-isolation PyFVS \
  --config-settings=setup-args="-Dfvsvariants=bc"
```

CI applies both, with `git apply --check` before each, in the job `P3.1` added. ADR 0004's twelve items
and its reasoning stand; only its rebuild instructions are superseded, and its status line points here.

## Consequences

- The recipe is reproducible from this repository alone, which `P2`'s third acceptance criterion claimed
  and did not establish for the PyFVS-repo half.
- A reader now needs both files, and the second is easy to miss because the first is the one ADR 0004
  names. The CI job is what keeps that from recurring.
- The PyFVS-repo patch is two files and 20 lines. It belongs to the fork rather than to the FVS source,
  and it is the half that an upstream contribution would carry first.

## Alternatives considered

- **Fold both into one patch and apply it at the PyFVS root**, with the FVS paths prefixed `fvs/`.
  Rejected: the FVS source is a submodule with its own commit, and a patch that spans it cannot be
  applied to the submodule's own history or checked against `ef5fa84` alone.
- **Have CI make the two PyFVS edits with `sed`.** Rejected: an ad-hoc edit at a call site is the defect
  `AGENTS.md` names for the tree-list writer, and it would leave the change unrecorded.
- **Leave the recipe as ADR 0004 states it and drop the CI job.** Rejected: the job is the evidence that
  the criterion is met, and deleting a gate to make it pass is forbidden.
