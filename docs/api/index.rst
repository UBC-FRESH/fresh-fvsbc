API reference
=============

The API reference is generated from the docstrings and annotations in ``src/fresh_fvsbc/`` and
``scripts/``. Every public function is listed with its signature, its parameter types, and its
return value. Search this reference before you call one of these functions. Add a page here, with
an ``automodule`` entry, whenever you add a module to the project.

The package is the library a caller imports. The scripts are the project's own tooling: they run
the gates and validate the planning surfaces, and they are not part of the installed package.

.. toctree::
   :maxdepth: 2

   package
   check-workflow
   dashboard
