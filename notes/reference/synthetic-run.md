# The synthetic BC run

The first run of BC driven by a tree list this project wrote. It completes, it reads the list, and it
computes. `P2.2`'s subtask 7 is **partly** done: the run exists, and the output reader does not.

Date: 2026-10-23
Issues: #12
Phase: P2
Build: the patched fork of `UBC-FRESH/PyFVS` at `e95172b`, submodule `ef5fa84`, recipe in ADR 0004

## The build survived the rename

`pyfvs.fvsbc` imports from the spike virtual environment, which sits under a directory that was
renamed in `P2.4`. `pyfvs` reports `0.3.11`, `importlib` finds `pyfvs.fvsbc`, and
`pyfvs.variants.variant_libs` is `{'BC': 'fvsbc'}`. Nothing needed rebuilding.

## The writer's record, read back by BC's own format

BC's `TREFMT` was used to read a record that `src/fresh_fvsbc/treelist.py` wrote, with FVS's own
variable list from `base/intree.f`. **Twenty-four of the twenty-five fields come back exactly as
written**, and `tree_num` comes back as the composite the contract predicts.

```text
written: '   1  7     13PW  21.4 3.2105.0  0.0  0.571112131415161233180 4567 80'

plot_id      1        tree_num     17 *      tree_count   1.0
tree_history 3        species      PW        diam        21.4
dg_incr      3.2      live_ht    105.0      trunc_ht     0.0
htg_incr     0.5      crown_ratio  7         damage/sev  11 12 13 14 15 16
tree_val     1        tree_rx      2         plot vars   33 180 45 6 7
tree_age    80.0
```

`*` The tree number is read from columns 1 to 7, so BC sees the plot id's digits followed by the tree
number's. That is the documented consequence of `T1`, and it is the reason the writer refuses a tree
number needing more than columns 5 to 7.

This was run with `gfortran`, the compiler that built BC. It is **not** in the test suite, because the
suite must not depend on a Fortran compiler; it is recorded here instead. It answers the question the
tree-list contract left open: BC's format reads a record this project writes as intended.

## The file handoff, resolved

FVS does not take a filename for tree data. `metric/base/intree.f` derives it from the keyword file's
name: it tries `<keywordfile base>.TRE`, then `<keywordfile base>.tre`, skips lines beginning with
`*`, and stops at a line containing `-999`. `TREEFMT` must precede `TREEDATA`, and `TREEFMT` reads its
format from the two lines that follow it.

## The run

Driven through PyFVS's step API, the pattern the smoke run used. `end_projection` returns `0`, the
stand has trees at year 0 and grows over 20 cycles, and `FVS_Cases` holds one row carrying the case id
and the run datetime.

```python
from pyfvs import fvs

f = fvs.FVS("bc")
f.init_projection("synthetic.key")
for _ in range(f.globals.ncyc):
    f.grow()
rc = f.end_projection()  # rc == 0
```

The keyword file is the smoke run's bare-ground key with the planting removed, and `TREEFMT`,
`TREEDATA`, `RANNSEED`, `ECHOSUM`, `PROCESS`, and `STOP` added. The tree list is eight stems: the two
stands of the `nemora`-shaped fixture, with `species` and `tree_age` supplied by hand because the
fixture carries neither.

## What the run does not do, and the decisions it forces

1. **`FVS_Error` holds warnings as well as errors.** Our run's single row is
   `FVS03 WARNING: FOREST CODE INDICATES THE GEOGRAPHIC LOCATION IS OUTSIDE THE RANGE OF THE MODEL`,
   which the site data causes and which is not a failure. So the output contract's "assert
   `FVS_Error` is empty" is not the rule to test; the rule is that it holds no *error*, and a fixture
   with a BC-valid forest code would hold nothing at all.
2. **The database holds only `FVS_Cases` and `FVS_Error`.** `FVS_Summary_Metric`, `FVS_Compute`, and
   `FVS_TreeList_Metric` are absent, because they need a `DATABASE` output block to ask for them — and
   PyFVS already occupies that block. A key that carries its own is refused:
   `FVS16 ERROR: KEYWORD ENTERED IS USED IN WRONG CONTEXT AND WAS IGNORED. RECORDS READ= 19`, and
   record 19 is `DSNOut`. The summary is available in memory instead: `f.summary` returns 21 rows with
   named columns. **Which route the reader should take is open.**
3. **PyFVS's guard wants lowercase `.tre`.** A list written as `.TRE` passes FVS, which tries `.TRE`
   first, and fails PyFVS, which checks for `.tre`.
4. **The height units are still not settled.** `top_ht` is 19 at year 0 where the tallest input
   height was 7.8 m, so BC did not take `live_ht` as the top height directly; `SITECODE FD 100`
   probably dominates it. Settling this needs a controlled run that varies `live_ht` alone and watches
   what changes. The crown-ratio scale is the same kind of question and the same kind of experiment.

## The two controlled runs, and what they settled

The first run could not separate the height units or the crown-ratio scale from the site index that
dominates FVS's own height calculation. Both are now settled, one by a run and one by a reading.

**The height units are metres on both sides.** One tree, one plot, the site fixed and only `live_ht`
varied:

| `live_ht` given | `top_ht` at year 0 |
| --- | --- |
| 5.0 | 16.0 |
| 50.0 | 164.0 |
| 200.0 | 656.0 |

The ratios are 3.2, 3.28, and 3.28. That is the metre-to-foot factor, so the field takes metres and
the summary reports feet; had the field taken feet, the ratio would have been 1.

**The tree-list field is a crown class, not a fraction, a tenth, or a percentage.** `base/intree.f`
says so in its own comment, at lines 349 to 357:

```fortran
C  CONVERT INPUT CROWN CLASS VALUES (1-9) TO PERCENT
C  CROWN RATIO (1-99) IF NEEDED
      IF(ICR(I).LE.0)GOTO 37
      IF(ICR(I).LT.10) THEN
        ICR(I)=ICR(I)*10-5
      ELSE
        IF(ICR(I).GT.99)ICR(I)=99
      ENDIF
```

So the field holds 1 to 9, class 7 means 65 percent, and a value of 10 or more is taken as an
already-percent crown ratio that BC's single-digit field cannot carry. The contract's framing of this
item offered three answers and the true one was a fourth thing.

Both are now on `docs/reference/tree-list.rst` and `docs/reference/nemora-ingest.rst`.

## The determinism runs

One case, run three times through the same path. Two runs with `RANNSEED 1` produced **byte-identical**
summaries; a third with `RANNSEED 2` differed in one value at one period, year 30, 56 cubic feet against
55. So the seed controls the variation these runs show, which answers the second item
`docs/reference/provenance.rst` had left open.

It answers it within a bound, and the bound is worth stating: two runs a second apart would not show a
source that varies over a longer timescale, and four cycles on two plots would not show one that needs
more. "No other source showed itself here" is the claim; "RANNSEED is the only source" is not.
