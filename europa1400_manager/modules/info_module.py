import hashlib
from pathlib import Path
from typing import Any

import typer

from europa1400_manager.config import Config
from europa1400_manager.const import AppMode
from europa1400_manager.database import Database
from europa1400_manager.models import (
    GameDistribution,
    GameDistributionTable,
    GameDrm,
    GameDrmTable,
    GameEdition,
    GameEditionTable,
    GameExecutable,
    GameExecutableTable,
    GameExecutableToMetadata,
    GameExecutableToMetadataTable,
    GameLanguage,
    GameLanguageTable,
    GameMetadata,
    GameVersion,
    GameVersionTable,
)
from europa1400_manager.modules.base_module import BaseModule
from europa1400_manager.utils import DialogUtils, MetadataUtils


class InfoModule(BaseModule):
    NAME = "info"
    FRIENDLY_NAME = "Information"
    game_metadata: GameMetadata = GameMetadata()
    executable: GameExecutable | None = None

    def __init__(self, config: Config, database: Database) -> None:
        super().__init__(config, database)

        self._reload_game_metadata()

    def show(self) -> None:
        """Display the game information."""
        typer.echo(self.game_metadata)

    def checksums(self) -> list[tuple[Path, str]] | None:
        """Display checksums of the game files."""
        if (
            self.game_metadata.edition is None
            or self._executable_path is None
            or self._tl_executable_path is None
        ):
            return None

        executable_checksum = self._calculate_checksum(self._executable_path)
        tl_executable_checksum = self._calculate_checksum(self._tl_executable_path)

        checksums = [
            (self._executable_path, executable_checksum),
            (self._tl_executable_path, tl_executable_checksum),
        ]

        if self.config.app_mode is AppMode.CLI:
            typer.echo(checksums)

        return checksums

    @property
    def _executable_path(self) -> Path | None:
        """Get the path to the game executable."""
        if self.executable is None:
            return None

        return self.config.game_path / self.executable.path

    @property
    def _tl_executable_path(self) -> Path | None:
        """Get the path to the TL executable."""
        if self.executable is None:
            return None

        return self.config.game_path / self.executable.tl_path

    def _reload_game_metadata(self) -> None:
        """Redetermine the game metadata by re-applying candidate groups."""
        self.game_metadata = GameMetadata()
        executable_mappings = self.database.get_table_elements(
            GameExecutableToMetadataTable, GameExecutableToMetadata
        )
        for executable_mapping in executable_mappings:
            self._apply_executable_mapping(executable_mapping)

    def _apply_executable_mapping(
        self, executable_mapping: GameExecutableToMetadata
    ) -> None:
        """Apply a group of candidate executable files to the game information."""
        game_executable = self.database.get_table_element(
            executable_mapping.executable, GameExecutableTable, GameExecutable
        )

        exe_path = self.config.game_path / game_executable.path
        tl_exe_path = self.config.game_path / game_executable.tl_path

        if not exe_path.exists() or not tl_exe_path.exists():
            return

        game_metadata = GameMetadata()
        if executable_mapping.metadata.edition:
            game_metadata.edition = self.database.get_table_element(
                executable_mapping.metadata.edition, GameEditionTable, GameEdition
            )
        if executable_mapping.metadata.version:
            game_metadata.version = self.database.get_table_element(
                executable_mapping.metadata.version, GameVersionTable, GameVersion
            )
        if executable_mapping.metadata.distribution:
            game_metadata.distribution = self.database.get_table_element(
                executable_mapping.metadata.distribution,
                GameDistributionTable,
                GameDistribution,
            )
        if executable_mapping.metadata.language:
            game_metadata.language = self.database.get_table_element(
                executable_mapping.metadata.language, GameLanguageTable, GameLanguage
            )
        if executable_mapping.metadata.drm:
            game_metadata.drm = self.database.get_table_element(
                executable_mapping.metadata.drm, GameDrmTable, GameDrm
            )

        changes = MetadataUtils.calc_changes(self.game_metadata, game_metadata)
        decisions: list[tuple[str, Any]] = []

        for change in changes:
            result = DialogUtils.ask_yes_no(
                self.config.app_mode,
                f"Change {change[0]} from {change[1][1]} to {change[1][0]}?",
            )

            decisions.append((change[0], change[1][0] if result else change[1][1]))

        MetadataUtils.merge(self.game_metadata, game_metadata, decisions)
        self.executable = game_executable

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate the checksum of a file."""
        hash_md5 = hashlib.md5()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
