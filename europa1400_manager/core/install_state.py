"""What the manager installed into a game folder, and how to undo it.

<game>/.europa1400-manager/state.json records per patch every file written (with its SHA-256 and the backup of the
file it replaced), every INI value changed (with the previous value) and the folders it owns. Installing runs as a
transaction: on any error everything done so far is rolled back. Uninstalling restores the backups and previous INI
values, but never deletes a file somebody changed after the install.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from europa1400_manager.core import ini
from europa1400_manager.core.download import sha256_of
from europa1400_manager.core.errors import PatchError
from europa1400_manager.i18n import tr

log = logging.getLogger(__name__)

STATE_DIR = ".europa1400-manager"
STATE_VERSION = 1


@dataclass
class FileRecord:
    path: str  # relative to the game folder, "/" separated
    sha256: str
    backup: str | None = None  # relative to the state folder


@dataclass
class IniRecord:
    file: str
    section: str
    key: str
    value: str | None  # what the patch set
    previous: str | None  # what was there before (None = key did not exist)


@dataclass
class PatchRecord:
    version: str | None = None
    installed_at: str = ""
    files: list[FileRecord] = field(default_factory=list)
    ini: list[IniRecord] = field(default_factory=list)
    owned_dirs: list[str] = field(
        default_factory=list
    )  # removed completely on uninstall

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatchRecord:
        return cls(
            version=data.get("version"),
            installed_at=data.get("installed_at", ""),
            files=[FileRecord(**f) for f in data.get("files", [])],
            ini=[IniRecord(**i) for i in data.get("ini", [])],
            owned_dirs=list(data.get("owned_dirs", [])),
        )


def _relative(path: str) -> PurePosixPath:
    relative = PurePosixPath(path.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise PatchError(tr("error.unsafe_path", path=path))
    return relative


class InstallState:
    def __init__(self, game_dir: Path) -> None:
        self.game_dir = game_dir
        self.dir = game_dir / STATE_DIR
        self.patches: dict[str, PatchRecord] = {}
        self._load()

    @property
    def file(self) -> Path:
        return self.dir / "state.json"

    def _load(self) -> None:
        if not self.file.exists():
            return
        try:
            data = json.loads(self.file.read_text(encoding="utf-8"))
            self.patches = {
                k: PatchRecord.from_dict(v) for k, v in data.get("patches", {}).items()
            }
        except (OSError, ValueError, TypeError) as error:
            raise PatchError(
                tr("error.state_unreadable", file=self.file, error=error)
            ) from error

    def save(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        data = {
            "version": STATE_VERSION,
            "patches": {k: asdict(v) for k, v in self.patches.items()},
        }
        temporary = self.file.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(self.file)

    def path(self, relative: str) -> Path:
        return self.game_dir.joinpath(*_relative(relative).parts)

    def owner_of(self, relative: str) -> str | None:
        wanted = str(_relative(relative)).lower()
        for patch_id, record in self.patches.items():
            if any(f.path.lower() == wanted for f in record.files):
                return patch_id
        return None

    def begin(self, patch_id: str, version: str | None) -> Transaction:
        return Transaction(self, patch_id, version)

    def uninstall(self, patch_id: str) -> list[str]:
        """Undo a recorded install; returns warnings (files kept because they were changed)."""
        record = self.patches.get(patch_id)
        if record is None:
            return []
        warnings: list[str] = []
        for item in reversed(record.ini):
            target = self.path(item.file)
            if (
                target.exists()
                and ini.get(target, item.section, item.key) == item.value
            ):
                ini.set_value(target, item.section, item.key, item.previous)
        owned = [str(_relative(d)).lower() + "/" for d in record.owned_dirs]
        for item in reversed(record.files):
            target = self.path(item.path)
            if any(item.path.lower().startswith(d) for d in owned):
                continue  # removed with its folder below
            if target.exists():
                if sha256_of(target) != item.sha256:
                    warnings.append(tr("warning.file_changed", path=item.path))
                    continue
                target.unlink()
            if item.backup:
                backup = self.dir / item.backup
                if backup.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(backup), str(target))
            _remove_empty_parents(target.parent, self.game_dir)
        for owned in record.owned_dirs:
            shutil.rmtree(self.path(owned), ignore_errors=True)
            _remove_empty_parents(self.path(owned).parent, self.game_dir)
        shutil.rmtree(self.dir / "backups" / patch_id, ignore_errors=True)
        del self.patches[patch_id]
        if self.patches:
            self.save()
        else:
            shutil.rmtree(self.dir, ignore_errors=True)
        return warnings


def _remove_empty_parents(folder: Path, stop: Path) -> None:
    folder = folder.resolve()
    stop = stop.resolve()
    while folder != stop and folder.is_relative_to(stop):
        try:
            folder.rmdir()
        except OSError:
            return
        folder = folder.parent


class Transaction:
    """Changes of one patch install; commit() records them, rollback() undoes them."""

    def __init__(self, state: InstallState, patch_id: str, version: str | None) -> None:
        self.state = state
        self.patch_id = patch_id
        self.record = PatchRecord(
            version=version,
            installed_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        self._created_dirs: list[Path] = []

    def write_file(self, source: Path, relative: str) -> None:
        """Copy source to <game>/relative; an existing file is backed up and restored on uninstall."""
        rel = _relative(relative)
        target = self.state.path(str(rel))
        owner = self.state.owner_of(str(rel))
        if owner and owner != self.patch_id:
            raise PatchError(tr("error.file_owned", path=str(rel), owner=owner))
        if any(f.path.lower() == str(rel).lower() for f in self.record.files):
            shutil.copy2(
                source, target
            )  # written twice in this install: keep the first backup
            next(
                f for f in self.record.files if f.path.lower() == str(rel).lower()
            ).sha256 = sha256_of(target)
            return
        backup_rel: str | None = None
        if target.exists():
            backup_rel = f"backups/{self.patch_id}/{rel}"
            backup = self.state.dir / backup_rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        self._make_dirs(target.parent)
        shutil.copy2(source, target)
        self.record.files.append(
            FileRecord(path=str(rel), sha256=sha256_of(target), backup=backup_rel)
        )

    def own_dir(self, relative: str) -> None:
        """A folder that belongs to the patch completely (removed on uninstall, also files created later).

        Call before writing into it; a folder that already exists stays the player's (only the recorded files are
        undone then)."""
        rel = str(_relative(relative))
        if self.state.path(rel).exists():
            return
        if rel not in self.record.owned_dirs:
            self.record.owned_dirs.append(rel)

    def set_ini(self, relative: str, section: str, key: str, value: str | None) -> None:
        target = self.state.path(relative)
        written = next(
            (
                f
                for f in self.record.files
                if f.path.lower() == str(_relative(relative)).lower()
            ),
            None,
        )
        if (
            written is not None
        ):  # a file of this patch: it goes away on uninstall, only its checksum changes
            ini.set_value(target, section, key, value)
            written.sha256 = sha256_of(target)
            return
        previous = ini.get(target, section, key) if target.exists() else None
        if not any(
            i.file == relative and i.section == section and i.key == key
            for i in self.record.ini
        ):
            self.record.ini.append(IniRecord(relative, section, key, value, previous))
        else:
            next(
                i
                for i in self.record.ini
                if i.file == relative and i.section == section and i.key == key
            ).value = value
        ini.set_value(target, section, key, value)

    def _make_dirs(self, folder: Path) -> None:
        missing: list[Path] = []
        while not folder.exists():
            missing.append(folder)
            folder = folder.parent
        for path in reversed(missing):
            path.mkdir()
            self._created_dirs.append(path)

    def commit(self) -> None:
        self.state.patches[self.patch_id] = self.record
        self.state.save()

    def rollback(self) -> None:
        for item in reversed(self.record.ini):
            try:
                ini.set_value(
                    self.state.path(item.file), item.section, item.key, item.previous
                )
            except OSError as error:
                log.error(
                    "rollback of %s [%s] %s failed: %s",
                    item.file,
                    item.section,
                    item.key,
                    error,
                )
        for item in reversed(self.record.files):
            target = self.state.path(item.path)
            try:
                target.unlink(missing_ok=True)
                if item.backup:
                    shutil.move(str(self.state.dir / item.backup), str(target))
            except OSError as error:
                log.error("rollback of %s failed: %s", item.path, error)
        for owned in self.record.owned_dirs:
            shutil.rmtree(self.state.path(owned), ignore_errors=True)
        for folder in reversed(self._created_dirs):
            try:
                folder.rmdir()
            except OSError:
                pass
        shutil.rmtree(self.state.dir / "backups" / self.patch_id, ignore_errors=True)
