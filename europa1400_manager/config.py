from dataclasses import dataclass
from pathlib import Path
from typing import Self

from dataclass_wizard import JSONWizard, YAMLWizard


@dataclass
class Config(YAMLWizard, JSONWizard):  # type: ignore
    game_path: Path

    def to_file(self, config_file_path: Path) -> None:
        """Write the configuration to a file."""

        config_file_path.parent.mkdir(parents=True, exist_ok=True)

        with config_file_path.open("w") as config_file:
            config_file.write(self.to_yaml())

    @classmethod
    def from_file(cls, config_file_path: Path) -> Self:
        """Read the configuration from a file."""

        if not config_file_path.exists():
            raise FileNotFoundError(
                f"Configuration file '{config_file_path}' does not exist."
            )

        with config_file_path.open("r") as config_file:
            config = cls.from_yaml(config_file.read())
            if not isinstance(config, cls):
                raise TypeError(
                    f"Expected instance of {cls.__name__}, got {type(config).__name__}"
                )
            return config
