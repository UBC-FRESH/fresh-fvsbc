Calibration bundle
==================

A versioned JSON document that names the build, the domain, the parameters, the
evidence, and the reviewer for a calibration. It is **data, not code**: the
package loads it, checks it, renders it into FVS keywords, and records its id in
provenance. It does not fit the parameters.

The contract lives in :class:`fresh_fvsbc.bundle.CalibrationBundle`. A
contract pilot is at ``notes/reference/calibration/pilot-bundle.json``; it is
deliberately unsigned and is not a calibration. The worked regional example is
``notes/reference/calibration/kc-pilot-bundle.json``; its protocol and claim
boundary are in ``notes/reference/calibration/kc-protocol.md``, and its results
are in ``notes/reference/calibration/kc-replication.md``.

Fields
------

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Field
     - What it carries
   * - ``bundle_id``
     - A stable lower-case identifier, such as ``bc-pilot-2026-11-02``
   * - ``version``
     - A semantic version, such as ``0.1.0``
   * - ``pins``
     - ``pyfvs_commit``, ``fvs_source_commit``, and ``variant``, plus optional ``wrapper_version``. The loader refuses a bundle whose pins do not match the package.
   * - ``domain``
     - ``regions``, ``tsas``, ``becs``, ``species_groups``, ``dbh_classes``, ``management``, and optional ``qmd_min`` and ``ba_min``. An empty list means no restriction; ``dbh_classes`` is a list of inclusive ``[min, max]`` ranges in centimetres; ``qmd_min`` is in centimetres and ``ba_min`` in square metres per hectare.
   * - ``parameters``
     - The keyword records: ``keyword``, ``fields``, ``units``, ``value_index``, and optional ``bounds``.
   * - ``training``
     - ``data_checksum`` (``sha256:`` and 64 hex), ``split``, ``objective``, and ``convergence``.
   * - ``review``
     - ``reviewer``, ``date`` (``YYYY-MM-DD``), and ``signed_off``.
   * - ``claim``
     - The claim boundary in one sentence.

A parameter
-----------

.. code-block:: json

   {
     "keyword": "MORTMULT",
     "fields": ["1", "FD", "1.8000", "0", "999"],
     "units": "multiplier",
     "value_index": 2,
     "bounds": {"min": 0.25, "max": 4.0}
   }

``value_index`` is zero-based. The bounded field must be numeric, and it must sit
strictly inside the bounds; a value equal to either bound loads with a warning,
because a parameter at a bound is not identified.

The accepted keywords are ``BAMAX``, ``SDIMAX``, ``SDICALC``, ``BAIMULT``,
``MORTMULT``, ``HTGMULT``, ``DGSTDEV``, ``CRNMULT``, ``FIXMORT``, and
``MORTMSB``. A bundle cannot invent a keyword.

Using a bundle
--------------

.. code-block:: python

   from fresh_fvsbc import load_bundle, run_case

   bundle = load_bundle("notes/reference/calibration/pilot-bundle.json")
   keywords = (*bundle.render(), *keywords)
   result = run_case(records, keywords, directory=run_dir, calibration=bundle)
   assert result.provenance.calibration_id == bundle.bundle_id

The run checks the bundle's domain against the run's BEC, species groups, DBHs,
and management, and it refuses a set that does not carry the rendered keywords. A
bundle whose data checksum is missing or whose pins differ from the package is
refused before the run starts.

What it does not do
-------------------

- It does not fit a parameter; W4 does.
- It does not certify a bundle; ``signed_off`` is a review record, not a proof.
- It does not claim a bundle is valid outside its domain. The domain check is
  the boundary.
