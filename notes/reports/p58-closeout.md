# Phase close-out report: P58 Oracle coverage

Phase: P58 Oracle coverage
Parent issue: #248
Pull request: #250
Evidence head: `d9dd9a8`
Date: 2026-10-27
Status: merged.

## Recommendation

**No release.** This phase changed notes and no code. The next release is whatever fixes
`FVS_Regen_SitePrep`'s divergence.

## 1. What was achieved

**Twenty-eight of the thirty-one exposed tables are produced, and twenty-seven match a standalone
`FVSbc` value for value.** Thirteen had a check before this phase.

| Verdict | Count |
| --- | --- |
| Match | 27 |
| Differs, and the difference is open | 1 (`FVS_Regen_SitePrep`) |
| Explained | 1 (`FVS_Cases`) |
| Not comparable | 2 (`FVS_Error`, `FVS_InvReference`) |

## 2. What each table needed

Every table needed a `DATABASE` option **and** something the run has to do, and the option alone is
always accepted. That is the trap, and it is why the surface looked covered when it was not:

- **A removal** for `FVS_CutList_Metric` and `FVS_ATRTList_Metric` — both writers are called from
  `cuts.f`.
- **A fire** for `FVS_Mortality_Metric` — the writer is called from `fmburn.f`.
- **More than one plot** for `FVS_Stats_Stand` — it is the distribution among sample points.
- **An infection** for the four mistletoe tables, through damage codes 30 to 34, with `NEWSPRED` for
  the fourth.
- **A `PLANT` line with stems per acre** for the regeneration tables.
- **An `RDIN` block with `RRINIT` and `RRDOUT`** for root disease. The docs had recorded its required
  parameters as undetermined; they are `RRINIT` and `RRDOUT`, and the two tables are written and match.

`notes/reference/oracle-coverage.md` carries the recipe and verdict for each table.

## 3. The first genuine difference

`FVS_Regen_SitePrep` reports `PCT: 74 20 6` where the standalone reports `PCT: 100 0 0`:

```text
this package:   PCT:  74   20    6
standalone:     PCT: 100    0    0
```

**In the same `.out` block**, so the divergence is in the model and not in the writer. Neither run
supplies a site-preparation keyword, so `estab.f` calls `ESPREP` for the default probabilities, and the
two runs must be handing it different stand variables. `notes/triage.md` records it with the next step:
compare those variables, not the table.

This is what the oracle is for. Twenty-seven tables agree and one does not, and the one that does not is
now a specific question about `ESPREP` rather than a suspicion about everything.

## 4. What this does not do

- It does not fix the divergence. That is a bounded investigation of its own.
- It does not cover `FVS_BurnReport_Metric`, which is not exposed and whose gate needs an invalid
  inventory year.

## 5. How the coverage was reached

Three phases of groundwork made this phase cheap: `P49` made the comparison trustworthy, `P50` gave the
fire-model block a writer, and `P54` found that three tables were silently absent when the block came
after `INVYEAR`. Without those, this sweep would have reported noise.

The sweep itself was mostly wrong guesses. Each table cost two or three runs, and the missing piece was
always the event rather than the option.
