# FVSbc build spike

The result of attempting to build the BC variant, which answers the uncertainty that ADR 0001 leaves
open.

Date: 2026-10-21
Issues: #12
Phase: P2
Fork: `UBC-FRESH/PyFVS` at `e95172b`
FVS source: submodule `forest-modeling/ForestVegetationSimulator` at `ef5fa84`, branch `pyfvs-features`

## The question

ADR 0001 recorded one central uncertainty: whether adding `bc` to the PyFVS variant matrix is sufficient,
or whether the FVS source submodule needs a patch.

## The answer

**Adding `bc` to the variant matrix is not sufficient.** The BC source list is materially incomplete
against what PyFVS's API and database layers require. Six defects were found; three are fixed, and the
sixth is a reconstruction task rather than a patch.

| # | Defect | Status |
| --- | --- | --- |
| 1 | `meson_options.txt` rejects `bc` before anything compiles | fixed |
| 2 | `fire/cfim` does not compile on Linux | fixed, by a compiler flag |
| 3 | `numpy.f2py` cannot parse `canada/bc/BCPLOT.F77` | fixed |
| 4 | PyFVS's API calls `cubrds`, which no BC source defines | fixed |
| 5 | The source list omits `vdbsqlite/dbsreference.f` and three `dbsqlite/dbs_fiavbc_*.f` | partly fixed |
| 6 | The source list omits the entire `volume/` subsystem, which `dbs_fiavbc_*` depend on | **open** |

The build now reaches `[433/569]`. It does not complete.

## How to reproduce

A sparse clone is not enough: the FVS fork has a nested submodule, and without it `pn` fails to configure
too. Use a recursive clone.

```bash
git clone --depth 1 https://github.com/UBC-FRESH/PyFVS.git tmp/pyfvs
git -C tmp/pyfvs submodule update --init --recursive --depth 1
python3 -m venv tmp/build-venv
tmp/build-venv/bin/python -m pip install meson ninja meson-python setuptools-scm numpy patchelf
export PATH="$PWD/tmp/build-venv/bin:$PATH"
cd tmp/pyfvs
meson setup build-bc -Dfvsvariants=bc
meson compile -C build-bc
```

## Defect 1: the variant is not a permitted choice

`meson setup build-bc -Dfvsvariants=bc` fails at configure:

```text
meson.build:4:0: ERROR: Value "bc" for option "fvsvariants" is not in allowed choices:
"pn, wc, so, op, oc, ec, ca, nc, bm, ie, ci, ak, ws"
```

Fix: add `'bc'` to the `choices` list in `meson_options.txt`. The `value` list, the default set, is
unchanged.

## Defect 2: `fire/cfim` does not compile on Linux

The compile fails on all 12 `fire/cfim` sources:

```text
FAILED: libfvsbc.a.p/fvs_fire_cfim_nrutilcpp.cpp.o
../fvs/fire/cfim/stdafx.h:17:10: fatal error: tchar.h: No such file or directory
```

**The first fix attempted was wrong.** Deleting the 12 `../fire/cfim/` lines from the BC source list does
clear the error, but it removes `cfim_driver`, which `canada/fire/bc/fmcfim.f` line 166 calls. The compile
error became a link error. Deleting the lines is a remedy for a defect that does not exist.

The real cause is a missing compiler definition. `fire/cfim/stdafx.h` guards the Windows header:

```c
#include <stdio.h>
#ifndef unix
#include <tchar.h>
#endif
```

and `fire/cfim/cfim.cpp` has three branches:

```cpp
#ifdef CMPgcc
  #ifdef unix
    extern "C" int cfim_driver_ (              // GCC compiler, Unix OS
  #else
    extern "C" { __stdcall __declspec(dllexport) int cfim_driver_ (   // GCC compiler, Windows OS
#else
  extern "C" __declspec(dllexport) int CFIM_DRIVER (                  // VS2010 compiler, Windows OS
```

A Linux-clean branch already exists. Nothing defined `CMPgcc`, so the MinGW branch was taken.

Fix: `add_project_arguments('-DCMPgcc', '-Dunix', language: 'cpp')` in `meson.build`.

Note the scope: both Canadian source lists carry the `fire/cfim` sources, and no US variant does. No US
variant compiles `cfim`, so PyFVS had never built it on Linux. The fix is likely of interest upstream.

## Defect 3: f2py cannot parse `BCPLOT.F77`

The signature step fails:

```text
FAILED: fvsbc_pre.pyf
Exception: crackline: groupcounter(=0) is nonpositive. Check the blocks.
```

`canada/bc/BCPLOT.F77` is not a Fortran program unit. Its first line is `CODE SEGMENT BCPLOT`, and it holds
Fortran 90 derived types that f2py's fixed-form parser cannot handle.

`canada/bc/blkdat.f` fails for the same reason by a route that is easy to miss. Its line 22 is
`INCLUDE 'BCPLOT.F77'`, and f2py resolves an `INCLUDE` relative to the including file's directory, where
that file sits. Its other `INCLUDE` lines name files in `common/`, which f2py cannot resolve and ignores.
`blkdat.f` does not reference anything from `BCPLOT.F77`; the include is vestigial.

