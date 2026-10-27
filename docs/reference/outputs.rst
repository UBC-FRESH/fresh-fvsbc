Output contract
===============

What `fresh-fvsbc` reads back from a run, and what shape it hands to a caller.

Read at: `forest-modeling/ForestVegetationSimulator`, branch `pyfvs-features`, commit `ef5fa84`.

Prefer the database
-------------------

FVS can write a SQLite database, and the BC build includes the component that does it: `dbsqlite` appears
52 times in `bin/FVSbc_sourceList.txt`. The `DATABASE` keyword, at slot 108 of the table in
`base/keywds.f`, turns it on.

This is the contract's primary output, and it is a deliberate choice over the alternatives:

- The database is **named and typed**. Its tables have declared columns, so a reader does not depend on
  column positions.
- It is **queryable**, so a caller can ask for one table rather than parse a whole run.
- It is **stable**, in the sense that a fixed-width report is not: an FVS report reflows when a value
  grows a digit.

Fixed-width output files, such as the summary and the main output, remain available. They are the
fallback for a value the database does not carry, and they are parsed in one tested reader, never by
ad-hoc slicing.

The tables
----------

The metric build creates 44 `FVS_`-prefixed tables. **An earlier revision listed 33, and they were
the *base* schema's names**: `dbsqlite/` creates `FVS_Down_Wood_Vol` and `FVS_SnagDet`, where this
variant's schema creates `FVS_Down_Wood_Vol_Metric` and `FVS_SnagDet_Metric`, so most of the old
list named tables a run here never writes. `notes/reference/table-names.md` has the evidence, and
the list below is derived from the schema's four layers with the most specific module winning:

.. code-block:: text

   FVS_ATRTList_Metric FVS_BurnReport_Metric FVS_CalibStats FVS_CanProfile
   FVS_Carbon_Metric FVS_Cases FVS_Climate_Metric FVS_Compute FVS_Consumption_Metric
   FVS_CutList_Metric FVS_DM_Spp_Sum_Metric FVS_DM_Stnd_Sum_Metric FVS_DM_Sz_Sum_Metric
   FVS_DM_TreeList_Metric FVS_Down_Wood_Cov_Metric FVS_Down_Wood_Vol_Metric
   FVS_EconHarvestValue_Metric FVS_EconSummary_Metric FVS_Error FVS_FIAVBC_ATRTList
   FVS_FIAVBC_CutList FVS_FIAVBC_Summary FVS_FIAVBC_TreeList FVS_Fuels_Metric
   FVS_Hrv_Carbon FVS_InvReference FVS_Mortality_Metric FVS_PotFire_Cond_Metric
   FVS_PotFire_Metric FVS_RD_Beetle_Metric FVS_RD_Det_Metric FVS_RD_Sum_Metric
   FVS_Regen_HabType FVS_Regen_Ingrow_Metric FVS_Regen_SitePrep FVS_Regen_Sprouts_Metric
   FVS_Regen_Tally_Metric FVS_SnagDet_Metric FVS_SnagSum_Metric FVS_Stats_Species_Metric
   FVS_Stats_Stand FVS_StrClass_Metric FVS_Summary_Metric FVS_TreeList_Metric

The run's identity is `FVS_Cases`. Its columns, from `dbsqlite/dbscase.f`, are:

.. code-block:: text

   CaseID  Stand_CN  StandID  MgmtID  RunTitle  KeywordFile
   SamplingWt  Variant  Version  RV  Groups  RunDateTime

`CaseID` is the primary key. `KeywordFile`, `Variant`, and `Version` are the columns that let a result
be traced back to what produced it, which is what :doc:`provenance` requires.

Contract rules
--------------

1. `fresh-fvsbc` asks for the database output by default. A run that cannot produce one is a reported failure,
   not a silent fall back to text. **Which tables it holds is the keyword set's business**: a `DATABASE`
   block names them, the model renders the block, and a table the block does not name is absent. An earlier
   revision of this page said the database held `FVS_Cases` and `FVS_Error` and no more, because PyFVS's
   step API occupied the block; that was wrong, and the run that reads eleven tables disproved it. A
   standalone `FVSbc` can be built from upstream `main` and writes the summary table, and it is **proven but
   not adopted** (ADR 0008, ADR 0009). The summary is also taken from `FVS.summary` in memory, and it is
   written as a fixed-width report beside the database.

   The database's name is **a default, not a fixture**: ``dbsqlite/dbsblkd.f`` initialises ``DSNOUT``
   to ``"FVSOut.db"``, and a ``DATABASE`` block may replace it with a ``DSNOut`` option, which
   ``dbsqlite/dbsin.f`` reads. The official case does exactly that, naming
   ``FVS-BC.Stand.Structure.Out.db``. So the name is a property of the keyword set. A run that does
   not name one gets ``FVSOut.db`` in its working directory, whatever the keyword file is called, and
   two such runs in one directory overwrite each other's database. A run therefore owns its
   directory: the projection is driven in a child process that changes into it, so the caller's
   directory is never touched and two runs in one process are independent (ADR 0010). **An earlier
   revision of this page said the name was fixed**, which the oracle test disproved the first time it
   ran, and an earlier revision of the orchestration ran in the caller's process, which made a run
   neither re-entrant nor thread-safe.
