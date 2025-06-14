from pathlib import Path

import typer

from europa1400_manager.config import Config
from europa1400_manager.const import (
    DEFAULT_CONFIG_FILE_PATH,
    ENV_CONFIG_FILE_PATH,
    AppMode,
)
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.utils import DialogUtils, EnvUtils


class ConfigModule(BaseModule):
    NAME = "config"
    FRIENDLY_NAME = "Configuration"

    config_file_path: Path
    config: Config

    def __init__(self, app_mode: AppMode) -> None:
        super().__init__(app_mode)

        self.config_file_path = Path(
            EnvUtils.read(ENV_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_PATH)
        )

        if not self.config_file_path.exists():
            result = DialogUtils.ask_yes_no(
                self.app_mode,
                f"Configuration file at {self.config_file_path} not found. Initialize default configuration?",
            )

            if result:
                self.init()
            else:
                raise typer.Exit(code=1)

        self.config = Config.from_file(self.config_file_path)

    def init(
        self,
        game_path: Path | None = None,
    ) -> None:
        if game_path is None:
            while True:
                game_path = Path(
                    DialogUtils.ask(
                        self.app_mode,
                        "Please enter the path to the game directory:",
                        default=str(Path.home() / "Europa 1400"),
                    )
                )

                if self._validate_game_path(game_path):
                    break

        self.config = Config(game_path=game_path)
        self.config.to_file(self.config_file_path)

        DialogUtils.tell(
            self.app_mode,
            f"Configuration initialized with game path: {self.config.game_path}",
        )

    async def show(self) -> None:
        """Show the current configuration."""
        typer.echo(f"Current configuration: {self.config.to_json(indent=2)}")

    def _validate_game_path(self, game_path: Path) -> bool:
        """Validate the game path."""
        if not game_path.exists():
            DialogUtils.tell(self.app_mode, "Invalid game path. Please try again.")
            return False

        return True