Fix, in two parts: remove the `INCLUDE 'BCPLOT.F77'` line from `canada/bc/blkdat.f`, and filter
`BCPLOT.F77` out of the f2py input in `meson.build`. The file is still compiled.

Verified: with both applied, the whole f2py step passes.

## Defect 4: `cubrds`

The link fails with `undefined symbol: cubrds_`. `cubrds` is defined in 20 variants and in no BC source.
PyFVS's `src/api/fvs_step.f90` references it from a subroutine that is never called:

```fortran
    subroutine donotcall()
        call blkdat()
        call esblkd()
        call cubrds()
        ...
```

Nothing calls `donotcall`; it exists to force the linker to keep the Fortran initializers. The symbol
reference is doing real work, so the answer is to satisfy it, not to delete it.

`cubrds` is 57 lines of zero-initialization for the `VOLSTD` common. Its `DATA` sizes follow `MAXSP`:
`wc` has `MAXSP=39` and writes `273*0.0` (`7*39`), `ca` has `MAXSP=50` and writes `350*0.0`, and **BC has
`MAXSP=15`, so it needs `105*0.0` and `15*0`**.

Fix: add `canada/bc/cubrds.f`, copied from `wc` with the sizes corrected for `MAXSP=15`, and add it to the
source list.

An earlier concern, that BC reads uninitialized volume arrays, is unfounded. `canada/bc/initre.f` writes
`CFVEQS` at lines 3522, 3537, and 3552. BC supplies its own coefficients, so a zero-initializing `cubrds`
is a link stub whose values BC overwrites.

## Defect 5: three database sources are missing

After `cubrds`, the link reports four more undefined symbols. Three are database routines the BC source
list omits and `pn`'s carries:

| Symbol | Defined in | In `pn`'s list |
| --- | --- | --- |
| `dbsreference_` | `vdbsqlite/dbsreference.f` | line 309 |
| `dbs_fiavbc_atrtls_` | `dbsqlite/dbs_fiavbc_atrtls.f` | line 311 |
| `dbs_fiavbc_cutlst_` | `dbsqlite/dbs_fiavbc_cutlst.f` | line 312 |
| `dbs_fiavbc_trls_` | `dbsqlite/dbs_fiavbc_trls.f` | line 313 |

All four were added to the BC source list. `dbsreference.f` is fine. The three `dbs_fiavbc_*` files are
not, and they lead to defect 6.

Not established: what references these four symbols. No source file calls them by name. The reference
must come from the database layer's own dispatch or from the f2py wrapper, and it was not traced.

## Defect 6: the `volume/` subsystem is absent, and `dbs_fiavbc_*` depend on it

Adding `dbs_fiavbc_cutlst.f` fails to compile:

```text
../fvs/dbsqlite/dbs_fiavbc_cutlst.f:36:0:
   36 |       INCLUDE 'wdbkwtdata.inc'
Fatal Error: Cannot open included file 'wdbkwtdata.inc'
```

`wdbkwtdata.inc` lives in `volume/NVEL/`. The scale of the gap:

| Source list | `volume/` entries | `.inc` entries |
| --- | --- | --- |
| `FVSpn_sourceList.txt` | 155 | 25 in `volume/NVEL` |
| `FVSwc_sourceList.txt` | 155 | — |
| `FVSak_sourceList.txt` | 155 | — |
| `FVSbc_sourceList.txt` | **1** | **0** |

The BC variant has its own volume equations, `canada/bc/cfvol.f` and `canada/bc/vols.f`, and it writes its
own `CFVEQS`. So the absent subsystem may be deliberate for the model, while `dbs_fiavbc_*` needs it for
the FIA volume and weight tables.

That is the open question, and it is not a patch. Either the BC list gains the volume subsystem, or the
`dbs_fiavbc_*` dependency is traced and removed. The second is more likely correct, because the first
would add a US volume library to a variant that does not use it.

## The patch set so far

Fork, `UBC-FRESH/PyFVS` at `e95172b`:

- `meson_options.txt`: add `'bc'` to `choices`.
- `meson.build`: `add_project_arguments('-DCMPgcc', '-Dunix', language: 'cpp')`, and filter
  `bcplot.f77` out of the f2py signature input.

Submodule, `ef5fa84`:

- `canada/bc/blkdat.f`: delete the `INCLUDE 'BCPLOT.F77'` line.
- `canada/bc/cubrds.f`: new, from `wc` with `MAXSP=15` sizes.
- `bin/FVSbc_sourceList.txt`: add `canada/bc/cubrds.f`, `vdbsqlite/dbsreference.f`, and the three
  `dbsqlite/dbs_fiavbc_*.f`.

## What this does not settle

- Defect 6, which blocks the build.
- Whether `FVSbc` produces correct results once it loads. Nothing has been run.
- The tree-record format hazard in `docs/reference/tree-list.rst`, the four output questions in
  `docs/reference/outputs.rst`, and the two units questions in `docs/reference/nemora-ingest.rst`. All
  need a module that imports.

The spike answers the build question: the variant matrix is not enough, and the work is a source-list
reconstruction rather than a small patch.
