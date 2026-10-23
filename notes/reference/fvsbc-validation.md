# Validating FVS-BC against the official test suite

This note records the first validation of FVS-BC against an official reference, the three build defects
that had to be fixed before the reference could run, and what the comparison now shows and does not show.

Read at: PyFVS fork `UBC-FRESH/PyFVS` at `e95172b`, with the FVS source at
`forest-modeling/ForestVegetationSimulator` branch `pyfvs-features`, commit `ef5fa84`. The oracle is
`fvs/tests/FVSbc/`.

## The oracle

The FVS source ships an official test suite for the BC variant:

| File | What it is |
| --- | --- |
| `StandStructure.key`, `StandStructure.sum.save` | Input and expected summary, four stands |
| `YSM-SkyRanch.key`, `YSM-SkyRanch.sum.save` | Input and expected summary, a second case |
| `FVS-BC.Stand.Structure.Data.db`, `FVS-BC.YSM-SkyRanch.db` | The input stands, as SQLite databases |
| `StandStructureDBdump.txt.save`, `YSM-SkyRanchDBdump.txt.save` | Expected database dumps |
| `makefile` | The official comparison |

The official comparison is a diff of the fixed-width summary:

```bash
../../bin/FVSbc --keywordfile=StandStructure.key
grep -v -- "-999" StandStructure.sum | diff -w - StandStructure.sum.save
```

The dumps are the better oracle. `StandStructureDBdump.txt.save` asserts table contents directly, so the
comparison is on named, typed columns rather than fixed-width text.

## Running it

The keyword files take their input through FVS's own database path — `DATABASE`, `DSNin`, `StandSQL`, and
`TreeSQL` — rather than through `STDINFO` and a treelist file. Two things are needed to drive them through
PyFVS:

- The keyword file and the input database must be in the working directory, because `DSNin` is a relative
  path.
- PyFVS's `init_projection` does a case-sensitive `find('TREESQL')`, and the official keyword files spell it
  `TreeSQL`, so it concludes there is no tree source and demands a treelist. An empty `.tre` file alongside
  the keyword file satisfies the check; FVS itself never reads it, because `TreeSQL` supplies the trees.

## Five defects stood in the way

### 1. `TreeSQL` segfaulted

Running either official case crashed with `exit 139` during `init_projection`. The cause was an argument
list mismatch in the source list:

| | call site | routine compiled |
| --- | --- | --- |
| `metric/base/intree.f` (BC) | 30 arguments | `dbsqlite/dbstreesin.f`, **33** arguments |
| `base/intree.f` (pn) | 33 arguments | `dbsqlite/dbstreesin.f`, 33 arguments |

BC compiled the metric `INTREE`, which calls `DBSTREESIN` with 30 arguments, but linked the *base*
`DBSTREESIN`, which expects 33. The callee read three argument slots that did not exist (`RCULL`,
`IDECAY`, `IWDLDSTMS`) and wrote through them, so it crashed as soon as `TreeSQL` reached `INTREE`.

This is why the defect had survived: `StandSQL` never touches `INTREE`, a failed `fsql3_prepare` never calls
it, and the smoke run used a bare-ground keyword file, so `INTREE` never ran at all. PyFVS has no test over
the `DATABASE` path either — `tests/test_fia.py` reads its SQLite database with pandas and builds a treelist
by hand.

Fix: point the source list at `../metric/dbsqlite/dbstreesin.f`, whose 30-argument signature matches the
caller. BC's list had exactly one such base-vs-metric slip among the `dbsqlite` entries.

### 2. That file had never compiled

`metric/dbsqlite/dbstreesin.f` used FVS's own preprocessor style, `# IF _WIN64` / `# ELSE` / `# ENDIF` —
with a space after the `#`. PyFVS's build passes `-cpp` to gfortran, which rejects that. Every sibling
metric file uses cpp style (`#if !(_WIN64)` / `#endif`), so this one file simply could not have been built.
The guarded block is Windows `!DEC$` DLL-import decoration, which Fortran treats as comments anyway.

Fix: normalize the three directives to `#if` / `#else` / `#endif`.

### 3. Every event-monitor expression failed

With the crash gone, the run completed but the numbers were wrong, and the output database contained 320
copies of:

```text
FVS21 ERROR: AN EXPRESSION WAS INCORRECTLY COMPUTED; ANSWER IS IGNORED.
```

That message comes from `ERRGRO` error 21, raised by `ALGEVL` returning `IRC=2` — "the op-code contained an
undecipherable code". `ALGEVL` is FVS's expression evaluator, so the failure disabled the `COMPUTE` keyword
and every `IF` block, which is what drives the official keyword files' harvest-and-replant logic.

The cause was in `metric/base/evldx.f`, the routine that decodes a variable or parameter load for the
evaluator. `common/OPCOM.F77` sets

