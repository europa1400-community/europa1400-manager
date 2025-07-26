from dataclasses import dataclass
from pathlib import Path

from dataclass_wizard import JSONWizard, YAMLWizard, json_field

from europa1400_manager.const import (
    AppMode,
)
from europa1400_manager.utils import DialogUtils, PathUtils


@dataclass
class Config(YAMLWizard, JSONWizard):
    game_path: Path
    app_mode: AppMode = json_field(
        "app_mode",
        init=False,
        dump=False,
    )
    config_file_path: Path = json_field(
        "config_file_path",
        dump=False,
        init=False,
        default=PathUtils.get_config_file_path(),
    )

    def to_file(self) -> None:
        """Write the configuration to a file."""

        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        with self.config_file_path.open("w") as config_file:
            config_file.write(self.to_yaml())

    def reset(self) -> None:
        """Reset the configuration to default values."""

        self.config_file_path.unlink(missing_ok=True)
        self.config_file_path = PathUtils.get_config_file_path()
        self.game_path = PathUtils.get_game_path(self.app_mode)

        self.to_file()

    @classmethod
    def init(
        cls,
        app_mode: AppMode,
        game_path: Path | None = None,
    ) -> "Config":
        """Initialize the configuration with default values."""
        if game_path is None:
            game_path = PathUtils.get_game_path(app_mode)

        config = Config(game_path=game_path, app_mode=app_mode)
        config.to_file()

        DialogUtils.tell(
            app_mode,
            f"Configuration initialized with game path: {config.game_path}",
        )

        return config

    @classmethod
    def load(cls, app_mode: AppMode) -> "Config":
        """Read the configuration from a file."""
        config_file_path = PathUtils.get_config_file_path()

        if not config_file_path.exists():
            if DialogUtils.ask_yes_no(
                app_mode,
                f"Configuration file at {config_file_path} not found. Initialize default configuration?",
            ):
                return cls.init(app_mode)
            else:
                exit(1)

        with config_file_path.open("r") as config_file:
            config = cls.from_yaml(config_file.read())
            if not isinstance(config, cls):
                raise TypeError(
                    f"Expected instance of {cls.__name__}, got {type(config).__name__}"
                )
            config.app_mode = app_mode
            return config
