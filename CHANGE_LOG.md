# Change Log

Newest entries last. Each milestone gets a dated entry that matches the roadmap status and the GitHub issue comments.

## 2026-10-21

- Created FVS-BC from the UBC-FRESH dev workflow seed. The agent contract, roadmap, docs skeleton, and validator came from the seed. Every phase is planned, and no parent issues exist yet.
- Recorded ADR 0001 (fork PyFVS as the FVS build and FFI layer) and created the fork `UBC-FRESH/PyFVS`.
- Recorded ADR 0002 (`fvsbc` is a standalone package), then corrected it: `nemora` is upstream, a producer of the tree lists that FVS consumes, not an unrelated package.
- Recorded ADR 0003 (`fvsbc` owns the bridge from synthetic stem populations).
- Created the public repository `UBC-FRESH/fvsbc` and pushed `main`.
- Created the `phase` and `task` labels that the seed's issue templates require.
- Activated P0: parent issue #1, child issues #2 and #3, branch `feature/p0-bootstrap`.
- P0.1: adapted `AGENTS.md` and `README.md` to this project.
- P0.2: installed the dev dependencies and ran `python scripts/dashboard.py`. All six gates green: lint, format, types, tests, validator, docs. Exit status 0. The dashboard is green on `d21d571`.
- P0 merged. Squash-merged pull request #4 as `9c576f3`, deleted `feature/p0-bootstrap`, and closed parent issue #1 with child issues #2 and #3.
- Enabled GitHub Pages with `build_type: workflow`. The `Docs` workflow now passes on `main` (run 39559881805), and the site is live at https://ubc-fresh.github.io/fvsbc/.
- Launched P1 (Scope and design): parent issue #5, child issues #6, #7, and #8, branch `feature/p1-scope-design`.
- P1.1: added the MIT licence, aligned `pyproject.toml` and `README.md`, and recorded the dependency licenses in `notes/reference/license-analysis.md`. Checked the FVS tree for copyleft and found none; FVS is U.S. public domain and PyFVS is MIT.
- P1.2: wrote the problem statement and scope in `notes/scope.md`, with the users, the in-scope surface, and ten out-of-scope items each with a reason.
