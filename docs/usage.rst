Running a case
==============

The command is the orchestration with a shell in front of it: it reads a population and a keyword
set, runs one case, and reports where the outputs are. It adds no modelling and no keyword the caller
did not write.

.. code-block:: bash

   python -m fresh_fvsbc population.json \
     --directory run \
     --species FD --tree-age 60 \
     --keyword "STDIDENT=SYNTHETIC   the command" \
     --keyword STDINFO=712,CHS131,0,200,35,16 \
     --keyword MANAGED=0,1 \
     --keyword SITECODE=FD,100 \
     --keyword INVYEAR=0 \
     --keyword DESIGN=0,1,999,1,0,1,1 \
     --keyword NUMCYCLE=4 \
     --keyword RANNSEED=1 \
     --keyword ECHOSUM \
     --keyword PROCESS \
     --keyword STOP

An installed package gets the same command as ``fresh-fvsbc``. The recorded invocation, with its exit
status and its outputs, is in ``notes/reference/synthetic-run.md``.

The population file
-------------------

A JSON list of stem records, shaped like `nemora`'s output. The adapter reads ``stand_id``,
``dbh_cm``, ``height_m`` and ``crown_ratio``, and ignores the rest.

.. code-block:: json

   [
     {"stand_id": "S1", "dbh_cm": 20.0, "height_m": 18.0, "crown_ratio": 0.5},
     {"stand_id": "S1", "dbh_cm": 26.0, "height_m": 22.0, "crown_ratio": 0.6}
   ]

``--species`` and ``--tree-age`` are required because `nemora` supplies neither, and the adapter fails
rather than defaulting. See :doc:`reference/nemora-ingest`.

The keyword set
---------------

``--keyword NAME=FIELD,...``, repeated in the order FVS will read them. The fields are FVS's own
parameter fields, so a blank field is written as a gap:

.. code-block:: bash

   --keyword TIMEINT=,5

The names are validated against FVS's table, so a typo is refused rather than passed to Fortran. Two
limits are worth knowing:

- A parameter cannot contain a comma, because the comma separates the fields. The API has no such
  limit.
- ``TREEFMT`` and ``TREEDATA`` are refused, because the run writes them. So are the block keywords
  (``COMMENT``, ``COMPUTE``, ``IF``, ``DATABASE``), because the keyword model has no room for a block
  yet. See :doc:`reference/keywords`.

Exit codes
----------

``0``
   The run completed and wrote its outputs.
``1``
   The run was attempted and failed: an error row, no database, a bad projection, or no extension.
   This is worth reporting.
``2``
   The input was wrong before any run: a missing or malformed population file, an unknown keyword, a
   parameter wider than its field, a species that does not resolve. This is worth fixing.

``argparse`` already exits 2 for a usage error, so the third code is the convention rather than an
invention.

What the run writes
-------------------

The directory named by ``--directory``, created if absent, holds:

- ``run.key``, the keyword file, with ``TREEFMT`` and ``TREEDATA`` inserted before ``PROCESS``;
- ``run.tre``, the tree list, ending with the ``-999`` line FVS reads to;
- ``FVSOut.db``, the database, under the fixed name ``dbsblkd.f`` declares;
- ``run.out`` and ``run.sum``, FVS's own report and summary;
- ``provenance.json``, the record described in :doc:`reference/provenance`.

A run owns its directory. The database's name is fixed, so two runs in one directory overwrite each
other's database. The command changes into the directory for the projection and restores the caller's
afterwards, which makes a run process-global rather than thread-safe.
