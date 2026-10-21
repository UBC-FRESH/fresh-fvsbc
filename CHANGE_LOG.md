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
