`nemora` ingestion contract
===========================

How `fresh-fvsbc` accepts a synthetic stem population and turns it into an FVS-BC tree list.

ADR 0003 assigns this bridge to `fresh-fvsbc`, so that `nemora` takes no dependency on FVS or on any simulator.
The adapter is a public interface of `fresh-fvsbc`, and its tests use fixture records shaped like `nemora`
output, so the test suite never imports `nemora`.

The input shape
---------------

`nemora.synthesis` emits a list of stem records. `place_trees_with_dbh` produces the base record, and
`attach_tree_attributes` enriches it. Flattened by `tree_records_to_dataframe`, the fields are:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - What it is
   * - ``stand_id``
     - The stand the stem belongs to
   * - ``bootstrap_id``
     - The bootstrap draw it came from
   * - ``sampler_type``
     - The sampler that produced the diameter
   * - ``x``, ``y``
     - Placement inside the polygon
   * - ``dbh``
     - Diameter, as drawn by the sampler
   * - ``dbh_cm``
     - Diameter, in centimetres
   * - ``height_m``
     - Height, in metres
   * - ``crown_ratio``
     - Crown ratio, as a fraction in [0, 1]
   * - ``basal_area_m2``, ``biomass_tonnes``, ``bark_thickness_cm``
     - Derived attributes
   * - ``attributes_provenance``
     - How the attributes were derived

The mapping
-----------

.. list-table::
   :header-rows: 1
   :widths: 26 20 54

   * - Tree-list field
     - Source
     - Rule
   * - ``plot_id``
     - derived
     - Assigned by the adapter, one per ``stand_id``, in order of first appearance
   * - ``tree_num``
     - derived
     - Assigned sequentially within a plot, from 1
   * - ``tree_count``
     - derived
     - ``1.0``. A `nemora` record is one stem, and it carries no expansion factor
   * - ``tree_history``
     - derived
     - ``0``
   * - ``species``
     - **required**
     - The caller must supply it. See below
   * - ``diam``
     - ``dbh_cm``
     - Direct. Units are centimetres on both sides
   * - ``live_ht``
     - ``height_m``
     - **Metres on both sides**, confirmed by experiment. The adapter converts nothing
   * - ``crown_ratio``
     - ``crown_ratio``
     - Unlike the above, the two sides are **not** the same shape. `nemora` emits a fraction, and the
       tree-list field is a crown class 1 to 9, which FVS expands to a percent by ``class*10-5``. The
       adapter converts, and rejects a fraction that maps outside 1 to 9, because the field's single
       digit cannot carry it
   * - ``dg_incr``, ``htg_incr``
     - derived
     - ``0``. FVS computes growth, so an input value is history rather than a prediction
   * - ``trunc_ht``
     - derived
     - ``0``
   * - ``damage1``..``damage3``, ``severity1``..``severity3``
     - derived
     - ``0``. `nemora` has no damage or vigor field
   * - ``tree_val``, ``tree_rx``
     - derived
     - ``0``
   * - ``plot_slope``, ``plot_aspect``, ``plot_habitat``, ``plot_topo_pos``, ``plot_site_prep``
     - keyword set
     - Supplied by the run's keywords, not by the stem population
   * - ``tree_age``
     - **required**
     - The caller must supply it, or the run must accept the FVS default

What the adapter cannot supply
------------------------------

Three things are absent from `nemora`'s output and cannot be invented:

1. **``species``.** FVS-BC needs a species to select a growth model. `nemora` does not emit one today. The
   adapter requires it from the caller, and it fails when it is missing rather than defaulting to a
   species.
2. **``tree_age``.** Not emitted.
3. **The plot-level fields.** These belong to a run, not to a stem population, so they come from the
   keyword set.

The spatial fields, ``x`` and ``y``, have no home in the FVS tree list. FVS is distance-independent, so
placement is dropped. It may still decide plot assignment, which is the one way it survives.

Not verified, and what the run answered
---------------------------------------

- **Answered: the height units are metres on both sides.** A run that varied `live_ht` alone, with the
  tree, the site, and everything else fixed, moved the summary's `top_ht` by 3.2 at one height and 3.28
  at two others. That factor is the metre-to-foot conversion, so the field takes metres and the summary
  reports feet. `nemora` emits metres, and the adapter passes them through unchanged.
- **Answered: the tree-list field is a crown class, not a fraction, a tenth, or a percentage.** It is one
  digit wide, it holds 1 to 9, and FVS expands it to a percent crown ratio by ``n*10-5``, which its own
  comment in `base/intree.f` states. So class 7 is 65 percent. `nemora` emits a fraction, so the adapter
  converts, and refuses a fraction whose class falls outside 1 to 9.
- Whether a caller will ever have ``species``, or whether the project needs a species-assignment step.
  `nemora` not emitting it is a fact about its current surface, and the note
  `notes/reference/bc-treelist-and-species.md` records it.

The first two were open when this page was written and are now settled, by the run recorded in
`notes/reference/synthetic-run.md` rather than by another reading.
