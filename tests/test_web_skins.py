"""The skin loader: manifests are validated, and an unknown name is refused rather than dropped."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fresh_fvsbc.web.skins import ACTIONS, PANELS, SkinError, load_skins


def _write(directory: Path, name: str, document: dict[str, object]) -> Path:
    """Write a manifest into a directory.

    Parameters
    ----------
    directory : Path
        Where the manifest goes.
    name : str
        The file's stem.
    document : dict
        The manifest's content.

    Returns
    -------
    Path
        The file written.
    """
    path = directory / f"{name}.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_the_shipped_skins_load_and_cover_the_panels() -> None:
    """Every shipped manifest is valid, and the four roles the design note names are present."""
    skins = load_skins()
    assert {skin.id for skin in skins} == {"analyst", "carbon", "reviewer", "tables"}
    for skin in skins:
        assert skin.panels, skin.id
        assert set(skin.panels) <= PANELS
        assert set(skin.actions) <= ACTIONS


def test_the_reviewer_is_read_only_and_has_no_actions() -> None:
    """``read_only`` removes every mutating action, whatever the manifest lists."""
    reviewer = next(skin for skin in load_skins() if skin.id == "reviewer")
    assert reviewer.read_only is True
    assert reviewer.actions == ()


def test_a_read_only_manifest_cannot_keep_an_action(tmp_path: Path) -> None:
    """A manifest that sets ``read_only`` and lists an action loses the action, not the flag."""
    _write(
        tmp_path,
        "x",
        {
            "id": "x",
            "title": "X",
            "panels": ["tables"],
            "actions": ["start_run"],
            "read_only": True,
        },
    )
    skin = load_skins(tmp_path)[0]
    assert skin.actions == ()
    assert skin.read_only is True


def test_an_unknown_panel_is_refused_by_name(tmp_path: Path) -> None:
    """A typo in a manifest is an error naming the entry, because a lost panel is a silent lie."""
    _write(tmp_path, "x", {"id": "x", "title": "X", "panels": ["tables", "nonsense"]})
    with pytest.raises(SkinError, match="'nonsense'"):
        load_skins(tmp_path)


def test_an_unknown_action_is_refused_by_name(tmp_path: Path) -> None:
    """Actions are validated against the registry exactly as panels are."""
    _write(
        tmp_path,
        "x",
        {"id": "x", "title": "X", "panels": ["tables"], "actions": ["delete_everything"]},
    )
    with pytest.raises(SkinError, match="'delete_everything'"):
        load_skins(tmp_path)


def test_a_manifest_missing_a_required_key_is_refused(tmp_path: Path) -> None:
    """A skin without a title is not a skin."""
    _write(tmp_path, "x", {"id": "x", "panels": ["tables"]})
    with pytest.raises(SkinError, match="'title'"):
        load_skins(tmp_path)


def test_a_manifest_that_is_not_an_object_is_refused(tmp_path: Path) -> None:
    """A JSON list is not a manifest, and the message says so."""
    (tmp_path / "x.json").write_text("[]", encoding="utf-8")
    with pytest.raises(SkinError, match="JSON object"):
        load_skins(tmp_path)


def test_panels_must_be_a_list_of_strings(tmp_path: Path) -> None:
    """A panel entry that is not a string is refused rather than coerced."""
    _write(tmp_path, "x", {"id": "x", "title": "X", "panels": [1, 2]})
    with pytest.raises(SkinError, match="list of strings"):
        load_skins(tmp_path)


def test_an_empty_directory_is_refused(tmp_path: Path) -> None:
    """A directory with no manifests is an error, not an empty application."""
    with pytest.raises(SkinError, match="no skin manifests"):
        load_skins(tmp_path)