2. A parsed table is returned as a dataframe whose column names are the database's column names.
   `fresh-fvsbc` does not rename a column to something friendlier, because a rename breaks the trace back to
   the FVS schema. `pandas` is a dependency for this reason, and it is the project's only runtime one. An
   earlier revision returned records, because the project declared no dependencies at all; that was a
   narrowing of this rule and it is withdrawn.
3. `fresh-fvsbc` exposes the tables it has tested. A table it has not tested is not in the public API, even if
   the database holds it. **Thirty-one are exposed**: `FVS_ATRTList_Metric`, `FVS_CanProfile`,
   `FVS_Carbon_Metric`,
   `FVS_Cases`, `FVS_Compute`, `FVS_Consumption_Metric`, `FVS_CutList_Metric`,
   `FVS_DM_Spp_Sum_Metric`, `FVS_DM_Stnd_Sum_Metric`, `FVS_DM_Sz_Sum_Metric`,
   `FVS_DM_TreeList_Metric`, `FVS_Down_Wood_Cov_Metric`,
   `FVS_Down_Wood_Vol_Metric`, `FVS_Error`, `FVS_Fuels_Metric`, `FVS_Hrv_Carbon`, `FVS_InvReference`,
   `FVS_Mortality_Metric`, `FVS_PotFire_Cond_Metric`, `FVS_PotFire_Metric`, `FVS_RD_Det_Metric`,
   `FVS_RD_Sum_Metric`, `FVS_Regen_SitePrep`, `FVS_Regen_Tally_Metric`,
   `FVS_SnagDet_Metric`, `FVS_SnagSum_Metric`, `FVS_Stats_Species_Metric`, `FVS_Stats_Stand`,
   `FVS_StrClass_Metric`,
   `FVS_Summary_Metric` and `FVS_TreeList_Metric`. Most are written only when a `DATABASE` block asks
   for them, and the block must come before the stand setup — see :doc:`keywords`. **Naming a table's
   option is never enough on its own** — see :doc:`table-recipes` for the second thing each one needs. The row counts
   of the four the official dump carries are checked against it in `tests/test_oracle.py`, and
   twenty-seven of the thirty-one are checked against a standalone `FVSbc` value for value.

   **`FVS_StrClass_Metric` carries the structural stage**, which is the currency of old-growth and
   habitat assessment in British Columbia: one row per stratum per period, with its diameter, heights,
   crown base, crown cover and species.

   **`FVS_TreeList_Metric` and `FVS_CutList_Metric` are the per-tree tables**, one row per tree per
   period, with the FVS, PLANTS and FIA species codes so a result can be joined to anything else.
   **FVS spells one column differently in the two**: `CCum` in the tree list and `CCuM` in the cut
   list. That is FVS's schema, and a caller joining on the name has to know it.

   **The cut list is empty unless something is cut.** The option and the request are not enough: a
   thinning whose residual is above the stand's basal area is cancelled by FVS, and a cancelled
   removal writes no rows.

   **A carbon table can carry NULLs.** `FVS_Carbon_Metric`'s `Total_Stand_Carbon` is NULL in a period
   where one of its components is undefined, and the reader returns it as `NaN` rather than inventing a
   zero. A caller summing that column has to decide what a missing component means, and the reader does
   not decide for them.
4. Every parsed table carries its `CaseID`, so a table can be joined back to `FVS_Cases`.
5. `FVS_Error` is read on every run, and it holds **warnings as well as errors**: a run whose site data is
   outside the model's range writes an `FVS03 WARNING` row, which is not a failure. So a run is reported as
   failed when it holds a row *of severity* `ERROR`, whatever the other tables contain, and its warnings are
   returned rather than discarded.

   **The table's presence is not guaranteed either.** FVS writes `FVS_Error` only when it has
   something to log: a run that raises no warning and no error has no such table. An earlier revision of
   this page said the extension wrote it on every run, and the reader treated an absent table as a
   failure to read on that premise. A 999-tree single-plot case disproved it — FVS logged nothing, wrote
   no table, and the package reported a good run as failed. The reader now answers an absent table with
   an empty frame of the table's columns, so silence reads as a clean run.

Not verified
------------

- The column list of the tables the reader does not expose. Eleven are read, and their columns are the
  schema's; the other thirty-three are still unread.
- Which of the 44 tables a given run writes. The list above is what the component can create, not what a
  run produces: a `DATABASE` block names the tables, and a table it does not name is absent.
- `FVS_Compute` holds the user's `COMPUTE` expressions, one row per stand-period and one column per
  expression, and a keyword set that defines none produces no table at all.
- **Which of the rest can be written.** `notes/reference/table-reachability.md` classifies all 44 by
  writer and call site: 25 have a writer and a call site and are candidates, five have a writer that
  nothing calls, and one has a gate no valid input satisfies. A call site is not a promise — each
  candidate needs a case, because the triggers found so far were options inside blocks, not keywords.
