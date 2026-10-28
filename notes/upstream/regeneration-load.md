# Draft: uninitialised `LOAD` in the BC regeneration model

A draft issue for the FVS maintainers. **Not posted.** Posting is the maintainer's decision, because
it is someone else's repository; the command is at the end.

Reported against `forest-modeling/ForestVegetationSimulator` at `28fda8ed`, which is the revision
this project builds its standalone `FVSbc` from (ADR 0008). The same code is present at
`UBC-FRESH/PyFVS`'s submodule, `ef5fa847`.

---

## Title

BC regeneration: `estab.f` reads an uninitialised `LOAD`, so site preparation is either sampled or
skipped at random

## What happens

`metric/strp/estab.f` decides whether to choose a site-preparation treatment for each plot with:

```fortran
      IF(NTALLY.NE.1) GO TO 242
      IF(LOAD.NE.1) GO TO 249          ! line 217
C
C     IF LOAD=1, REP PLOT PREPS; IF NEEDED COMPRESS ARRAY IPPREP.
C
```

**`LOAD` is assigned in exactly two places, and neither is reached by an ordinary run:**

- `estab.f` line 101, inside `IF(KDT+1-IY(1).GT.20) THEN; INADV=1; LOAD=0; ENDIF` — only when the
  regeneration date is more than twenty years past the inventory year.
- `strp/esetpr.f` lines 33 and 67, `IP=0` — only inside the `BURNPREP` (activity 491) and `MECHPREP`
  (activity 493) loops, and only when such an activity exists.

`LOAD` is a member of `COMMON /ESHAP/` (`common/ESHAP.F77`, the Canada-BC code segment) and is not
initialised in `BLKDAT` or anywhere else. A run that is within twenty years of inventory and supplies
no site-preparation keyword therefore reads **whatever was left in that common block**.

## Why it matters

The value decides between two different models:

- **`LOAD = 0`** takes the `249` branch, calls `ESPREP` for the default probabilities and **samples a
  treatment for each plot** out of the pre-generated `WK6` array.
- **`LOAD = 1`** takes the compress branch and **reuses `IPPREP` as it stands**, which on a first
  tally is the initialised value for every plot — so **no site preparation is applied at all**,
  whatever the probabilities say.

So the regeneration model either applies a site-preparation treatment or applies none, depending on
the contents of an uninitialised variable.

## Evidence

Two builds of the **same source** disagree, which is how this was found. Instrumenting `estab.f` in
each and running one identical case — a 1,000-tree stand, `DESIGN 0 1 999 1 0 1 1`, one `ESTAB` block
with `PLANT 0 FD 3680 90`, no site-preparation keyword:

| Build | `LOAD` | `PNONE` / `PMECH` / `PBURN` | `SUMPRE(1..5)` | reported `PCT: NONE MECH BURN` |
| --- | --- | --- | --- | --- |
| A | **0** | 0.75 / 0.20 / 0.05 | 37, 10, 3, 0, 50 | `74 20 6` |
| B | **1** | 0.00 / 0.00 / 0.00 | 50, 0, 0, 0, 50 | `100 0 0` |

Both print a `SITE PREP SUMMARY`; only A sampled. `IDUP=50`, `DUPNPT=50` and `NPTIDS=1` in both, so
the replication is identical and `LOAD` is the only difference.

## Reproduction

1. Build `FVSbc` from `28fda8ed` with the BC source list.
2. Run any BC stand whose inventory year is the current one and which supplies no `MECHPREP` or
   `BURNPREP`.
3. Read `SITE PREP SUMMARY` in the `.out`, or `FVS_Regen_SitePrep`'s `PcntNone`, `PcntMech` and
   `PcntBurn` if a `DATABASE` block asks for it.
4. Rebuild — for example with a different optimisation level, or from a different revision with the
   same code — and run the same case.

The three numbers change, and the regeneration results with them.

## Suggested fix

Initialise it, in the same place the rest of the BC common block is initialised — or defensively at
the top of `estab.f`:

```fortran
      LOAD = 0
```

before line 217's test, so that a run with no site-preparation activity and no replication takes the
sampling branch rather than the compress branch. `ESPREP` then supplies the probabilities, which is
what the `246`/`249` comment says should happen.

If `LOAD = 1` is meant to be the default for a first tally, the fix is the opposite constant — but it
should be a constant rather than whatever the linker left behind.

## Related, and lower priority

`strp/esprep.f` in this variant is a stub that returns `0.75 / 0.20 / 0.05` with no regression:

```fortran
      PNONE = 0.75
      PMECH = 0.20
      PBURN = 0.05
```

The predictive model is in `estb/esprep.f`, which this source list does not compile. That may be
deliberate for BC; it is mentioned only because it is what the sampling in the table above is
drawing from.

---

## Posting

To the repository that owns `metric/strp/estab.f`. That is `forest-modeling/ForestVegetationSimulator`
for this project's build; if the file also lives in `USDAForestService/ForestVegetationSimulator`,
that is the better target.

```bash
gh issue create --repo USDAForestService/ForestVegetationSimulator \
  --title "BC regeneration: estab.f reads an uninitialised LOAD, so site preparation is sampled or skipped at random" \
  --body-file <this file, without this section>
```
