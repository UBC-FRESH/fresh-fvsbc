Calibration dataset
===================

What the calibration workstream reads, how it is built, and what it is allowed to
claim.

This page describes the **input dataset**, not a calibration. It turns the public
FAIB permanent-sample-plot files into tidy tables. The parameters are fitted in a
later workstream, on a train/validation split that is fixed before fitting.

Inputs
------

The builder reads four CSV files from one directory:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - What it carries
   * - ``faib_header.csv``
     - Site identity, BEC zone/subzone/variant, TSA, ownership
   * - ``faib_sample_byvisit.csv``
     - Visit number and measurement year
   * - ``faib_plot_header.csv``
     - Plot identity and design
   * - ``faib_tree_detail.csv``
     - Tree species, DBH, height, live/dead status, expansion factor, basal area,
       and merchantable volume

The archive is public, but it is not downloaded by this project. The caller names
the directory, and the manifest records each file's size and SHA-256.

Outputs
-------

The builder writes six tables and a manifest:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Table
     - One row per
   * - ``visits.csv``
     - Plot visit: live BA (m2/ha), TPH, volume (m3/ha), top height, QMD
   * - ``intervals.csv``
     - Consecutive visit pair: years, dead BA, dead TPH, BA mortality, net and gross BA rate
   * - ``tree_survival.csv``
     - Live tree at the start of an interval: species group, DBH, BA, end status
   * - ``bec_coverage.csv``
     - BEC: sites, visits, repeat sites, intervals, live/dead/missing/damaged trees
   * - ``bec_envelope.csv``
     - BEC: BA p50/p90/p99/max, mean TPH, mean volume
   * - ``bec_species_envelope.csv``
     - BEC and species group: the same envelope
   * - ``species_crosswalk.csv``
     - PSP species code: FVS code, calibration group, known flag
   * - ``manifest.json``
     - Input and output rows, checksums, interval bounds, and zones

**The tree-level tables carry site identifiers.** They stay in the caller's
output directory. Only the aggregate tables are copied into
``notes/reference/calibration/``.

Inclusion rules
---------------

- **Supported zones only, for tree tables.** The BC variant resolves ``ESSF``,
  ``ICH``, ``IDF``, ``MS``, ``PP``, ``SBS``, and ``SBPS``. ``CWH``, ``CDF``,
  ``BWBS``, ``CMA``, and ``MH`` are counted in ``bec_coverage.csv`` but contribute
  no interval or tree-survival row until the upstream extension (W2) lands.
- **Live trees at the start.** A tree is in an interval only if it is live at the
  first visit with a positive expansion factor and a DBH.
- **Dead, live, or missing at the end.** A tree recorded dead is ``dead``; a tree
  recorded live is ``live``; a tree absent from the second visit is ``missing``.
  Missing is not counted as dead.
- **Interval length 2 to 40 years.** Shorter intervals are mostly measurement
  noise; longer ones mix several disturbances and a climate trend.
- **``PHF_TREE`` is the expansion factor.** It already includes ``TREE_WT`` and
  ``PLOT_WT`` in the FAIB compilation; the builder still multiplies by
  ``TREE_WT`` defensively, because a future extract may not fold it.
- **Damage is a partial disturbance flag.** A tree is ``damage=True`` when any
  of the five ``DAM_AGN*`` columns is positive. Those columns identify an agent,
  not a harvest or a fire; the extract does not carry a reliable harvest or fire
  history, so an interval with a known harvest must be excluded by the analyst.


Columns
-------

``visits.csv``

- ``SITE_IDENTIFIER``, ``CLSTR_ID``, ``VISIT_NUMBER``, ``PLOT``, ``MEAS_YR``
- ``BEC``, ``TSA_DESC``, ``supported``
- ``ba``, ``tph``, ``volume``, ``top_height``, ``qmd``, ``live_trees``

``intervals.csv``

- ``interval_id``: ``site|cluster|plot|year0|year1``
- ``year0``, ``year1``, ``years``, ``ba0``, ``tph0``, ``next_ba``, ``next_tph``
- ``dead_ba``, ``dead_tph``, ``ba_mortality``, ``tph_mortality``
- ``net_ba_rate``, ``gross_ba_rate``, ``BEC``, ``TSA_DESC``

``tree_survival.csv``

- ``interval_id``, ``BEC``, ``TSA_DESC``, ``CLSTR_ID``, ``PLOT``, ``group``
- ``dbh``, ``phf``, ``ba``, ``years``, ``ba0``, ``tph0``
- ``damage``, ``status`` (``live``, ``dead``, ``missing``), ``dead``, ``known``, ``exposure``

Running it
----------

.. code-block:: bash

   python scripts/build_calibration_dataset.py \
     --psp-dir "$FAIB_PSP_DIR" \
     --out-dir runtime/calibration

The command writes the tables and prints the manifest's row counts. It exits 2
when an input file is missing.

Current snapshot
----------------

The 2026-11-02 build of the archive holds **7,341 sites and 23,956 visits**. Of
those, **4,430 sites** and **13,191 visits** are in the seven supported zones;
9,186 interval pairs and 1,031,828 tree-survival rows are in the supported-zone
dataset. The aggregate tables, including 594 BEC × species envelope rows, are in
``notes/reference/calibration/``.

The `IDFdk3` envelope is an independent check of the ingest: BA p50 26.1, p90
43.6, p99 54.1, maximum 63.7, mean TPH 2,820, and mean volume 134.2, which match
the WS4 IDF audit to the published precision.

Baseline backtest
-----------------

`scripts/run_baseline_backtest.py` grows a BEC-stratified sample of intervals
from the first measurement to the second with no cut and no calibration. It
writes the per-interval comparison, the BEC summary, the grouped summaries, and
the envelope flags. The per-interval file carries site identifiers and stays in
the runtime directory; the grouped tables and the report are in
``notes/reference/calibration/``.

The 2026-11-02 run compared 89 intervals and skipped 19 BEC variants the variant
does not resolve. The initial stand was reproduced closely (mean BA bias -0.87
m2/ha, MAE 0.93); the end of the interval was not, with five predictions above
the observed maximum. The grouped summaries also carry annual **net** BA and TPH
change; the gross mortality table is not requested by this baseline. That is the
reference the calibration is judged against, not a calibration.

Full-domain design
------------------

`notes/reference/calibration/full-domain-design.md` groups the 47 data-rich
supported variants into 12 calibration domains, fixes the power thresholds and
the holdouts, and sets the W2–W6 sequence. `domain-plan.csv` carries the counts;
`w2-upstream-package.md` scopes the upstream work for `CWH`, `CDF`, `BWBS`,
`CMA`, `MH`, and the 19 subzones the variant does not resolve. `cciss-leads.md`
records the public CCISS code and data leads: seven high-priority missing
species (six coastal plus black spruce), the BEC/site-series tables for the
missing subzones, and the `w2-species-bec-crosswalk.csv` / `w2-bec-gap.csv`
working tables. `w2-source-audit.md` reads the pinned Fortran and records the
go/no-go: 18 subzones are a bounded extension, while the five zones need a
separate parameter-development project; site index is not used by the variant.
`w2-subzone-patch.md` carries the W2.3 patch for the 19 subzones and its
provisional PSP-p99 defaults; it is prepared and apply-checked, not yet built.

What it does not do
-------------------

- It does not fit a parameter. That is W4.
- It does not download the archive or resolve its licence. The archive is the
  caller's, and the manifest names the snapshot.
- It does not claim the PSP plots represent every BC stand. They are
  subjectively located and over-represent older and accessible stands; the
  calibration report must state that limit.
