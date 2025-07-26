import hashlib
import tkinter as tk
from pathlib import Path
from tkinter import ttk
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

    def _initialize_gui(self, root: tk.Tk, tab: ttk.Frame):
        def reload_button_clicked() -> None:
            """Reload the game metadata."""
            # Reload game metadata by re-applying candidates
            self.game_metadata = GameMetadata()
            for candidate_group in CANDIDATE_GROUPS:
                self._apply_candidate_group(candidate_group)

            # Update all value labels
            update_all_fields()

        def update_all_fields():
            """Update all field values in the GUI."""
            # Update path fields
            game_path_value.config(text=str(self.config_module.config.game_path))
            executable_path_value.config(text=str(self.executable_path))
            tl_executable_path_value.config(text=str(self.tl_executable_path))

            # Update metadata fields
            edition_value.config(
                text=self.game_metadata.edition.value
                if self.game_metadata.edition
                else "Unknown"
            )
            version_value.config(
                text=self.game_metadata.version.value
                if self.game_metadata.version
                else "Unknown"
            )
            distribution_value.config(
                text=self.game_metadata.distribution.value
                if self.game_metadata.distribution
                else "Unknown"
            )
            language_value.config(
                text=self.game_metadata.language.value
                if self.game_metadata.language
                else "Unknown"
            )
            drm_value.config(
                text=self.game_metadata.drm.value
                if self.game_metadata.drm
                else "Unknown"
            )

            # Update checksum fields
            checksums = self.checksums()
            executable_checksum_value.config(
                text=checksums[0][1] if checksums else "N/A"
            )
            tl_executable_checksum_value.config(
                text=checksums[1][1] if len(checksums) > 1 else "N/A"
            )

        # Top row with reload button
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill="x", pady=(0, 10))
        reload_button = ttk.Button(
            top_frame, text="Reload", command=reload_button_clicked
        )
        reload_button.pack(side="right", padx=(5, 0))

        # Main content frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(expand=True, fill="both")

        # Path information section
        path_frame = ttk.LabelFrame(main_frame, text="Paths", padding="10")
        path_frame.pack(fill="x", pady=(0, 10))

        # Game Path
        game_path_frame = ttk.Frame(path_frame)
        game_path_frame.pack(fill="x", pady=2)
        ttk.Label(game_path_frame, text="Game Path:", width=20, anchor="w").pack(
            side="left"
        )
        game_path_value = ttk.Label(game_path_frame, text="", anchor="w")
        game_path_value.pack(side="left", fill="x", expand=True)

        # Executable Path
        executable_path_frame = ttk.Frame(path_frame)
        executable_path_frame.pack(fill="x", pady=2)
        ttk.Label(
            executable_path_frame, text="Executable Path:", width=20, anchor="w"
        ).pack(side="left")
        executable_path_value = ttk.Label(executable_path_frame, text="", anchor="w")
        executable_path_value.pack(side="left", fill="x", expand=True)

        # TL Executable Path
        tl_executable_path_frame = ttk.Frame(path_frame)
        tl_executable_path_frame.pack(fill="x", pady=2)
        ttk.Label(
            tl_executable_path_frame, text="TL Executable Path:", width=20, anchor="w"
        ).pack(side="left")
        tl_executable_path_value = ttk.Label(
            tl_executable_path_frame, text="", anchor="w"
        )
        tl_executable_path_value.pack(side="left", fill="x", expand=True)

        # Game metadata section
        metadata_frame = ttk.LabelFrame(main_frame, text="Game Metadata", padding="10")
        metadata_frame.pack(fill="x", pady=(0, 10))

        # Edition
        edition_frame = ttk.Frame(metadata_frame)
        edition_frame.pack(fill="x", pady=2)
        ttk.Label(edition_frame, text="Edition:", width=20, anchor="w").pack(
            side="left"
        )
        edition_value = ttk.Label(edition_frame, text="", anchor="w")
        edition_value.pack(side="left", fill="x", expand=True)

        # Version
        version_frame = ttk.Frame(metadata_frame)
        version_frame.pack(fill="x", pady=2)
        ttk.Label(version_frame, text="Version:", width=20, anchor="w").pack(
            side="left"
        )
        version_value = ttk.Label(version_frame, text="", anchor="w")
        version_value.pack(side="left", fill="x", expand=True)

        # Distribution
        distribution_frame = ttk.Frame(metadata_frame)
        distribution_frame.pack(fill="x", pady=2)
        ttk.Label(distribution_frame, text="Distribution:", width=20, anchor="w").pack(
            side="left"
        )
        distribution_value = ttk.Label(distribution_frame, text="", anchor="w")
        distribution_value.pack(side="left", fill="x", expand=True)

        # Language
        language_frame = ttk.Frame(metadata_frame)
        language_frame.pack(fill="x", pady=2)
        ttk.Label(language_frame, text="Language:", width=20, anchor="w").pack(
            side="left"
        )
        language_value = ttk.Label(language_frame, text="", anchor="w")
        language_value.pack(side="left", fill="x", expand=True)

        # DRM
        drm_frame = ttk.Frame(metadata_frame)
        drm_frame.pack(fill="x", pady=2)
        ttk.Label(drm_frame, text="DRM:", width=20, anchor="w").pack(side="left")
        drm_value = ttk.Label(drm_frame, text="", anchor="w")
        drm_value.pack(side="left", fill="x", expand=True)

        # Checksums section
        checksum_frame = ttk.LabelFrame(main_frame, text="File Checksums", padding="10")
        checksum_frame.pack(fill="x", pady=(0, 10))

        # Executable Checksum
        executable_checksum_frame = ttk.Frame(checksum_frame)
        executable_checksum_frame.pack(fill="x", pady=2)
        ttk.Label(
            executable_checksum_frame, text="Executable MD5:", width=20, anchor="w"
        ).pack(side="left")
        executable_checksum_value = ttk.Label(
            executable_checksum_frame, text="", anchor="w", font=("Courier", 9)
        )
        executable_checksum_value.pack(side="left", fill="x", expand=True)

        # TL Executable Checksum
        tl_executable_checksum_frame = ttk.Frame(checksum_frame)
        tl_executable_checksum_frame.pack(fill="x", pady=2)
        ttk.Label(
            tl_executable_checksum_frame,
            text="TL Executable MD5:",
            width=20,
            anchor="w",
        ).pack(side="left")
        tl_executable_checksum_value = ttk.Label(
            tl_executable_checksum_frame, text="", anchor="w", font=("Courier", 9)
        )
        tl_executable_checksum_value.pack(side="left", fill="x", expand=True)

        # Initialize all field values
        update_all_fields()
