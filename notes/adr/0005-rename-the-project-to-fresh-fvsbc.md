# ADR 0005: Rename the project to `fresh-fvsbc`

Status: accepted on 2026-10-23. The maintainer chose the rename.
Date: 2026-10-23
Issues: #14 (P2.4)

## Context

Three different things carry a name that reads as `fvsbc`, and prose cannot tell them apart.

| What it is | Its name today |
| --- | --- |
| This project's wrapper package | the top-level module `fvsbc` |
| PyFVS's BC variant extension | the submodule `pyfvs.fvsbc` |
| The FVS variant itself | `BC`, called `FVSbc` in the FVS tree — `bin/FVSbc_sourceList.txt`, `canada/bin/`, and the standalone `bin/FVSbc` executable that the official test `makefile` invokes |

The confusion is nominal, not mechanical. It is worth saying plainly, because a claim made earlier in this
project's work said otherwise: there is no import collision. `pyfvs/fvs.py` builds the extension name as
`'pyfvs.fvs%s' % variant[:2]`, so it is a submodule of `pyfvs`, and a top-level `fvsbc` does not shadow it.
Both already coexist. What cannot coexist is three names and one spelling.

The string `fvsbc` appears **161 times in 28 tracked files**. Ten of those files hold it as history: the
changelog, whose entries are append-only; the P0 and P1 close-out reports; and ADRs 0001 to 0004, which are
accepted and are not rewritten.

## Decision

Rename this project to `fresh-fvsbc`, in four places and one rule. Approved by the maintainer on
2026-10-23, and the repository rename ran that day:

- the distribution name is `fresh-fvsbc`, and the import name is `fresh_fvsbc`, with the package at
  `src/fresh_fvsbc/`. The underscore form is forced, because a hyphen is not valid in a Python identifier;
- the GitHub repository is `UBC-FRESH/fresh-fvsbc`, and the URLs in `pyproject.toml` and `CITATION.cff`
  follow it;
- the local checkout directory is renamed to `fresh-fvsbc`, and the workspace symlink that points at it is
  repointed. The absolute paths are machine-specific, so they are not recorded here;
- the FVS variant is unaffected. It stays `bc`, the PyFVS build flag stays `-Dfvsvariants=bc`, and the
  banked patch set is unchanged.

The rule is that the names mean different things and are written differently: `fresh-fvsbc` is this project,
`FVS-BC` or "the BC variant" is the variant, and `pyfvs.fvsbc` and `FVSbc` are written in full when FVS's own
artifact is meant. The reference pages state the rule once, and the rest link to it.

## Consequences

- Three names, three referents. The docs stop needing a sentence of explanation every time the wrapper
  drives the variant.
- **The published Pages URL changes**, from `ubc-fresh.github.io/fvsbc/` to
  `ubc-fresh.github.io/fresh-fvsbc/`. GitHub redirects a renamed repository's URL, but a renamed project's
  old Pages path is not redirected, so every outward link must be updated in the same change set as the
  rename. Two tracked files carry both URLs today.
- The repository rename is a public change. `approval-gates.rst` puts settings and Pages on the ask-first
  list, and a rename republishes every URL, so it is treated the same way: it is named with its command and
  runs only after its own approval.
- The history stays legible. The changelog, the two close-out reports, and the accepted ADRs keep the old
  name, because they record what was true when they were written. ADRs 0001 to 0004 each gain one
  `Renamed by ADR 0005` line on their status line, which is the form the `ubc-fresh-dev-workflow` seed
  uses in its own `notes/adr/0004-human-approval-gates.md`. An earlier version of this paragraph
  attributed that form to this repository's ADR 0004, which carries no such line and is still proposed.
- Several note filenames carry the old name, including the banked patch set. They are stable paths that
  other files cite, so renaming them is its own step, done deliberately rather than by a search and replace.

## Alternatives considered

- **Rename only the distribution, and keep the import name `fvsbc`.** Rejected: the import name is what a
  caller types, and it is the name that collides in prose and in a traceback with `pyfvs.fvsbc`.
- **Keep the name, and disambiguate in prose only.** Rejected: the repository, the Pages site, and the
  package index each publish the name, and each is read by people who never see our prose.
- **Ask upstream to rename PyFVS's extension instead**, for instance to `pyfvs.bc`. Rejected for now: that
  is a fork change made for our convenience, and it belongs to the upstream policy that ADR 0001 leaves open.
- **Rename everything in one commit.** Rejected: 161 occurrences across code, documents, and history, where
  the history must not move and the public URL change needs its own approval.
