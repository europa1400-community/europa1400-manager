import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.const import EVENT_UPDATE_ALL_MODULES
from europa1400_manager.modules.base_module_gui import BaseModuleGui
from europa1400_manager.modules.info_module import InfoModule


@dataclass
class InfoModuleGui(BaseModuleGui, InfoModule):
    FRIENDLY_NAME = "Information"

    def __init__(
        self,
        config: Config,
        event_emitter: EventEmitter,
        root: tk.Tk,
        notebook: ttk.Notebook,
    ) -> None:
        super().__init__(config, event_emitter, root, notebook)

        # Top row with reload button
        top_frame = ttk.Frame(self.tab)
        top_frame.pack(fill="x", pady=(0, 10))
        reload_button = ttk.Button(
            top_frame, text="Reload", command=self._on_reload_button_clicked
        )
        reload_button.pack(side="right", padx=(5, 0))

        # Main content frame
        main_frame = ttk.Frame(self.tab)
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
        self.game_path_value = ttk.Label(game_path_frame, text="", anchor="w")
        self.game_path_value.pack(side="left", fill="x", expand=True)

        # Executable Path
        executable_path_frame = ttk.Frame(path_frame)
        executable_path_frame.pack(fill="x", pady=2)
        ttk.Label(
            executable_path_frame, text="Executable Path:", width=20, anchor="w"
        ).pack(side="left")
        self.executable_path_value = ttk.Label(
            executable_path_frame, text="", anchor="w"
        )
        self.executable_path_value.pack(side="left", fill="x", expand=True)

        # TL Executable Path
        tl_executable_path_frame = ttk.Frame(path_frame)
        tl_executable_path_frame.pack(fill="x", pady=2)
        ttk.Label(
            tl_executable_path_frame, text="TL Executable Path:", width=20, anchor="w"
        ).pack(side="left")
        self.tl_executable_path_value = ttk.Label(
            tl_executable_path_frame, text="", anchor="w"
        )
        self.tl_executable_path_value.pack(side="left", fill="x", expand=True)

        # Game metadata section
        metadata_frame = ttk.LabelFrame(main_frame, text="Game Metadata", padding="10")
        metadata_frame.pack(fill="x", pady=(0, 10))

        # Edition
        edition_frame = ttk.Frame(metadata_frame)
        edition_frame.pack(fill="x", pady=2)
        ttk.Label(edition_frame, text="Edition:", width=20, anchor="w").pack(
            side="left"
        )
        self.edition_value = ttk.Label(edition_frame, text="", anchor="w")
        self.edition_value.pack(side="left", fill="x", expand=True)

        # Version
        version_frame = ttk.Frame(metadata_frame)
        version_frame.pack(fill="x", pady=2)
        ttk.Label(version_frame, text="Version:", width=20, anchor="w").pack(
            side="left"
        )
        self.version_value = ttk.Label(version_frame, text="", anchor="w")
        self.version_value.pack(side="left", fill="x", expand=True)

        # Distribution
        distribution_frame = ttk.Frame(metadata_frame)
        distribution_frame.pack(fill="x", pady=2)
        ttk.Label(distribution_frame, text="Distribution:", width=20, anchor="w").pack(
            side="left"
        )
        self.distribution_value = ttk.Label(distribution_frame, text="", anchor="w")
        self.distribution_value.pack(side="left", fill="x", expand=True)

        # Language
        language_frame = ttk.Frame(metadata_frame)
        language_frame.pack(fill="x", pady=2)
        ttk.Label(language_frame, text="Language:", width=20, anchor="w").pack(
            side="left"
        )
        self.language_value = ttk.Label(language_frame, text="", anchor="w")
        self.language_value.pack(side="left", fill="x", expand=True)

        # DRM
        drm_frame = ttk.Frame(metadata_frame)
        drm_frame.pack(fill="x", pady=2)
        ttk.Label(drm_frame, text="DRM:", width=20, anchor="w").pack(side="left")
        self.drm_value = ttk.Label(drm_frame, text="", anchor="w")
        self.drm_value.pack(side="left", fill="x", expand=True)

        # Checksums section
        checksum_frame = ttk.LabelFrame(main_frame, text="File Checksums", padding="10")
        checksum_frame.pack(fill="x", pady=(0, 10))

        # Executable Checksum
        executable_checksum_frame = ttk.Frame(checksum_frame)
        executable_checksum_frame.pack(fill="x", pady=2)
        ttk.Label(
            executable_checksum_frame, text="Executable MD5:", width=20, anchor="w"
        ).pack(side="left")
        self.executable_checksum_value = ttk.Label(
            executable_checksum_frame, text="", anchor="w", font=("Courier", 9)
        )
        self.executable_checksum_value.pack(side="left", fill="x", expand=True)

        # TL Executable Checksum
        tl_executable_checksum_frame = ttk.Frame(checksum_frame)
        tl_executable_checksum_frame.pack(fill="x", pady=2)
        ttk.Label(
            tl_executable_checksum_frame,
            text="TL Executable MD5:",
            width=20,
            anchor="w",
        ).pack(side="left")
        self.tl_executable_checksum_value = ttk.Label(
            tl_executable_checksum_frame, text="", anchor="w", font=("Courier", 9)
        )
        self.tl_executable_checksum_value.pack(side="left", fill="x", expand=True)

    def _on_reload_button_clicked(self) -> None:
        """Reload the game metadata."""
        self.event_emitter.emit(EVENT_UPDATE_ALL_MODULES)

    def _update_gui(self) -> None:
        self._reload_game_metadata()

        # Update path fields
        self.game_path_value.config(text=str(self.config.game_path))
        self.executable_path_value.config(text=str(self._executable_path))
        self.tl_executable_path_value.config(text=str(self._tl_executable_path))

        # Update metadata fields
        self.edition_value.config(
            text=self.game_metadata.edition.value
            if self.game_metadata.edition
            else "Unknown"
        )
        self.version_value.config(
            text=self.game_metadata.version.value
            if self.game_metadata.version
            else "Unknown"
        )
        self.distribution_value.config(
            text=self.game_metadata.distribution.value
            if self.game_metadata.distribution
            else "Unknown"
        )
        self.language_value.config(
            text=self.game_metadata.language.value
            if self.game_metadata.language
            else "Unknown"
        )
        self.drm_value.config(
            text=self.game_metadata.drm.value if self.game_metadata.drm else "Unknown"
        )

        # Update checksum fields
        checksums = self.checksums()
        self.executable_checksum_value.config(
            text=checksums[0][1] if checksums else "N/A"
        )
        self.tl_executable_checksum_value.config(
            text=checksums[1][1] if checksums else "N/A"
        )
