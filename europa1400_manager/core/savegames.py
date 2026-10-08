"""Savegames: listing, backing up to a zip and restoring.

The game saves to <GfxPath>/gamedata/*.SAV (single player) and gamedata/network/*.SAV (multiplayer); GfxPath comes
from game.ini (default: the resources folder). Backups go to Documents/Europa 1400 Manager/Backups.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from platformdirs import user_documents_path

from europa1400_manager.core import ini
from europa1400_manager.core.errors import ManagerError
from europa1400_manager.core.game import Game
from europa1400_manager.i18n import tr


@dataclass
class Savegame:
    path: Path
    relative: str  # relative to the gamedata folder, "/" separated
    multiplayer: bool
    size: int
    modified: datetime


def gamedata_dir(game: Game) -> Path:
    gfx = (
        ini.get(game.game_ini, "General", "GfxPath") if game.game_ini.exists() else None
    )
    candidates = []
    if gfx and Path(gfx).is_dir():
        candidates.append(Path(gfx))
    candidates += [
        p for p in game.path.iterdir() if p.is_dir() and p.name.lower() == "resources"
    ]
    for base in candidates:
        found = next(
            (p for p in base.iterdir() if p.is_dir() and p.name.lower() == "gamedata"),
            None,
        )
        if found:
            return found
    return (candidates[0] if candidates else game.path / "Resources") / "gamedata"


def backup_dir() -> Path:
    return user_documents_path() / "Europa 1400 Manager" / "Backups"


def list_savegames(game: Game) -> list[Savegame]:
    root = gamedata_dir(game)
    if not root.is_dir():
        return []
    saves = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() == ".sav":
            relative = path.relative_to(root).as_posix()
            stat = path.stat()
            saves.append(
                Savegame(
                    path,
                    relative,
                    relative.lower().startswith("network/"),
                    stat.st_size,
                    datetime.fromtimestamp(stat.st_mtime),
                )
            )
    return saves


def backup(game: Game, label: str = "") -> Path:
    saves = list_savegames(game)
    if not saves:
        raise ManagerError(tr("error.no_savegames"))
    folder = backup_dir()
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = folder / f"savegames_{stamp}{'_' + label if label else ''}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for save in saves:
            archive.write(save.path, save.relative)
    return target


def list_backups() -> list[Path]:
    folder = backup_dir()
    return (
        sorted(folder.glob("savegames_*.zip"), reverse=True) if folder.is_dir() else []
    )


def restore(game: Game, archive: Path) -> int:
    """Restore a backup (the current savegames are backed up first); returns the number of files restored."""
    game.ensure_not_running()
    root = gamedata_dir(game)
    with zipfile.ZipFile(archive) as zip_file:
        names = [n for n in zip_file.namelist() if n.lower().endswith(".sav")]
        for name in names:
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ManagerError(tr("error.archive_unsafe", member=name))
        if list_savegames(game):
            backup(game, "before-restore")
        for name in names:
            target = root.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zip_file.read(name))
    return len(names)
