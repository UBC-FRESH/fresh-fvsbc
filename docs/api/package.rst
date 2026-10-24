``fresh_fvsbc``
===============

The package. It re-exports the names the reference pages name, so a caller can write
``fresh_fvsbc.check_run`` or ``fresh_fvsbc.outputs.check_run`` and reach the same function. The
five modules are the units the contracts are written against, and each is listed below in the
order the pipeline uses them: build a tree list, build a keyword set, run, read the outputs, and
record the provenance.

.. automodule:: fresh_fvsbc

The package's re-exports are documented once, in the module that defines them, and the modules
below are listed in the order the pipeline uses them.

.. automodule:: fresh_fvsbc.treelist
   :members:
   :show-inheritance:

.. automodule:: fresh_fvsbc.keywords
   :members:
   :show-inheritance:

.. automodule:: fresh_fvsbc.nemora
   :members:
   :show-inheritance:

.. automodule:: fresh_fvsbc.outputs
   :members:
   :show-inheritance:

.. automodule:: fresh_fvsbc.provenance
   :members:
   :show-inheritance:

.. automodule:: fresh_fvsbc.run
   :members:
   :show-inheritance:
