import hashlib
from pathlib import Path
from typing import Any

import typer

from europa1400_manager.const import AppMode
from europa1400_manager.game_metadata import CANDIDATE_GROUPS, GameMetadata
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.modules.config_module import ConfigModule
from europa1400_manager.utils import DialogUtils


class InfoModule(BaseModule):
    NAME = "info"
    FRIENDLY_NAME = "Information"
    game_metadata: GameMetadata = GameMetadata()

    def __init__(self, app_mode: AppMode, config_module: ConfigModule) -> None:
        super().__init__(app_mode)
        self.config_module = config_module

        for candidate_group in CANDIDATE_GROUPS:
            self._apply_candidate_group(candidate_group)

    def show(self) -> None:
        """Display the game information."""
        typer.echo(self.game_metadata)

    def checksums(self) -> list[tuple[Path, str]]:
        """Display checksums of the game files."""
        executable_checksum = self._calculate_checksum(self.executable_path)
        tl_executable_checksum = self._calculate_checksum(self.tl_executable_path)

        checksums = [
            (self.executable_path, executable_checksum),
            (self.tl_executable_path, tl_executable_checksum),
        ]

        if self.app_mode is AppMode.CLI:
            typer.echo(checksums)

        return checksums

    @property
    def executable_path(self) -> Path:
        """Get the path to the game executable."""
        return self.config_module.config.game_path / self.game_metadata.executable_path

    @property
    def tl_executable_path(self) -> Path:
        """Get the path to the TL executable."""
        return (
            self.config_module.config.game_path / self.game_metadata.tl_executable_path
        )

    def _apply_candidate_group(
        self, candidate_group: list[tuple[str, GameMetadata]]
    ) -> None:
        """Apply a group of candidate executable files to the game information."""
        for file_name, game_metadata in candidate_group:
            file_path = self.config_module.config.game_path / file_name

            if not file_path.exists():
                continue

            changes = self.game_metadata.calc_changes(game_metadata)
            decisions: list[tuple[str, Any]] = []

            for change in changes:
                result = DialogUtils.ask_yes_no(
                    self.app_mode,
                    f"Change {change[0]} from {change[1][1]} to {change[1][0]}?",
                )

                decisions.append((change[0], change[1][0] if result else change[1][1]))

            self.game_metadata.merge(game_metadata, decisions)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate the checksum of a file."""
        hash_md5 = hashlib.md5()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
