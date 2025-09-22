from abc import ABC, abstractmethod
from pathlib import Path

from europa1400_manager.config import Config
from europa1400_manager.models import FileOperation, GamePatch
from europa1400_manager.utils import IniUtils


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
    @abstractmethod
    def is_installed(self) -> bool:
        """Check if the patch is installed."""

    @abstractmethod
    async def install(self) -> None:
        """Install the patch."""

    @abstractmethod
    async def uninstall(self) -> None:
        """Uninstall the patch."""

    async def execute_file_operations(self) -> None:
        """Execute file operations defined in the game patch configuration."""
        if not self.game_patch.file_operations:
            return

        for file_operation in self.game_patch.file_operations:
            if file_operation.type == "ini":
                await self._execute_ini_file_operation(file_operation)
            else:
                raise ValueError(
                    f"Unsupported file operation type: {file_operation.type}"
                )

    async def _execute_ini_file_operation(self, operation: FileOperation) -> None:
        """Execute an INI file operation."""
        if (
            not operation.file_name
            or not operation.section
            or not operation.key
            or not operation.value
        ):
            raise ValueError(
                "file_name, section, key, and value must be set for INI operations"
            )

        ini_file_path = self.config.game_path / Path(operation.file_name)

        IniUtils.set_key_value(
            ini_file_path, operation.section, operation.key, operation.value
        )
