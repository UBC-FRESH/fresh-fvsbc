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

The database component creates 32 `FVS_`-prefixed tables:

.. code-block:: text

   FVS_BurnReport FVS_CalibStats FVS_CanProfile FVS_Carbon FVS_Cases FVS_Climate
   FVS_Compute FVS_Consumption FVS_DM_Spp_Sum FVS_DM_Stnd_Sum FVS_DM_Sz_Sum
   FVS_Down_Wood_Cov FVS_Down_Wood_Vol FVS_EconHarvestValue FVS_EconSummary
   FVS_Error FVS_Fuels FVS_Hrv_Carbon FVS_Mortality FVS_RD_Beetle FVS_RD_Det
   FVS_RD_Sum FVS_Regen_HabType FVS_Regen_Ingrow FVS_Regen_SitePrep
   FVS_Regen_Sprouts FVS_Regen_Tally FVS_SnagDet FVS_SnagSum FVS_Stats_Species
   FVS_Stats_Stand FVS_StrClass

The run's identity is `FVS_Cases`. Its columns, from `dbsqlite/dbscase.f`, are:

.. code-block:: text

   CaseID  Stand_CN  StandID  MgmtID  RunTitle  KeywordFile
   SamplingWt  Variant  Version  RV  Groups  RunDateTime

`CaseID` is the primary key. `KeywordFile`, `Variant`, and `Version` are the columns that let a result
be traced back to what produced it, which is what :doc:`provenance` requires.

Contract rules
--------------

1. `fresh-fvsbc` asks for the database output by default. A run that cannot produce one is a reported failure,
   not a silent fall back to text. Through PyFVS's step API — the route this project uses — the database holds
   `FVS_Cases` and `FVS_Error`, and no more. The other tables need a `DATABASE` output block, PyFVS already
   occupies that block, and PyFVS's own API exposes no way to ask for one. A standalone `FVSbc` can be
   built from upstream `main` and does write the summary table, and it is **proven but not adopted**
   (ADR 0008, ADR 0009). The summary is taken from `FVS.summary` in memory, and it is also written as a
   fixed-width report beside the database.
2. A parsed table is returned as a sequence of records whose keys are the database's column names.
   `fresh-fvsbc` does not rename a column to something friendlier, because a rename breaks the trace back to the
   FVS schema. A dataframe is one conversion away, and making it is the caller's choice, because `pandas` is not
   a dependency of this project.
3. `fresh-fvsbc` exposes the tables it has tested. A table it has not tested is not in the public API, even if
   the database holds it.
4. Every parsed table carries its `CaseID`, so a table can be joined back to `FVS_Cases`.
5. `FVS_Error` is read on every run, and it holds **warnings as well as errors**: a run whose site data is
   outside the model's range writes an `FVS03 WARNING` row, which is not a failure. So a run is reported as
   failed when it holds a row *of severity* `ERROR`, whatever the other tables contain, and its warnings are
   returned rather than discarded.

Not verified
------------

- The column list of every table other than `FVS_Cases` and `FVS_Error`. Those two were read; neither of the
  other thirty is exposed, so their columns are still unread.
- **Answered by the first synthetic run.** BC populates only some of the thirty-two tables: through PyFVS's
  step API the database holds `FVS_Cases` and `FVS_Error`, and the official cases write a further set because
  their keyword files ask for it. So the list above is what the component can create, not what a given run
  writes.
- **Answered the same way.** BC's `dbsqlite` **is** reached, and the database is written without wiring in the
  BC variant. What cannot be reached through PyFVS is the request for a named table.
- **Answered: `FVS_Compute` is not a general output table.** It holds the user's `COMPUTE` expressions, one
  row per stand-period and one column per expression, and a keyword set that defines none produces no table
  at all. This project defines none, so the table does not exist for its runs and is not in the reader's
  surface. `FVS_TreeList_Metric` needs a `TREELIST` request, which the project does not make. See ADR 0009.

All four are `P2.2` work, and the first three are answered by a single successful run.
