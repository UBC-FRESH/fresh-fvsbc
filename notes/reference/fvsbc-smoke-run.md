# FVSbc smoke run

The first execution of the built BC variant. It runs, and it computes, but one column is wrong.

Date: 2026-10-21
Issues: #12
Phase: P2
Build: the patched fork of `UBC-FRESH/PyFVS` at `e95172b`, submodule `ef5fa84`, recipe in ADR 0004

## What was run

The fork was installed into the spike virtual environment with the BC variant:

```bash
SETUPTOOLS_SCM_PRETEND_VERSION=0.3.11 python -m pip install --no-build-isolation . \
    --config-settings=setup-args="-Dfvsvariants=bc"
```

`SETUPTOOLS_SCM_PRETEND_VERSION` is needed because the shallow clone carries no tags, and setuptools_scm
then produces `0.3.11.dev0.post0`, which is not a valid version.

PyFVS registers the variant:

```python
>>> import pyfvs.variants as v
>>> v.variant_libs
{'BC': 'fvsbc'}
```

The run uses PyFVS's own step API, the same pattern as its `tests/test_variants.py`:

```python
from pyfvs import fvs

f = fvs.FVS("bc")
f.init_projection("bc_bareground.key")
for c in range(f.globals.ncyc):
    f.grow()
rc = f.end_projection()  # rc == 0
```

The keyword file is `pn`'s bare-ground fixture, adapted. Two changes: the species code becomes `FD`, which
is BC's code, where the US variants use `DF`; and `VOLEQNUM` is dropped, because it names a US volume
equation.

```text
STDIDENT
TEST_BC   BC smoke test - bare ground, one planting
STDINFO          712    CHS131         0       200        35        16
MANAGED            0         1
SITECODE          FD       100
INVYEAR            0
DESIGN             0         1       999         1         0         1         1
NUMCYCLE          20
NOTREES
ESTAB              0
PLANT              1        FD       450        95         2         1         0
END
ECHOSUM
PROCESS
STOP
```

`end_projection()` returns 0, and `f.summary` returns the in-memory summary table.

## The result

| year | age | tpa | tcuft | mcuft | baa | ccf | top_ht | for_type | size | stock |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 999 | 5 | 5 |
| 10 | 10 | 173 | 0 | 0 | 1 | 3 | 9 | 201 | 3 | 4 |
| 20 | 20 | 168 | 48 | 0 | 6 | 12 | 22 | 201 | 3 | 4 |
| 40 | 40 | 162 | 588 | 0 | 36 | 50 | 46 | 201 | 2 | 4 |
| 60 | 60 | 158 | 2,126 | 0 | 88 | 104 | 75 | 201 | 1 | 3 |
| 100 | 100 | 133 | 7,391 | 0 | 209 | 188 | 117 | 201 | 1 | 2 |
| 140 | 140 | 110 | 10,652 | 0 | 266 | 214 | 131 | 201 | 1 | 2 |
| 200 | 200 | 90 | 13,108 | 0 | 297 | 223 | 142 | 201 | 1 | 2 |

The trajectory is coherent. The stand starts bare. Planting establishes 173 trees per acre by year 10.
Height climbs from 9 to 142 feet, basal area from 1 to 297 square feet per acre, crown closure from 3 to
223, and total cubic volume from 0 to 13,108 cubic feet per acre. Self-thinning reduces trees per acre
from 173 to 90. The size class improves from 5 to 1 and the stocking class from 4 to 2. The forest type
settles at 201.

**This is a working FVS-BC run, not a stub returning zero.**

## The defect this exposes

**`mcuft` is 0 for all 200 years.** Merchantable cubic volume never accumulates, while total cubic volume
does. Every other column behaves.

That is not a rounding artifact and not a plotting choice. A 200-year-old stand with 297 square feet of
basal area and 142 feet of top height has merchantable volume.

The most likely cause is that the merchantable volume equations are unset. The smoke keyword file drops
`VOLEQNUM`, which names a volume equation, and BC's volume coefficients are written by
`canada/bc/initre.f` into `CFVEQS`, which `cubrds` zeroes. Whether BC needs its own `VOLEQNUM`-equivalent
keyword, or a coefficient table, was not established.

Not verified: the cause. The observation is solid; the explanation is a hypothesis.

## What this does and does not settle

Settled:

- The BC variant builds, imports, and runs a 20-cycle, 200-year projection.
- The step API works: `init_projection`, `grow`, and `end_projection` return cleanly.
- The summary table is populated and internally consistent for total volume, height, basal area, crown
  closure, trees per acre, and the classification columns.
- BC's species code `FD` is accepted by `SITECODE` and `PLANT`.

Not settled:

- The `mcuft` defect above.
- Whether the numbers are *correct*, as opposed to merely plausible. Nothing has been compared against an
  official FVS-BC output. PyFVS does that for its variants by comparing a `.sum` file against a saved
  reference; `fvsbc` has no such reference yet.
- The tree-record format hazard in `docs/reference/tree-list.rst`. The smoke run uses PyFVS's own tree
  handling, so it does not exercise a treelist that `fvsbc` wrote.
- The output contract in `docs/reference/outputs.rst`. The run used the in-memory summary, not the SQLite
  database, so the 32 tables remain unverified.
- The two units questions in `docs/reference/nemora-ingest.rst`. The summary reports feet and square feet
  per acre, which suggests imperial output for a BC metric variant, and that was not investigated.
