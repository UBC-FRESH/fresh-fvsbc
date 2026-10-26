# The fresh-fvsbc web front end: design

Status: design for `P37`. **No UI code lands before this note is on `main`.** This is the same rule the
ws4 and fhops front ends were built under, and this note follows their architecture deliberately.

## Prior art: what FVS Online actually is

The 2022 FVS-BC training bundle (`2022 FVS-BC Workshop-2`) points every participant at **FVS Online**, and
the workshop's own user manual describes it precisely:

> FVSOnline is an interface to the Forest Vegetation Simulator using the **Shiny web application framework**
> … implemented using the **R programming language** for the server code and **html plus JavaScript** for the
> client code. FVSOnline also relies on **rFVS** to interact with FVS.

| | |
| --- | --- |
| Product name | FVS Online, shipped as the R package **`fvsOL`** |
| Server | R + Shiny |
| Client | HTML + JavaScript |
| Bridge to FVS | `rFVS` (R bindings to the FVS shared libraries) |
| Data | SQLite, with mdbtools for Access import |
| Hosted instance used by the workshop | `charcoal2.cnre.vt.edu/FVSOnline/` (Virginia Tech) |
| Local install | `svn checkout svn://svn.code.sf.net/p/open-fvs/code/Rcode/fvsOLtrunk/fvsOL` |
| Source today | migrated to **`github.com/USDAForestService/ForestVegetationSimulator-Interface`** |

**So the source is available**, and it is an R/Shiny application. This project does **not** port it: the
backend here is Python, the run engine is the pinned BC variant behind PyFVS, and the front end is a
vanilla ES module shell. What we take from `fvsOL` is the *shape of the job* — pick a project, load a tree
list and keyword set, run, read outputs, compare — not its code.

## Goal and non-goals

A browser surface over **the artefacts a run already wrote**: the keyword set, the tree list, the output
database, the summary, and the provenance. Skins are manifests over one application.

Non-goals for the first cut: a second variant, UI-only state, multi-user authentication, a database of its
own, a map, and 3D. **The CLI remains the only way to produce a result**; the service starts a run by
invoking it, exactly as the existing `run_case` drives FVS in a child process (ADR 0010).

## The artefact contract

The service reads files and computes nothing the CLI cannot reproduce. These are the files a run directory
already holds, verified against the current implementation:

| artefact | what the UI uses it for |
| --- | --- |
| `run.key` | the keyword set as written — the run's identity and its configuration |
| `run.tre` | the tree list as written, parsed by the one writer in `treelist.py` |
| `FVSOut.db` | **the primary surface**: 31 exposed tables out of 44 the schema can create |
| `run.sum` | the fixed-width summary, as FVS wrote it |
| `summary.csv` | the parsed summary, for the trajectory chart |
| `variants.json` | provenance: the PyFVS commit, the FVS source submodule commit, the variant list |

**A run directory is the unit.** The service is given one or more roots and lists the run directories under
them. It never writes into a run directory, with one exception: starting a run creates a new one through
the CLI.

## The service surface

An optional extra, `fresh-fvsbc[web]` (FastAPI + uvicorn + pandas, which the core already has). The core
install is unchanged, and the command line imports the application lazily so the core never needs FastAPI.

| method | path | purpose |
| --- | --- | --- |
| GET | `/api/runs` | run directories under the configured roots, with summary and status |
| GET | `/api/runs/{id}/summary` | `summary.csv` rows, plus the run's identity |
| GET | `/api/runs/{id}/tables` | the exposed tables present in this run's database |
| GET | `/api/runs/{id}/tables/{name}?limit=&offset=` | one table's rows, with its column list |
| GET | `/api/runs/{id}/keywords` | `run.key`, as text and as parsed keywords |
| GET | `/api/runs/{id}/provenance` | `variants.json`, and the package version |
| GET | `/api/skins` | the shipped skin manifests |
| POST | `/api/runs` | start a run from a population + keyword set; returns its id |
| GET | `/api/runs/{id}/events` | the SSE stream |

Every table endpoint returns the **column list from the schema** alongside the rows, because the UI must
show what a table carries even when a run wrote none of it.

**The oracle flag is part of the table contract.** Four of the 31 exposed tables are checked against FVS's
own database dump; the rest are not. The API reports `oracle: true|false` per table, and the UI shows it.
A number whose provenance is unverified must not look like one whose provenance is checked — that is the
single most useful thing this UI can do for a modeller.

## The skin manifest

A skin is a JSON document, not a route or a fork, following ws4 and fhops exactly:

