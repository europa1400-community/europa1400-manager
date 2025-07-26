import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Any

from pyee import EventEmitter

from europa1400_manager.config import Config
from europa1400_manager.const import EVENT_UPDATE_ALL_MODULES
from europa1400_manager.modules.base_module_gui import BaseModuleGui
from europa1400_manager.modules.config_module import ConfigModule
from europa1400_manager.utils import DialogUtils


class ConfigModuleGui(BaseModuleGui, ConfigModule):
    FRIENDLY_NAME = "Configuration"

    def __init__(
        self,
        config: Config,
        event_emitter: EventEmitter,
        root: tk.Tk,
        notebook: ttk.Notebook,
    ) -> None:
        super().__init__(config, event_emitter, root, notebook)

        top_frame = ttk.Frame(self.tab)
        top_frame.pack(fill="x", pady=(0, 10))
        reset_button = ttk.Button(
            top_frame,
            text="Reset to Defaults",
            command=self._on_reset_to_defaults_clicked,
        )
        reset_button.pack(side="right", padx=(5, 0))

        self.game_path_var = tk.StringVar()
        self.game_path_var.trace_add("write", self._on_game_path_changed)

        main_frame = ttk.Frame(self.tab)
        main_frame.pack(expand=True, fill="both")

        config_frame = ttk.LabelFrame(
            main_frame, text="Game Configuration", padding="10"
        )
        config_frame.pack(fill="x", pady=(0, 10))

        game_path_frame = ttk.Frame(config_frame)
        game_path_frame.pack(fill="x", pady=2)
        ttk.Label(game_path_frame, text="Game Path:", width=15, anchor="w").pack(
            side="left"
        )
        game_path_entry = ttk.Entry(game_path_frame, textvariable=self.game_path_var)
        game_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        browse_button = ttk.Button(
            game_path_frame, text="Browse...", command=self._on_browse_game_path_clicked
        )
        browse_button.pack(side="right")

    def _on_config_changed(self) -> None:
        self.config.game_path = Path(self.game_path_var.get())
        self.config.to_file()
        self.event_emitter.emit(EVENT_UPDATE_ALL_MODULES)

    def _on_game_path_changed(self, *args: Any) -> None:
        self._on_config_changed()

    def _on_reset_to_defaults_clicked(self) -> None:
        if not DialogUtils.ask_yes_no(
            self.config.app_mode,
            "Are you sure you want to reset the configuration to defaults? This will delete the current configuration.",
            default=False,
        ):
            return

        self.config.reset()

        self.event_emitter.emit(EVENT_UPDATE_ALL_MODULES)

    def _on_browse_game_path_clicked(self) -> None:
        selected_path = filedialog.askdirectory(
            title="Select Europa 1400 Game Directory",
            initialdir=str(self.config.game_path)
            if self.config.game_path.exists()
            else str(Path.home()),
        )
        if selected_path:
            self.game_path_var.set(selected_path)
            self._on_config_changed()

    def _update_gui(self) -> None:
        self.game_path_var.set(str(self.config.game_path))
