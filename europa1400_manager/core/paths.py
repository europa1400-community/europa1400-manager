"""Where the manager keeps its files.

Settings and caches live in the user's standard folders (platformdirs), never next to the executable: the manager may
sit in a read-only or synced folder, and several copies must share one configuration. Per-game state (installed
patches, backups) lives in the game folder itself, see `install_state.py`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from platformdirs import user_cache_path, user_config_path, user_log_path

APP_NAME = "europa1400-manager"
APP_AUTHOR = "europa1400-community"


def _override(variable: str) -> Path | None:
    value = os.environ.get(variable)
    return Path(value) if value else None


def config_dir() -> Path:
    return _override("E1400_MANAGER_CONFIG_DIR") or user_config_path(
        APP_NAME, APP_AUTHOR, roaming=True
    )


def cache_dir() -> Path:
    return _override("E1400_MANAGER_CACHE_DIR") or user_cache_path(APP_NAME, APP_AUTHOR)


def log_dir() -> Path:
    return _override("E1400_MANAGER_LOG_DIR") or user_log_path(APP_NAME, APP_AUTHOR)


def resource_dir() -> Path:
    """Bundled read-only files (licenses, icons); inside the PyInstaller bundle when frozen."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


def package_resource(name: str) -> Path:
    """A file in europa1400_manager/resources."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "europa1400_manager" / "resources" / name
    return Path(__file__).resolve().parent.parent / "resources" / name
