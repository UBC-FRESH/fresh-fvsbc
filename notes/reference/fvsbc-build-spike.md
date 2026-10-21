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
or whether the FVS source submodule needs a patch. Every later phase depended on the answer.

## The answer

**Adding `bc` to the variant matrix is not sufficient.** The variant compiles, links, and produces a
Python extension module, but the module cannot be imported. Four separate defects stand in the way, and
three are fixed.

| # | Defect | Fixed |
| --- | --- | --- |
| 1 | `meson_options.txt` rejects `bc` before anything is compiled | yes |
| 2 | The BC source list carries 12 Windows-only C++ sources | yes |
| 3 | `numpy.f2py` cannot parse `canada/bc/BCPLOT.F77` | yes |
| 4 | PyFVS's API calls `cubrds`, which no BC source defines | **no** |

## How to reproduce

A sparse clone is not enough: the FVS fork has a nested submodule, and without it `pn` fails to configure
too. Use a recursive clone.

```bash
git clone --depth 1 https://github.com/UBC-FRESH/PyFVS.git tmp/pyfvs
git -C tmp/pyfvs submodule update --init --recursive --depth 1
python3 -m venv tmp/build-venv
tmp/build-venv/bin/python -m pip install meson ninja meson-python setuptools-scm numpy patchelf
export PATH="$PWD/tmp/build-venv/bin:$PATH"
```

Then, with the three patches below applied:

```bash
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

Fix: add `'bc'` to the `choices` list in `meson_options.txt`. The `value` list, which is the default set,
was left alone.

## Defect 2: the source list carries Windows-only sources

With defect 1 fixed, the compile fails in the C++ phase, on all 12 `fire/cfim` sources:

```text
FAILED: libfvsbc.a.p/fvs_fire_cfim_nrutilcpp.cpp.o
../fvs/fire/cfim/stdafx.h:17:10: fatal error: tchar.h: No such file or directory
```

`tchar.h` is an MSVC header. `fire/cfim/stdafx.h` includes it, so the whole component is Windows-only.

The BC source list carries these; the US variants do not:

| Source list | `fire/cfim` entries |
| --- | --- |
| `FVSbc_sourceList.txt` | 12 |
| `FVSon_sourceList.txt` | 12 |
| `FVSpn_sourceList.txt` | 0 |
| `FVSwc_sourceList.txt` | 0 |
| `FVSak_sourceList.txt` | 0 |

Both Canadian variants carry them, and no US variant does. Fix: delete the 12 lines. The BC source list
goes from 655 lines to 643, and the C++ phase then passes.

## Defect 3: f2py cannot parse `BCPLOT.F77`

With defects 1 and 2 fixed, the only failure is the signature step:

```text
FAILED: fvsbc_pre.pyf
Exception: crackline: groupcounter(=0) is nonpositive. Check the blocks.
```

Bisecting the f2py input list isolated it to two files, and then to one cause.

`canada/bc/BCPLOT.F77` is not a Fortran program unit. Its first line is `CODE SEGMENT BCPLOT`, and it
holds Fortran 90 derived types:

```fortran
      TYPE BEC_DESCRIPTION
        SEQUENCE
        CHARACTER (LEN=3)  :: Region
        ...
      END TYPE
```

`numpy.f2py` parses fixed-form Fortran and cannot handle that construct.

`canada/bc/blkdat.f` fails for the same reason, by a route that is easy to miss. Its line 22 is:

```fortran
      INCLUDE 'BCPLOT.F77'
```

f2py resolves an `INCLUDE` relative to the including file's directory, and `BCPLOT.F77` sits beside
`blkdat.f`. So f2py reads it and dies. Its other `INCLUDE` lines name files in `common/`, which it cannot
resolve, and it ignores those.

Two things follow:

- `blkdat.f` does not reference anything from `BCPLOT.F77`. The include is vestigial, and removing it does
  not change what the file compiles to.
- `BCPLOT.F77` is also passed to f2py directly, as line 1 of the source list, so it must be excluded from
  the signature input as well as from the include.

Fix, in two parts:

1. Remove the `INCLUDE 'BCPLOT.F77'` line from `canada/bc/blkdat.f`.
2. Filter `BCPLOT.F77` out of the f2py input in `meson.build`. The file is still compiled; it is only
   dropped from the signature generation.

Verified: with both applied, the whole f2py step passes.

## Defect 4: a symbol the BC variant does not provide

With defects 1 to 3 fixed, the build **succeeds**:

```text
[531/531] Linking target fvsbc.cpython-312-x86_64-linux-gnu.so
```

PyFVS also registers the variant correctly. Its generated `variants.py` reads:

```python
variant_libs = {
    "BC": "fvsbc",
}
variants = [v.upper() for v in variant_libs.keys()]
```

The module still cannot be imported:

```text
ImportError: .../fvsbc.cpython-312-x86_64-linux-gnu.so: undefined symbol: cubrds_
```

`cubrds` is defined in 23 variants — `acd ak bm ca ci cr cs ec em ie kt ls nc ne sn so tt ut wc ws` — and
in no BC source. The reference comes from PyFVS's own API, `src/api/fvs_step.f90`:

```fortran
    subroutine donotcall()
        ! external fmcblk !NOTE: This did not work as-is
        call blkdat()
        call esblkd()
        call cubrds()
        call keywds()
        call svblkd()
        call dbsblkd()
        call fmcblk()
```

So PyFVS's API layer hardcodes a call that the BC variant cannot satisfy. This is an integration gap
between PyFVS and the BC variant, not a defect in the BC variant's own sources.

Not resolved. The options are to supply a BC `cubrds`, to guard the call, or to check whether `cfvol`
covers what `cubrds` provides. Deciding that is `P3` work.

## A second gap, not yet a blocker

The BC source list has **1** `volume/` entry. `pn`, `wc`, and `ak` each have **155**, including the whole
of `volume/NVEL`, the volume library. The BC variant does have `canada/bc/cfvol.f` and
`canada/bc/vols.f`, so this may be deliberate. It is not established either way, and it is recorded as a
question rather than a finding.

## The patch set

Fork, `UBC-FRESH/PyFVS` at `e95172b`:

- `meson_options.txt`: add `'bc'` to `choices`.
- `meson.build`: filter `bcplot.f77` out of the f2py signature input.

Submodule, `ef5fa84`:

- `bin/FVSbc_sourceList.txt`: delete the 12 `../fire/cfim/` lines.
- `canada/bc/blkdat.f`: delete the `INCLUDE 'BCPLOT.F77'` line.

## What this does not settle

- The `cubrds` gap, which blocks the import.
- Whether `FVSbc` produces correct results once it loads. Nothing has been run.
- The tree-record format hazard in `docs/reference/tree-list.rst`. The three-format conflict could not be
  tested, because the module does not import.
- The four output questions in `docs/reference/outputs.rst`, for the same reason.
- The two units questions in `docs/reference/nemora-ingest.rst`.

The spike answers the build question. It does not answer whether the result is usable.
