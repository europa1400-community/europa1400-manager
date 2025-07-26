from abc import ABC, abstractmethod

from europa1400_manager.config import Config


class BasePatch(ABC):
    NAME: str
    FRIENDLY_NAME: str
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config

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
