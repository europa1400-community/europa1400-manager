from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from europa1400_manager.core import download
from europa1400_manager.core.game import Game
from europa1400_manager.core.install_state import Transaction
from europa1400_manager.core.models import GamePatch

Progress = Callable[[str, float | None], None]  # (message, fraction 0..1 or None)


class Handler:
    """Installs one database patch into one game."""

    def __init__(self, patch: GamePatch, game: Game) -> None:
        self.patch = patch
        self.game = game

    async def fetch(self, progress: Progress | None) -> Path:
        def report(done: int, total: int | None) -> None:
            if progress:
                progress(self.patch.name, done / total if total else None)

        return await download.download(self.patch.url, self.patch.sha256, report)

    async def install(
        self, transaction: Transaction, progress: Progress | None
    ) -> None:
        raise NotImplementedError

    def present_unmanaged(self) -> bool:
        """The patch looks installed although the manager has no record (installed by hand or by manager <= 1.2)."""
        return False

    def can_remove_unmanaged(self) -> bool:
        return False

    def remove_unmanaged(self) -> None:
        raise NotImplementedError