```json
{
  "id": "analyst",
  "title": "Analyst",
  "panels": ["tables", "summary", "trees", "keywords", "provenance", "compare"],
  "actions": ["start_run", "export"],
  "read_only": false
}
```

The loader checks every panel and action against a registry; **an unknown name is refused with the name**,
not ignored. `read_only` removes every mutating action.

Four skins ship, chosen for who actually opens this thing:

| skin | panels | who it is for |
| --- | --- | --- |
| `analyst` | all | the default: run, browse, compare |
| `reviewer` | tables, summary, provenance | read-only; checking someone else's result |
| `carbon` | summary, tables, provenance | the carbon accounting workflow |
| `tables` | tables | raw table browser for a caller debugging a reader |

## Panels

- **Tables.** A list of the exposed tables the run wrote, with row counts; selecting one shows the rows
  with the schema's column names, the oracle flag, and an export. This is the panel that makes 31 tables
  usable instead of a list in a document.
- **Summary.** The stand trajectory from `summary.csv` — basal area, volume, trees per hectare by year —
  drawn as a plain SVG chart, no chart library.
- **Trees.** `FVS_TreeList_Metric` and `FVS_CutList_Metric` side by side, joined on `TreeId`, so a caller
  can see what a treatment took. The `CCum`/`CCuM` difference between the two tables is labelled in the UI
  rather than left as a trap.
- **Keywords.** `run.key` rendered read-only with the keyword names highlighted, and the run's identity.
- **Provenance.** The three pins, the variant list, and the package version — the thing that makes a result
  reproducible.
- **Compare.** Two runs, A and B: the same table's rows joined on the identity columns, sorted by absolute
  difference, capped at 200 rows. Client-side only.

## Running a case

`POST /api/runs` takes a population file path and a keyword set, and invokes the CLI in a subprocess with
`--directory` pointing at a new run directory under the configured root. It returns immediately with the
run id; progress arrives on the SSE stream.

**The service never imports the Fortran extension into the request process.** A crash in a projection
cannot take the UI down, and the existing child-process design (ADR 0010) already gives us this for free.

SSE events, throttled to 2 Hz:

```
event: status
data: {"run": "2026-10-26T01-30-00", "state": "running", "detail": "cycle 2 of 4"}

event: done
data: {"run": "2026-10-26T01-30-00", "state": "ok", "tables": 31}
```

A finished run's `/events` returns **204**, not a short stream EventSource reconnects to — the same
decision ws4 records, for the same reason.

## Stack decisions

1. **FastAPI + uvicorn as an extra**, with a **vanilla ES module shell**. No Node build, no JavaScript
   toolchain, no framework. `index.html`, `app.js`, `style.css`, and nothing to compile.
2. **The service is a reader.** A run is started by invoking the CLI; the service holds no model state.
3. **Skins are manifests** checked against a registry; unknown entries fail loudly.
4. **Local-only by default.** The default bind is `127.0.0.1`, and a non-loopback bind is refused unless
   `--allow-remote` is passed. There is no authentication in the first cut, and that refusal is the
   security decision until there is one.
5. **The SPA is prefix-relative.** `--root-path` supports a notebook proxy subpath
   (`/user/<name>/proxy/<port>/`), and the browser uses relative API and asset URLs so one build works at
   both `/` and under a prefix.
6. **No map.** The runs here are a stand, not a land base; a map would be decoration. It is the one place
   this design diverges from ws4 and fhops, and it diverges because the artefacts differ, not the taste.

## Testing

- API contract tests with `fastapi.testclient` over a fixture run directory: every endpoint returns what
  the file holds, and a missing table is a 404 naming it.
- Skin loader: an unknown panel or action is refused by name; `read_only` cannot start a run.
- The oracle flag: a checked table reports `true` and an unchecked one `false`, asserted against
  `EXPOSED_TABLES` and the oracle set in `tests/test_oracle.py`.
- The table endpoint's column list matches `read_table` for every exposed table the fixture holds.
- UI: a smoke test that the SPA's static files are served and the panel registry covers every skin's
  panels. Browser automation stays optional and must not gate the core install.
- The core install is unchanged: `pip install fresh-fvsbc` still pulls pandas and nothing else.

## What this note does not decide

- Whether the keyword panel becomes editable and re-runnable. That is a modelling-interface question, not
  a reader question, and it needs its own note.
- Authentication, if this is ever hosted beyond a notebook proxy.
- Any visual design beyond "the same shell as ws4 and fhops", which the first cut copies deliberately so
  the three tools feel like one family.