```fortran
MAXPRM=7999, MXCACT=10000, MXEXPR=2000, MXLREG=400,
```

so the parameter array holds 7999 entries, and a parameter reference is encoded as an instruction in
`1000..8999`, decoded as `PARMS(INSTR-1000)`. The two versions of `evldx.f` disagree about that range:

| | PARMS range handled |
| --- | --- |
| `base/evldx.f` | `INSTR.GT.1000 .AND. INSTR.LT.9000` — correct for `MAXPRM=7999` |
| `metric/base/evldx.f` | `INSTR.GT.1000 .AND. INSTR.LT.7000` — only reaches `PARMS(5999)` |

The metric version is stale: it was written when `MAXPRM` was 5999 and never updated. Any parameter
reference at index 6000 or above fell through to the next branch and was rejected as an undecipherable
code. Instrumenting `ALGEVL` to dump the failing instruction lists confirmed it — the codes were
`8999  8998  8997  8996  8995  8994`, that is `PARMS(7999)` downwards.

The metric version's unit conversions (`/ ACRtoHA`, `* FT3pACRtoM3pHA`) are wanted, so replacing it with
the base version is not an option. Fix: widen the range check to `INSTR.LT.9000`, matching `MAXPRM`.

Once fixed, the run produces **no error rows at all**.

### 4. The summary read `IOSUM` with the wrong stride

With the projection correct, the summary's period rows were still garbage: `Year = 0`, `Age = 0`, and
scrambled values, while the first row was correct. That pattern — row 1 right, every later row wrong — is
the signature of a leading-dimension mismatch.

`common/OUTCOM.F77` declares one array for the whole model:

```fortran
      INTEGER*4 IOSUM(22,MAXCY1)
```

`metric/vbase/sumout.f` takes it as a dummy, `IOSUM(I20,LENG)`, and indexes it with `I20` as the leading
dimension. The two callers disagree about what to pass:

| caller | passes |
| --- | --- |
| `vbase/disply.f` | `CALL SUMOUT (IOSUM,22,...)` — matches the declaration |
| `metric/vbase/disply.f` | `CALL SUMOUT (IOSUM,20,...)` — does not |

So the metric variant indexed a stride-22 array with stride 20. Only column 1 agrees between the two, which
is exactly why the initial row matched and everything after it did not. Fix: pass 22.

### 5. Newly established trees inherited a dead tree's merchantable volume

Four rows still differed, all in the merchantable cubic column, and all in cycles where trees are *added* —
the three rotation resets and the infill year. At the resets the summary reported `MCuM = 115` with
`TCuM = 0`: merchantable volume exceeding total volume, which is impossible.

`ARRAYS.F77` documents the array:

```fortran
C      MCFV -- MERCHANTABLE CUBIC FOOT VOLUME PER TREE CALCULTED IN **VOLS**
```

When a tree is established, the code resets the per-tree volumes for the new tree:

```fortran
      ITRN=ITRN+1
      ISP(ITRN)=I
      CFV(ITRN)=0.
      ITRUNC(ITRN)=0
```

`CFV` is reset; `MCFV` is not. So a newly established tree silently inherits the *previous occupant's*
merchantable volume. New trees are added after the growth phase, so `gradd.f` sums them into `OMCCUR`
before `vols.f` ever reaches them.

BC compiles `metric/strp/estab.f` (its own `canada/bc/estab.f` is not in the source list), and the same
omission is in `metric/strp/esuckr.f`. Both now reset `MCFV` alongside `CFV`.

This is the fourth instance of one pattern in this variant: a newer per-tree array was introduced, and one
of the places that initialises the older arrays was never updated. The `vols.f` `MCFV` work recorded in
`fvsbc-smoke-run.md` is the same pattern — and it is confirmed here, not merely plausible: the fix
reproduces, value for value, all nine of the oracle's nonzero merchantable-volume rows.

## Two smaller alignments

`rd/rdin.f` and `rd/rdsout.f` now use their `metric/` twins. Ontario — the closest working Canadian metric
variant — makes the same choice, and it makes the base choice for `isstag.f`, so a speculative swap of
`isstag.f` to the metric version was reverted.

## The `FVS_Compute` table

**`FVS_Compute` matches the oracle exactly.** That table asserts, per stand and year, three named volumes:
`SMVOL`, `MDVOL`, and `LGVOL`. For stand 101 all **40 of 40 rows are identical** to
`StandStructureDBdump.txt.save`:

