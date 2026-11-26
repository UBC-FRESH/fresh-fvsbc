Installing
==========

The BC variant is Fortran. There are two ways to get it, and the first is the one to try.

From PyPI
---------

.. code-block:: console

   $ pip install "fresh-fvsbc[fvs]"


That is the whole install. The `fvs` extra pulls **`fresh-fvsbc-pyfvs`**, which is the BC variant
itself: a self-contained wheel with `libgfortran` bundled inside it by `auditwheel repair`. **Nothing
else has to be installed** — no gfortran, no meson, no patch sets — and the extension loads the bundled
library through its patched `RPATH`.

The wheels are **Linux x86_64, glibc 2.28 or later**: RHEL 8+, Ubuntu 20.04+, Debian 10+, and every
current cluster. `ldd --version` on the machine answers whether it will run there. One wheel is
published per Python from 3.10 to 3.13.

.. note::

   **Do not install upstream ``pyfvs`` in the same environment.** The fork installs the same
   ``pyfvs`` import package under a different distribution name, ``fresh-fvsbc-pyfvs``, so that the
   two cannot be confused; pip will not stop you from installing both, and whichever wins the import
   is the one you get.

From source
-----------

If there is no wheel for your platform, the build recipe is ADR 0004, ADR 0006, and ADR 0013: clone the pinned
fork, apply eleven patch sets, and build. It needs `gfortran`, `meson`, `ninja` and `patchelf`, and it
takes a few minutes:

.. code-block:: console

   $ git clone https://github.com/UBC-FRESH/PyFVS.git
   $ git -C PyFVS checkout e95172b
   $ git -C PyFVS submodule update --init --recursive
   $ gunzip -c notes/reference/pyfvs-patchset.diff.gz  | git -C PyFVS apply -
   $ gunzip -c notes/reference/fvsbc-patchset.diff.gz   | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w2-subzones.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w3-habtyp-boundary.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w2-five-zone.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w4-sbps-small-tree.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w5-bwbs-v3.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w6-sbs-large-tree.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w7-sbps-large-tree.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w8-cwh-v3.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w9-mh-cdf-v3.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w10-mh-cdf-own-dg.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w11-cwh-height.patch.gz | git -C PyFVS/fvs apply -
   $ gunzip -c notes/reference/calibration/w12-sbs-bamax.patch.gz | git -C PyFVS/fvs apply -
   $ SETUPTOOLS_SCM_PRETEND_VERSION=0.4.5 pip install --no-build-isolation ./PyFVS \
       --config-settings=setup-args="-Dfvsvariants=bc"
   $ pip install fresh-fvsbc

The third patch adds the 19 W2.3 subzones and their provisional defaults. Without it the variant still
builds, but those codes fall back to ``ICHmw2/01``; ``run_case`` refuses that fallback rather than
returning a plausible run. The fourth fixes the ``KAM`` + ``MS`` boundary collision that made
``MSxk1`` resolve as ``MSmm``. The final seven patches add the five-zone prototype, fix the SBPS small-tree height branch, add the BWBS V3 growth and mortality tables, restore SBS large-tree growth, put CWH, MH, and CDF on the V3 path with fitted large-tree diameter growth, fit CWH height growth for six species, and give SBS a per-subzone maximum basal area. The
patched wheel is versioned ``0.4.5`` and is the ``fvs`` extra for ``fresh-fvsbc 0.28.0``. The wrapper
now accepts the five prototype zones; the binary carries their provisional parser and defaults. That
is deployment plumbing, not calibration: IDFdk and SBS have passed holdouts; CWH has an
unsigned growth pilot and BWBS carries the unsigned V3 calibration in ``w5-bwbs-v3``; none is certified. CDF and MH carry V3 candidates; CMA is out of scope by decision.


What you get
------------

.. code-block:: console

   $ python -c "import pyfvs; print(pyfvs.list_variants())"
   {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
   $ fresh-fvsbc population.json --directory run --species FD --tree-age 21 ...


If `list_variants()` reports anything but `OK` for `BC`, the build did not produce the variant and no
run will work. That is the first thing to check, and `notes/reference/fvsbc-smoke-run.md` is a worked
example.
