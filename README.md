# FVS-BC

fvsbc is a Python wrapper for the BC variant of the Forest Vegetation Simulator. It builds the FVSbc variant from a pinned fork of PyFVS and exposes BC keywords, species and BEC handling, and tidy simulation I/O.

## Status

Phase 0 (bootstrap) is planned. `ROADMAP.md` lists the phases, and the GitHub issues carry the live status.

## How this project works

This project follows the UBC-FRESH dev workflow. Work is planned as phases, tasks, and subtasks in `ROADMAP.md`, mirrored in GitHub issues, and recorded in `CHANGE_LOG.md`. The agent operating contract is in `AGENTS.md`. Read `AGENTS.md`, then `ROADMAP.md`, before you change anything.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python scripts/check_workflow.py
```

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating contract for coding agents |
| `ROADMAP.md` | Plan of record and issue tracker map |
| `CHANGE_LOG.md` | Dated narrative of changes |
| `docs/` | Documentation site |
| `notes/` | Decisions (ADRs), reference notes, and focused plans |
| `scripts/check_workflow.py` | Workflow validator |
| `tests/` | pytest suite, including a check that the planning surfaces pass the validator |

## License

Choose and add a license before the first public release.