| Year | SMVOL | MDVOL | LGVOL |
| --- | --- | --- | --- |
| 2020 | 0.07 | 0.0 | 0.0 |
| 2024 | 1.7 | 0.0 | 0.0 |
| 2029 | 10.67 | 0.0 | 0.0 |
| 2034 | 28.19 | 0.15 | 0.0 |
| 2039 | 50.19 | 3.1 | 0.0 |
| 2044 | 65.96 | 13.08 | 0.0 |
| 2049 | 70.29 | 33.09 | 0.0 |
| 2054 | 72.37 | 51.81 | 0.0 |
| 2059 | 65.87 | 75.69 | 0.0 |
| 2064 | 0.0 | 0.0 | 0.0 |

The 2064 reset is the rotation the `IF MOD(AGE,60) EQ 0` block performs, so the fix is confirmed by the
treatment firing as well as by the volumes.

## Running the official test as the project runs it

PyFVS's step API is single-stand by design: `init_projection` calls `filclose()` and then `INITRE`, so it
always restarts at the top of the keyword file. Driving it once per stand re-runs the first stand every
time, which is what produced the earlier one-block result.

The FFI does expose the native `fvs` routine — one `PROCESS` per call, which is what the real driver does:

```fortran
  DO
    CALL FVS(rtnCode)      ! one PROCESS = one stand
    IF (rtnCode .NE. 0) EXIT
  ENDDO
```

So the whole official test can be run without splitting the keyword file:

```python
f = fvs.FVS("bc")
f.fvslib.fvssetcmdline(kw, len(kw))
while int(f.fvslib.fvs()) == 0:
    pass
```

That reproduces the `-999` headers exactly — `41 101`, `41 103`, `41 251`, `41 253` — and writes one
`FVS_Cases` row per stand.

## What the comparison shows

**The first official case passes, with the project's own command.** From `fvs/tests/FVSbc/makefile`:

```bash
grep -v -- "-999" StandStructure.sum      > StandStructure.tmp
grep -v -- "-999" StandStructure.sum.save > StandStructure.tmp.save
diff -w StandStructure.tmp StandStructure.tmp.save
```

`diff` exits 0 with **zero differing lines across all 164 rows**, covering all four stands. The run writes
no error rows. One comparison therefore exercises the database read, the tree decode, the metric units, the
column order, the summary stride, and the establishment initialisation together.

**`FVS_Compute` also matches exactly**, 40 of 40 rows for stand 101, which independently confirms the
projection against named, typed columns rather than fixed-width text:

| Year | SMVOL | MDVOL | LGVOL |
| --- | --- | --- | --- |
| 2020 | 0.07 | 0.0 | 0.0 |
| 2024 | 1.7 | 0.0 | 0.0 |
| 2029 | 10.67 | 0.0 | 0.0 |
| 2034 | 28.19 | 0.15 | 0.0 |
| 2039 | 50.19 | 3.1 | 0.0 |
| 2044 | 65.96 | 13.08 | 0.0 |
| 2049 | 70.29 | 33.09 | 0.0 |
| 2054 | 72.37 | 51.81 | 0.0 |
| 2059 | 65.87 | 75.69 | 0.0 |
| 2064 | 0.0 | 0.0 | 0.0 |

The 2064 reset is the rotation the `IF MOD(AGE,60) EQ 0` block performs, so the treatment fires as well.

**The second official case is close but not exact.** `YSM-SkyRanch` now runs all fifteen stands — 375 rows,
the same length as the oracle — again with no error rows. 328 of 375 rows are identical, and twelve of the
fifteen blocks match exactly. The three that do not are `SkyRanch-Control`, `SkyRanch-1.0m`, and
`SkyRanch-2.0m`; `SkyRanch-0.3m` matches.

The disagreement is small and spread across the aggregate columns rather than concentrated in one:

| column | rows differing | largest difference |
| --- | --- | --- |
| `MCuM` | 35 | 6 |
| `TCuM` | 35 | 7 |
| `Tph` | 23 | 30 |
| `TopHt` | 22 | 2 |
| `SDI` | 14 | 3 |
| `QMD` | 12 | 0.1 |
| `CCF` | 11 | 1 |

That is the signature of a slightly different tree population rather than of a formatting or stride fault,
and it appears late: in `SkyRanch-Control` the rows agree through 2049 and diverge from 2054. Not yet
root-caused.

**All five asserted tables now have the oracle's shape.** The dump compares them row by row, and the
`DBSMIS2` fix brought `FVS_DM_Stnd_Sum_Metric` from fifteen rows to the oracle's 375:

| table | rows | row content identical |
| --- | --- | --- |
| `FVS_Cases` | 15 | 15 of 15 |
| `FVS_DM_Spp_Sum_Metric` | 400 | 336 |
| `FVS_DM_Stnd_Sum_Metric` | 375 | 311 |
| `FVS_DM_Sz_Sum_Metric` | 1875 | 1789 |
| `FVS_Summary_Metric` | 375 | 322 |

