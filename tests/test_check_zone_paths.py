"""The zone-path checker keeps the wrapper's registry honest against the variant source."""

from __future__ import annotations

from pathlib import Path

import pytest

import check_zone_paths as checker


def _source(tmp_path: Path, zones: str) -> Path:
    """Write a minimal becset.f with the given V3 zone list."""
    body = f"""      LV2ATV = .TRUE.
      IF ({zones}) THEN
        LV2ATV = .FALSE.
        RETURN
      ENDIF
"""
    path = tmp_path / "becset.f"
    path.write_text(body, encoding="latin-1")
    return path


def test_the_engine_list_is_read_from_the_if(tmp_path: Path) -> None:
    """Only zones between ``LV2ATV = .TRUE.`` and its ``ENDIF`` count."""
    zones = " .OR. ".join(f"INDEX(BEC%Zone,'{zone}') .GT. 0" for zone in ("ICH", "SBS", "CWH"))
    path = _source(tmp_path, zones)
    assert checker.engine_v3_zones(path) == {"ICH", "SBS", "CWH"}


def test_a_matching_registry_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No divergence means exit 0."""
    zones = " .OR. ".join(f"INDEX(BEC%Zone,'{z}') .GT. 0" for z in ("ICH", "SBS"))
    monkeypatch.setattr(checker, "ZONE_PATH", {"ICH": "V3", "SBS": "V3", "MS": "V2"})
    assert checker.main(["--source", str(_source(tmp_path, zones))]) == checker.EXIT_OK


def test_an_engine_zone_missing_from_the_registry_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A zone the engine runs as V3 and the registry calls V2 is a divergence."""
    zones = "INDEX(BEC%Zone,'MS') .GT. 0"
    monkeypatch.setattr(checker, "ZONE_PATH", {"MS": "V2"})
    status = checker.main(["--source", str(_source(tmp_path, zones))])
    assert status == checker.EXIT_DIVERGED
    assert "MS: the engine runs V3" in capsys.readouterr().out


def test_a_registry_zone_missing_from_the_engine_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A zone the registry calls V3 that the engine runs as V2 is the other divergence."""
    zones = "INDEX(BEC%Zone,'ICH') .GT. 0"
    monkeypatch.setattr(checker, "ZONE_PATH", {"ICH": "V3", "PP": "V3"})
    status = checker.main(["--source", str(_source(tmp_path, zones))])
    assert status == checker.EXIT_DIVERGED
    assert "PP: ZONE_PATH says V3" in capsys.readouterr().out
