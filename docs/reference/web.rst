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

The optional LLM assistant
--------------------------

The cockpit ships a local summary reader and an optional LLM agent. The reader answers from the
open run's summary and provenance. The agent runs one turn through the installed ``opencode`` CLI,
which owns its own model authentication; the service never reads or stores a provider key.

The agent is off by default because it runs with the service user's permissions and can read the
workspace. Enable it explicitly, and only behind an authenticating proxy:

.. code-block:: bash

   fresh-fvsbc web --runs runs/ --host 127.0.0.1 \
     --allow-agent --agent-workspace /path/to/fresh-fvsbc \
     --agent-model opencode-go/deepseek-v4.1-flash

The agent runs in OpenCode's **plan** agent, not the build agent: it may read the workspace but the
cockpit is a reader and the assistant must not edit a run, calibration bundle, or repository. The
service also strips common provider and cloud secrets from the child environment. This is a
risk-reduction measure, not a sandbox or an authentication boundary.

``GET /api/agent`` reports whether the agent is enabled, whether ``opencode`` is on the path, the
default model, the models reported by ``opencode models``, the workspace, and the timeout.
``GET /api/agent/guide.md`` returns the instruction sheet. ``POST /api/agent/chat`` accepts
``message``, optional ``session``, optional ``model``, compact UI ``context``, ``run``, and
``year``; the server injects the run's summary, provenance pins, and calibration review state. A
non-default model must appear in the CLI's reported list, so the browser cannot invent a provider
or model string.
A validated reply may carry safe UI chips for opening a workspace, panel, run, or stand year,
for opening a table filtered to a cited column/value, or for putting a follow-up prompt in the
input. The server checks a table citation against the open run before returning it.

The browser keeps the current assistant conversation and OpenCode session in ``sessionStorage``
for that tab; **New** clears both. **Copy** and **Export** write a Markdown transcript with the
run, context, mode, model, session, messages, citations, tool use, and follow-up chips. Each
assistant reply also records the model that produced it, so a transcript remains accurate after
the selector changes. **Stop waiting** aborts the browser request, but the local OpenCode process
may still finish in the background, and the panel says so rather than pretending the model was
cancelled.

**Saved chats** pins the current transcript and session under a name in ``localStorage``. The
drawer can load, rename, or delete a pinned chat; **New** clears the active conversation but leaves
pinned ones alone. At most ten are kept, they never reach the service, and **Load** restores the same
session id so the next turn can continue it when the local agent still knows that session.
**Export JSON** downloads every saved chat with ``version``, ``exported_at``, names, timestamps,
sessions, saved run/view/model context, and message metadata; rename refuses a name already used by
another saved chat. Selecting a saved chat shows that saved context and message count, and flags
when the current run or workspace differs from the saved one.

In the browser, **Enter sends** and **Shift+Enter inserts a newline**. The composer grows with the
message, the header selector switches between the models the local CLI reports, and each reply
shows its model. Tool use appears as read-only chips, and the local summary reader remains the
fallback when the agent is disabled or OpenCode is unavailable.

Shareable analysis state
------------------------

The cockpit keeps the useful view in the URL:

- ``workspace``, ``run``, ``panel``, and ``year`` for the open view;
- ``table``, ``q``, ``column``, ``limit``, and ``offset`` for a filtered table page;
- ``a``, ``b``, ``metric``, ``ctable``, and ``ccolumns`` for the two-run comparison and its
  selected diff columns.

Those values are restored on reload, so a reviewer can send a link to the exact table filter or
comparison instead of describing where to click. Named comparisons are also kept in the browser's
``localStorage`` for reuse; loading one replaces the current A/B/metric/table/diff-column state.

**Export JSON** writes those named comparisons to a versioned file with ``version``,
``exported_at``, and ``comparisons``. **Import JSON** accepts that file or a bare comparison array,
validates every row, merges by name, and keeps at most 20 entries. Each comparison includes its
``ccolumns`` diff selection. The service never stores the file; the browser owns this state.

The row-level diff has its own **Diff columns** disclosure. Selecting a subset changes which deltas
are shown and which rows rank highest; the summary metrics above it are unaffected. The selection
is encoded in ``ccolumns`` and saved with named comparisons.

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
``summary.csv``     the parsed FVS summary; the UI uses it only when no metric table exists
``provenance.json`` the PyFVS commit, the FVS source commit, the variant list
``variants.json``   the build's variant list
=================== =========================================================

The overview reads **``FVS_Summary_Metric``** rather than ``summary.csv``. The native summary uses
FVS's internal units, so a card that labelled its ``tpa`` as metric TPH would be wrong. When the
metric table is absent, the panel falls back to ``summary.csv`` and labels every value as native
(ft²/ac, trees/ac, ft); it does not silently mix units.

Table headers show the units this reader declares, and the Tables panel names ``FVSOut.db`` as the
source. Units come from the reader's column table, not from FVS, which does not attach units to
output columns; a blank unit means the reader does not declare one, not that the column is
dimensionless. The same declared units travel in the export's ``metadata.json`` sidecar. The column
filter repeats the declared unit in each option while keeping the URL value as the bare column
name.

