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

## The `mcuft` defect — root-caused and fixed

**`mcuft` was 0 for all 200 years.** It is now populated. The cause was a two-line omission in the BC
variant, and finding it took four disproofs.

### The chain

`IOSUM(5)` is merchantable cubic, and PyFVS's label for it is correct — `metric/vbase/disply.f` line 427
sets `IOSUM(05)=INT(OMCCUR(7)/GROSPC+0.5)`. So `OMCCUR` was genuinely zero.

`base/gradd.f` builds it:

```fortran
CALL PCTILE(ITRN,IND,CFV, WK3,OCVCUR(7))    <- total cubic, from CFV
CALL PCTILE(ITRN,IND,MCFV,WK3,OMCCUR(7))    <- merch cubic, from MCFV
```

`common/ARRAYS.F77` line 57 states the contract for the second array:

```text
C      MCFV -- MERCHANTABLE CUBIC FOOT VOLUME PER TREE CALCULTED IN **VOLS**
```

**BC's `vols.f` never sets `MCFV`.** It computes merchantable volume into `WK1` and sets only
`CFV(I)=VN` at line 188. So `MCFV` stayed 0, `OMCCUR` stayed 0, and `IOSUM(5)` stayed 0.

The US variants migrated. `ie/vols.f` says so in place:

```fortran
C  LOAD WK1 WITH MERCH CUBIC VOLUME PER TREE.
C  WK1 array has been replaced with MCFV
!      WK1(I)=VM          <- commented out
       MCFV(I)=MCF        <- the replacement
```

BC was left behind on the old array.

### The fix

Two lines in `canada/bc/vols.f`, mirroring `MCFV(I)` from the final `WK1(I)` at both points where the
merch total is accumulated — the `METHC == 4` branch, and after the defect correction:

```fortran
        MCFV(I)=WK1(I)      <- before the METHC==4 accumulation
        ...
      MCFV(I)=WK1(I)        <- before the IF(IPASS.EQ.1) accumulation
```

Result: `mcuft` is nonzero in 17 of 21 rows, reaching 12,751 at year 200 against a total cubic of 13,108.
It matches the accumulated `SPCMC(ISPC,1)` exactly, which closes the chain.

### Four hypotheses disproved along the way

Recording these because each cost a build, and three of them were mine:

1. **That PyFVS's summary labels were wrong for BC.** They are correct. The IOSUM row order is shared
   between the imperial and metric builds; only the *display* order and units differ.
2. **That `METHC = 4` was the cause.** Setting it via a `VOLUME` keyword changed nothing. `SPCMC`
   accumulates fine under the default `METHC = 6`.
3. **That the tree geometry was implausible.** `min.f`'s debug output labels its values `DBH (cm)` and
   `Height (m)`, but it prints the *input* arguments, which are inches and feet. Checked against two known
   constants: the printed stump height `0.9843` is 30 cm in feet, and the top diameter `3.9370` is 10 cm in
   inches. Both match, so the stand is a plausible 21.5 in DBH and 145 ft.
4. **That `SPCMC` was not accumulating.** Instrumenting `vols.f` showed `IPASS = 1` on all 2,850 calls and
   `SPCMC(ISPC,1)` reaching 12,751. The data was fine; only its consumer was starved.

### Board feet

`mbdft` remains 0, and that is by design, not a second defect: `vols.f` carries the comment
"Board feet not computed in this variant".

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
