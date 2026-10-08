"""Finding game installations and identifying them.

Identification, from exact to heuristic:
1. SHA-256 of the executables and server.dll against europa1400-database (game_file.yml): exact build, version,
   language, store.
2. Heuristics for unknown builds: the renderer from the PE imports (Direct3D 8 or DirectDraw), the language from
   game.ini, the store from its files (GOG, Steam), the version from the patch readme.
Every field remembers where it came from, so the UI can say how sure it is.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from europa1400_manager.core import ini, pe
from europa1400_manager.core.database import Database
from europa1400_manager.core.download import sha256_of

log = logging.getLogger(__name__)

STEAM_APP_ID = "39520"
# executable names of all known editions; the database adds more (executable.yml)
KNOWN_EXECUTABLES = [
    "GildeGold_TL.exe",
    "GildeGold.exe",
    "Europa1400Gold_TL.exe",
    "Europa1400Gold.exe",
    "Gilde_TL.exe",
    "Gilde.exe",
    "Europa1400_TL.exe",
    "Europa1400.exe",
]
LANGUAGES = {"german": "de", "deutsch": "de", "english": "en", "russian": "ru"}
FIELDS = ("edition", "version", "distribution", "language", "drm")


@dataclass
class GameExe:
    path: Path
    renderer: str | None  # "d3d8", "dx6"
    sha256: str
    known: bool = False  # hash in the database


@dataclass
class GameInfo:
    path: Path
    executables: list[GameExe] = field(default_factory=list)
    metadata: dict[str, str | None] = field(
        default_factory=lambda: dict.fromkeys(FIELDS)
    )
    sources: dict[str, str] = field(
        default_factory=dict
    )  # field -> "hash" | "heuristic"
    server_sha256: str | None = None

    @property
    def exe_d3d8(self) -> Path | None:
        return next((e.path for e in self.executables if e.renderer == "d3d8"), None)

    @property
    def exe_dx6(self) -> Path | None:
        return next((e.path for e in self.executables if e.renderer == "dx6"), None)

    @property
    def main_exe(self) -> Path | None:
        return (
            self.exe_d3d8
            or self.exe_dx6
            or (self.executables[0].path if self.executables else None)
        )

    @property
    def exactly_known(self) -> bool:
        return any(e.known for e in self.executables)

    def matches(self, wanted: dict[str, str | None]) -> bool:
        """True if every field given in wanted equals the detected one (unknown fields do not match)."""
        return all(
            value is None or self.metadata.get(key) == value
            for key, value in wanted.items()
        )


def executable_names(database: Database | None) -> list[str]:
    names = list(KNOWN_EXECUTABLES)
    for executable in database.executables if database else []:
        for name in (executable.path, executable.tl_path):
            if name not in names:
                names.append(name)
    return names


def _existing(folder: Path, name: str) -> Path | None:
    """Case-insensitive lookup of a file in folder (Linux/Wine installs differ in case)."""
    direct = folder / name
    if direct.exists():
        return direct
    try:
        lower = name.lower()
        return next((p for p in folder.iterdir() if p.name.lower() == lower), None)
    except OSError:
        return None


def is_game_folder(folder: Path, database: Database | None = None) -> bool:
    try:
        if not folder.is_dir():
            return False
    except OSError:
        return False
    return any(_existing(folder, name) for name in executable_names(database))


def identify(folder: Path, database: Database) -> GameInfo:
    info = GameInfo(path=folder)
    known_files = {f.sha256.lower(): f for f in database.files}

    for name in executable_names(database):
        path = _existing(folder, name)
        if path is None or any(e.path == path for e in info.executables):
            continue
        sha256 = sha256_of(path)
        known = known_files.get(sha256)
        renderer = pe.renderer(path)
        if known and known.role in ("game_d3d8", "game_dx6"):
            renderer = known.role.removeprefix("game_")
        info.executables.append(GameExe(path, renderer, sha256, known is not None))
        if known:
            _apply(info, known.metadata, "hash")

    server_dir = _existing(
        folder, "server"
    )  # "Server" or "server" (case matters under Linux/Wine)
    server = _existing(server_dir, "server.dll") if server_dir else None
    if server:
        info.server_sha256 = sha256_of(server)
        known = known_files.get(info.server_sha256)
        if known:
            _apply(info, known.metadata, "hash")

    _heuristics(info, database)
    log.info("identified %s: %s (%s)", folder, info.metadata, info.sources)
    return info


def _apply(info: GameInfo, metadata: object, source: str) -> None:
    for key in FIELDS:
        value = getattr(metadata, key, None)
        if value and (
            info.metadata.get(key) is None or info.sources.get(key) != "hash"
        ):
            info.metadata[key] = value
            info.sources[key] = source


def _guess(info: GameInfo, key: str, value: str | None) -> None:
    if value and info.metadata.get(key) is None:
        info.metadata[key] = value
        info.sources[key] = "heuristic"


def _heuristics(info: GameInfo, database: Database) -> None:
    folder = info.path
    game_ini = folder / "game.ini"
    if game_ini.exists():
        language = (ini.get(game_ini, "General", "language") or "").strip().lower()
        _guess(info, "language", LANGUAGES.get(language))

    names = [p.name.lower() for p in _safe_iterdir(folder)]
    if any(n.startswith("goggame") for n in names):
        _guess(info, "distribution", "gog")
        _guess(info, "drm", "none")
    elif "steamapps" in [p.lower() for p in folder.parts] or any(
        n.endswith("_install.vdf") or n in ("steam_api.dll", "steam_appid.txt")
        for n in names
    ):
        _guess(info, "distribution", "steam")
        _guess(info, "drm", "steam")

    exe_names = [e.path.name.lower() for e in info.executables]
    if any("gold" in n for n in exe_names):
        _guess(info, "edition", "gold")
    elif exe_names:
        _guess(info, "edition", "standard")
    if any("2.06" in n for n in names if n.startswith("readme")):
        _guess(info, "version", "v2.06")

    # the old name-based table as a last resort (it cannot tell German Steam from English GOG)
    for mapping in database.executable_mappings:
        executable = next(
            (e for e in database.executables if e.id == mapping.executable), None
        )
        if executable and _existing(folder, executable.path):
            for key in FIELDS:
                _guess(info, key, getattr(mapping.metadata, key, None))


def _safe_iterdir(folder: Path) -> list[Path]:
    try:
        return list(folder.iterdir())
    except OSError:
        return []


# --- finding installations ----------------------------------------------------------------------------------------


def find_installations(
    database: Database | None = None, extra: Iterable[str] = ()
) -> list[Path]:
    """Game folders found on this computer (Steam, GOG, uninstall entries, common folders), without duplicates."""
    candidates: list[Path] = [Path(p) for p in extra]
    for finder in (_steam_folders, _gog_folders, _uninstall_folders, _common_folders):
        try:
            candidates.extend(finder())
        except Exception as error:  # noqa: BLE001 - a broken registry entry must not stop the search
            log.debug("%s failed: %s", finder.__name__, error)
    found: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        key = str(resolved).lower() if sys.platform == "win32" else str(resolved)
        if key in seen:
            continue
        seen.add(key)
        if is_game_folder(resolved, database):
            found.append(resolved)
    return found


def _registry_values(root: int, path: str, value: str) -> Iterable[str]:
    if sys.platform != "win32":
        return []
    import winreg

    results: list[str] = []
    for view in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | view) as key:
                results.append(str(winreg.QueryValueEx(key, value)[0]))
        except OSError:
            continue
    return results


def _registry_subkeys(root: int, path: str) -> Iterable[tuple[str, int]]:
    if sys.platform != "win32":
        return []
    import winreg

    results: list[tuple[str, int]] = []
    for view in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | view) as key:
                for index in range(winreg.QueryInfoKey(key)[0]):
                    name = winreg.EnumKey(key, index)
                    results.append((f"{path}\\{name}", view))
        except OSError:
            continue
    return results


def _steam_libraries() -> list[Path]:
    roots: list[Path] = []
    if sys.platform == "win32":
        import winreg

        for value in _registry_values(
            winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"
        ):
            roots.append(Path(value))
        for value in _registry_values(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"
        ):
            roots.append(Path(value))
    else:
        home = Path.home()
        roots += [
            home / ".steam/steam",
            home / ".local/share/Steam",
            home / ".var/app/com.valvesoftware.Steam/data/Steam",
        ]
    libraries: list[Path] = []
    for root in roots:
        libraries.append(root)
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            text = vdf.read_text(encoding="utf-8", errors="replace")
            libraries += [
                Path(m.replace("\\\\", "\\"))
                for m in re.findall(r'"path"\s+"([^"]+)"', text)
            ]
    return libraries


def _steam_folders() -> list[Path]:
    folders: list[Path] = []
    for library in _steam_libraries():
        manifest = library / "steamapps" / f"appmanifest_{STEAM_APP_ID}.acf"
        if manifest.exists():
            match = re.search(
                r'"installdir"\s+"([^"]+)"',
                manifest.read_text(encoding="utf-8", errors="replace"),
            )
            if match:
                folders.append(library / "steamapps" / "common" / match.group(1))
        common = library / "steamapps" / "common"
        for name in (
            "Europa 1400 Gold",
            "Europa 1400 The Guild Gold",
            "Die Gilde Gold",
        ):
            folders.append(common / name)
    return folders


def _gog_folders() -> list[Path]:
    if sys.platform != "win32":
        return []
    import winreg

    folders: list[Path] = []
    for subkey, view in _registry_subkeys(
        winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\Games"
    ):
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_READ | view
            ) as key:
                folders.append(Path(str(winreg.QueryValueEx(key, "path")[0])))
        except OSError:
            continue
    return folders


def _uninstall_folders() -> list[Path]:
    if sys.platform != "win32":
        return []
    import winreg

    folders: list[Path] = []
    path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for subkey, view in _registry_subkeys(root, path):
            try:
                with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | view) as key:
                    name = str(winreg.QueryValueEx(key, "DisplayName")[0]).lower()
                    if "europa 1400" in name or "gilde" in name or "the guild" in name:
                        folders.append(
                            Path(str(winreg.QueryValueEx(key, "InstallLocation")[0]))
                        )
            except OSError:
                continue
    return folders


def _common_folders() -> list[Path]:
    folders: list[Path] = []
    bases: list[Path] = []
    if sys.platform == "win32":
        for variable in ("ProgramFiles(x86)", "ProgramFiles"):
            if os.environ.get(variable):
                bases.append(Path(os.environ[variable]))
        for drive in "CDEF":
            bases += [Path(f"{drive}:/GOG Games"), Path(f"{drive}:/Games")]
    else:
        bases += [
            Path.home() / ".wine/drive_c/GOG Games",
            Path.home() / ".wine/drive_c/Program Files (x86)",
        ]
    for base in bases:
        for entry in _safe_iterdir(base):
            lower = entry.name.lower()
            if (
                "europa" in lower
                or "gilde" in lower
                or "guild" in lower
                or "jowood" in lower
            ):
                folders.append(entry)
                folders += [
                    p for p in _safe_iterdir(entry) if p.is_dir()
                ]  # JoWooD/Die Gilde Gold
    return folders
