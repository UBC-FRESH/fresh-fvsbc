"""The optional HTTP surface over a run's artefacts.

Importing this package is free: the application lives in :mod:`fresh_fvsbc.web.app`, which needs the
``web`` extra (FastAPI and uvicorn). The command line imports it lazily, so the core install never
needs
it, and :mod:`fresh_fvsbc.web.runs` — the readers — has no web dependency at all.

See ``notes/design/fresh-fvsbc-web-frontend.md`` for the contract this implements.
"""
