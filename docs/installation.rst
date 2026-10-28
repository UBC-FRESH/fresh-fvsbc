Installing
==========

The BC variant is Fortran. There are two ways to get it, and the first is the one to try.

From a wheel
------------

Each release carries a self-contained wheel for the pinned fork:

.. code-block:: console

   $ pip install https://github.com/UBC-FRESH/fresh-fvsbc/releases/download/v0.20.0/fresh_fvsbc_pyfvs-0.3.11-cp312-cp312-manylinux_2_28_x86_64.whl
   $ pip install "git+https://github.com/UBC-FRESH/fresh-fvsbc@v0.20.0"


Nothing else is needed: `auditwheel` bundles `libgfortran` into the wheel, so **gfortran does not
have to be installed**, and the extension loads the bundled copy through its patched `RPATH`.

.. note::

   ``fresh-fvsbc`` itself is **not on PyPI yet**, so the second line installs it from the tag rather
   than by name. When it is published, ``pip install fresh-fvsbc`` replaces it and nothing else about
   this page changes.

Pick the wheel that matches your Python — one is attached per version from 3.10 to 3.13 — and
replace `v0.20.0` and the tag in the file name with the release you want. Check the release page for
the exact list:

.. code-block:: console

   $ gh release view v0.20.0 --repo UBC-FRESH/fresh-fvsbc --json assets --jq '.assets[].name'


**The wheel is Linux x86_64 and glibc 2.28 or later**, which covers RHEL 8+, Ubuntu 20.04+, Debian 10+
and every current cluster. `ldd --version` on the machine answers whether it will run there.

.. note::

   **Do not install upstream ``pyfvs`` in the same environment.** The fork installs the same
   ``pyfvs`` import package under a different distribution name, ``fresh-fvsbc-pyfvs``, so that the
   two cannot be confused; pip will not stop you from installing both, and whichever wins the import
   is the one you get. A wheel for the fork is a wheel for this package.

From source
-----------

If there is no wheel for your platform, the build recipe is ADR 0004 and ADR 0006: clone the pinned
fork, apply two patch sets, and build. It needs `gfortran`, `meson`, `ninja` and `patchelf`, and it
takes a few minutes:

.. code-block:: console

   $ git clone https://github.com/UBC-FRESH/PyFVS.git
   $ git -C PyFVS checkout e95172b
   $ git -C PyFVS submodule update --init --recursive
   $ gunzip -c notes/reference/pyfvs-patchset.diff.gz  | git -C PyFVS apply -
   $ gunzip -c notes/reference/fvsbc-patchset.diff.gz   | git -C PyFVS/fvs apply -
   $ SETUPTOOLS_SCM_PRETEND_VERSION=0.3.11 pip install --no-build-isolation ./PyFVS \
       --config-settings=setup-args="-Dfvsvariants=bc"
   $ pip install fresh-fvsbc


What you get
------------

.. code-block:: console

   $ python -c "import pyfvs; print(pyfvs.list_variants())"
   {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
   $ fresh-fvsbc population.json --directory run --species FD --tree-age 21 ...


If `list_variants()` reports anything but `OK` for `BC`, the build did not produce the variant and no
run will work. That is the first thing to check, and `notes/reference/fvsbc-smoke-run.md` is a worked
example.
