from abc import ABC, abstractmethod

from europa1400_manager.config import Config


class BaseTool(ABC):
    NAME: str
    FRIENDLY_NAME: str
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the tool is installed."""

    @abstractmethod
    async def install(self) -> None:
        """Install the tool."""
