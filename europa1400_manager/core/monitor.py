"""The monitor the game starts on: `gfxfix.ini` of the Gfxfix patch (a d3d8.dll in the game folder)."""

from __future__ import annotations

from pathlib import Path

from europa1400_manager.core import ini

FILE_NAME = "gfxfix.ini"
LOG_NAME = "gfxfix.log"
MAXIMUM = 8


def config_path(game_folder: Path) -> Path:
    return game_folder / FILE_NAME


def installed(game_folder: Path) -> bool:
    return config_path(game_folder).exists()


def read(game_folder: Path) -> int:
    """0 = off, 1 = first monitor, ...; 1 when the file has no (valid) value."""
    value = ini.get(config_path(game_folder), "gfxfix", "monitor")
    try:
        return max(0, min(MAXIMUM, int((value or "").strip())))
    except ValueError:
        return 1


def write(game_folder: Path, number: int) -> None:
    if not 0 <= number <= MAXIMUM:
        raise ValueError(f"monitor must be 0..{MAXIMUM}")
    ini.set_value(config_path(game_folder), "gfxfix", "monitor", str(number))