**Every remaining difference in the second case is in the same three stands** — `SkyRanch-Control`,
`SkyRanch-1.0m`, and `SkyRanch-2.0m` — across all four tables. `SkyRanch-0.3m` and all eleven `YSM029-*`
stands match the oracle exactly in every table. So the growth divergence above is the only outstanding defect
in `YSM-SkyRanch`, and the table-level view does not reveal a second one.

## What it does not show

- **`YSM-SkyRanch`'s residual is attributable to upstream changes made after the reference was generated,
  not to this build.** The two `.sum.save` files carry `06-28-2022` in their `-999` headers; the source built
  here is `ef5fa84`, dated 2026-09-10, and sixty-one commits touched the BC, `base`, `metric`, `vbase`, and
  `common` directories in between. The change matching the symptom most closely is `66a5e14e` (2026-03-06),
  "Sdi reporting update", which adds `ATDR016` and `ODR016` to `CONTRL.F77` — the Reineke diameter and the
  Reineke diameter at the end of the previous cycle, both by the Zeide method. The Reineke diameter is the
  quantity behind SDI, and an SDI difference is the first thing to appear in `SkyRanch-Control`: QMD 3.45
  against 3.44 at 2049, then SDI 298 against 296 at 2054. The same commit changes
  `metric/vdbsqlite/dbssumry.f` by 53 lines, and that routine writes `FVS_Summary_Metric`, whose QMD, SDI,
  MAI, and TPH columns are precisely the ones that differ. It also explains why only the three densest stands
  differ: SDI enters the model through density-dependent mortality, so a changed SDI formula bites where SDI
  approaches the species maximum and is inconsequential in sparse stands, twelve of which match exactly.
  The divergence correlates with the number of tree records rather than stand density — `YSM029-246` carries
  3699 trees per hectare from only 56 records and matches — but that is a consequence of how much mortality
  is executed, not an independent cause.
- **That attribution is not a proof.** Constructing one would mean building the source as of 2022-06-28, and
  that is not reachable by this path: the BC variant is not in `meson_options.txt` at that revision, and
  `src/api/fvs_step.f90`, which is how PyFVS drives the library, did not exist yet. What is documented is
  that the fixtures are old and that the project's own result checker currently skips this variant: the
  checker carries `#FVSbc -- Omit currently 20260226`. That omission predates `66a5e14e`, so the change
  above is a candidate rather than a demonstrated cause, and there may be more than one. An earlier version
  of this note read `canada/bin/FVSbcc_notReady.txt` as a marker that the variant is unready; it is not one.
  The 2018 change notes describe it as an old source list for the BC variant.
- **The residual is not floating-point ordering.** Building at `-O2 -ffp-contract=off -fno-tree-vectorize`
  produces output bit-identical to plain `-O2` — zero differing lines between the two builds themselves.
  A scan of every compiled source for a literal array dimension between 300 and 900 found only
  `fire/vbase/fmpocr.f`'s `CRFILL(400)`, `ADCRN(400)`, and `WPROP(400)`, and those index vertical fuel
  sections rather than trees, so a tree-record capacity limit is ruled out too.
- **A separate robustness problem: the build behaves differently at `-O0`.** Configured at `-O0`, the variant
  processes no stand at all: `fvs` returns 2 after its first call, no summary is written, and the output
  database is empty, where at `-O2` it runs all fifteen stands. `-fcheck=all` reports nothing, so whatever
  is at fault is not a Fortran array-bounds violation the runtime can see. This is independent of the
  residual above and is worth pursuing on its own.
- **One DM table's `gt45` column is the only non-`Summary` difference, and it is not separate.** Every real
  difference in `FVS_DM_Sz_Sum_Metric` is in the `gt45` column — the >45 cm class — and all of them are in
  the same three SkyRanch stands, so they are a consequence of the growth divergence rather than an
  independent defect. An earlier note in this file claimed that table differed for all fifteen stands; that
  was a comparison bug, where the literal `INF` in the `Type` column parsed as a floating-point infinity and
  made every `INF` row compare unequal.
- **Down woody debris is essentially exact.** `FVS_Down_Wood_Vol_Metric` matches the oracle on 159 of its
  160 asserted rows. The single difference is one cell, `3.5` against `3.49` in the hard component at one
  year — a rounding boundary, not a defect. An earlier version of this note claimed the soft component read
  0.0 where the oracle had 11.02. That was a comparison bug: it compared all nineteen columns of the table
  against the four the makefile actually selects.
- **The database dumps are compared for the tables this run populates.** The `StandStructure` dump's
  `FVS_Compute` and `FVS_Down_Wood_Vol_Metric` sections are compared row by row, and the `YSM-SkyRanch`
  dump's five tables are tabulated above. Tables this run does not populate — the fuels and potential-fire
  tables, for instance — are not compared.
