# What the fixture can and cannot express

`P29`'s close-out recommended the fixture as the next phase, on the claim that it was "the binding
constraint, not the code". `P30` tested that claim with three experiments. **Two of the three suspected
blockers are not the fixture at all**, and the third needs a route that was not found.

This note exists so the next attempt starts from the evidence rather than from the recommendation it
replaces.

## The fixture already produces several plots

`to_tree_list` assigns `plot_id` per stand — `plots.setdefault(stand, len(plots) + 1)` — so passing five
stands gives five plots. The tree list proves it:

```text
   1  1     10FD  18.9 0.0  4.9 ...
   1  4     10FD  21.3 0.0  5.1 ...
   2  1     10FD  53.1 0.0  7.8 ...
```

Plot 1 has trees, plot 2 has trees, and so on to plot 5. **Nothing needs adding to the fixture for
multi-plot input.**

## `FVS_Stats_Stand` is not blocked by the plot count

The run with five plots still writes only `FVS_Stats_Species_Metric`, and its report says:

```text
DISTRIBUTION OF ATTRIBUTES AMONG SAMPLE POINTS CANNOT BE COMPUTED WITH ONE SAMPLE POINT.
```

So FVS counts **one** sample point although the tree list carries five plot ids. `stats.f` returns early on
`IF(.NOT.LSTATS .OR. ITRN.EQ.0)`, and its comment at line 147 is explicit: with one point it writes the
species statistics and goes on. Whatever makes FVS see a single point, it is not the number of plot ids in
the tree list — so **the fixture is not the blocker**, and the next thing to read is how FVS derives its
point count.

## `FVS_Mortality_Metric` is not blocked by the stand size

A five-plot population with **40 trees per stand** and a 100 percent `SIMFIRE` burn writes `FVS_Fuels_Metric`
and no mortality table. `MORTREDB` is accepted — the report echoes `FFE MORTALITY INFO SENT TO SPECIFIED
DATABASE` — and the writer returns early on `IF(IMORTF.EQ.0)`, which the option sets to 1. So the call is
not reached, or nothing dies.

**What would settle it**: a fire the FFE mortality model acts on, which needs a fuel model the stand's fuel
load actually supports. That is a keyword question before it is a fixture question.

## The dwarf-mistletoe rating is not the damage field

Setting `damage1 = 21` with severity 2 on every tree, with a `MISTOE` block and `MISRPTS`, produces:

```text
NUMBER OF RECORDS WITH MISTLETOE                  0
```

and no dwarf-mistletoe table. The rating is not read from the damage columns: `comprs.f` moves it with
`MISGET`/`MISPUT`, and the only `MISPUT` callers in the source are `MISPUTZ` in the regeneration routines,
which **zero** it. Where the input sets a non-zero rating was not found.

So `damage1` is the wrong lever, and a fixture parameter for it would be a guess dressed as a feature.

## What this changes

- **The recommendation was wrong in two places.** `FVS_Stats_Stand` and `FVS_Mortality_Metric` are not
  fixture problems; they are questions about how FVS counts sample points and what makes FFE kill a tree.
- **The mistletoe route is unknown, not absent.** It exists — `MISGET`/`MISPUT` are the interface — but the
  input path to it was not found in the time this note took.
- **Nothing was added to the fixture**, because nothing was shown to be missing. A parameter that does not
  reach FVS would be worse than none: it would look like capability.
