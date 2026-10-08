"""An identified game installation: launching, running check, write access, game.ini paths."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import psutil
import shutil

from europa1400_manager.core import ini
from europa1400_manager.core.database import Database
from europa1400_manager.core.detection import GameInfo, identify, is_game_folder
from europa1400_manager.core.errors import (
    GameNotFoundError,
    GameRunningError,
    ManagerError,
    PermissionProblemError,
)
from europa1400_manager.i18n import tr

log = logging.getLogger(__name__)

GAME_INI_BACKUP = "game.ini.manager-backup"
PATH_KEYS = (
    ("General", "GamePath", ""),
    ("General", "GfxPath", "resources"),
    ("General", "MoviePath", "movie"),
)


class Game:
    def __init__(self, info: GameInfo) -> None:
        self.info = info

    @classmethod
    def open(cls, folder: Path, database: Database) -> Game:
        if not is_game_folder(folder, database):
            raise GameNotFoundError(tr("error.not_a_game_folder", path=folder))
        return cls(identify(folder, database))

    @property
    def path(self) -> Path:
        return self.info.path

    @property
    def game_ini(self) -> Path:
        return self.path / "game.ini"

    # --- running and launching ---------------------------------------------------------------------------------

    def running_processes(self) -> list[psutil.Process]:
        executables = {str(e.path.resolve()).lower() for e in self.info.executables}
        running = []
        for process in psutil.process_iter(["exe"]):
            exe = process.info.get("exe")
            if exe and str(Path(exe).resolve()).lower() in executables:
                running.append(process)
        return running

    def ensure_not_running(self) -> None:
        if self.running_processes():
            raise GameRunningError(tr("error.game_running"))

    def launch(self, renderer: str = "d3d8") -> None:
        exe = self.info.exe_d3d8 if renderer == "d3d8" else self.info.exe_dx6
        exe = exe or self.info.main_exe
        if exe is None:
            raise GameNotFoundError(tr("error.no_executable", path=self.path))
        log.info("launching %s", exe)
        try:
            if sys.platform == "win32":
                # ShellExecute honours the compatibility settings and asks for elevation if the exe needs it
                os.startfile(str(exe), cwd=str(self.path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(
                    ["wine", str(exe)], cwd=self.path, start_new_session=True
                )
        except OSError as error:
            raise ManagerError(
                tr("error.launch_failed", exe=exe.name, error=error)
            ) from error

    # --- write access ------------------------------------------------------------------------------------------

    def check_writable(self) -> None:
        """Raise if the manager cannot write into the game folder (e.g. Program Files without admin rights)."""
        try:
            with tempfile.NamedTemporaryFile(
                dir=self.path, prefix=".e1400-write-test-", delete=True
            ):
                pass
            if self.game_ini.exists():
                with self.game_ini.open("r+b"):
                    pass
        except OSError as error:
            raise PermissionProblemError(
                tr("error.not_writable", path=self.path)
            ) from error

    # --- game.ini paths ----------------------------------------------------------------------------------------

    def path_problems(self) -> list[tuple[str, str, str]]:
        """(key, current value, expected value) for game.ini paths that do not point into this folder."""
        if not self.game_ini.exists() or sys.platform != "win32":
            return []  # under Wine game.ini holds Windows paths of the prefix; not checked from Linux
        problems = []
        for section, key, sub in PATH_KEYS:
            current = ini.get(self.game_ini, section, key)
            if current is None:
                continue
            expected = self._expected_path(sub, current)
            if (
                Path(current.rstrip("\\/")) != Path(expected.rstrip("\\/"))
                or not Path(current).is_dir()
            ):
                problems.append((key, current, expected))
        return problems

    def _expected_path(self, sub: str, current: str) -> str:
        target = self.path
        if sub:
            existing = next(
                (
                    p
                    for p in self.path.iterdir()
                    if p.is_dir() and p.name.lower() == sub
                ),
                None,
            )
            target = existing or (self.path / sub)
        text = str(target)
        if current.endswith(("\\", "/")) or not current:
            text += "\\"
        return text

    def backup_game_ini(self) -> None:
        """Keep the game.ini as it was before the manager changed it for the first time."""
        backup = self.path / GAME_INI_BACKUP
        if self.game_ini.exists() and not backup.exists():
            shutil.copy2(self.game_ini, backup)

    def repair_paths(self) -> list[str]:
        problems = self.path_problems()
        if problems:
            self.ensure_not_running()
            ini.set_values(
                self.game_ini,
                {("General", key): expected for key, _, expected in problems},
            )
        return [key for key, _, _ in problems]
