"""The game.ini settings the manager offers with a proper control (everything else: raw editor).

Only keys whose meaning is known; values as the game writes them (0/1 for switches).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from europa1400_manager.core import ini


@dataclass(frozen=True)
class GameSetting:
    section: str
    key: str
    kind: str  # "bool", "int", "choice", "text"
    label: str  # i18n key
    group: str  # i18n key
    minimum: int = 0
    maximum: int = 100
    choices: tuple[tuple[str, str], ...] = ()  # (value, i18n key)


DISPLAY = "settings.group.display"
SOUND = "settings.group.sound"
GAMEPLAY = "settings.group.gameplay"
NETWORK = "settings.group.network"

SETTINGS: list[GameSetting] = [
    GameSetting(
        "General",
        "Bildmodus",
        "choice",
        "settings.display_mode",
        DISPLAY,
        choices=(
            ("FULLSCREEN", "settings.fullscreen"),
            ("DIRECTWINDOW", "settings.window"),
        ),
    ),
    GameSetting("General", "show_intro", "bool", "settings.show_intro", DISPLAY),
    GameSetting("Sound", "msx", "bool", "settings.music", SOUND),
    GameSetting("Sound", "sfx", "bool", "settings.effects", SOUND),
    GameSetting("Sound", "weather", "bool", "settings.weather_sound", SOUND),
    GameSetting("Sound", "master_vol", "int", "settings.master_volume", SOUND, 0, 127),
    GameSetting("Sound", "msx_vol", "int", "settings.music_volume", SOUND, 0, 127),
    GameSetting("Sound", "sfx_vol", "int", "settings.effects_volume", SOUND, 0, 127),
    GameSetting("Sound", "speech_vol", "int", "settings.speech_volume", SOUND, 0, 127),
    GameSetting("Game", "invert_mouse", "bool", "settings.invert_mouse", GAMEPLAY),
    GameSetting("Game", "hints", "bool", "settings.hints", GAMEPLAY),
    GameSetting("Game", "show_cursor_txt", "bool", "settings.cursor_text", GAMEPLAY),
    GameSetting("Network", "Name", "text", "settings.first_name", NETWORK),
    GameSetting("Network", "Familienname", "text", "settings.family_name", NETWORK),
    GameSetting("Network", "Host", "text", "settings.host", NETWORK),
    GameSetting("Network", "Port", "int", "settings.port", NETWORK, 1, 65535),
]


def read(game_ini: Path) -> dict[tuple[str, str], str | None]:
    values = ini.read_all(game_ini)
    return {
        (s.section, s.key): values.get(s.section.lower(), {}).get(s.key.lower())
        for s in SETTINGS
    }
