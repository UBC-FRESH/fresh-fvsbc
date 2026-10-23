Reference contracts
===================

Reference pages are contracts. They say what `fresh-fvsbc` requires, precisely enough for a test or a
validator to apply. Procedures live in the guides and in `AGENTS.md`.

Each contract names the revision of the pinned fork it was read from, and it separates what is verified
from what is not. The reading method, and the provenance for every claim, are in the repository note
`notes/reference/bc-treelist-and-species.md`.

Names
-----

Three names are easy to confuse, so this project uses them distinctly.

* ``fresh-fvsbc`` is this project. Prose writes it with hyphens, and Python identifiers write it
  ``fresh_fvsbc``.
* **FVS-BC** is the FVS variant that this project wraps. It stays ``bc`` wherever FVS or PyFVS names
  it, as in the build flag ``-Dfvsvariants=bc``.
* ``pyfvs.fvsbc`` and ``FVSbc`` name FVS's own artifacts: PyFVS's BC extension module, and the
  variant as the FVS source tree spells it. Write them in full when those are what you mean.

`ADR 0005` decides this.

.. toctree::
   :maxdepth: 1

   tree-list
   keywords
   outputs
   provenance
   nemora-ingest
