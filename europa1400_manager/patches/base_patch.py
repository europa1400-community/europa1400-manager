from abc import ABC, abstractmethod

from europa1400_manager.config import Config
from europa1400_manager.models import GamePatch


class BasePatch(ABC):
    config: Config
    game_patch: GamePatch

    def __init__(self, config: Config, game_patch: GamePatch) -> None:
        self.config = config
        self.game_patch = game_patch

    @property
    def name(self) -> str:
        """Get the name of the patch."""
        return self.game_patch.id

    @property
    def friendly_name(self) -> str:
        """Get the friendly name of the patch."""
        return self.game_patch.name

    @property
    def file_name(self) -> str | None:
        """Get the file name for the patch."""
        return self.game_patch.file_name

    @property
    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the patch is installed."""

    @abstractmethod
    async def install(self) -> None:
        """Install the patch."""

    @abstractmethod
    async def uninstall(self) -> None:
        """Uninstall the patch."""
