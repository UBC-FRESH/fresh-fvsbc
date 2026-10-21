Output contract
===============

What `fvsbc` reads back from a run, and what shape it hands to a caller.

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

1. `fvsbc` asks for the database output by default. A run that cannot produce one is a reported failure,
   not a silent fall back to text.
2. A parsed table is returned as a dataframe whose column names are the database's column names. `fvsbc`
   does not rename a column to something friendlier, because a rename breaks the trace back to the FVS
   schema.
3. `fvsbc` exposes the tables it has tested. A table it has not tested is not in the public API, even if
   the database holds it.
4. Every parsed table carries its `CaseID`, so a table can be joined back to `FVS_Cases`.
5. `FVS_Error` is read on every run. A run whose `FVS_Error` is non-empty is reported as failed, whatever
   the other tables contain.

Not verified
------------

- The column list of every table other than `FVS_Cases`. Only that one was read.
- Whether the BC variant populates every table, or whether some are for other variants.
- Whether the BC build's `dbsqlite` is reached by the `DATABASE` keyword in the BC variant, or whether
  the variant needs its own wiring.
- Whether any value the project needs exists only in the fixed-width reports.

All four are `P2.2` work, and the first three are answered by a single successful run.
