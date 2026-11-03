# Publishing to PyPI

Two distributions are published, and neither uses an API token.

| Distribution | Workflow | What it is |
| --- | --- | --- |
| `fresh-fvsbc` | `release.yaml`, environments `pypi` and `testpypi` | this package, pure Python, sdist and wheel |
| `fresh-fvsbc-pyfvs` | `wheels.yml`, environments `pypi` and `testpypi` | the built BC variant, four wheels, one per Python |

Both use **trusted publishing**: GitHub mints a short-lived OIDC token, and PyPI accepts it for the
repository, workflow, and environment named in the project's publisher. Nothing is stored in this
repository and nothing has to be rotated.

**The binary is versioned separately.** `fresh-fvsbc-pyfvs 0.3.12` is tied to the PyFVS/FVS pin and
the three patch sets; it does not change with every `fresh-fvsbc` release. Its publish jobs are
manual, so a wrapper tag cannot republish the binary by accident.

## The one-time setup, which needs the PyPI account

An agent cannot do this part: it creates an external account. Each step below is done once, in the
PyPI web interface, signed in as the owner of the project names.

1. **Create the accounts.** A PyPI account at <https://pypi.org/account/register/>, and — strongly
   recommended — the same at <https://test.pypi.org/account/register/> so the first publish can be
   rehearsed against a throwaway index.

2. **Reserve both names.** Under *Your projects → Publishing*, upload any placeholder for
   `fresh-fvsbc-pyfvs` and for `fresh-fvsbc`, or use *Pending publishers* before the first upload.
   The names must be yours before a trusted publisher can be attached to them.

3. **Add a trusted publisher for each project and index.** *Project → Settings → Publishing → Add a
   new pending publisher → GitHub*, with these exact values:

   | Project | Index | Repository | Workflow | Environment |
   | --- | --- | --- | --- | --- |
   | `fresh-fvsbc` | PyPI | `UBC-FRESH/fresh-fvsbc` | `release.yaml` | `pypi` |
   | `fresh-fvsbc` | TestPyPI | `UBC-FRESH/fresh-fvsbc` | `release.yaml` | `testpypi` |
   | `fresh-fvsbc-pyfvs` | PyPI | `UBC-FRESH/fresh-fvsbc` | `wheels.yml` | `pypi` |
   | `fresh-fvsbc-pyfvs` | TestPyPI | `UBC-FRESH/fresh-fvsbc` | `wheels.yml` | `testpypi` |

   The workflow name and the environment are matched exactly. A publisher that names
   `fresh-fvsbc-pyfvs` as the **repository** does not match this build: the wheels are built in
   `UBC-FRESH/fresh-fvsbc` by `wheels.yml`.

4. **Create both environments** in the repository's *Settings → Environments*: `pypi` and
   `testpypi`, with no secrets. They exist so the trusted publisher has something to match, and so
   an approval rule can be added later without touching the workflows.

## Publishing the binary

The wheels are built by `wheels.yml`, then the selected publish job uploads them:

```bash
# TestPyPI first; the version can be uploaded to both indexes.
gh workflow run wheels.yml -f publish=testpypi

# Production, after the TestPyPI install has been checked.
gh workflow run wheels.yml -f publish=pypi
```

`publish=testpypi` uses `https://test.pypi.org/legacy/` and `skip-existing`; `publish=pypi` uses
PyPI and does not skip an existing version. `publish=none`, the default, only builds and keeps the
artifacts.

A tag still runs the build and the `release` job, which attaches the four wheels to the GitHub
release; it does not publish them. Publication is always an explicit manual dispatch.

## Publishing the wrapper

`v*` triggers `release.yaml`, which builds the sdist and wheel, runs `twine check`, and publishes
`fresh-fvsbc` under the `pypi` environment. The manual `rehearse` job publishes the same build to
TestPyPI under `testpypi`.

The `fvs` extra in `pyproject.toml` names the binary version, so publish the binary first and then
release the wrapper that pins it.

## Checking a TestPyPI install

TestPyPI does not proxy PyPI, so install the binary from TestPyPI and its dependencies from PyPI:

```bash
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  "fresh-fvsbc-pyfvs==0.3.12"
```

Then check `pyfvs.list_variants()` reports `BC: OK` and run a W2 subzone smoke case before publishing
the same version to PyPI.
