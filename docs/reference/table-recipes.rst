Table recipes
=============

A ``DATABASE`` block names the tables a run may write, and **naming one is never enough on its own**.
The option is accepted whether or not the run does what the writer reports on, and the table is then
simply absent: the projection succeeds, the database is written, and nothing says the table is missing.
This page gives the second thing each table needs.

Every recipe here has been run, and every table in the *Checked* column has been compared against a
standalone ``FVSbc`` built from the same source and found to match **value for value**.

The keyword set that produces each table is in the repository note
``notes/reference/oracle-coverage.md``; this page is the contract, and that note is the evidence.

Always
------

These need only their option, plus the keyword where one is named.

.. list-table::
   :header-rows: 1

   * - Table
     - Option
     - Also needs
   * - ``FVS_Summary_Metric``
     - ``Summary``
     -
   * - ``FVS_Compute``
     - ``ComputDB``
     - a ``COMPUTE`` block, or there is nothing to write
   * - ``FVS_TreeList_Metric``
     - ``TREELIDB``
     - a ``TREELIST`` keyword
   * - ``FVS_StrClass_Metric``
     - ``STRCLSDB``
     - a ``STRCLASS`` keyword
   * - ``FVS_Stats_Species_Metric``
     - ``INVSTATS``
     - a ``STATS`` keyword
   * - ``FVS_Stats_Stand``
     - ``INVSTATS``
     - a ``STATS`` keyword **and ``DESIGN``'s fourth field above 1**: it is the distribution among
       sample points, and a one-plot stand has none

The fire-model block
--------------------

**Put ``FMIN`` before ``INVYEAR``.** ``FUELOUT`` and ``POTFIRE`` capture the inventory year when they are
read, and FVS treats a positive value as "suppress this report" — read after ``INVYEAR`` they switch
their own reports off and the tables are silently absent. The validator warns.

.. list-table::
   :header-rows: 1

   * - Table
     - Option
     - Also needs
   * - ``FVS_Fuels_Metric``
     - ``FuelsOut``
     - ``FUELOUT``
   * - ``FVS_PotFire_Metric``, ``FVS_PotFire_Cond_Metric``
     - ``PotfirDB``
     - ``POTFIRE``
   * - ``FVS_Consumption_Metric``
     - ``FuelReDB``
     - ``FUELREPT`` **and a fire**
   * - ``FVS_SnagDet_Metric``, ``FVS_SnagSum_Metric``
     - ``SnagOuDB``, ``SnagSuDB``
     - ``SNAGOUT``, ``SNAGSUM``
   * - ``FVS_Down_Wood_Vol_Metric``, ``FVS_Down_Wood_Cov_Metric``
     - ``DWDVLDB``, ``DWDCVDB``
     - ``DWDVLOUT``, ``DWDCVOUT``
   * - ``FVS_Carbon_Metric``, ``FVS_Hrv_Carbon``
     - ``CarbReDB``
     - ``CARBREPT``
   * - ``FVS_Mortality_Metric``
     - ``MORTREDB``
     - ``MORTREPT`` **and a fire**: the writer is called from ``fmburn.f``
   * - ``FVS_CanProfile``
     - —
     - ``CANFPROF``

``SIMFIRE`` schedules a fire: ``SIMFIRE=1,20,1,21,1,100,1`` is cycle 1, wind 20 km/h, moisture
condition 1, 21 °C, FFE mortality, the whole stand, early spring. Without one, the fire tables report
the initial state and the mortality table never appears.

The event tables
----------------

.. list-table::
   :header-rows: 1

   * - Table
     - Option
     - Also needs
   * - ``FVS_CutList_Metric``
     - ``CUTLIDB``
     - a ``CUTLIST`` keyword **and a removal** — the writer is called from ``cuts.f``
   * - ``FVS_ATRTList_Metric``
     - ``ATRTLIDB``
     - an ``ATRTLIST`` keyword **and a removal** — it is the after-treatment listing
   * - ``FVS_Regen_Tally_Metric``, ``FVS_Regen_SitePrep``
     - ``REGREPTS``
     - an ``ESTAB`` block with a ``PLANT`` or ``NATURAL`` line **carrying stems per acre**; a line
       with zero is refused and takes the whole keyword set with it

The blocks
----------

``RDIN``, ``MISTOE`` and ``ESTAB`` are blocks of **keywords**, written by the same writer as everything
else and checked against their readers' own tables. A hand-spaced line is read as different numbers with
no error, which is why they are not lines any more.

.. list-table::
   :header-rows: 1

   * - Table
     - Block
     - Option
   * - ``FVS_RD_Det_Metric``, ``FVS_RD_Sum_Metric``
     - ``RDIN`` with ``RRINIT`` and ``RRDOUT``
     - ``RDDETAIL``, ``RDSUM``
   * - ``FVS_DM_Spp_Sum_Metric``, ``FVS_DM_Stnd_Sum_Metric``, ``FVS_DM_Sz_Sum_Metric``,
       ``FVS_DM_TreeList_Metric``
     - ``MISTOE`` with ``MISTPINF``, ``MISTPRT`` and ``NEWSPRED``
     - ``MISRPTS``

**The dwarf-mistletoe tables also need an infection.** The rating enters through the damage columns —
code ``30`` with the Hawksworth rating as the severity — and ``NEWSPRED`` is what makes the per-tree
table appear. Without it, three of the four are written and the fourth is not.

``FVS_InvReference``
--------------------

It needs **no keyword at all** and is written on every run: species limits, site indices and volume
equations, one row per species. It is produced by ``DBSREFERENCE``, which ``fvs.f`` calls immediately
after ``STATS``.

**Before `0.18.0` no run of this package produced it.** The extension is driven by PyFVS's
``src/api/fvs_step.f90``, an extraction of ``fvs.f``'s initialisation that calls ``STATS`` and omitted
``DBSREFERENCE``; the original ``fvs_`` is dead code in the extension, so the writer was compiled in and
never called. The build recipe's PyFVS patch set now carries the missing call.

The two that are not recipes
----------------------------

* ``FVS_Error`` is written only when FVS logs something. A run that logs nothing has no such table,
  and that is a clean run.

.. note::

   ``FVS_Regen_SitePrep``'s ``PcntNone``, ``PcntMech`` and ``PcntBurn`` **cannot be relied on**. FVS
   decides whether to sample site preparation by branching on a local, ``LOAD``, that it only assigns
   when the stand is more than twenty years past inventory or a site-preparation keyword is present —
   so an ordinary run reads an uninitialised value. Two builds of the same source disagree. Every other
   table in the same run is unaffected; ``notes/triage.md`` carries the evidence.