A page with more than 120 rows renders only the visible window plus a small overscan, with spacer
rows preserving the full scroll height. Filtering and paging stay server-side, so virtualizing does
not change which rows the reader returns or exports.

On viewports wider than 900 pixels, a table with more than five columns pins its first useful key
column while the rest scrolls sideways. A column of repeated UUID ``CaseID`` values is skipped so
the pin lands on something readable such as ``StandID`` or ``Year``. Long pinned values ellipsize
with the full value in a tooltip; narrower screens leave every column unpinned.

At phone widths the table toolbar becomes a compact grid: full-width search, column selector with
Apply/Clear, then the CSV and package actions. The pager uses two columns for page size and jump
controls, with full-width Previous/Next buttons below the row summary.

A **Columns** disclosure hides, restores, and reorders columns for the current table. Hidden
columns also leave the filter menu, at least one column always remains, and CSV/package exports
still contain the full table. Order and visibility are saved per table in ``localStorage`` and
restored on reload; **Show all columns** only unhides, while **Reset layout** clears both the saved
order and the hidden set. An **Exports follow this layout** checkbox makes CSV and package exports
use the visible columns in their current order; it is saved with the layout. **Export layouts**
downloads every saved table layout as versioned JSON, and **Import layouts** validates and merges a
layout file by table; the current table reloads immediately after import.

A separate **Saved filters** disclosure stores the current literal query and column scope under a
name, per table, in ``localStorage``. Loading one restores both and unhides its column if the saved
layout had hidden it. Filters remain in the URL after loading; the named list itself is
browser-local and is not exported.

A run is ``complete`` once ``summary.csv`` exists and ``running`` until then. The service never writes into
a run directory, with one exception: starting a run creates a new one through the CLI.

The stand visuals
-----------------

The **visuals** panel draws the stand from two tables in ``FVSOut.db``:

- ``FVS_TreeList_Metric`` is the live stand, one row per tree per period.
- ``FVS_CutList_Metric`` marks the trees a treatment removed. It is optional: a run that cut nothing
  does not write it, and the view then shows no cut trees rather than inventing them.

The 2D map and the 3D viewer share **one payload** from ``GET /api/runs/{id}/visuals``. The map is a
canvas; the 3D view is three.js with orbit and zoom. Both are read-only. Neither is a map in the
geographic sense:

- **FVS writes no x/y coordinates.** The layout is schematic: each plot (``PtIndex``) gets a square
  cell, and its trees are spaced on a stable golden-angle spiral ordered by ``TreeIndex``. The same
  rows always produce the same picture.
- **The 3D ground is flat.** The per-tree tables carry no terrain, so the viewer draws a ground plane
  and a grid rather than a surface it cannot support.
- **Every displayed value comes from the run**: species, DBH, height, TPH, crown ratio, the year, and
  whether a tree is in the cut list. Only the arrangement is computed.

The three.js runtime is **vendored** under ``static/vendor/three/`` with its MIT licence, and loaded
only when a caller chooses the 3D view. The 2D map needs no WebGL, and the main shell stays light.

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
role can do. ``read_only`` removes every mutating action. The ``analyst`` and ``reviewer`` skins carry
the ``visuals`` panel; the reviewer sees the same stand read-only.

Endpoints
---------

``GET /api/skins``
    the shipped manifests
``GET /api/oracle``
    how many exposed tables have an independent check, against the dump and against a standalone
``GET /api/runs``
    run directories under the roots, with state
``GET /api/runs/{id}/summary``
    ``summary.csv`` rows, in FVS native units
``GET /api/runs/{id}/metric-summary``
    ``FVS_Summary_Metric`` rows, the metric source the overview renders
``GET /api/runs/{id}/tables``
    exposed tables written, with counts, declared units, and the flag
``GET /api/runs/{id}/tables/{name}``
    one table, paged, with its columns, source, and declared units; ``q`` filters before paging
    and ``column`` restricts it
``GET /api/runs/{id}/tables/{name}/csv``
    the filtered table as a CSV attachment; optional ``columns`` limits and orders its columns
``GET /api/runs/{id}/tables/{name}/export``
    a ZIP with the filtered ``data.csv``, ``metadata.json``, and a README; ``columns`` limits and
    orders both the data and the listed metadata columns
``GET /api/runs/{id}/visuals?year=``
    the schematic stand payload: layout, trees, cut trees, species and the year's summary row
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
- **No geographic map.** The 2D and 3D views are a schematic stand view over the per-tree tables. They
  carry no coordinates, no block polygon, no road, and no land base. The ws4 and fhops front ends have a
  map because their artefacts are spatial; FVS's per-tree tables are not.
- **No 3D editing.** The viewer orbits and zooms; it does not move a tree, paint terrain, or write a
  project. That is the Scenario Studio's job, over its own artefacts.
