# Publishing to PyPI

Two distributions are published, and neither uses an API token.

| Distribution | Workflow | What it is |
| --- | --- | --- |
| `fresh-fvsbc` | `release.yaml`, environment `pypi` | this package, pure Python, sdist and wheel |
| `fresh-fvsbc-pyfvs` | built by `wheels.yml`, uploaded by hand | the built BC variant, four wheels, one per Python |

**The workflow name and the environment names follow PyPI, not this repository.** PyPI was configured
with `release.yaml` and the environments `pypi` and `testpypi`; the file and the environments are
named that way so the two cannot drift. `release.yaml` also carries a manual `rehearse` job that
publishes to TestPyPI under the `testpypi` environment, which is what that pending publisher is for.

**`fresh-fvsbc-pyfvs` is uploaded by hand** when the pin changes, because its version is tied to the
fork commit and does not change with every release of this package. Automating it needs a second
trusted publisher on that project, with the same workflow and environment.

Both use **trusted publishing**: GitHub mints a short-lived OIDC token, and PyPI accepts it for the
workflow named in its configuration. Nothing is stored in this repository and nothing has to be
rotated.

## The one-time setup, which needs the PyPI account

An agent cannot do this part: it creates an external account. Each step below is done once, in the
PyPI web interface, signed in as the owner of the project names.

1. **Create the accounts.** A PyPI account at <https://pypi.org/account/register/>, and — strongly
   recommended — the same at <https://test.pypi.org/account/register/> so the first publish can be
   rehearsed against a throwaway index.

2. **Reserve both names.** Under *Your projects → Publishing*, upload any placeholder for
   `fresh-fvsbc-pyfvs` and for `fresh-fvsbc`, or use *Pending publishers* before the first upload.
   The names must be yours before a trusted publisher can be attached to them.

3. **Add a trusted publisher to each project.** *Project → Settings → Publishing → Add a new pending
   publisher → GitHub*, with these exact values:

   | Field | `fresh-fvsbc` | `fresh-fvsbc` (TestPyPI) |
   | --- | --- | --- |
   | Owner | `UBC-FRESH` | `UBC-FRESH` |
   | Repository | `fresh-fvsbc` | `fresh-fvsbc` |
   | Workflow name | `release.yaml` | `release.yaml` |
   | Environment | `pypi` | `testpypi` |

   Add a third, with the same workflow and environment `pypi`, if `fresh-fvsbc-pyfvs` is to be
   published automatically rather than by hand.

   The workflow name and the environment are matched exactly. `wheels.yml` and `publish.yml` both
   declare `environment: pypi`, which is why that field is not blank.

4. **Create the `pypi` environment** in the repository's *Settings → Environments*, with no secrets in
   it. It exists so the trusted publisher has something to match, and so an approval rule can be added
   later without touching the workflows.

## Rehearsing

Run `publish.yml` and `wheels.yml` by hand against TestPyPI first, by adding `repository-url:
https://test.pypi.org/legacy/` to the publish step in a scratch branch. A real rehearsal needs both
distributions, in that order — `fresh-fvsbc` names `fresh-fvsbc-pyfvs` in its `fvs` extra, and TestPyPI
does not proxy PyPI.

## What happens on a tag

`v*` triggers both workflows. `wheels.yml` builds the four wheels, attaches them to the GitHub release,
and publishes them; `publish.yml` builds the sdist and wheel of this package and publishes them. The
fork's publish uses `skip-existing`, because its version is pinned to the commit and does not change
with every release of this package.

## Before the first publish

`docs/installation.rst` tells a reader to install from the release URL and from the git tag, because
neither distribution is on PyPI yet. After the first successful publish, the second line becomes
`pip install fresh-fvsbc` and nothing else on that page changes.
