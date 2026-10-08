"""Manager settings (settings.json in the user's config folder).

Managers up to 1.2 wrote config.yml (game_path) into the working directory; it is taken over once.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

from europa1400_manager.core import paths

log = logging.getLogger(__name__)


@dataclass
class Settings:
    game_path: str | None = None
    known_game_paths: list[str] = field(
        default_factory=list
    )  # installations the player used before
    language: str | None = None  # "en", "de"; None = system language
    database_branch: str = "master"
    check_updates: bool = True
    skipped_manager_version: str | None = None

    @property
    def game_dir(self) -> Path | None:
        return Path(self.game_path) if self.game_path else None

    def remember_game(self, path: Path) -> None:
        self.game_path = str(path)
        if str(path) not in self.known_game_paths:
            self.known_game_paths.append(str(path))

    @staticmethod
    def file() -> Path:
        return paths.config_dir() / "settings.json"

    @classmethod
    def load(cls) -> Settings:
        path = cls.file()
        if path.exists():
            try:
                data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
                names = {f.name for f in fields(cls)}
                return cls(**{k: v for k, v in data.items() if k in names})
            except (OSError, ValueError, TypeError) as error:
                log.warning("settings unreadable, starting fresh: %s", error)
                return cls()
        settings = cls()
        legacy = _legacy_game_path()
        if legacy:
            settings.remember_game(legacy)
            settings.save()
            log.info("took over the game folder from config.yml: %s", legacy)
        return settings

    def save(self) -> None:
        path = self.file()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        temporary.replace(path)


def _legacy_game_path() -> Path | None:
    candidates = [Path.cwd() / "config.yml"]
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).parent / "config.yml")
    for candidate in candidates:
        try:
            data = (
                yaml.safe_load(candidate.read_text(encoding="utf-8"))
                if candidate.exists()
                else None
            )
        except (OSError, yaml.YAMLError):
            continue
        if (
            isinstance(data, dict)
            and data.get("game_path")
            and Path(str(data["game_path"])).is_dir()
        ):
            return Path(str(data["game_path"]))
    return None
