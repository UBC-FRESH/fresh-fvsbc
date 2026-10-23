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
     - Units are **not** yet verified. See below
   * - ``crown_ratio``
     - ``crown_ratio``
     - The tree-list field is one digit wide, so the adapter must know whether the source is a fraction or
       a percentage, and must reject a value it cannot represent
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

Not verified
------------

- **Units for height.** `nemora` emits metres. Whether FVS-BC's ``live_ht`` expects metres or feet was not
  established. The BC build includes `METRIC.F77` and `canada/bc/blkdat.f` includes it, which suggests
  metric, but that is an inference and not a read.
- **The crown-ratio scale.** Whether the tree-list field is a fraction, tenths, or a percentage. The
  source side is settled by reading `nemora`: it clamps `crown_ratio` to [0, 1] and defaults it to
  0.45, so the value that arrives at the adapter is a fraction rather than a percentage.
- Whether a caller will ever have ``species``, or whether the project needs a species-assignment step.
  `nemora` not emitting it is a fact about its current surface, and the note
  `notes/reference/bc-treelist-and-species.md` records it.

The first two are settled by the same successful run that answers the format hazard in
:doc:`tree-list`.
