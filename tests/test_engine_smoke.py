"""The engine smoke is exercised with fakes here; CI runs it against the real extension."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

import engine_smoke


class _Ingrowth:
    def estab_keyword(self, **_kwargs: object) -> object:
        return object()


class _Bundle:
    def __init__(self, bundle_id: str, *, ingrowth: bool = False) -> None:
        self.bundle_id = bundle_id
        self.ingrowth = _Ingrowth() if ingrowth else None

    def render(self) -> tuple[object, ...]:
        return ()

    def ingrowth_keyword(self, **_kwargs: object) -> object:
        assert self.ingrowth is not None
        return object()


def _database(path: Path) -> Path:
    connection = sqlite3.connect(path)
    try:
        for name in ("runs", "stands", "trees", "events", "landscape", "dataset_meta"):
            connection.execute(f"create table {name} (x integer)")
        connection.commit()
    finally:
        connection.close()
    return path


def test_the_smoke_passes_with_the_pieces_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every step is called and the exit status is zero."""

    def fake_bundle(name: str) -> _Bundle:
        return _Bundle(name, ingrowth=name == "recruitment-bc-v1")

    class _Result:
        database = tmp_path / "FVSOut.db"

    monkeypatch.setattr(engine_smoke, "load_default_bundle", fake_bundle)
    monkeypatch.setattr(engine_smoke, "run_case", lambda *_a, **_k: _Result())
    monkeypatch.setattr(
        engine_smoke,
        "read_table",
        lambda *_a, **_k: pd.DataFrame({"Year": [1985, 1990, 1995], "Tph": [17, 17, 56]}),
    )
    monkeypatch.setattr(
        engine_smoke,
        "build_dataset",
        lambda *_a, **_k: {"sqlite": _database(tmp_path / "dataset.sqlite")},
    )
    assert engine_smoke.main(["--directory", str(tmp_path / "out")]) == engine_smoke.EXIT_OK
    assert "OK (" in capsys.readouterr().out


def test_the_smoke_reports_a_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A step that raises becomes exit 1 with the reason, not a traceback."""

    def fake_bundle(name: str) -> _Bundle:
        return _Bundle(name, ingrowth=name == "recruitment-bc-v1")

    class _Result:
        database = tmp_path / "FVSOut.db"

    monkeypatch.setattr(engine_smoke, "load_default_bundle", fake_bundle)
    monkeypatch.setattr(engine_smoke, "run_case", lambda *_a, **_k: _Result())
    monkeypatch.setattr(
        engine_smoke,
        "read_table",
        lambda *_a, **_k: pd.DataFrame({"Year": [1985, 1990, 1995], "Tph": [17, 17, 17]}),
    )
    status = engine_smoke.main(["--directory", str(tmp_path / "out")])
    assert status == engine_smoke.EXIT_FAILED
    assert "SMOKE FAILED" in capsys.readouterr().err
