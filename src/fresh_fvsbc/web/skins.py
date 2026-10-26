"""The skin loader: role manifests over one application.

A skin is a JSON document listing which panels and actions a role gets, following the ws4 and fhops
front
ends. **An unknown panel or action is refused with its name**, because a manifest that silently
loses a
panel is a manifest that lies about what a role can do.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ACTIONS",
    "PANELS",
    "Skin",
    "SkinError",
    "load_skins",
]

#: Every panel the application can draw. A manifest may name only these.
PANELS: frozenset[str] = frozenset(
    {
        "tables",
        "summary",
        "trees",
        "keywords",
        "provenance",
        "compare",
    }
)

#: Every action that changes something. ``read_only`` removes all of them.
ACTIONS: frozenset[str] = frozenset({"start_run", "export"})

#: The directory the shipped manifests live in.
SKIN_DIRECTORY: Path = Path(__file__).resolve().parent / "skins"


class SkinError(Exception):
    """A skin manifest names something the application does not have."""


@dataclass(frozen=True)
class Skin:
    """One role's view of the application.

    Attributes
    ----------
    id : str
        The manifest's identifier, which is also its file name.
    title : str
        The name a person sees.
    panels : tuple of str
        The panels this role gets, in the order the manifest lists them.
    actions : tuple of str
        The mutating actions this role may take. Empty when ``read_only``.
    read_only : bool
        Whether the role is barred from every mutating action.
    """

    id: str
    title: str
    panels: tuple[str, ...]
    actions: tuple[str, ...]
    read_only: bool


def _refuse(unknown: Iterable[str], known: frozenset[str], kind: str, source: Path) -> None:
    """Raise when a manifest names something that is not in a registry.

    Parameters
    ----------
    unknown : iterable of str
        The names the manifest carries that the registry does not.
    known : frozenset of str
        The registry.
    kind : str
        What the names are, for the message: ``"panel"`` or ``"action"``.
    source : Path
        The manifest, for the message.

    Raises
    ------
    SkinError
        Always, naming every unknown entry and the ones that would have been valid.
    """
    missing = sorted(set(unknown) - known)
    if missing:
        raise SkinError(
            f"{source.name}: unknown {kind}(s) {', '.join(repr(name) for name in missing)}; "
            f"this application has {', '.join(sorted(known))}"
        )


def _load(path: Path) -> Skin:
    """Load and validate one manifest.

    Parameters
    ----------
    path : Path
        The manifest to load.

    Returns
    -------
    Skin
        The validated skin.

    Raises
    ------
    SkinError
        If the document is not an object, is missing a required key, or names an unknown panel or
        action.
    """
    document: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise SkinError(f"{path.name}: a skin must be a JSON object")
    for key in ("id", "title", "panels"):
        if key not in document:
            raise SkinError(f"{path.name}: a skin needs a {key!r}")
    panels = document["panels"]
    actions = document.get("actions", [])
    if not isinstance(panels, list) or not all(isinstance(item, str) for item in panels):
        raise SkinError(f"{path.name}: 'panels' must be a list of strings")
    if not isinstance(actions, list) or not all(isinstance(item, str) for item in actions):
        raise SkinError(f"{path.name}: 'actions' must be a list of strings")
    _refuse(panels, PANELS, "panel", path)
    _refuse(actions, ACTIONS, "action", path)
    read_only = bool(document.get("read_only", False))
    return Skin(
        id=str(document["id"]),
        title=str(document["title"]),
        panels=tuple(panels),
        actions=() if read_only else tuple(actions),
        read_only=read_only,
    )


def load_skins(directory: Path | None = None) -> tuple[Skin, ...]:
    """Load every skin manifest in a directory.

    Parameters
    ----------
    directory : Path, optional
        The directory to read. Defaults to the shipped manifests.

    Returns
    -------
    tuple of Skin
        The skins, ordered by identifier.

    Raises
    ------
    SkinError
        If any manifest is invalid, or the directory holds none.
    """
    root = directory or SKIN_DIRECTORY
    skins = tuple(sorted((_load(path) for path in root.glob("*.json")), key=lambda s: s.id))
    if not skins:
        raise SkinError(f"{root} holds no skin manifests")
    return skins
