The web surface
===============

`fresh-fvsbc web` serves a browser surface over the artefacts a run already wrote. It is **a reader**: it
holds no model state and computes no value the CLI cannot reproduce. The design, including what was
rejected and why, is `notes/design/fresh-fvsbc-web-frontend.md`.

It is an optional extra. The core install pulls pandas and nothing else.

.. code-block:: bash

   pip install 'fresh-fvsbc[web]'
   fresh-fvsbc web --runs path/to/runs

The bind is ``127.0.0.1`` by default, and a non-loopback address is refused unless ``--allow-remote`` is
passed, because there is no authentication. ``--root-path`` makes the app work under a notebook proxy
prefix such as ``/user/<name>/proxy/8765/``.

Deploying in a dev container
-----------------------------

The FRESH dev container is a **pre-authenticated** environment: JupyterHub authenticates the browser and
proxies a local port to a generated path, so a service on port 9999 is reached at
``https://fresh01.01101.dev/jupyterhub32/user/<name>/codeserver/proxy/9999/``. The service therefore has to
listen **off loopback**, and it has to answer **under the prefix**:

.. code-block:: bash

   fresh-fvsbc web --runs runs/ \
     --host 0.0.0.0 --allow-remote \
     --root-path /jupyterhub32/user/<name>/codeserver/proxy/9999 \
     --port 9999

``--allow-remote`` is required because the proxy connects from outside the loopback interface. **The proxy
is what authenticates**: the service has none of its own, and this is the deployment that supplies it. Do
not expose the port directly.

``--root-path`` is what makes the prefix work. The service answers both at ``/api/runs`` and under the
prefix, and the front end asks for relative URLs, so one build serves either way.

What it reads
-------------

A **run directory** is the unit. It holds the files the CLI already writes:

=================== =========================================================
File                What the surface uses it for
=================== =========================================================
``run.key``         the keyword set, shown read-only
``run.tre``         the tree list as written
``FVSOut.db``        the output database: the primary surface
``run.sum``         the fixed-width summary, as FVS wrote it
``summary.csv``     the parsed summary, for the trajectory chart
``provenance.json`` the PyFVS commit, the FVS source commit, the variant list
``variants.json``   the build's variant list
=================== =========================================================

A run is ``complete`` once ``summary.csv`` exists and ``running`` until then. The service never writes into
a run directory, with one exception: starting a run creates a new one through the CLI.

The oracle flag
---------------

**This is the reason the surface exists.** Two independent sources check the exposed tables, and the
broader one is not the obvious one:

- **Four** are checked against FVS's own database dump — the tables the official case ships.
- **Twenty-eight** are checked against a **standalone ``FVSbc``** built from the same source, and agree
  value for value. That covers every table either build writes, not only the four the dump carries.
  ``FVS_Regen_SitePrep`` is not among them: its site-preparation allocation differs, for a reason that is
  not this package's. ``FVS_Error`` is not either: FVS writes it only when it logs something, so the two
  builds cannot be made to agree on its presence.

``GET /api/oracle`` reports both counts and both table lists, every table record carries ``oracle`` — which
means *checked against a reference*, either one — and the front end marks an unverified table in the table
list and above its rows. **The badge leads with the standalone count**, because reporting the dump's four
alone would understate the surface by a factor of seven.

A number whose provenance is unchecked must not look like one whose provenance is checked. `Output contract`
says the same thing in prose; this surface says it on screen.

Skins
-----

A skin is a JSON manifest listing the panels and actions a role gets. Four ship: ``analyst``, ``carbon``,
``reviewer`` and ``tables``. The loader validates every panel and action against a registry and **refuses an
unknown name rather than dropping it**, because a manifest that silently loses a panel lies about what a
role can do. ``read_only`` removes every mutating action.

Endpoints
---------

``GET /api/skins``
    the shipped manifests
``GET /api/oracle``
    how many exposed tables have an independent check, against the dump and against a standalone
``GET /api/runs``
    run directories under the roots, with state
``GET /api/runs/{id}/summary``
    ``summary.csv`` rows
``GET /api/runs/{id}/tables``
    exposed tables written, with counts and the flag
``GET /api/runs/{id}/tables/{name}``
    one table, paged, with its columns
``GET /api/runs/{id}/keywords``
    ``run.key`` as text
``GET /api/runs/{id}/provenance``
    the pins and the variant list
``POST /api/runs``
    start a run by invoking the CLI
``GET /api/runs/{id}/log``
    the log the service captured, which is where a failed run's traceback is
``GET /api/runs/{id}/events``
    an SSE stream, or **204** when the run is done

A table the reader does not expose is refused with its name, and so is a table the run did not write. An
absent table is never rendered as an empty one.

Starting a run
--------------

``POST /api/runs`` takes ``population``, ``species``, ``tree_age``, an optional ``id``, and ``keywords``: an
**ordered** list in which an entry carrying ``|`` is a block (``NAME|LINE|LINE``) and anything else is a
keyword (``NAME=FIELD,...``).

Order is part of the contract. A ``DATABASE`` block must precede the stand setup, and ``FMIN``, ``MISTOE``,
``RDIN`` and ``ESTAB`` follow it — so the list is passed through in the order given rather than grouped.
Without a ``DATABASE`` block a run writes ``FVS_Cases`` and ``FVS_Error`` and nothing else, which is the
first surprise a caller meets.

A run whose child died is reported as ``failed``, and its traceback is at
``GET /api/runs/{id}/log``. A run the service did not start has no log and reports an empty body.

Not verified
------------

- **No authentication, and no plan for one in this surface.** That is why a remote bind is refused.
- **No live progress.** The event stream reports what the run directory holds — running, then complete — and
  does not invent a cycle count the child did not write.
- **No map.** A run here is a stand, not a land base. The ws4 and fhops front ends have one because their
  artefacts are spatial; these are not.
