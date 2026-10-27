# Deploying this into a real modelling workflow

What to expect on first real use, what has been verified, and what has not. Written to be read *before*
the first production case, and to be contradicted by it — a real workflow is the test this project has
been missing.

## The install that actually works

This package needs **PyFVS built with the BC variant**; it does not build FVS itself (ADR 0004). The recipe
below was run end to end five times at release tags, and it is the one to copy:

```bash
python3 -m venv .venv
. .venv/bin/activate
export PATH="$PWD/.venv/bin:$PATH"          # meson, ninja and patchelf must be on PATH
python -m pip install --upgrade pip meson-python meson ninja numpy setuptools_scm patchelf

# the pinned PyFVS source, checked out at the commit this release records
SETUPTOOLS_SCM_PRETEND_VERSION=0.3.11 \
  python -m pip install --no-build-isolation ./pyfvs \
    --config-settings=setup-args="-Dfvsvariants=bc"

python -m pip install --no-deps ./fresh-fvsbc
python -c "import pyfvs; print(pyfvs.list_variants())"   # {'BC': {'lib': 'pyfvs.fvsbc', 'status': 'OK'}}
```

**Two steps cost an hour each the first time**, and neither is obvious from the error:

- **`meson`, `ninja` and `patchelf` must be on `PATH`.** Installing `meson-python` is not enough; the
  build looks for the executables and fails at metadata generation with `meson executable "meson" not
  found`.
- **A detached checkout makes `setuptools_scm` produce an invalid version** (`0.3.11.dev0.post0`, which
  `packaging` rejects). Pin it with `SETUPTOOLS_SCM_PRETEND_VERSION`.

The build needs `gfortran` and takes several minutes. `-O0` makes the variant write **no database at all**;
the optimiser is a build requirement, not a preference.

## The provenance to record with every run

`provenance.py` records the PyFVS commit, the FVS source submodule commit, and the variant list. A result
that does not carry those cannot be reproduced, and this is scientific software. Check the values against
the release notes at the tag you installed.

## What real use will exercise that the tests do not

The suite runs one synthetic stand, and the oracle runs one official case. A real project will do things
neither does, and these are the places a break is most likely:

| What to watch | Why it is untested |
| --- | --- |
| **A large tree list** (thousands of stems) | every test uses 3 to 200 trees |
| **A keyword set from an existing project** | the suite builds its own; a real one may use keywords this model refuses by name |
| **Several cycles with management** | most tests run two cycles; a rotation is 10 to 30 |
| **More than one stand per run** | the adapter maps one plot per stand, and only a few tests use more than two |
| **A variant other than `BC`** | refused by design — this package wraps BC only |
| **Units** | the tables are metric, and the tree list is written with the BC fixed-width record; a caller mixing imperial assumptions will get plausible wrong numbers |

**The largest known blind spot is that 27 of the 31 exposed tables have no independent oracle.** Only four
are checked against FVS's own database dump. For the rest, the reader proves the table exists and its
columns match the schema; it does not prove the numbers are right. `notes/reference/table-reachability.md`
says which is which.

## The browser surface

There is an optional one: ``pip install 'fresh-fvsbc[web]'`` then ``fresh-fvsbc web --runs DIR``. It reads
the artefacts a run already wrote and starts a run by invoking the CLI, never by importing the extension.
`docs/reference/web.rst` is the contract.

**In the dev container, run it like this**, because the container is pre-authenticated and JupyterHub
publishes the port under a path::

    fresh-fvsbc web --runs runs/ \
      --host 0.0.0.0 --allow-remote \
      --root-path /jupyterhub32/user/<name>/codeserver/proxy/9999 \
      --port 9999

Then open the proxy URL. ``--allow-remote`` is not a risk taken lightly: it is required because the proxy
connects from outside the loopback, and **the proxy is what authenticates**. The service has no
authentication of its own, so never bind it to a public interface without a proxy in front of it.

## How to report what you find

1. **Check `notes/triage.md` first.** Nine gaps are recorded there with dispositions and reopen conditions;
   several are known and accepted, and one of them will look like a bug the first time you meet it.
2. **A finding that changes a disposition reopens it** — that is the process, not an exception. Write the
   case that produced it.
3. **A finding that is new** becomes a row in `notes/triage.md` with a disposition and what would reopen
   it, then a phase in `ROADMAP.md`.
4. **If a number looks wrong, say what it should have been and where that expectation comes from.** This
   project has spent four phases correcting claims made without that.

## What is deliberately not here

- **No PyPI release.** The package is installed from a checkout, and the variant must be built separately.
  That is a real deployment cost and it is recorded as a gap, not hidden.
- **No calibration workflow.** `FVS_CalibStats` exists in the schema, is created on every run, and carries
  nothing. It is not exposed.
- **No climate extension.** It needs an external attribute file this project does not ship.
