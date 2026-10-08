"""Application state shared by all pages; pages react to its signals instead of calling each other."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox, QWidget

from europa1400_manager.core import database as database_module
from europa1400_manager.core import detection, updates
from europa1400_manager.core.database import Database
from europa1400_manager.core.errors import ManagerError
from europa1400_manager.core.game import Game
from europa1400_manager.core.patches import PatchService
from europa1400_manager.core.settings import Settings
from europa1400_manager.i18n import tr

log = logging.getLogger(__name__)


class AppState(QObject):
    database_loaded = Signal()
    game_changed = Signal()  # game (or no game) selected
    patches_changed = Signal()  # something was installed or removed
    busy_changed = Signal(bool, str)  # busy, message
    progress = Signal(str, float)  # message, fraction (-1: unknown)
    update_available = Signal(object)  # updates.Update

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.database = Database()
        self.game: Game | None = None
        self.installations: list[Path] = []
        self._busy = 0

    @property
    def service(self) -> PatchService | None:
        return PatchService(self.game, self.database) if self.game else None

    # --- background work ---------------------------------------------------------------------------------------

    def run(
        self,
        parent: QWidget | None,
        work: Callable[[], Awaitable[Any]],
        message: str = "",
        done: Callable[[Any], None] | None = None,
    ) -> None:
        """Run a coroutine; ManagerError is shown to the player, other errors too (with a hint to the log)."""

        async def runner() -> None:
            self._set_busy(1, message)
            try:
                result = await work()
                if done:
                    done(result)
            except ManagerError as error:
                QMessageBox.warning(parent, tr("ui.error"), str(error))
            except Exception as error:  # noqa: BLE001 - shown, and logged with traceback
                log.exception("unexpected error")
                QMessageBox.critical(
                    parent, tr("ui.error"), tr("ui.unexpected_error", error=error)
                )
            finally:
                self._set_busy(-1, "")

        asyncio.ensure_future(runner())

    def _set_busy(self, delta: int, message: str) -> None:
        self._busy = max(0, self._busy + delta)
        self.busy_changed.emit(self._busy > 0, message)

    @property
    def busy(self) -> bool:
        return self._busy > 0

    # --- loading -----------------------------------------------------------------------------------------------

    async def load(self) -> None:
        self.database = await database_module.load(self.settings.database_branch)
        self.database_loaded.emit()
        self.installations = await asyncio.to_thread(
            detection.find_installations, self.database, self.settings.known_game_paths
        )
        path = self.settings.game_dir
        if path is None and len(self.installations) == 1:
            path = self.installations[0]
        if path is not None:
            try:
                await self.open_game(path)
            except ManagerError as error:
                log.warning("configured game folder unusable: %s", error)
                self.game = None
                self.game_changed.emit()
        else:
            self.game_changed.emit()
        if self.settings.check_updates:
            update = await updates.check()
            if update and update.version != self.settings.skipped_manager_version:
                self.update_available.emit(update)

    async def open_game(self, path: Path) -> None:
        game = await asyncio.to_thread(Game.open, path, self.database)
        self.game = game
        self.settings.remember_game(game.path)
        self.settings.save()
        if game.path not in self.installations:
            self.installations.append(game.path)
        self.game_changed.emit()

    async def reload_database(self) -> None:
        self.database = await database_module.load(self.settings.database_branch)
        self.database_loaded.emit()
        if self.game:
            await self.open_game(self.game.path)
